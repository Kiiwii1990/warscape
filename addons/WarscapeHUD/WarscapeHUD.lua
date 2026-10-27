-- OSRS navigation with the native minimap and Blizzard's Dwarf action-bar art.
-- Design geometry lives in one assembly; the root retains the saved user scale.
local SCALE_MIN, SCALE_MAX, SCALE_STEP = 0.50, 1.50, 1.05
local BUTTON, GAP, MAP, MAP_Y = 44, 4, 140, 8
local RING = MAP * 152 / 140
local CAP_W, CAP_H = 160, 160 * 76 / 128
-- The opaque front-claw tip is at source x=101 in its lowest 16 rows.
-- Anchor that point a quarter-slot over the outer button; do not anchor the beak.
local CAP_OVERLAP = CAP_W * (1 - 101 / 128) + BUTTON / 4
local RAIL_H, BUTTON_Y = 64, 6
local hud = CreateFrame("Frame", "WarscapeHUDFrame", UIParent)
local assembly = CreateFrame("Frame", "WarscapeHUDAssembly", hud)
local shell = CreateFrame("Frame", "WarscapeHUDArt", assembly)
local cluster, map = MinimapCluster, Minimap
local buttons = {}

local coreWidth = MAP + BUTTON * 10 + GAP * 10
local baseWidth = coreWidth + 2 * (CAP_W - CAP_OVERLAP)
local baseHeight = MAP_Y + RING
hud:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, 0)
hud:SetFrameStrata("MEDIUM")
hud:SetClampedToScreen(true)
hud:EnableMouseWheel(true)
assembly:SetSize(baseWidth, baseHeight)
assembly:SetPoint("BOTTOM", hud, "BOTTOM", 0, 0)
shell:SetAllPoints(assembly)
shell:SetFrameLevel(assembly:GetFrameLevel() + 6)

local function fitViewport()
    -- 100% user scale occupies approximately the central half of the window,
    -- independent of its resolution, aspect ratio or global UI scale.
    local fit = UIParent:GetWidth() * 0.52 / baseWidth
    assembly:SetScale(fit)
    hud:SetSize(baseWidth * fit, baseHeight * fit)
end
UIParent:HookScript("OnSizeChanged", fitViewport)
fitViewport()

local backing = CreateFrame("Frame", "WarscapeHUDRail", assembly)
backing:SetSize(coreWidth, RAIL_H)
backing:SetPoint("BOTTOM", assembly, "BOTTOM", 0, 0)
backing:SetFrameLevel(assembly:GetFrameLevel() + 1)
-- Repeat the blank 192 x 43 native metal strip at one uniform scale. The last
-- tile is cropped, rather than squeezed; there are no vertical joins at the map.
local tileWidth = 192 * RAIL_H / 43
local covered = 0
while covered < coreWidth do
    local width = math.min(tileWidth, coreWidth - covered)
    local tile = backing:CreateTexture(nil, "BACKGROUND")
    tile:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeRail.tga")
    tile:SetSize(width, RAIL_H)
    tile:SetPoint("BOTTOMLEFT", backing, "BOTTOMLEFT", covered, 0)
    tile:SetTexCoord(0, (192 / 256) * width / tileWidth, 0, 43 / 64)
    covered = covered + width
end

local leftCap = shell:CreateTexture("WarscapeHUDLeftGryphon", "ARTWORK")
leftCap:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeGryphonWarscape.tga")
leftCap:SetTexCoord(0, 1, 52 / 128, 1)
leftCap:SetSize(CAP_W, CAP_H)
leftCap:SetPoint("BOTTOMLEFT", shell, "BOTTOMLEFT", 0, 0)
local rightCap = shell:CreateTexture("WarscapeHUDRightGryphon", "ARTWORK")
rightCap:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeGryphonWarscape.tga")
rightCap:SetTexCoord(1, 0, 52 / 128, 1)
rightCap:SetSize(CAP_W, CAP_H)
rightCap:SetPoint("BOTTOMRIGHT", shell, "BOTTOMRIGHT", 0, 0)

local function place(frame, x, y)
    if frame then
        frame:ClearAllPoints()
        frame:SetPoint("CENTER", map, "CENTER", x, y)
    end
end

