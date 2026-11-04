"""Run with Python + lupa (Lua 5.1). No client or account data is read."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]
lua = LuaRuntime()
lua.execute((root / 'Protocol.lua').read_text())
lua.execute(r'''
local P = WarscapeSkillsProtocol
local s = P.New("abc")
local function feed(m, now) return P.Receive(s, m, now or 1) end
assert(not feed("B|2|abc|1|1"))
assert(not feed("B|1|wrong|1|1"))
assert(not s.pending)
feed("B|1|abc|1|1")
assert(not feed("E|1|abc|1")) -- incomplete snapshot is never displayed
feed("S|1|abc|1|attack|1|-|0|0|83")
local d = feed("E|1|abc|1")
assert(d.rows.attack.base == 1 and not d.rows.attack.effective)
assert(not feed("B|1|abc|1|1")) -- replay ignored
feed("B|1|abc|2|1")
feed("S|1|abc|2|attack|12|15|1585|1584|1833")
d = feed("E|1|abc|2")
assert(d.rows.attack.base == 12 and d.rows.attack.effective == 15)
feed("B|1|abc|3|1")
feed("S|1|abc|3|prayer|99|-|200000000|13034431|-")
assert(feed("E|1|abc|3").rows.prayer.nextXP == nil)
feed("B|1|abc|4|2")
feed("S|1|abc|4|attack|1|-|0|0|83")
feed("S|1|abc|4|attack|1|-|0|0|83")
assert(not feed("E|1|abc|4")) -- duplicate cannot satisfy row count
for _, row in ipairs({
    "S|1|abc|5|attack|0|-|0|0|83", "S|1|abc|5|attack|1|bad|0|0|83",
    "S|1|abc|5|attack|1|-|83|0|83", "S|1|abc|5|attack|1|-|-1|0|83",
    "S|1|abc|5|attack|99|-|200000001|13034431|-",
    "S|1|abc|5|attack|1|-|0|0|bad", "S|1|abc|5|a/b|1|-|0|0|83"
}) do
    feed("B|1|abc|5|1")
    feed(row)
    assert(not feed("E|1|abc|5"))
end
feed("B|1|abc|6|1")
feed("S|1|abc|6|attack|1|-|0|0|83", 7)
assert(not feed("E|1|abc|6", 7)) -- timed out
feed("B|1|abc|7|1")
feed("S|1|abc|7|mining|1|-|0|0|83")
assert(feed("E|1|abc|7").rows.mining) -- future IDs need no layout redesign
''')

# Real UI logic uses the shared 3.3.5 widget/geometry harness.
lua.execute((root.parent / 'WarscapePanels/tests/ui_harness.lua').read_text())
lua.execute((root / 'Skin.lua').read_text())
lua.execute((root.parent / 'WarscapePanels' / 'Panels.lua').read_text())
lua.execute((root / 'WarscapeSkills.lua').read_text())
lua.execute(r'''
local events
for _, w in ipairs(widgets) do if w.scripts.OnEvent then events = w end end
local panel = WarscapeSkillsFrame
assert(panel.width==700 and panel.height==460)
WarscapePanels:ToggleOrientation("skills")
assert(not panel:IsShown())
assert(WarscapeSkillsScrollBar.SetShown == nil,
    "3.3.5 frames must use Show/Hide, not SetShown")
assert(WarscapeSkillsScrollBar.SetObeyStepOnDrag == nil,
    "3.3.5 slider compatibility must not depend on SetObeyStepOnDrag")
events.scripts.OnEvent(events, "PLAYER_LOGIN")
assert(#messages == 1 and messages[1][3] == "WHISPER" and messages[1][4] == "Tester")
local token = string.match(messages[1][2], "HELLO|1|(.+)")
local function receive(m, sender, channel)
    events.scripts.OnEvent(events, "CHAT_MSG_ADDON", "WCSkills", m, channel or "WHISPER", sender or "Tester")
end
receive("B|1|"..token.."|1|7", "Other")
local ids = {"attack","strength","defence","hitpoints","ranged","magic","prayer","mining"}
receive("B|1|"..token.."|1|8")
for _, id in ipairs(ids) do
    receive("S|1|"..token.."|1|"..id.."|1|-|0|0|83")
end
receive("E|1|"..token.."|1")
local cells = {}
for _, w in ipairs(widgets) do if w.data then cells[#cells+1] = w end end
assert(#cells == 8)
local placeholder
for _, w in ipairs(widgets) do if w.placeholder then placeholder=w end end
assert(placeholder and placeholder.label == "Next skill")
assert(not WarscapeSkillsScrollBar:IsShown())
assert(cells[1].label == "Attack" and cells[1].level.text == "1/1" and cells[1].bar.value == 0)
assert(cells[1].name == nil, "skill names stay in tooltips, not in the cells")
assert(cells[1].icon.width == 64 and cells[1].icon.height == 64)
assert(cells[1].icon.width > 1.5 * 26, "skill icons are substantially larger")
assert(cells[2].label == "Hitpoints" and cells[3].label == "Strength")
assert(cells[4].label == "Ranged" and cells[5].label == "Defence" and cells[6].label == "Magic")
assert(cells[7].label == "Prayer" and cells[8].label == "Mining")
assert(cells[1].width == 80 and cells[1].height == 104)
assert(cells[1].point[4] == 0 and cells[1].point[5] == 0)
assert(cells[2].point[4] == 87 and cells[2].point[5] == 0)
assert(cells[3].point[4] == 174 and cells[3].point[5] == 0)
assert(cells[7].point[4] == 0 and cells[7].point[5] == -224)
assert(placeholder.point[4] == 174 and placeholder.point[5] == -224)
assert(WarscapeSkillsTotal.value.text == "Total level: 8")
assert(panel.width == 430 and panel.height == 756)
cells[1].scripts.OnEnter(cells[1])
assert(GameTooltip.text == "Attack" and #GameTooltip.lines == 6)
assert(GameTooltip.lines[1][1] == "Current level" and GameTooltip.lines[2][1] == "Attained level")
assert(GameTooltip.lines[1][2] == "1" and GameTooltip.lines[2][2] == "1")
SlashCmdList.WARSCAPESKILLS()
assert(panel:IsShown())
SlashCmdList.WARSCAPESKILLS()
assert(not panel:IsShown())
WarscapeSkills_Toggle()
WarscapeSkillsCloseButton.scripts.OnClick()
assert(not panel:IsShown())
-- Future stable IDs fill remaining cells automatically and expand scrolling.
local expanded = {"attack","hitpoints","strength","ranged","defence","magic","prayer","mining"}
for i=1,17 do expanded[#expanded+1] = string.format("future_%02d", i) end
receive("B|1|"..token.."|2|25")
for _, id in ipairs(expanded) do
    if id == "attack" then
        receive("S|1|"..token.."|2|attack|12|15|1585|1584|1833")
    else
        receive("S|1|"..token.."|2|"..id.."|1|-|0|0|83")
    end
end
receive("E|1|"..token.."|2")
assert(cells[1].level.text == "15/12")
assert(WarscapeSkillsTotal.value.text == "Total level: 36")
assert(cells[1].bar.value > 0 and cells[1].bar.value < 1)
assert(WarscapeSkillsScrollBar:IsShown() and WarscapeSkillsScrollBar.maxValue > 0)
assert(WarscapeSkillsScrollBar.valueStep == 112)
WarscapeSkillsList.scripts.OnMouseWheel(WarscapeSkillsList, -1)
assert(WarscapeSkillsScrollBar.value == 112)
WarscapeSkillsScrollBar:SetValue(WarscapeSkillsScrollBar.maxValue)
assert(WarscapeSkillsList.verticalScroll == WarscapeSkillsScrollBar.maxValue)
local dynamicCells = {}
for _, w in ipairs(widgets) do if w.data then dynamicCells[#dynamicCells+1] = w end end
assert(#dynamicCells == 25 and dynamicCells[9].label == "future_01")
-- Effective levels remain distinct from attained levels and the total.
dynamicCells[1].scripts.OnEnter(dynamicCells[1])
assert(GameTooltip.lines[1][2] == "15" and GameTooltip.lines[2][1] == "Attained level"
    and GameTooltip.lines[2][2] == "12")
assert(GameTooltip.lines[4][1] == "XP to next level" and GameTooltip.lines[5][1] == "XP remaining")

-- Ctrl-wheel scales the panel through the shared saved scale manager without
-- scrolling the grid. Ordinary wheel input continues scrolling by one row.
local scaleBefore = panel:GetScale()
local scrollBefore = WarscapeSkillsScrollBar:GetValue()
ctrl = true
WarscapeSkillsList.scripts.OnMouseWheel(WarscapeSkillsList, 1)
ctrl = false
assert(panel:GetScale() > scaleBefore)
assert(WarscapePanels:GetScale("skills") == panel:GetScale())
assert(WarscapeSkillsScrollBar:GetValue() == scrollBefore)
local savedScale = panel:GetScale()
WarscapePanels:RestoreScales()
assert(panel:GetScale() == savedScale, "Skills scale preference restores from saved panel settings")
WarscapeSkillsList.scripts.OnMouseWheel(WarscapeSkillsList, 1)
assert(WarscapeSkillsScrollBar:GetValue() == math.max(0, scrollBefore - 112),
    "normal wheel scrolls exactly one row when Ctrl is released")
assert(panel:GetScale() == savedScale, "normal scrolling leaves panel scale unchanged")

-- No Warscape boost/drain system exists currently; the server's '-' effective
-- marker means display the actual unmodified attained level in both positions.
receive("B|1|"..token.."|4|8")
for _, id in ipairs({"attack","hitpoints","strength","ranged","defence","magic","prayer","mining"}) do
    receive("S|1|"..token.."|4|"..id.."|10|-|1154|1154|1358")
end
receive("E|1|"..token.."|4")
assert(dynamicCells[1].level.text == "10/10")
assert(WarscapeSkillsTotal.value.text == "Total level: 80")
receive("B|1|"..token.."|5|8")
for _, id in ipairs({"attack","hitpoints","strength","ranged","defence","magic","prayer","mining"}) do
    local effective = id == "attack" and "8" or "-"
    receive("S|1|"..token.."|5|"..id.."|10|"..effective.."|1154|1154|1358")
end
receive("E|1|"..token.."|5")
assert(dynamicCells[1].level.text == "8/10", "drained current level differs from attained")
assert(WarscapeSkillsTotal.value.text == "Total level: 80", "total uses attained levels")
receive("B|1|"..token.."|6|8")
for _, id in ipairs({"attack","hitpoints","strength","ranged","defence","magic","prayer","mining"}) do
    local effective = id == "attack" and "13" or "-"
    receive("S|1|"..token.."|6|"..id.."|10|"..effective.."|1154|1154|1358")
end
receive("E|1|"..token.."|6")
assert(dynamicCells[1].level.text == "13/10", "boosted current level differs from attained")
dynamicCells[1].scripts.OnEnter(dynamicCells[1])
assert(GameTooltip.lines[1][2] == "13" and GameTooltip.lines[2][2] == "10")

-- A level-99 skill gets a full bar and has no phantom next-level XP.
receive("B|1|"..token.."|7|8")
for _, id in ipairs({"attack","hitpoints","strength","ranged","defence","magic","prayer","mining"}) do
    if id == "prayer" then
        receive("S|1|"..token.."|7|prayer|99|-|200000000|13034431|-")
    else
        receive("S|1|"..token.."|7|"..id.."|1|-|0|0|83")
    end
end
receive("E|1|"..token.."|7")
assert(dynamicCells[7].bar.value == 1)
WarscapePanels:SetLocked("skills",false)
local header=WarscapePanels.entries.skills.header
header.scripts.OnDragStart(header)
panel:ClearAllPoints();panel:SetPoint("BOTTOM",UIParent,"BOTTOMLEFT",900/panel:GetScale(),220/panel:GetScale())
header.scripts.OnDragStop(header)
local saved=WarscapeWindowLayouts.right.position
assert(saved and math.abs(saved.x-900/UIParent:GetWidth())<.0001)
local x,y=panel:GetCenter();local bottom=panel:GetBottom()
WarscapePanels:RestoreScales()
assert(math.abs(panel:GetBottom()-bottom)<.0001 and math.abs(panel:GetCenter()-x)<.0001)
receive("B|1|"..token.."|8|9")
for _, id in ipairs({"attack","hitpoints","strength","ranged","defence","magic","prayer","mining","smithing"}) do
    receive("S|1|"..token.."|8|"..id.."|1|-|0|0|83")
end
receive("E|1|"..token.."|8")
local smith
for _, w in ipairs(widgets) do if w.label == "Smithing" then smith=w end end
assert(smith and smith.level.text == "1/1" and smith.bar.value == 0)
smith.scripts.OnEnter(smith)
assert(GameTooltip.lines[3][2] == "0")
receive("B|1|"..token.."|9|1")
receive("S|1|"..token.."|9|smithing|99|-|13034431|13034431|-")
receive("E|1|"..token.."|9")
for _, w in ipairs(widgets) do if w.label == "Smithing" and w.shown then smith=w end end
assert(smith.level.text == "99/99" and smith.bar.value == 1)

-- Real fractional snapshots and the single-recipe card use the same panel.
receive("B|1|"..token.."|10|1")
receive("S|1|"..token.."|10|smithing|1|-|6.2|0|83")
receive("E|1|"..token.."|10")
for _, w in ipairs(widgets) do if w.label == "Smithing" and w.shown then smith=w end end
assert(math.abs(smith.data.xp-6.2)<.00001)
smith.scripts.OnEnter(smith)
assert(GameTooltip.lines[3][2] == "6.2")
receive("B|1|"..token.."|11|10")
for _, id in ipairs({"attack","strength","defence","hitpoints","ranged","magic","prayer","mining","smithing","agility"}) do
    receive("S|1|"..token.."|11|"..id.."|1|-|0|0|83")
end
receive("E|1|"..token.."|11")
local agility
for _, w in ipairs(widgets) do if w.label == "Agility" and w.shown then agility=w end end
assert(agility and agility.level.text == "1/1" and agility.bar.value == 0)
''')
print('PASS: Lua 5.1 protocol validation and UI event smoke tests')
