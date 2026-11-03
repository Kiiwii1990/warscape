-- OSRS navigation with the native minimap and Blizzard's Dwarf action-bar art.
-- Design geometry lives in one assembly; the root retains the saved user scale.
local SCALE_MIN, SCALE_MAX, SCALE_STEP = 0.50, 1.50, 1.05
local metrics = WarscapeSkillsSkin.metrics
local BUTTON, GAP, MAP, MAP_Y = metrics.hudGrid, metrics.hudGap, 140, 8
local BUTTON_SIZE = metrics.hudButton
local RING = MAP * 152 / 140
local CAP_W, CAP_H = 160, 160 * 76 / 128
-- The opaque front-claw tip is at source x=101 in its lowest 16 rows.
-- Anchor that point a quarter-slot over the outer button; do not anchor the beak.
local CAP_OVERLAP = CAP_W * (1 - 101 / 128) + BUTTON / 4
local RAIL_H, BUTTON_Y, HUD_BOTTOM_OFFSET = 74, 22, 0
local CAP_OUTWARD = 8
local hud = CreateFrame("Frame", "WarscapeHUDFrame", UIParent)
local assembly = CreateFrame("Frame", "WarscapeHUDAssembly", hud)
local shell = CreateFrame("Frame", "WarscapeHUDArt", assembly)
local cluster, map = MinimapCluster, Minimap
local buttons = {}

local coreWidth = MAP + BUTTON * 10 + GAP * 10
local baseWidth = coreWidth + 2 * (CAP_W - CAP_OVERLAP)
local baseHeight = MAP_Y + RING
hud:SetPoint("BOTTOM", UIParent, "BOTTOM", 0, HUD_BOTTOM_OFFSET)
hud:SetFrameStrata("MEDIUM")
hud:SetClampedToScreen(true)
hud:EnableMouseWheel(true)
assembly:SetSize(baseWidth, baseHeight)
assembly:SetPoint("BOTTOM", hud, "BOTTOM", 0, 0)
shell:SetAllPoints(assembly)
shell:SetFrameLevel(assembly:GetFrameLevel() + 6)

local function fitViewport()
    -- 100% user scale occupies approximately the lower width of the window,
    -- independent of its resolution, aspect ratio or global UI scale.
    local fit = math.min(UIParent:GetWidth() * 0.90 / baseWidth, UIParent:GetWidth() * 0.98 / (baseWidth * hud:GetScale()))
    assembly:SetScale(fit)
    hud:SetSize(baseWidth * fit, baseHeight * fit)
end
UIParent:HookScript("OnSizeChanged", fitViewport)
fitViewport()

local backing = CreateFrame("Frame", "WarscapeHUDRail", assembly)
backing:SetSize(coreWidth, RAIL_H)
backing:SetPoint("BOTTOM", assembly, "BOTTOM", 0, 0)
backing:SetFrameLevel(assembly:GetFrameLevel() + 1)
-- Match the Prayer panel's exact tiled Stone backdrop and styling.
backing:SetBackdrop({bgFile="Interface\\AddOns\\WarscapeSkills\\art\\Stone",
    tile=true, tileSize=100})
backing:SetBackdropColor(1, 1, 1, 1)
-- Repeat the complete original bronze top bevel over the shared Stone
-- material. The transparent center reveals the backdrop; last tile is cropped.
local tileWidth = 192 * RAIL_H / 43
local covered = 0
while covered < coreWidth do
    local width = math.min(tileWidth, coreWidth - covered)
    local tile = backing:CreateTexture(nil, "BACKGROUND")
    tile:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeRailTrim.tga")
    tile:SetSize(width, RAIL_H)
    tile:SetPoint("BOTTOMLEFT", backing, "BOTTOMLEFT", covered, 0)
    tile:SetTexCoord(0, (192 / 256) * width / tileWidth, 0, 43 / 64)
    covered = covered + width
end

-- Reuse the Skills panels' bronze HeaderRail edge as a distinct top border.
-- This sits above the Stone fill, but below the minimap, buttons and gryphons;
-- its backing-relative anchor carries it through HUD scaling and resolution fit.
local topBorder = backing:CreateTexture("WarscapeHUDTopBorder", "ARTWORK")
topBorder:SetTexture("Interface\\AddOns\\WarscapeSkills\\art\\HeaderRail")
topBorder:SetTexCoord(0, 1, 5 / 32, 10 / 32)
topBorder:SetSize(coreWidth, 6)
topBorder:SetPoint("TOPLEFT", backing, "TOPLEFT", 0, 0)

