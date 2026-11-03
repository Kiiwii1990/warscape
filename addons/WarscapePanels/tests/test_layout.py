"""Layout/control regression suite using actual Lua 5.1 addon code."""
from ui_fixture import load

lua = load()
lua.execute(r'''
local P=WarscapePanels
WarscapeHUDScales=WarscapeHUDScales or {}
local ids={"settings","friends","quests","inventory","skills","equipment","attackStyles","prayer","spellbook"}
assert(#P.order==9)
function near(a,b) assert(math.abs(a-b)<.001,tostring(a).." != "..tostring(b)) end
function visibleGroups()
    local counts={left=0,right=0}
    for _,e in pairs(P.entries) do if e.frame:IsShown() then counts[e.group]=counts[e.group]+1 end end
    assert(counts.left<=1 and counts.right<=1)
end
function docked(e)
    local x,y,w,h=e.frame:Rect()
    local dx,dy,dw=P.docks[e.group]:Rect()
    near(y,dy)
    near(e.group=="left" and x+w or x,e.group=="left" and dx+dw or dx)
    local _,railY,_,railH=WarscapeHUDRail:Rect();near(y,railY+railH)
end
local before={}
for i=1,28 do
    local b=_G["WarscapeInventorySlot"..i]
    before[i]={b,b:GetParent(),b:GetID(),b.scripts.OnClick,b.scripts.OnDragStart,b.scripts.OnEnter}
end
for _,id in ipairs(ids) do
    local e=P.entries[id];local state=P:State(id)
    assert(state.locked and state.orientation=="landscape")
    assert(e.frame:GetWidth()==700 and e.frame:GetHeight()==460)
    P:Open(id);docked(e);visibleGroups()
    local chrome=e.frame.warscapeChrome
    assert(chrome.lock and chrome.rotate and chrome.close and chrome.locked)
    chrome.lock.scripts.OnEnter(chrome.lock);assert(GameTooltip.text=="Locked to HUD")
    chrome.rotate.scripts.OnEnter(chrome.rotate);assert(GameTooltip.text=="Change orientation")
    e.header.scripts.OnDragStart(e.header);assert(not e.frame.moving)
    for i=1,4 do
        chrome.rotate.scripts.OnClick();docked(e)
        assert(P:State(id).locked and P:State(id).orientation==(i%2==1 and "portrait" or "landscape"))
    end
    local x,y=e.frame:GetCenter();local bottom=e.frame:GetBottom()
    chrome.lock.scripts.OnClick()
    near(x,e.frame:GetCenter());near(bottom,e.frame:GetBottom())
    assert(not P:State(id).locked and not chrome.locked)
    e.header.scripts.OnDragStart(e.header);assert(e.frame.moving)
    e.frame:ClearAllPoints();e.frame:SetPoint("BOTTOM",UIParent,"BOTTOMLEFT",960/e.frame:GetScale(),200/e.frame:GetScale())
    e.header.scripts.OnDragStop(e.header);assert(not e.frame.moving)
    local x=e.frame:GetCenter()*e.frame:GetScale();local y=e.frame:GetBottom()*e.frame:GetScale()
    for i=1,4 do
        chrome.rotate.scripts.OnClick()
        near(x,e.frame:GetCenter()*e.frame:GetScale());near(y,e.frame:GetBottom()*e.frame:GetScale())
        P:AdjustScale(id,i%2==1 and -1 or 1)
        near(x,e.frame:GetCenter()*e.frame:GetScale());near(y,e.frame:GetBottom()*e.frame:GetScale())
        visibleGroups()
    end
    chrome.rotate.scripts.OnClick();assert(P:State(id).orientation=="portrait")
    chrome.lock.scripts.OnClick();assert(P:State(id).locked and P:State(id).position==nil)
    assert(P:State(id).orientation=="portrait");docked(e)
    P:AdjustScale(id,1);docked(e)
    P:Close(id);P:Open(id);assert(P:State(id).orientation=="portrait");docked(e)
    chrome.rotate.scripts.OnClick();P:Close(id)
end
-- Settings follows Blizzard's post-toggle state without treating ancestor
-- visibility as the menu's logical open/closed state or recursing into toggle.
local settings=P.entries.settings.frame
menuToggleCount=menuToggleCount or 0
assert(secureHooks.ToggleGameMenu==1, "Settings installs one secure post-hook")
P:Open("skills")
WarscapeHUDMenuButton1.scripts.OnClick(WarscapeHUDMenuButton1)
assert(GameMenuFrame:IsShown() and settings:IsShown(),
    "HUD Settings button opens Blizzard and Warscape together")
WarscapeHUDMenuButton1.scripts.OnClick(WarscapeHUDMenuButton1)
assert(not GameMenuFrame:IsShown() and not settings:IsShown(), "HUD Settings button closes both together")
for pass=1,8 do
    local toggles=menuToggleCount
    ToggleGameMenu()
    assert(menuToggleCount==toggles+1, "post-hook must not recursively toggle Blizzard's menu")
    assert(GameMenuFrame:IsShown() and settings:IsShown() and GameMenuFrame:IsVisible() and settings:IsVisible())
    assert(WarscapeSkillsFrame:IsShown(), "Settings must preserve the other panel group")
    ToggleGameMenu()
    assert(not GameMenuFrame:IsShown() and not settings:IsShown())
end
ToggleGameMenu()
assert(GameMenuFrame:IsShown() and settings:IsShown())
UIParent:Hide()
assert(GameMenuFrame:IsShown() and settings:IsShown() and not GameMenuFrame:IsVisible()
    and not settings:IsVisible(), "IsShown remains authoritative under a hidden ancestor")
ToggleGameMenu()
assert(not GameMenuFrame:IsShown() and not settings:IsShown(), "Escape closes despite IsShown/IsVisible divergence")
UIParent:Show()
P:Close("settings")
-- Orientation is independent; detached same-side windows still replace one another.
P:Open("inventory");P:Open("skills");P:SetLocked("inventory",false)
P:ToggleOrientation("inventory")
assert(P:State("skills").orientation=="landscape")
P:Open("friends");assert(not WarscapeInventoryFrame:IsShown() and WarscapeSkillsFrame:IsShown())
P:SetLocked("friends",false);P:Open("quests")
assert(not FriendsFrame:IsShown() and not P.entries.friends.frame:IsShown());visibleGroups()
ToggleFriendsFrame();assert(FriendsFrame:IsShown() and not QuestLogFrame:IsShown())
nativeControl.scripts.OnClick(nativeControl);assert(socialClicks==1)
ctrl=false;nativeControl.scripts.OnMouseWheel(nativeControl,-1);assert(socialWheels==1)
local scale=P:GetScale("friends")
local rightScale=P:GetScale("skills")
ctrl=true;nativeControl.scripts.OnMouseWheel(nativeControl,-1);ctrl=false
assert(P:GetScale("friends")<scale and socialWheels==1)
for _,e in pairs(P.entries) do if e.group=="left" then near(e.frame:GetScale(),WarscapeInventoryFrame:GetScale()) end end
assert(P:GetScale("skills")==rightScale)
-- Reflow never recreates or renumbers a slot, or swaps native callbacks.
for i=1,28 do
    local b=_G["WarscapeInventorySlot"..i];local old=before[i]
    assert(b==old[1] and b:GetParent()==old[2] and b:GetID()==old[3])
    assert(b.scripts.OnClick==old[4] and b.scripts.OnDragStart==old[5] and b.scripts.OnEnter==old[6])
    assert(not b.scripts.OnDragStop and not b.warscapeChrome)
end
-- Initial 24-slot authorization, unchanged native mapping and cursor safety.
local token
for _,m in ipairs(messages) do if m[1]=="WCInventory" then token=m[2]:match("HELLO|1|(.+)") end end
dispatch("CHAT_MSG_ADDON","WCInventory","STATE|1|"..token.."|1|READY|24|1","WHISPER","Tester")
cursorItem=true;local callCount=#calls
for pass=1,12 do
    P:ToggleOrientation("inventory")
    for i=25,28 do
        local b=_G["WarscapeInventorySlot"..i]
        assert(b.warscapeLocked and b.padlock:IsShown())
        b.scripts.OnClick(b,"RightButton");b.scripts.OnDragStart(b);b.scripts.OnReceiveDrag(b)
    end
end
assert(cursorItem and #calls==callCount)
-- Resolution, global UI scale, HUD scale, user scale and both shapes.
for _,resolution in ipairs({{1280,720},{1920,1080},{2560,1440},{3440,1440}}) do
 for _,uiScale in ipairs({.64,.8,1}) do
  UIParent:SetScale(uiScale);UIParent:SetSize(resolution[1]/uiScale,resolution[2]/uiScale)
  for _,hudScale in ipairs({.5,1,1.5}) do
   WarscapeHUDScales.hud=hudScale;dispatch("PLAYER_LOGIN")
   local _,_,hudWidth=WarscapeHUDFrame:Rect();assert(hudWidth<=UIParent:GetWidth()*.981)
   for _,preference in ipairs({.5,1,1.5}) do
    P:State("left").scale=preference;P:State("right").scale=preference
    for _,orientation in ipairs({"landscape","portrait"}) do
     for _,e in pairs(P.entries) do
      local state=P:State(e.id);state.locked=true;state.orientation=orientation;P:Layout(e)
     end
     P:RestoreScales()
     for _,e in pairs(P.entries) do
      docked(e)
      local x,y,w,h=e.frame:Rect()
      assert(x>=7.9 and x+w<=UIParent:GetWidth()-7.9 and y+h<=UIParent:GetHeight()-7.9)
     end
    end
   end
  end
 end
end
UIParent:SetScale(1);UIParent:SetSize(1920,1080)
WarscapeHUDScales.hud=1;P:State("left").scale=1;P:State("right").scale=1;dispatch("PLAYER_LOGIN")
for _,e in pairs(P.entries) do
 local state=P:State(e.id);state.locked=true;state.orientation="landscape";state.position=nil;P:Layout(e)
end
P:RestoreScales()
P:ToggleOrientation("inventory");P:SetLocked("inventory",false)
local f=WarscapeInventoryFrame
local header=P.entries.inventory.header
header.scripts.OnDragStart(header)
f:ClearAllPoints();f:SetPoint("BOTTOM",UIParent,"BOTTOMLEFT",1000/f:GetScale(),210/f:GetScale())
header.scripts.OnDragStop(header)
P:Close("inventory");P:Open("inventory")
near(f:GetCenter()*f:GetScale(),1000);near(f:GetBottom()*f:GetScale(),210)
P:Close("inventory")
''')


def plain(value):
    if hasattr(value, 'items'):
        return {k: plain(v) for k, v in value.items()}
    return value


saved = {name: plain(lua.globals()[name]) for name in ['WarscapeWindowLayouts', 'WarscapePanelScales', 'WarscapePanelLayouts', 'WarscapeHUDScales']}
reloaded = load(saved)
reloaded.execute('''
    local P=WarscapePanels
    assert(not P:State("inventory").locked and P:State("inventory").orientation=="portrait")
    assert(P:State("skills").locked and P:State("skills").orientation=="landscape")
    local f=WarscapeInventoryFrame
    assert(math.abs(f:GetCenter()*f:GetScale()-1000)<.001)
    assert(math.abs(f:GetBottom()*f:GetScale()-210)<.001)
    P:SetLocked("inventory",true)
    assert(P:State("inventory").orientation=="portrait" and not P:State("inventory").position)
''')
print('PASS: nine menus, anchors, independent locks/orientations, stable dragging/scaling, slot safety, native controls, replacement, saved-state reload, and 216 viewport/scale/shape combinations across nine menus')