local function layoutMinimap()
    cluster:SetParent(assembly)
    cluster:ClearAllPoints()
    cluster:SetSize(RING, RING)
    cluster:SetFrameLevel(assembly:GetFrameLevel() + 2)
    cluster:SetPoint("BOTTOM", assembly, "BOTTOM", 0, MAP_Y)
    map:ClearAllPoints()
    map:SetSize(MAP, MAP)
    map:SetPoint("CENTER", cluster, "CENTER", 0, 0)
    map:SetFrameLevel(assembly:GetFrameLevel() + 3)
    if MinimapBackdrop then
        MinimapBackdrop:ClearAllPoints()
        MinimapBackdrop:SetSize(RING, RING)
        MinimapBackdrop:SetPoint("CENTER", map, "CENTER", 0, 0)
        MinimapBackdrop:SetFrameLevel(map:GetFrameLevel() + 1)
    end
    if MinimapBorder then
        MinimapBorder:SetTexture("Interface\\Minimap\\UI-Minimap-Border")
        -- The atlas circle is centred at (168,105); exclude the header above it.
        MinimapBorder:SetTexCoord(92 / 256, 244 / 256, 29 / 256, 181 / 256)
        MinimapBorder:SetSize(RING, RING)
        MinimapBorder:SetVertexColor(1, 0.91, 0.75)
        place(MinimapBorder, 0, 0)
    end
    if MinimapNorthTag then
        MinimapNorthTag:SetSize(16 * MAP / 140, 16 * MAP / 140)
        place(MinimapNorthTag, 0, 67 * MAP / 140)
    end
    if MinimapCompassTexture then
        -- Keep Blizzard's 365/140 ratio: native SetRotation expands the UVs.
        MinimapCompassTexture:SetSize(365 * MAP / 140, 365 * MAP / 140)
        place(MinimapCompassTexture, 0, 0)
    end
    local controlRadius = RING / 2 + 16
    local plusAngle = math.pi / 6
    -- Preserve the stock XML's centre-to-centre zoom-button spacing (26, 28).
    local separation = 2 * math.asin(math.sqrt(26 * 26 + 28 * 28) / (2 * controlRadius))
    place(MinimapZoomIn, controlRadius * math.cos(plusAngle), controlRadius * math.sin(plusAngle))
    place(MinimapZoomOut, controlRadius * math.cos(plusAngle - separation), controlRadius * math.sin(plusAngle - separation))
    place(MiniMapWorldMapButton, -controlRadius * math.cos(plusAngle), controlRadius * math.sin(plusAngle))
    place(MiniMapTracking, -controlRadius, 0)
    map:Show()
    cluster:Show()
end

local function hideMinimapExtras()
    for _, name in ipairs({"GameTimeFrame", "MinimapCalendarButton", "TimeManagerClockButton",
        "MinimapZoneTextButton", "MinimapToggleButton"}) do
        local frame = _G[name]
        if frame and frame.Hide then
            if not frame.warscapeHudHiddenHook then
                frame.warscapeHudHiddenHook = true
                frame:HookScript("OnShow", function(self) self:Hide() end)
            end
            frame:Hide()
        end
    end
    if MinimapBorderTop then MinimapBorderTop:Hide() end
end
layoutMinimap()
hideMinimapExtras()

local leftStart = -MAP / 2 - GAP - 5 * BUTTON - 4 * GAP
local rightStart = MAP / 2 + GAP
for i = 1, 10 do
    local button = CreateFrame("Button", "WarscapeHUDMenuButton" .. i, assembly)
    button:SetSize(BUTTON, BUTTON)
    local index = i <= 5 and i - 1 or i - 6
    local x = i <= 5 and (leftStart + index * (BUTTON + GAP)) or (rightStart + index * (BUTTON + GAP))
    button:SetPoint("BOTTOMLEFT", assembly, "BOTTOM", x, BUTTON_Y)
    button:SetFrameLevel(assembly:GetFrameLevel() + 5)
    button:SetBackdrop({bgFile="Interface\\Buttons\\WHITE8X8", insets={left=5, right=5, top=5, bottom=5}})
    button:SetBackdropColor(0.035, 0.028, 0.02, 0.98)
    WarscapeSkillsSkin.NineSlice(button, "Cell", 406, 155, 512, 256, 16, BUTTON * 8 / 68, "BORDER")(BUTTON, BUTTON)
    if i == 5 or i == 6 then
        button.icon = button:CreateTexture(nil, "ARTWORK")
        button.icon:SetTexture(i == 5 and "Interface\\Buttons\\Button-Backpack-Up" or "Interface\\Icons\\INV_Misc_PunchCards_Prismatic")
        button.icon:SetTexCoord(4 / 64, 60 / 64, 4 / 64, 60 / 64)
        button.icon:SetSize(BUTTON * 56 / 68, BUTTON * 56 / 68)
        button.icon:SetPoint("CENTER", button, "CENTER", 0, 0)
    end
    button:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    button:SetPushedTexture("Interface\\Buttons\\UI-Quickslot-Depress")
    button:SetScript("OnClick", function() end)
    button:RegisterForClicks("LeftButtonUp")
    buttons[i] = button