local leftCap = shell:CreateTexture("WarscapeHUDLeftGryphon", "ARTWORK")
leftCap:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeGryphonDesign5HD.tga")
leftCap:SetTexCoord(0, 1, 52 / 128, 1)
leftCap:SetSize(CAP_W, CAP_H)
leftCap:SetPoint("BOTTOMLEFT", shell, "BOTTOMLEFT", -CAP_OUTWARD, 0)
local rightCap = shell:CreateTexture("WarscapeHUDRightGryphon", "ARTWORK")
rightCap:SetTexture("Interface\\AddOns\\WarscapeHUD\\art\\WarscapeGryphonDesign5HD.tga")
rightCap:SetTexCoord(1, 0, 52 / 128, 1)
rightCap:SetSize(CAP_W, CAP_H)
rightCap:SetPoint("BOTTOMRIGHT", shell, "BOTTOMRIGHT", CAP_OUTWARD, 0)

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
    -- Bring the frames a few pixels over the bronze ring so their borders
    -- visually meet it; preserve stock spacing and the 2/3 o'clock angles.
    local controlRadius = RING / 2 + 10
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
        "MinimapZoneTextButton", "MinimapToggleButton", "MiniMapTracking", "MiniMapWorldMapButton"}) do
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
local groupWidth = 5 * BUTTON + 4 * GAP

-- Empty layout anchors reserve room above each button group for future
-- resources. They have no textures, values or gameplay behavior in this phase.
local healthBarAnchor = CreateFrame("Frame", "WarscapeHUDHealthBarAnchor", assembly)
healthBarAnchor:SetSize(groupWidth, 22)
healthBarAnchor:SetPoint("BOTTOMLEFT", assembly, "BOTTOM", leftStart, BUTTON_Y + BUTTON + 16)
local prayerBarAnchor = CreateFrame("Frame", "WarscapeHUDPrayerBarAnchor", assembly)
prayerBarAnchor:SetSize(groupWidth, 22)
prayerBarAnchor:SetPoint("BOTTOMLEFT", assembly, "BOTTOM", rightStart, BUTTON_Y + BUTTON + 16)

local keybinds = {[1]="ESC", [2]="O", [4]="L", [5]="B", [6]="N", [7]="C", [8]="K", [9]="I", [10]="P"}
for i = 1, 10 do
    local button = CreateFrame("Button", "WarscapeHUDMenuButton" .. i, assembly)
    button:SetSize(BUTTON_SIZE, BUTTON_SIZE)
    local index = i <= 5 and i - 1 or i - 6
    local x = i <= 5 and (leftStart + index * (BUTTON + GAP)) or (rightStart + index * (BUTTON + GAP))
    -- Keep the established grid centres and spacing; only shrink the hitbox
    -- and its proportionate artwork to harmonise with the enlarged panel slots.
    button:SetPoint("CENTER", assembly, "BOTTOM", x + BUTTON / 2, BUTTON_Y + BUTTON / 2)
    button:SetFrameLevel(assembly:GetFrameLevel() + 5)
    button:SetBackdrop({bgFile="Interface\\Buttons\\WHITE8X8", insets={left=5, right=5, top=5, bottom=5}})
    button:SetBackdropColor(0.035, 0.028, 0.02, 0.98)
    WarscapeSkillsSkin.NineSlice(button, "Cell", 406, 155, 512, 256, 16, BUTTON_SIZE * 8 / 68, "BORDER")(BUTTON_SIZE, BUTTON_SIZE)
    if i == 5 or i == 6 then
        button.icon = button:CreateTexture(nil, "ARTWORK")
        button.icon:SetTexture(i == 5 and "Interface\\Buttons\\Button-Backpack-Up" or "Interface\\Icons\\INV_Misc_PunchCards_Prismatic")
        button.icon:SetTexCoord(4 / 64, 60 / 64, 4 / 64, 60 / 64)
        button.icon:SetSize(BUTTON_SIZE * 56 / 68, BUTTON_SIZE * 56 / 68)
        button.icon:SetPoint("CENTER", button, "CENTER", 0, 0)
    end
    button:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    button:SetPushedTexture("Interface\\Buttons\\UI-Quickslot-Depress")
    button:SetScript("OnClick", function() end)
    button:RegisterForClicks("LeftButtonUp")
    if i == 3 then
        button:EnableMouse(false)
        button:SetScript("OnClick", nil)
    elseif keybinds[i] then
        local label = button:CreateFontString("WarscapeHUDKeybind" .. i, "OVERLAY")
        label:SetFont("Fonts\\FRIZQT__.TTF", 13, "OUTLINE")
        label:SetTextColor(0.92, 0.90, 0.82)
        label:SetShadowColor(0, 0, 0, 1)
        label:SetShadowOffset(1, -1)
        label:SetPoint("TOP", button, "BOTTOM", 0, -2)
        label:SetText(keybinds[i])
        button.warscapeKeybind = label
    end
    buttons[i] = button
end

-- Use the Inventory button as the vertical reference so future per-button
-- edits cannot leave its neighbours or their labels on a different row.
local inventoryButton = buttons[5]
local anchor, relative, relativePoint, _, inventoryY = inventoryButton:GetPoint()
for i = 1, 10 do
    local button = buttons[i]
    if button ~= inventoryButton then
        local _, _, _, x = button:GetPoint()
        button:ClearAllPoints()
        button:SetPoint(anchor, relative, relativePoint, x, inventoryY)
    end
