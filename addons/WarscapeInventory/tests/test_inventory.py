"""Real addon integration plus native 3.3.5 item scripts read from wowdecomp assets.

Mocks replace the engine/network; this is not a live loot or rendering test.
"""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

ADDONS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ADDONS / 'WarscapeHUD/tools'))
from client_assets import ClientAssets

assets = ClientAssets(Path(r'C:\WoWDev\wowdecomp\bin\Win'))
lua = LuaRuntime()
lua.execute((ADDONS / 'WarscapePanels/tests/ui_harness.lua').read_text(encoding='utf-8'))
for path in ['ItemButtonTemplate.lua', 'ContainerFrame.lua']:
    data, _ = assets.get('Interface\\FrameXML\\' + path)
    lua.execute(data.decode('utf-8-sig'))
data, _ = assets.get('Interface\\FrameXML\\ContainerFrame.xml')
template = ET.fromstring(data).find("{*}Button[@name='ContainerFrameItemButtonTemplate']/{*}Scripts")
scripts = lua.table()
for script in template:
    key = script.tag.rsplit('}', 1)[-1]
    scripts[key] = lua.eval('function(self, button, motion)\n' + (script.text or '') + '\nend')
lua.globals().nativeTemplateScripts = scripts
for folder, files in [
    ('WarscapePanels', ['Panels.lua']),
    ('WarscapeSkills', ['Protocol.lua', 'Skin.lua', 'WarscapeSkills.lua', 'Bindings.lua']),
    ('WarscapeInventory', ['Inventory.lua', 'Bindings.lua']),
    ('WarscapeHUD', ['WarscapeHUD.lua']),
]:
    for file in files:
        lua.execute((ADDONS / folder / file).read_text(encoding='utf-8'))
actions = lua.table()
for folder in ['WarscapeInventory', 'WarscapeSkills']:
    for binding in ET.parse(ADDONS / folder / 'Bindings.xml').getroot():
        actions[binding.attrib['name']] = lua.eval('function() ' + binding.text + ' end')