end

local function styleMenuButton(b, open)
    if open then
        b:LockHighlight()
        b:SetBackdropColor(0.16, 0.105, 0.025, 1)
        b:SetAlpha(0.82)
    else
        b:UnlockHighlight()
        b:SetBackdropColor(0.035, 0.028, 0.02, 0.98)
        b:SetAlpha(1)
    end
end
WarscapePanels:AttachButton("inventory", buttons[5], styleMenuButton)
WarscapePanels:AttachButton("skills", buttons[6], styleMenuButton)
WarscapePanels:SetHudFrame(hud)

local scaler = CreateFrame("Frame", nil, UIParent)
scaler:SetAllPoints(UIParent)
scaler:EnableMouseWheel(true)
scaler:EnableKeyboard(true)
local lens = scaler:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
lens:SetText("⌕")
lens:SetTextColor(1, 0.82, 0.36)
lens:Hide()
local scaleLabel = scaler:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
scaleLabel:SetTextColor(1, 0.82, 0.36)
scaleLabel:Hide()

local function readScale(key, frame)
    local value = WarscapeHUDScales and WarscapeHUDScales[key]
    if type(value) ~= "number" then value = 1 end
    value = math.max(SCALE_MIN, math.min(SCALE_MAX, value))
    frame:SetScale(value)
    return value
end
local hudScale = 1
local function persist()
    WarscapeHUDScales = WarscapeHUDScales or {}
    WarscapeHUDScales.hud = hudScale
end
local function hoveredComponent()
    local panelId = WarscapePanels:HoveredPanel()
    if panelId then return panelId end -- Dialog panels can overlap the HUD.
    if MouseIsOver(hud) then return "hud" end
end
local hovered
scaler:SetScript("OnMouseWheel", function(_, delta)
    if not IsControlKeyDown() or not hovered then return end
    if hovered == "hud" then
        hudScale = math.max(SCALE_MIN, math.min(SCALE_MAX, hudScale * (delta > 0 and SCALE_STEP or 1 / SCALE_STEP)))
        hud:SetScale(hudScale)
        WarscapePanels:RestoreScales()
    else
        WarscapePanels:AdjustScale(hovered, delta)
    end
    persist()
end)
-- The full-screen wheel receiver is enabled only while Ctrl is held and the
-- pointer is over a component, leaving normal camera zoom unchanged elsewhere.
scaler:SetScript("OnUpdate", function(self, elapsed)
    local target = hoveredComponent()
    local active = IsControlKeyDown() and target ~= nil
    self:EnableMouseWheel(active)
    if active then
        hovered = target
        local x, y = GetCursorPosition()
        local scale = UIParent:GetEffectiveScale()
        lens:ClearAllPoints(); lens:SetPoint("BOTTOMLEFT", UIParent, "BOTTOMLEFT", x / scale + 12, y / scale + 8); lens:Show()
        scaleLabel:ClearAllPoints(); scaleLabel:SetPoint("TOPLEFT", lens, "BOTTOMLEFT", 1, -1); scaleLabel:Show()
        scaleLabel:SetText(string.format("%d%%", math.floor((target == "hud" and hudScale or WarscapePanels:GetScale(target)) * 100 + 0.5)))
    else
        hovered = nil
        lens:Hide(); scaleLabel:Hide()
    end
end)

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("DISPLAY_SIZE_CHANGED")
events:SetScript("OnEvent", function(_, event)
    fitViewport()
    if event == "PLAYER_LOGIN" then
        hudScale = readScale("hud", hud)
    end
    if event == "PLAYER_LOGIN" or event == "DISPLAY_SIZE_CHANGED" then WarscapePanels:RestoreScales() end
    layoutMinimap()
    hideMinimapExtras()
    WarscapePanels:SyncButtons()
end)
