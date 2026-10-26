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

# Exercise the real UI event handlers with a small 3.3.5-style widget harness.
# This checks script execution, not client rendering or server networking.
lua.execute(r'''
widgets, messages, UISpecialFrames, SlashCmdList = {}, {}, {}, {}
clock = 10
function GetTime() return clock end
function UnitName() return "Tester" end
function SendAddonMessage(p, m, d, t) messages[#messages+1] = {p,m,d,t} end
local methods = {}
function methods:SetScript(k,v) self.scripts[k] = v end
function methods:SetText(t) self.text = t end
function methods:SetValue(v) self.value = v end
function methods:SetSize(w,h) self.width=w; self.height=h end
function methods:SetHeight(v) self.height = v end
function methods:SetTexture(...) self.texture = {...} end
function methods:SetTexCoord(...) self.uv = {...} end
function methods:SetFont(path,size,flags) self.font=path; self.fontSize=size end
function methods:SetTextColor(...) self.color = {...} end
function methods:SetStatusBarColor(...) self.barColor = {...} end
function methods:SetBackdrop(v) self.backdrop = v end
function methods:SetBackdropColor(...) self.backdropColor = {...} end
function methods:SetPoint(...) self.point = {...} end
function methods:GetPoint() return unpack(self.point) end
function methods:Show() self.shown = true end
function methods:Hide() self.shown = false end
function methods:IsShown() return self.shown end
function MouseIsOver() return false end
function methods:CreateTexture(name,layer) local t=CreateFrame("Texture",name,self); t.layer=layer; return t end
function methods:CreateFontString(name,layer,template)
    local t=CreateFrame("FontString",name,self); t.layer=layer; t.fontSize=10; return t
end
function methods:AddDoubleLine(...) self.lines[#self.lines+1] = {...} end
function methods:AddLine(...) self.lines[#self.lines+1] = {...} end
function methods:SetPushedTexture() self.pushedTexture = self:CreateTexture() end
function methods:GetPushedTexture() return self.pushedTexture end
for _, name in ipairs({"SetFrameStrata","SetClampedToScreen","SetMovable","EnableMouse","RegisterForDrag",
    "StartMoving","StopMovingOrSizing","SetBackdropBorderColor",
    "SetStatusBarTexture","SetMinMaxValues","SetAllPoints","SetOwner","RegisterEvent","ClearAllPoints",
    "SetShadowColor","SetShadowOffset","SetHighlightTexture","SetVertexColor"}) do
    methods[name] = function() end
end
function methods:SetNormalTexture(path) self.normalTexture=path end
local meta = {__index=methods}
function CreateFrame(kind, name, parent)
    local w = setmetatable({kind=kind,name=name,parent=parent,scripts={},lines={},shown=true},meta)
    if name then _G[name] = w end
    widgets[#widgets+1] = w
    return w
end
UIParent = CreateFrame("Frame")
GameTooltip = CreateFrame("Tooltip")
''')
lua.execute((root / 'Skin.lua').read_text())
lua.execute((root / 'WarscapeSkills.lua').read_text())
lua.execute(r'''
local events
for _, w in ipairs(widgets) do if w.scripts.OnEvent then events = w end end
local panel = WarscapeSkillsFrame
assert(not panel:IsShown())
events.scripts.OnEvent(events, "PLAYER_LOGIN")
assert(#messages == 1 and messages[1][3] == "WHISPER" and messages[1][4] == "Tester")
local token = string.match(messages[1][2], "HELLO|1|(.+)")
local function receive(m, sender, channel)
    events.scripts.OnEvent(events, "CHAT_MSG_ADDON", "WCSkills", m, channel or "WHISPER", sender or "Tester")
end
receive("B|1|"..token.."|1|7", "Other")
local ids = {"attack","strength","defence","hitpoints","ranged","magic","prayer"}
receive("B|1|"..token.."|1|7")
for _, id in ipairs(ids) do
    receive("S|1|"..token.."|1|"..id.."|1|-|0|0|83")
end
receive("E|1|"..token.."|1")
local cells = {}
for _, w in ipairs(widgets) do if w.data then cells[#cells+1] = w end end
assert(#cells == 7)
assert(cells[1].label == "Attack" and cells[1].level.text == "1 |cffddd6c6/ 1|r" and cells[1].bar.value == 0)
assert(cells[2].label == "Hitpoints" and cells[3].label == "Strength")
assert(WarscapeSkillsTotal.value.text == "Total level: 7")
assert(panel.width == 500 and panel.height == 514)
assert(cells[1].width == 206 and cells[1].height == 76)
cells[1].scripts.OnEnter(cells[1])
assert(GameTooltip.text == "Attack" and #GameTooltip.lines == 5)
SlashCmdList.WARSCAPESKILLS()
assert(panel:IsShown())
SlashCmdList.WARSCAPESKILLS()
assert(not panel:IsShown())
WarscapeSkills_Toggle()
WarscapeSkillsCloseButton.scripts.OnClick()
assert(not panel:IsShown())
-- Data updates preserve the complete UI and sum BASE levels, never boosts.
receive("B|1|"..token.."|2|1")
receive("S|1|"..token.."|2|attack|12|15|1585|1584|1833")
receive("E|1|"..token.."|2")
assert(cells[1].level.text == "15 |cffddd6c6/ 12|r")
assert(WarscapeSkillsTotal.value.text == "Total level: 12")
assert(cells[1].bar.value > 0 and cells[1].bar.value < 1)
assert(not cells[2]:IsShown())
panel:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 123, -234)
panel.scripts.OnDragStop(panel)
assert(WarscapeSkillsPosition.x == 123 and WarscapeSkillsPosition.y == -234)
events.scripts.OnEvent(events, "PLAYER_LOGIN")
local point, _, relative, x, y = panel:GetPoint()
assert(point == "TOPLEFT" and relative == "TOPLEFT" and x == 123 and y == -234)
''')
print('PASS: Lua 5.1 protocol validation and UI event smoke tests')
