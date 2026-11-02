"""Quantify paired layout and sizing using the real Lua addon code, not a game."""
import argparse
import json
from pathlib import Path

import test_layout

lua = test_layout.load()
lua.execute('''
local P=WarscapePanels
-- Legacy texture regions inherit their parent's scale; GetEffectiveScale is a
-- Frame method in the real client, even though the generic mock exposes it.
local original=WarscapeHUDLeftGryphon
WarscapeHUDLeftGryphon={GetLeft=function() return 10 end,GetBottom=function() return 5 end,
 GetWidth=function() return 20 end,GetHeight=function() return 15 end,
 GetParent=function() return UIParent end,IsShown=function() return true end}
assert(P:GeometrySnapshot().leftGryphon.width==20*UIParent:GetEffectiveScale())
WarscapeHUDLeftGryphon=original
function closeAll() for _,id in ipairs(P.order) do P:Close(id) end end
function assertSymmetry()
 local snapshot=P:GeometrySnapshot()
 local c=snapshot.comparison
 assert(c and c.comparable)
 for _,key in ipairs({"widthError","heightError","topError","bottomError","mirrorError"}) do
  assert(c[key]<.001,key..": "..tostring(c[key]))
 end
 return snapshot
end
local left={"inventory","settings","friends","quests"}
local right={"skills","equipment","attackStyles","prayer","spellbook"}
pairedChecks=0
for _,orientation in ipairs({"landscape","portrait"}) do
 for _,a in ipairs(left) do for _,b in ipairs(right) do
  closeAll()
  for _,id in ipairs({a,b}) do
   local e=P.entries[id];local s=P:State(id);s.locked=true;s.orientation=orientation;P:Layout(e)
  end
  P:RestoreScales();P:Open(a);P:Open(b);assertSymmetry();pairedChecks=pairedChecks+1
 end end
end
closeAll()
local configurations=0
for _,resolution in ipairs({{1280,720},{1920,1080},{2560,1440},{3440,1440}}) do
 for _,uiScale in ipairs({.64,.8,1}) do
  UIParent:SetScale(uiScale);UIParent:SetSize(resolution[1]/uiScale,resolution[2]/uiScale)
  for _,hudScale in ipairs({.5,1,1.5}) do
   WarscapeHUDScales={hud=hudScale};dispatch("PLAYER_LOGIN")
   for _,userScale in ipairs({.5,1,1.5}) do
    for _,orientation in ipairs({"landscape","portrait"}) do
     for _,id in ipairs({"inventory","skills"}) do
      local s=P:State(id);s.locked=true;s.orientation=orientation;P:Layout(P.entries[id])
     end
     P:State("left").scale=userScale;P:State("right").scale=userScale;P:RestoreScales()
     P:Open("inventory");P:Open("skills")
     local snapshot=assertSymmetry()
     local center=snapshot.minimap.left+snapshot.minimap.width/2
     assert(math.abs(center-resolution[1]/2)<.001)
     for i=1,5 do
      local a,b=snapshot.buttons[i],snapshot.buttons[11-i]
      assert(math.abs(a.width-b.width)<.001 and math.abs(a.height-b.height)<.001)
      assert(math.abs((a.left+a.width/2)+(b.left+b.width/2)-2*center)<.001)
      assert(math.abs(a.bottom-b.bottom)<.001)
     end
     configurations=configurations+1
    end
   end
  end
 end
end
assert(configurations==216 and pairedChecks==40)
-- A utility command obtains the same bounds without changing layout or settings.
local position=P:State("inventory").position
local scale=P:GetScale("inventory")
DEFAULT_CHAT_FRAME={AddMessage=function(self,line) self[#self+1]=line end}
SlashCmdList.WARSCAPEGEOMETRY()
assert(#DEFAULT_CHAT_FRAME>=3 and P:GetScale("inventory")==scale)
assert(P:State("inventory").position==position)

-- Reference sizing uses the common default preference; HUD and panels retain
-- their independently adjustable established settings outside this reference.
UIParent:SetScale(1);UIParent:SetSize(1920,1080)
WarscapeHUDScales={hud=1};P:State("left").scale=1;P:State("right").scale=1;dispatch("PLAYER_LOGIN")
for _,e in pairs(P.entries) do local s=P:State(e.id);s.locked=true;s.orientation="landscape";P:Layout(e) end
P:RestoreScales();P:Open("inventory");P:Open("skills")
reference=assertSymmetry()
local slot=WarscapeInventorySlot1
local slotPixels=slot:GetWidth()*slot:GetEffectiveScale()
local hudPixels=WarscapeHUDMenuButton5:GetWidth()*WarscapeHUDMenuButton5:GetEffectiveScale()
assert(hudPixels>slotPixels and hudPixels/slotPixels<1.3)
assert(hudPixels>=56-1 and hudPixels<=60+1 and slotPixels>=46-1 and slotPixels<=50+1)
local lock=WarscapeInventoryFrame.warscapeChrome.lock
assert(lock:GetWidth()*lock:GetEffectiveScale()<slotPixels*.6)
for i=1,28 do
 local button=_G["WarscapeInventorySlot"..i]
 assert(button:GetWidth()==76 and button:GetHeight()==76)
 local left=button:GetLeft()*button:GetEffectiveScale()
 local bottom=button:GetBottom()*button:GetEffectiveScale()
 local parent=reference.panels.inventory
 assert(left>parent.left and left+slotPixels<parent.left+parent.width)
 assert(bottom>parent.bottom+48*button:GetEffectiveScale())
end
reference.slotPixels=slotPixels;reference.hudButtonPixels=hudPixels
reference.landscape={width=WarscapeSkillsSkin.profiles.landscape.width,height=WarscapeSkillsSkin.profiles.landscape.height}
reference.portrait={width=WarscapeSkillsSkin.profiles.portrait.width,height=WarscapeSkillsSkin.profiles.portrait.height}
''')


def plain(value):
    if hasattr(value, 'items'):
        return {str(key): plain(item) for key, item in value.items()}
    return value


report = {
    'passed': True,
    'method': 'Lua 5.1 addon execution with mock engine geometry; no in-game validation',
    'matching_menu_pairs_checked': int(lua.globals().pairedChecks),
    'viewport_scale_orientation_configurations': 216,
    'symmetry_tolerance_pixels': .001,
    'reference_1920x1080': plain(lua.globals().reference),
}
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print('PASS: 40 matching menu pairs, 216 mirrored viewport/scale/orientation configurations, hitbox sizing and read-only /wgeometry diagnostic')