end
local inventoryLabel = inventoryButton.warscapeKeybind
local labelPoint, _, labelRelativePoint, labelX, labelY = inventoryLabel:GetPoint()
for i = 1, 10 do
    local button, label = buttons[i], buttons[i].warscapeKeybind
    if label and label ~= inventoryLabel then
        label:ClearAllPoints()
        label:SetPoint(labelPoint, button, labelRelativePoint, labelX, labelY)
    end
end

local selectedIcons = {
    [1]="INV_Gizmo_02", [2]="INV_Misc_GroupNeedMore", [4]="INV_Misc_Note_05",
    [7]="INV_Chest_Chain_04", [8]="Ability_DualWield", [9]="INV_Jewelry_Talisman_08",
    [10]="INV_Misc_Book_01",
}
for index, iconName in pairs(selectedIcons) do
    local button = buttons[index]
    button.icon = button:CreateTexture(nil, "ARTWORK")
    button.icon:SetTexture("Interface\\Icons\\" .. iconName)
    button.icon:SetTexCoord(4 / 64, 60 / 64, 4 / 64, 60 / 64)
    button.icon:SetSize(BUTTON_SIZE * 56 / 68, BUTTON_SIZE * 56 / 68)
    button.icon:SetPoint("CENTER", button, "CENTER", 0, 0)
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
WarscapePanels:AttachButton("attackStyles", buttons[8], styleMenuButton)
WarscapePanels:AttachButton("prayer", buttons[9], styleMenuButton)
WarscapePanels:AttachButton("spellbook", buttons[10], styleMenuButton)
WarscapePanels:SetHudFrame(hud, HUD_BOTTOM_OFFSET)
-- Dock at the rail's actual upper edge, inside the original gryphon beaks.
-- Reserve the same minimap + native zoom-control gutter on BOTH sides.
-- Derive it from actual region sizes, never screenshot coordinates.
local zoomWidth = math.max(MinimapZoomIn:GetWidth(),MinimapZoomOut:GetWidth())
local menuGap = RING/2 + zoomWidth + 2
local leftInner, rightInner = -menuGap, menuGap
local nose = baseWidth/2 + CAP_OUTWARD - CAP_W - 4
local leftDock=CreateFrame("Frame","WarscapeHUDLeftMenuDock",assembly)
leftDock:SetSize(1,1);leftDock:SetPoint("BOTTOMRIGHT",backing,"TOP",leftInner,0)
local rightDock=CreateFrame("Frame","WarscapeHUDRightMenuDock",assembly)
rightDock:SetSize(1,1);rightDock:SetPoint("BOTTOMLEFT",backing,"TOP",rightInner,0)
WarscapePanels:SetDocks(leftDock,rightDock,nose-menuGap, WarscapeSkillsSkin.profiles.landscape.width)

local nativeMenus = {
    {
        id = "settings",
        name = "GameMenuFrame",
        group = "left",
        toggle = function()
            if GameMenuFrame:IsShown() then
                GameMenuFrame:Hide()
            else
                GameMenuFrame:Show()
            end
        end
    },
    {id="friends", name="FriendsFrame", group="left", toggle=function() ToggleFriendsFrame() end},
    {id="quests", name="QuestLogFrame", group="left", toggle=function() ToggleFrame(QuestLogFrame) end},
    {id="equipment", name="CharacterFrame", group="right", toggle=function() ToggleCharacter("PaperDollFrame") end},
}
local nativeButtons = {settings=buttons[1], friends=buttons[2], quests=buttons[4], equipment=buttons[7]}
local registeredNativeButtons = {}
local function registerNativeMenus()
    for _, definition in ipairs(nativeMenus) do
        local frame = _G[definition.name]
        if frame and not WarscapePanels.entries[definition.id] then
            WarscapeMenuPanels_RegisterNative(definition, frame)
        end
        if frame and WarscapePanels.entries[definition.id] and not registeredNativeButtons[definition.id] then
            WarscapePanels:AttachButton(definition.id, nativeButtons[definition.id], styleMenuButton)
            registeredNativeButtons[definition.id] = true
        end
    end
end
registerNativeMenus()

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
        fitViewport()
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
events:RegisterEvent("UI_SCALE_CHANGED")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:SetScript("OnEvent", function(_, event)
    registerNativeMenus()
    if event == "PLAYER_LOGIN" then
        hudScale = readScale("hud", hud)
    end
    fitViewport()
    if event == "PLAYER_LOGIN" or (event == "DISPLAY_SIZE_CHANGED" or event == "UI_SCALE_CHANGED") then WarscapePanels:RestoreScales() end
    layoutMinimap()
    hideMinimapExtras()
    WarscapePanels:SyncButtons()
end)
