"""Lua 5.1 HUD interaction smoke tests; rendering needs the user's client review."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
lua = LuaRuntime()
lua.execute(r'''
widgets = {}
ctrl, cursorX, cursorY = false, 100, 100
function IsControlKeyDown() return ctrl end
function GetCursorPosition() return cursorX, cursorY end
function MouseIsOver(frame) return frame.over == true end
local methods = {}
function methods:SetScript(k, v) self.scripts[k] = v end
function methods:HookScript(k, v) self.hooks[k] = v end
function methods:SetSize(w, h) self.width, self.height = w, h end
function methods:GetWidth() return self.width end
function methods:GetHeight() return self.height end
function methods:SetPoint(...) self.point = {...} end
function methods:ClearAllPoints() self.point = nil end
function methods:SetAllPoints(frame) self.allPoints = frame or self.parent end
function methods:SetFrameStrata() end
function methods:SetFrameLevel(v) self.level = v end
function methods:GetFrameLevel() return self.level or 1 end
function methods:SetClampedToScreen() end
function methods:EnableMouseWheel(v) self.wheel = v end
function methods:EnableKeyboard() end
function methods:EnableMouse() end
function methods:RegisterForClicks() end
function methods:RegisterEvent(e) self.events[e] = true end
function methods:SetBackdrop(v) self.backdrop = v end
function methods:SetBackdropColor(...) self.bg = {...} end
function methods:SetBackdropBorderColor(...) self.border = {...} end
function methods:SetHighlightTexture() end
function methods:SetPushedTexture() end
function methods:LockHighlight() self.highlightLocked = true end
function methods:UnlockHighlight() self.highlightLocked = false end
function methods:SetTexture(v) self.texture = v end
function methods:SetTexCoord(...) self.texcoord = {...} end
function methods:SetVertexColor(...) self.color = {...} end
function methods:SetMaskTexture(v) self.mask = v end
function methods:SetParent(p) self.parent = p end
function methods:GetParent() return self.parent end
function methods:SetScale(v) self.scale = v end
function methods:GetScale() return self.scale or 1 end
function methods:SetAlpha(v) self.alpha = v end
function methods:GetEffectiveScale()
    return (self.scale or 1) * (self.parent and self.parent:GetEffectiveScale() or 1)
end
function methods:SetText(v) self.text = v end
function methods:SetTextColor() end
function methods:Show()
    self.shown = true
    if self.hooks.OnShow then self.hooks.OnShow(self) end
end
function methods:Hide()
    self.shown = false
    if self.hooks.OnHide then self.hooks.OnHide(self) end
end
function methods:IsShown() return self.shown end
function methods:CreateTexture(name, layer)
    local t = CreateFrame("Texture", name, self)
    t.layer = layer
    return t
end
function methods:CreateFontString() return CreateFrame("FontString", nil, self) end
function CreateFrame(kind, name, parent)
    local f = setmetatable({kind=kind, name=name, parent=parent, scripts={}, hooks={}, events={}, shown=true}, {__index=methods})
    if name then _G[name] = f end
    widgets[#widgets+1] = f
    return f
end
UIParent = CreateFrame("Frame", "UIParent")
UIParent:SetSize(1920, 1080)
MinimapCluster = CreateFrame("Frame", "MinimapCluster", UIParent)
Minimap = CreateFrame("Frame", "Minimap", MinimapCluster)
MinimapBackdrop = CreateFrame("Frame", "MinimapBackdrop", Minimap)
MinimapBorder = CreateFrame("Texture", "MinimapBorder", MinimapBackdrop)
MinimapBorderTop = CreateFrame("Texture", "MinimapBorderTop", MinimapCluster)
MinimapNorthTag = CreateFrame("Texture", "MinimapNorthTag", MinimapBackdrop)
MinimapCompassTexture = CreateFrame("Texture", "MinimapCompassTexture", MinimapBackdrop)
MinimapZoomIn = CreateFrame("Button", "MinimapZoomIn", Minimap)
MinimapZoomOut = CreateFrame("Button", "MinimapZoomOut", Minimap)
MiniMapWorldMapButton = CreateFrame("Button", "MiniMapWorldMapButton", MinimapBackdrop)
MiniMapTracking = CreateFrame("Frame", "MiniMapTracking", MinimapBackdrop)
MinimapZoneTextButton = CreateFrame("Button", "MinimapZoneTextButton", MinimapCluster)
MinimapToggleButton = CreateFrame("Button", "MinimapToggleButton", MinimapCluster)
local nativeClick = function() end
MinimapZoomIn:SetScript("OnClick", nativeClick)
MinimapZoomOut:SetScript("OnClick", nativeClick)
MiniMapWorldMapButton:SetScript("OnClick", nativeClick)
MiniMapTracking:SetScript("OnMouseDown", nativeClick)
nativeMinimapClick = nativeClick
GameTimeFrame = CreateFrame("Button", "GameTimeFrame", MinimapCluster)
MinimapCalendarButton = CreateFrame("Button", "MinimapCalendarButton", MinimapCluster)
TimeManagerClockButton = CreateFrame("Button", "TimeManagerClockButton", MinimapCluster)
WarscapeSkillsFrame = CreateFrame("Frame", "WarscapeSkillsFrame", UIParent)
WarscapeSkillsFrame:SetSize(500, 514)
WarscapeSkillsFrame:Hide()
WarscapeInventoryFrame = CreateFrame("Frame", "WarscapeInventoryFrame", UIParent)
WarscapeInventoryFrame:SetSize(500, 514)
WarscapeInventoryFrame:Hide()
function WarscapeSkills_Toggle()
    WarscapePanels:Toggle("skills")
end
''')
lua.execute((ROOT.parent / "WarscapePanels" / "Panels.lua").read_text())
lua.execute('WarscapePanels:Register("skills", WarscapeSkillsFrame); WarscapePanels:Register("inventory", WarscapeInventoryFrame)')
lua.execute((ROOT.parent / "WarscapeSkills" / "Skin.lua").read_text())
lua.execute((ROOT / "WarscapeHUD.lua").read_text())
lua.execute(r'''
local events, scaler
for _, f in ipairs(widgets) do
    if f.events.PLAYER_LOGIN then events = f end
    if f.scripts.OnMouseWheel then scaler = f end
end
assert(events and scaler)
events.scripts.OnEvent(events, "PLAYER_LOGIN")
assert(Minimap:GetParent() == MinimapCluster and MinimapCluster:GetParent() == WarscapeHUDAssembly)
assert(Minimap:IsShown() and Minimap.width == Minimap.height)
assert(Minimap.point[1] == "CENTER" and Minimap.point[4] == 0 and Minimap.point[5] == 0)
assert(MinimapBorder.point[2] == Minimap and MinimapBackdrop.point[2] == Minimap)
assert(MinimapBorder.point[4] == 0 and MinimapBorder.point[5] == 0)
assert(MinimapBorder.width == MinimapBorder.height and MinimapBorder.width > Minimap.width)
assert(MinimapBackdrop.width == MinimapBorder.width and MinimapCluster.width == MinimapBorder.width)
assert(MinimapNorthTag.point[2] == Minimap and MinimapCompassTexture.point[2] == Minimap)
assert(not MinimapBorderTop:IsShown() and not MinimapZoneTextButton:IsShown() and not MinimapToggleButton:IsShown())
local zoomDx = MinimapZoomIn.point[4] - MinimapZoomOut.point[4]
local zoomDy = MinimapZoomIn.point[5] - MinimapZoomOut.point[5]
assert(math.abs(zoomDx^2 + zoomDy^2 - (26^2 + 28^2)) < 0.001, "native control separation is retained")
for _, control in ipairs({MinimapZoomIn, MinimapZoomOut}) do
    local distance = math.sqrt(control.point[4]^2 + control.point[5]^2)
    assert(distance > MinimapBorder.width / 2 and distance - MinimapBorder.width / 2 <= 16.01)
    assert(control.scripts.OnClick == nativeMinimapClick)
end
assert(MiniMapWorldMapButton.scripts.OnClick == nativeMinimapClick and MiniMapTracking.scripts.OnMouseDown == nativeMinimapClick)
assert(GameTimeFrame:IsShown() == false and MinimapCalendarButton:IsShown() == false and TimeManagerClockButton:IsShown() == false)
GameTimeFrame:Show(); MinimapCalendarButton:Show(); TimeManagerClockButton:Show()
assert(not GameTimeFrame:IsShown() and not MinimapCalendarButton:IsShown() and not TimeManagerClockButton:IsShown())
local skillButton = WarscapeHUDMenuButton6
assert(skillButton.icon.texture == "Interface\\Icons\\INV_Misc_PunchCards_Prismatic")
assert(skillButton.icon.width == skillButton.icon.height and skillButton.icon.width / skillButton.width > 0.8)
assert(skillButton.icon.texcoord[1] == 4 / 64 and skillButton.icon.texcoord[2] == 60 / 64)
assert(skillButton.icon.texcoord[3] == 4 / 64 and skillButton.icon.texcoord[4] == 60 / 64)
assert(WarscapeHUDMenuButton5.icon.texture == "Interface\\Buttons\\Button-Backpack-Up")
assert(WarscapeHUDMenuButton5.icon.width == skillButton.icon.width)
for i = 1, 10 do
    local b = _G["WarscapeHUDMenuButton" .. i]
    assert(b and b.parent == WarscapeHUDAssembly and b.width == b.height)
    if i ~= 5 and i ~= 6 then
        assert(not b.icon and not b.warscapeSkills)
        b.scripts.OnClick(b)
        assert(not WarscapeSkillsFrame:IsShown(), "placeholder buttons have no panel action")
    end
end
assert(WarscapeHUDLeftGryphon.width / WarscapeHUDLeftGryphon.height == 128 / 76)
assert(WarscapeHUDLeftGryphon.texcoord[3] == 52 / 128 and WarscapeHUDLeftGryphon.texcoord[4] == 1)
assert(WarscapeHUDRightGryphon.texcoord[1] == 1 and WarscapeHUDRightGryphon.texcoord[2] == 0)
assert(WarscapeHUDArt.level > WarscapeHUDMenuButton1.level, "gryphon claws draw above the adjoining slots")
local tileEnd = 0
for _, w in ipairs(widgets) do
    if w.parent == WarscapeHUDRail and w.kind == "Texture" then
        assert(math.abs(w.point[4] - tileEnd) < 0.001, "no backing gaps or overlaps")
        local sourceWidth = (w.texcoord[2] - w.texcoord[1]) * 256
        local sourceHeight = (w.texcoord[4] - w.texcoord[3]) * 64
        assert(math.abs(w.width / sourceWidth - w.height / sourceHeight) < 0.001, "native rail is never stretched")
        tileEnd = tileEnd + w.width
    end
end
assert(math.abs(tileEnd - WarscapeHUDRail.width) < 0.001)
local first, last = WarscapeHUDMenuButton1, WarscapeHUDMenuButton10
assert(first.point[4] == -WarscapeHUDRail.width / 2 and last.point[4] + last.width == WarscapeHUDRail.width / 2)
local capOverlap = (WarscapeHUDLeftGryphon.width * 2 + WarscapeHUDRail.width - WarscapeHUDAssembly.width) / 2
local clawInsideSlot = WarscapeHUDLeftGryphon.width * 101 / 128 - (WarscapeHUDLeftGryphon.width - capOverlap)
assert(capOverlap > 0 and clawInsideSlot > 0 and clawInsideSlot <= first.width * 0.35,
    "the measured front claw overlaps the outer button, not just the beak")
WarscapeHUDMenuButton6.scripts.OnClick(WarscapeHUDMenuButton6)
assert(WarscapeSkillsFrame:IsShown() and WarscapeHUDMenuButton6.alpha < 1 and skillButton.highlightLocked)
WarscapeSkillsFrame:Hide()
assert(WarscapeHUDMenuButton6.alpha == 1 and not skillButton.highlightLocked)
WarscapeHUDMenuButton5.scripts.OnClick(WarscapeHUDMenuButton5)
assert(WarscapeInventoryFrame:IsShown() and WarscapeHUDMenuButton5.highlightLocked)
WarscapeSkills_Toggle()
assert(not WarscapeInventoryFrame:IsShown() and not WarscapeHUDMenuButton5.highlightLocked)
assert(WarscapeSkillsFrame:IsShown() and WarscapeHUDMenuButton6.highlightLocked)
WarscapeSkills_Toggle()

ctrl = true
WarscapeHUDFrame.over = true
scaler.scripts.OnUpdate(scaler, 0)
assert(scaler.wheel and scaler.scripts.OnMouseWheel)
scaler.scripts.OnMouseWheel(scaler, 1)
assert(WarscapeHUDFrame.scale > 1 and WarscapeSkillsFrame.scale == 1)
for i = 1, 30 do scaler.scripts.OnMouseWheel(scaler, 1) end
assert(WarscapeHUDFrame.scale == 1.5, "HUD maximum is 150%")
for i = 1, 40 do scaler.scripts.OnMouseWheel(scaler, -1) end
assert(WarscapeHUDFrame.scale == 0.5, "HUD minimum is 50%")

WarscapeHUDFrame.over = false
local hudBeforeSkillsScale = WarscapeHUDFrame.scale
WarscapeSkillsFrame:Show()
WarscapeSkillsFrame.over = true
scaler.scripts.OnUpdate(scaler, 0)
scaler.scripts.OnMouseWheel(scaler, 1)
assert(WarscapeSkillsFrame.scale > 1 and WarscapeHUDFrame.scale == hudBeforeSkillsScale)
for i = 1, 30 do scaler.scripts.OnMouseWheel(scaler, 1) end
assert(WarscapeSkillsFrame.scale == 1.5, "Skills maximum is 150% at this resolution")
for i = 1, 40 do scaler.scripts.OnMouseWheel(scaler, -1) end
assert(WarscapeSkillsFrame.scale == 0.5, "Skills minimum is 50%")
assert(WarscapeHUDScales.hud == WarscapeHUDFrame.scale and WarscapePanelScales.skills == WarscapeSkillsFrame.scale)

ctrl = false
scaler.scripts.OnUpdate(scaler, 0)
assert(not scaler.wheel)
WarscapeHUDScales = {hud=1.2, skills=0.9}
WarscapePanelScales = nil -- Upgrade migrates the existing Skills preference once.
events.scripts.OnEvent(events, "PLAYER_LOGIN")
assert(WarscapeHUDFrame.scale == 1.2 and WarscapeSkillsFrame.scale == 0.9)
-- Model UIParent in logical units at different global UI scales. The root's
-- effective pixel width must stay at 52% * saved HUD scale of the viewport.
for _, resolution in ipairs({{1280,720}, {1920,1080}, {2560,1440}, {3440,1440}}) do
    for _, uiScale in ipairs({0.64, 0.8, 1.0}) do
        UIParent:SetScale(uiScale)
        UIParent:SetSize(resolution[1] / uiScale, resolution[2] / uiScale)
        UIParent.hooks.OnSizeChanged(UIParent)
        for _, userScale in ipairs({0.5, 1.0, 1.5}) do
            WarscapeHUDScales.hud = userScale
            events.scripts.OnEvent(events, "PLAYER_LOGIN")
            local width = WarscapeHUDFrame.width * WarscapeHUDFrame:GetEffectiveScale()
            assert(math.abs(width / resolution[1] - 0.52 * userScale) < 0.0001)
            local mapScale = Minimap:GetEffectiveScale()
            local bottom = MinimapCluster.point[5] * mapScale
            local top = (MinimapCluster.point[5] + MinimapBorder.height) * mapScale
            assert(bottom > 0 and top <= WarscapeHUDFrame.height * WarscapeHUDFrame:GetEffectiveScale() + 0.0001)
            assert(WarscapeHUDFrame.point[1] == "BOTTOM" and WarscapeHUDFrame.point[4] == 0)
        end
    end
end
UIParent:SetScale(1)
UIParent:SetSize(800, 640)
WarscapeHUDScales = {hud=1.0, skills=1.5}
WarscapePanelScales.skills = 1.5
events.scripts.OnEvent(events, "PLAYER_LOGIN")
assert(WarscapeHUDFrame.scale == 1.0 and WarscapeSkillsFrame.scale <= (640 - WarscapeHUDFrame.height - 18) / 514)
''')
print("PASS: concentric native minimap, original control callbacks, continuous rail, gryphon crop, selected icon, panel sync, saved scales and 36 viewport/scale cases")