lua.globals().bindingActions = actions
lua.execute(r'''
function press(key)
    for _,w in ipairs(widgets) do
        if w.overrides and w.overrides[key] then return bindingActions[w.overrides[key]]() end
    end
    error("missing key override: "..key)
end
WarscapeHUDScales={hud=1,skills=0.9}
dispatch("PLAYER_LOGIN")
assert(WarscapePanelScales.skills==0.9 and WarscapePanelScales.inventory==1)
assert(WarscapeSkillsFrame.width==WarscapeInventoryFrame.width and WarscapeSkillsFrame.height==WarscapeInventoryFrame.height)
assert(WarscapeSkillsTotal~=WarscapeInventoryTotal, "shared artwork must not duplicate named panel regions")
assert(not WarscapeInventoryFrame:IsShown() and not WarscapeSkillsFrame:IsShown())
local token
for _,m in ipairs(messages) do if m[1]=="WCInventory" then token=m[2]:match("HELLO|1|(.+)") end end
assert(token)
local function state(revision,count,sender,wire)
    dispatch("CHAT_MSG_ADDON","WCInventory",wire or ("STATE|1|"..token.."|"..revision.."|READY|"..count.."|1"),"WHISPER",sender or "Tester")
end
state(1,28,"Attacker")
assert(WarscapeInventorySlot1.warscapeLocked)
state(1,24)
for i=1,28 do
    local b=_G["WarscapeInventorySlot"..i]
    assert(b.logical==i and b.point[4]==78+((i-1)%4)*100 and b.point[5]==-102-math.floor((i-1)/4)*46)
    assert(b:GetParent():GetID()==(i<=16 and 0 or 1))
    assert(b:GetID()==(i<=16 and i or i-16))
    assert(b.warscapeLocked==(i>24))
    assert(b.padlock:IsShown()==(i>24))
end
assert(WarscapeInventorySlot1.count==10)
local firstCall=#calls
cursorItem=true
for i=25,28 do
    local b=_G["WarscapeInventorySlot"..i]
    b.scripts.OnClick(b,"LeftButton");b.scripts.OnClick(b,"RightButton")
    b.scripts.OnDragStart(b,"LeftButton");b.scripts.OnReceiveDrag(b)
end
assert(#calls==firstCall, "locked slots never invoke native item actions")
assert(cursorItem, "rejected locked-slot drops preserve the carried cursor item")
cursorItem=false
press("B")
assert(WarscapeInventoryFrame:IsShown() and WarscapeHUDMenuButton5.highlight and not WarscapeHUDMenuButton6.highlight)
press("N")
assert(WarscapeSkillsFrame:IsShown() and not WarscapeInventoryFrame:IsShown())
assert(WarscapeHUDMenuButton6.highlight and not WarscapeHUDMenuButton5.highlight)
press("N");assert(not WarscapeSkillsFrame:IsShown() and not WarscapeHUDMenuButton6.highlight)
press("N");press("B")
assert(WarscapeInventoryFrame:IsShown() and not WarscapeSkillsFrame:IsShown())
press("B");assert(not WarscapeInventoryFrame:IsShown() and not WarscapeHUDMenuButton5.highlight)
WarscapeHUDMenuButton5.scripts.OnClick();WarscapeHUDMenuButton6.scripts.OnClick()
assert(WarscapeSkillsFrame:IsShown() and not WarscapeInventoryFrame:IsShown())
WarscapeHUDMenuButton5.scripts.OnClick();WarscapeInventoryCloseButton.scripts.OnClick()
assert(not WarscapeInventoryFrame:IsShown() and not WarscapeHUDMenuButton5.highlight)
-- Direct Show/Hide and Escape-style dismissal still enforce exclusivity/state.
WarscapeSkillsFrame:Show();WarscapeInventoryFrame:Show()
assert(not WarscapeSkillsFrame:IsShown() and WarscapeHUDMenuButton5.highlight)
WarscapeInventoryFrame:Hide();assert(not WarscapeHUDMenuButton5.highlight)
assert(LootFrame:IsShown() and Confirmation:IsShown(), "temporary interfaces are outside the manager")
local future=CreateFrame("Frame","FuturePrayer",UIParent);future:SetSize(500,514);future:Hide()
WarscapePanels:Register("prayer",future)
press("B");WarscapePanels:Open("prayer")
assert(future:IsShown() and not WarscapeInventoryFrame:IsShown() and not WarscapeHUDMenuButton5.highlight)
WarscapePanels:Close("prayer")
press("N");ContainerFrame1:Show()
assert(not ContainerFrame1:IsShown() and WarscapeInventoryFrame:IsShown() and not WarscapeSkillsFrame:IsShown())
ContainerFrame2:Show();assert(ContainerFrame2:IsShown(), "bank bag windows remain native")
-- Native callbacks, rather than replacement item behavior, handle interactions.
local b=WarscapeInventorySlot1
b.scripts.OnClick(b,"LeftButton")
assert(calls[#calls][1]=="pickup" and calls[#calls][2]==0 and calls[#calls][3]==1)
WarscapeInventorySlot20.scripts.OnReceiveDrag(WarscapeInventorySlot20)
assert(calls[#calls][1]=="pickup" and calls[#calls][2]==1 and calls[#calls][3]==4)
b.scripts.OnClick(b,"RightButton")
assert(calls[#calls][1]=="use" and calls[#calls][2]==0 and calls[#calls][3]==1)
modified="SPLITSTACK";b.scripts.OnClick(b,"LeftButton");modified=nil
assert(calls[#calls][1]=="split-dialog" and calls[#calls][2]==10)
b.SplitStack(b,3)
assert(calls[#calls][1]=="split" and calls[#calls][2]==0 and calls[#calls][3]==1 and calls[#calls][4]==3)
b.scripts.OnEnter(b)
assert(calls[#calls][1]=="tooltip" and calls[#calls][2]==0 and calls[#calls][3]==1)
items["1:8"]={"Interface\\Icons\\INV_Misc_Bone_01",4};dispatch("BAG_UPDATE",1)
assert(WarscapeInventorySlot24.count==4, "native bag update refreshes actual slot/count")
state(1,28);assert(WarscapeInventorySlot28.warscapeLocked, "replayed state cannot unlock")
for _,invalid in ipairs({"STATE|1|"..token.."|2|READY|25|1", "STATE|1|"..token.."|2|READY|28|2",
    "STATE|2|"..token.."|2|READY|28|1", "STATE|1|wrongtoken|2|READY|28|1"}) do
    state(2,28,nil,invalid)
    assert(WarscapeInventorySlot28.warscapeLocked)
end
state(2,28)
assert(WarscapeInventorySlot28.warscapeLocked, "server authorization alone does not invent native storage")
bagSizes[1]=12
for _,w in ipairs(widgets) do
    if w.events.CHAT_MSG_ADDON and w.events.BAG_UPDATE then w.scripts.OnUpdate(w,3.1) end
end
assert(not WarscapeInventorySlot28.warscapeLocked and not WarscapeInventorySlot28.padlock:IsShown())
WarscapeInventorySlot28.scripts.OnClick(WarscapeInventorySlot28,"RightButton")
assert(calls[#calls][1]=="use" and calls[#calls][2]==1 and calls[#calls][3]==12)
-- Each scale changes independently and switching panels never resets it.
local scaler
for _,w in ipairs(widgets) do if w.scripts.OnMouseWheel then scaler=w end end
ctrl=true;WarscapeHUDFrame.over=true;scaler.scripts.OnUpdate(scaler,0)
scaler.scripts.OnMouseWheel(scaler,-1);local h=WarscapeHUDFrame.scale
WarscapeHUDFrame.over=false;WarscapeInventoryFrame.over=true;scaler.scripts.OnUpdate(scaler,0)
scaler.scripts.OnMouseWheel(scaler,-1);local inv=WarscapeInventoryFrame.scale
assert(inv<1 and WarscapeSkillsFrame.scale==0.9 and WarscapeHUDFrame.scale==h)
WarscapeHUDFrame.over=true
scaler.scripts.OnUpdate(scaler,0);scaler.scripts.OnMouseWheel(scaler,-1)
assert(WarscapeHUDFrame.scale==h and WarscapeInventoryFrame.scale<inv, "front panel owns scaling when it overlaps the HUD")
inv=WarscapeInventoryFrame.scale
WarscapeHUDFrame.over=false
press("N");WarscapeInventoryFrame.over=false;WarscapeSkillsFrame.over=true
scaler.scripts.OnUpdate(scaler,0);scaler.scripts.OnMouseWheel(scaler,-1)
local sk=WarscapeSkillsFrame.scale
assert(sk<0.9 and WarscapeInventoryFrame.scale==inv and WarscapeHUDFrame.scale==h)
press("B");assert(WarscapeInventoryFrame.scale==inv)
assert(WarscapePanelScales.inventory==inv and WarscapePanelScales.skills==sk and WarscapeHUDScales.hud==h)
for _,id in ipairs({"inventory","skills"}) do
    for i=1,50 do WarscapePanels:AdjustScale(id,-1) end
    assert(WarscapePanels:GetScale(id)==0.5)
    for i=1,80 do WarscapePanels:AdjustScale(id,1) end
    assert(WarscapePanels:GetScale(id)==1.5)
end
dispatch("PLAYER_LOGIN")
assert(WarscapeInventoryFrame.scale==1.5 and WarscapeSkillsFrame.scale==1.5)
assert(LootFrame:IsShown() and Confirmation:IsShown())
''')
print('PASS: B/N/HUD exclusivity and highlight, future registration, native item/split/drag/tooltip callbacks, 28 slots/24 active, locked interactions, server-state validation, transient windows and independent saved scales')
