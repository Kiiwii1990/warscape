from pathlib import Path
from lupa.lua51 import LuaRuntime
root=Path(__file__).resolve().parents[1]
lua=LuaRuntime()
for p in [root.parent/'WarscapePanels/tests/ui_harness.lua',root/'Skin.lua',root.parent/'WarscapePanels/Panels.lua',root/'Smelting.lua']:
 lua.execute(p.read_text())
lua.execute(r"""
local events
for _,w in ipairs(widgets)do if w.events.CHAT_MSG_ADDON then events=w end end
local function recv(m,sender,channel) events.scripts.OnEvent(events,"CHAT_MSG_ADDON","WCSmelt",m,channel or "WHISPER",sender or "Tester") end
local f=WarscapeSmeltingFrame
assert(not f:IsShown())
recv("OPEN|7","Other");assert(not f:IsShown())
recv("OPEN|7","Tester","PARTY");assert(not f:IsShown())
recv("OPEN|7");assert(f:IsShown())
assert(f.width==700 and f.height==460)
assert(not WarscapePanels.entries.smelting)
assert(WarscapePanels.interactions.smelting==f)
assert(not WarscapePanels.activeGroups.left and not WarscapePanels.activeGroups.right)
for i=1,8 do assert(_G["WarscapeSmeltBar"..i].icon.desaturated) end
recv("STATE|7|1|10|10|1|0")
assert(not WarscapeSmeltBar1.icon.desaturated)
for i=2,8 do assert(_G["WarscapeSmeltBar"..i].icon.desaturated) end
local previous=#messages
WarscapeSmeltBar2.scripts.OnClick();assert(#messages==previous)
for i,q in ipairs({1,5,10,0}) do
 _G["WarscapeSmeltQuantity"..i].scripts.OnClick()
 for j=1,4 do assert(_G["WarscapeSmeltQuantity"..j].selected:IsShown()==(i==j)) end
 WarscapeSmeltBar1.scripts.OnClick()
 assert(messages[#messages][1]=="WCSmelt")
 assert(messages[#messages][2]=="START|7|"..i.."|bronze|"..q)
end
recv("STATE|7|1|0|10|0|0");assert(WarscapeSmeltBar1.icon.desaturated)
WarscapeSmeltBar1.scripts.OnEnter(WarscapeSmeltBar1)
assert(string.find(GameTooltip.lines[#GameTooltip.lines][1],"Missing ingredients"))
recv("STATE|7|0|10|10|1|0");assert(WarscapeSmeltBar1.icon.desaturated)
recv("STATE|7|1|10|10|0|0");assert(WarscapeSmeltBar1.icon.desaturated)
recv("STATE|7|1|10|10|1|1");assert(WarscapeSmeltBar1.icon.desaturated)
local scale=f:GetScale()
controlDown=true
-- Harness uses a global ctrl flag for IsControlKeyDown; override only the test input.
function IsControlKeyDown()return true end
f.scripts.OnMouseWheel(f,1);assert(f:GetScale()>scale)
assert(WarscapeWindowLayouts==nil or not WarscapeWindowLayouts.left)
recv("STATE|7|1|10|10|1|0")
WarscapeSmeltBar1.scripts.OnClick();assert(messages[#messages][2]=="START|7|5|bronze|0")
local before=#messages
recv("ACCEPT|7|5");assert(not f:IsShown() and #messages==before)
recv("OPEN|8");recv("CLOSE|7");assert(f:IsShown())
recv("STATE|8|1|10|10|1|0");WarscapeSmeltBar1.scripts.OnClick();assert(f:IsShown())
recv("REJECT|8|1");assert(f:IsShown() and string.find(f.status.text,"Request rejected"))
recv("CLOSE|8");assert(not f:IsShown())
""")
print('PASS: Smelting Lua 5.1 availability, disabled slots, quantities, tokens, close and independent scale')
