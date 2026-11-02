"""Side-owned layout migration, exact content handoff and fresh-runtime restore."""
from ui_fixture import load


def plain(value):
    return {k: plain(v) for k, v in value.items()} if hasattr(value, 'items') else value


lua = load()
lua.execute('''
local P=WarscapePanels
function near(a,b) assert(math.abs(a-b)<.001,tostring(a).." != "..tostring(b)) end
function at(id,x,y)
 local frame=P.entries[id].frame
 near(frame:GetCenter()*frame:GetScale(),x)
 near(frame:GetBottom()*frame:GetScale(),y)
end
function drag(id,x,y)
 local entry=P.entries[id];local frame=entry.frame
 entry.header.scripts.OnDragStart(entry.header);assert(frame.moving)
 frame:ClearAllPoints();frame:SetPoint("BOTTOM",UIParent,"BOTTOMLEFT",x/frame:GetScale(),y/frame:GetScale())
 entry.header.scripts.OnDragStop(entry.header);assert(not frame.moving)
 at(id,x,y)
end
function maximumTwo()
 local counts={left=0,right=0}
 for _,entry in pairs(P.entries) do if entry.frame:IsShown() then counts[entry.group]=counts[entry.group]+1 end end
 assert(counts.left<=1 and counts.right<=1)
end
assert(P:State("attackStyles")==P:State("skills"))
assert(P:State("skills")==P:State("equipment"))
assert(P:State("inventory")==P:State("friends"))
assert(P:State("inventory")~=P:State("skills"))
assert(P.entries.inventory.window==P.windows.left and P.entries.skills.window==P.windows.right)

-- Each replacement is already positioned before its OnShow script runs.
P:Open("attackStyles");P:SetLocked("attackStyles",false);drag("attackStyles",1100,240)
local right=P:State("right")
local originalScale=P.entries.attackStyles.frame:GetScale()
local showCount=0
for _,id in ipairs({"skills","equipment","prayer","spellbook","attackStyles"}) do
 local target=id
 P.entries[id].frame:SetScript("OnShow",function()
  at(target,1100,240)
  assert(not P:State(target).locked)
  near(P.entries[target].frame:GetScale(),originalScale)
  showCount=showCount+1
 end)
end
for _,id in ipairs({"skills","equipment","prayer","spellbook","attackStyles","skills"}) do
 P:Open(id);at(id,1100,240);maximumTwo()
 assert(P.activeGroups.right==id and right.lastMenu==id)
end
assert(showCount==6)
for _,entry in pairs(P.entries) do entry.frame:SetScript("OnShow",nil) end
assert(not WarscapeAttackStylesFrame:IsShown() and WarscapeSkillsFrame:IsShown())
assert(WarscapeHUDMenuButton6.highlight and not WarscapeHUDMenuButton8.highlight)

-- Left movement, state and scale do not change the right container or HUD.
P:Open("inventory");P:SetLocked("inventory",false);drag("inventory",650,190)
local left=P:State("left")
for _,id in ipairs({"friends","quests","settings","inventory"}) do
 P:Open(id);at(id,650,190);maximumTwo();at("skills",1100,240)
end
local leftScale,hudScale=P:GetScale("left"),WarscapeHUDFrame:GetScale()
P:AdjustScale("skills",1)
assert(P:GetScale("right")>leftScale and P:GetScale("left")==leftScale)
assert(WarscapeHUDFrame:GetScale()==hudScale)
originalScale=P.entries.skills.frame:GetScale()
P:ToggleOrientation("skills")
assert(right.orientation=="portrait" and left.orientation=="landscape")
for _,id in ipairs({"attackStyles","equipment","skills"}) do
 P:Open(id);at(id,1100,240)
 assert(P:State(id)==right and P:State(id).orientation=="portrait")
 near(P.entries[id].frame:GetScale(),originalScale)
end
P:AdjustScale("inventory",-1)
assert(left.scale<1 and right.scale>1)
P:ToggleOrientation("inventory")
P:Open("friends");at("friends",650,190)
assert(left.orientation=="portrait" and not left.locked)

-- Larger/smaller future content shares the bottom centre and side envelope.
for _,spec in ipairs({{"tinyRight",300,180},{"largeRight",1000,850}}) do
 local frame=CreateFrame("Frame",spec[1],UIParent);frame:SetSize(spec[2],spec[3]);frame:Hide()
 P:Register(spec[1],frame,{group="right"})
end
P:Open("tinyRight");local effective=P.entries.tinyRight.frame:GetScale()
at("tinyRight",1100,240)
P:Open("largeRight");at("largeRight",1100,240)
near(effective,P.entries.largeRight.frame:GetScale())
right.position={x=.97,y=.9};P:RefreshWindow("right")
local preferred=right.position
local resolved=P.windows.right.position
for _,id in ipairs({"tinyRight","largeRight","skills","largeRight"}) do
 P:Open(id)
 at(id,resolved.x*1920,resolved.y*1080)
 assert(right.position==preferred and right.position.x==.97 and right.position.y==.9)
end
local x,y,w,h=P.entries.largeRight.frame:Rect()
assert(x>=7.99 and y>=7.99 and x+w<=1912.01 and y+h<=1072.01)

-- Relocking is side-wide and does not reset its scale or chosen orientation.
local orientation,scale=right.orientation,right.scale
P:SetLocked("skills",true)
assert(right.position==nil and right.locked and right.orientation==orientation and right.scale==scale)
assert(not left.locked and left.position and left.orientation=="portrait")
for _,id in ipairs({"skills","attackStyles","equipment"}) do
 P:Open(id)
 local point,dock=P.entries[id].frame:GetPoint()
 assert(point=="BOTTOMLEFT" and dock==WarscapeHUDRightMenuDock)
 assert(P.entries[id].frame.warscapeChrome.locked)
 P.entries[id].header.scripts.OnDragStart(P.entries[id].header)
 assert(not P.entries[id].frame.moving)
end
P:SetLocked("skills",false);drag("skills",1100,240)
P:Close("skills");P:Open("attackStyles");at("attackStyles",1100,240)
P:Close("attackStyles");P:Close("friends")
''')

saved = {key: plain(lua.globals()[key]) for key in ['WarscapeWindowLayouts', 'WarscapeHUDScales']}
for restart in range(2):  # /reload and a second fresh client-like Lua lifetime
    restarted = load(saved)
    restarted.execute('''
        local P=WarscapePanels
        assert(not P:State("left").locked and not P:State("right").locked)
        assert(P:State("left").orientation=="portrait" and P:State("right").orientation=="portrait")
        assert(P:GetScale("left")<1 and P:GetScale("right")>1)
        for _,id in ipairs({"attackStyles","skills","equipment"}) do
            P:Open(id)
            local f=P.entries[id].frame
            assert(math.abs(f:GetCenter()*f:GetScale()-1100)<.001)
            assert(math.abs(f:GetBottom()*f:GetScale()-240)<.001)
        end
        for _,id in ipairs({"inventory","friends","quests"}) do
            P:Open(id)
            local f=P.entries[id].frame
            assert(math.abs(f:GetCenter()*f:GetScale()-650)<.001)
            assert(math.abs(f:GetBottom()*f:GetScale()-190)<.001)
        end
    ''')
    saved = {key: plain(restarted.globals()[key]) for key in saved}

# Detached legacy records outrank the default records created for every menu.
legacy = {
    'WarscapePanelLayouts': {
        'skills': {'locked': True, 'orientation': 'landscape'},
        'attackStyles': {'locked': False, 'orientation': 'portrait', 'position': {'x': .60, 'y': .20}},
        'inventory': {'locked': True, 'orientation': 'landscape'},
        'friends': {'locked': False, 'orientation': 'landscape', 'position': {'x': .30, 'y': .15}},
    },
    'WarscapePanelScales': {'universal': 1.15},
}
migrated = load(legacy)
assert plain(migrated.globals().WarscapePanelLayouts) == legacy['WarscapePanelLayouts']
assert plain(migrated.globals().WarscapePanelScales) == legacy['WarscapePanelScales']
migrated.execute('''
    local P=WarscapePanels
    local left,right=P:State("left"),P:State("right")
    assert(left.migratedFrom=="friends" and right.migratedFrom=="attackStyles")
    assert(not left.locked and not right.locked and right.orientation=="portrait")
    assert(left.position.x==.30 and right.position.x==.60)
    assert(left.scale==1.15 and right.scale==1.15)
    assert(left.position~=WarscapePanelLayouts.friends.position)
    P:SetLocked("attackStyles",true)
    assert(WarscapePanelLayouts.attackStyles.locked==false)
    P:AdjustScale("skills",-1)
    assert(WarscapePanelScales.universal==1.15 and left.scale==1.15)
''')
saved = dict(legacy, WarscapeWindowLayouts=plain(migrated.globals().WarscapeWindowLayouts))
again = load(saved)
assert plain(again.globals().WarscapeWindowLayouts) == saved['WarscapeWindowLayouts']
assert plain(again.globals().WarscapePanelLayouts) == legacy['WarscapePanelLayouts']
print('PASS: side-owned position/lock/orientation/scale, pre-Show handoff, native/menu switching, independent sides, size envelope, two fresh-runtime restores and non-destructive migration')
