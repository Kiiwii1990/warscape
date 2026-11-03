"""Lua 5.1 HUD interaction smoke tests; rendering needs the user's client review."""
from pathlib import Path
from lupa.lua51 import LuaRuntime
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
rail = Image.open(ROOT / "art" / "WarscapeRail.tga").convert("RGBA")
trim = Image.open(ROOT / "art" / "WarscapeRailTrim.tga").convert("RGBA")
header_rail = Image.open(ROOT.parent / "WarscapeSkills" / "art" / "HeaderRail.tga").convert("RGBA")
assert rail.size == trim.size == (256, 64)
assert header_rail.size == (512, 32), "the existing panel rail remains the HUD border source"
assert all(trim.getpixel((x, y)) == rail.getpixel((x, y)) for y in range(5) for x in range(256))
assert all(trim.getpixel((x, y))[3] == 0 for y in range(5, 64) for x in range(256))
lua = LuaRuntime()
lua.execute((ROOT.parent / 'WarscapePanels/tests/ui_harness.lua').read_text())
lua.execute(r'''
function nativeMinimapClick() end
for _,frame in ipairs({MinimapZoomIn,MinimapZoomOut,MiniMapWorldMapButton}) do frame:SetScript("OnClick",nativeMinimapClick) end
MiniMapTracking:SetScript("OnMouseDown",nativeMinimapClick)
WarscapeSkillsFrame=CreateFrame("Frame","WarscapeSkillsFrame",UIParent);WarscapeSkillsFrame:SetSize(700,460);WarscapeSkillsFrame:Hide()
WarscapeInventoryFrame=CreateFrame("Frame","WarscapeInventoryFrame",UIParent);WarscapeInventoryFrame:SetSize(700,460);WarscapeInventoryFrame:Hide()
function WarscapeSkills_Toggle() WarscapePanels:Toggle("skills") end
''')
lua.execute((ROOT.parent / "WarscapePanels" / "Panels.lua").read_text())
lua.execute('WarscapePanels:Register("skills", WarscapeSkillsFrame, {group="right"}); WarscapePanels:Register("inventory", WarscapeInventoryFrame, {group="left"})')
lua.execute((ROOT.parent / "WarscapeSkills" / "Skin.lua").read_text())
lua.execute((ROOT.parent / "WarscapeMenuPanels" / "MainPanels.lua").read_text())
lua.execute((ROOT.parent / "WarscapeMenuPanels" / "NativePanels.lua").read_text())
lua.execute((ROOT / "WarscapeHUD.lua").read_text())
lua.execute(r'''
local events, scaler
for _, f in ipairs(widgets) do
    if f.events.PLAYER_LOGIN then events = f end
    if f.scripts.OnMouseWheel then scaler = f end
end
assert(events and scaler)
dispatch("PLAYER_LOGIN")
assert(WarscapeHUDFrame.point[1] == "BOTTOM" and WarscapeHUDFrame.point[4] == 0 and WarscapeHUDFrame.point[5] == 0)
assert(WarscapeHUDAssembly.point[1] == "BOTTOM" and WarscapeHUDAssembly.point[5] == 0)
assert(WarscapeHUDRail.point[1] == "BOTTOM" and WarscapeHUDRail.point[5] == 0,
    "decorative backing meets the viewport bottom")
assert(WarscapeHUDRail.height == 74, "taller backing contains the raised buttons and labels")
assert(WarscapeHUDTopBorder.parent == WarscapeHUDRail
    and WarscapeHUDTopBorder.texture == "Interface\\AddOns\\WarscapeSkills\\art\\HeaderRail"
    and WarscapeHUDTopBorder.layer == "ARTWORK", "distinct trim draws over the textured fill")
assert(WarscapeHUDTopBorder.width == WarscapeHUDRail.width and WarscapeHUDTopBorder.height == 6
    and WarscapeHUDTopBorder.point[1] == "TOPLEFT" and WarscapeHUDTopBorder.point[2] == WarscapeHUDRail
    and WarscapeHUDTopBorder.point[3] == "TOPLEFT" and WarscapeHUDTopBorder.point[4] == 0
    and WarscapeHUDTopBorder.point[5] == 0, "top border spans the backing and stays top-anchored")
assert(WarscapeHUDTopBorder.texcoord[1] == 0 and WarscapeHUDTopBorder.texcoord[2] == 1
    and WarscapeHUDTopBorder.texcoord[3] == 5 / 32 and WarscapeHUDTopBorder.texcoord[4] == 10 / 32,
    "only the existing gold panel border band is shown")
assert(WarscapeHUDRail.height - WarscapeHUDTopBorder.height
    > WarscapeHUDMenuButton5.point[5] + WarscapeHUDMenuButton5.height / 2,
    "the border sits above the button frames without overlapping them")
assert(WarscapeHUDRail.backdrop.bgFile == "Interface\\AddOns\\WarscapeSkills\\art\\Stone"
    and WarscapeHUDRail.backdrop.tile and WarscapeHUDRail.backdrop.tileSize == 100,
    "HUD uses the Prayer panel's exact tiled background asset and sizing")
assert(WarscapePrayerFrame.backdrop.bgFile == WarscapeHUDRail.backdrop.bgFile
    and WarscapePrayerFrame.backdrop.tile == WarscapeHUDRail.backdrop.tile
    and WarscapePrayerFrame.backdrop.tileSize == WarscapeHUDRail.backdrop.tileSize)
for channel = 1, 4 do assert(WarscapeHUDRail.bg[channel] == WarscapePrayerFrame.bg[channel]) end
assert(Minimap:GetParent() == MinimapCluster and MinimapCluster:GetParent() == WarscapeHUDAssembly)
assert(WarscapeHUDRail.level < MinimapCluster.level and WarscapeHUDArt.level > WarscapeHUDRail.level,
    "the ring and gryphons cover the trim intersections naturally")
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
    assert(math.abs(distance - (MinimapBorder.width / 2 + 10)) < 0.001,
        "zoom button centres sit close enough for their frames to touch the ring")
    assert(control.scripts.OnClick == nativeMinimapClick)
end
assert(MiniMapWorldMapButton.scripts.OnClick == nativeMinimapClick and MiniMapTracking.scripts.OnMouseDown == nativeMinimapClick)
assert(not MiniMapWorldMapButton:IsShown() and not MiniMapTracking:IsShown())
MiniMapWorldMapButton:Show();MiniMapTracking:Show()
assert(not MiniMapWorldMapButton:IsShown() and not MiniMapTracking:IsShown(), "hidden minimap controls stay hidden")
assert(MiniMapWorldMapButton.scripts.OnClick == nativeMinimapClick
    and MiniMapTracking.scripts.OnMouseDown == nativeMinimapClick, "hidden controls keep their Blizzard handlers")
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
for index, iconName in pairs({[1]="INV_Gizmo_02",[2]="INV_Misc_GroupNeedMore",[4]="INV_Misc_Note_05",
    [7]="INV_Chest_Chain_04",[8]="Ability_DualWield",[9]="INV_Jewelry_Talisman_08",[10]="INV_Misc_Book_01"}) do
    local button=_G["WarscapeHUDMenuButton"..index]
    assert(button.icon.texture=="Interface\\Icons\\"..iconName)
    assert(button.icon.width==skillButton.icon.width and button.icon.height==skillButton.icon.height)
end
local inventoryPoint, inventoryRelative, inventoryRelativePoint, inventoryX, inventoryY =
    WarscapeHUDMenuButton5:GetPoint()
local inventoryLabelPoint, _, inventoryLabelRelativePoint, inventoryLabelX, inventoryLabelY =
    WarscapeHUDMenuButton5.warscapeKeybind:GetPoint()
assert(inventoryPoint == "CENTER" and inventoryRelative == WarscapeHUDAssembly
    and inventoryRelativePoint == "BOTTOM" and inventoryX == -116 and inventoryY == 44,
    "Inventory remains the fixed vertical reference, lowered slightly as requested")
for i = 1, 10 do
    local b = _G["WarscapeHUDMenuButton" .. i]
    assert(b and b.parent == WarscapeHUDAssembly and b.width == b.height)
    assert(math.abs(b.width - WarscapeSkillsSkin.metrics.hudButton) < 0.001, "button size comes from the shared visual metrics")
    local index = i <= 5 and i - 1 or i - 6
    local originalX = i <= 5 and (-140 / 2 - 24 - 5 * 44 - 4 * 24 + index * 68)
        or (140 / 2 + 24 + index * 68)
    assert(b.point[1] == inventoryPoint and b.point[2] == inventoryRelative
        and b.point[3] == inventoryRelativePoint and b.point[4] == originalX + 22
        and b.point[5] == inventoryY,
        "every frame shares the Inventory vertical anchor without changing its x position")
    assert(b.point[5] - b.height / 2 >= 0 and b.point[5] + b.height / 2 <= WarscapeHUDRail.height,
        "each button frame fits within the background height")
    if b.icon then
        assert(math.abs(b.icon.width - b.width * 56 / 68) < 0.001 and b.icon.width == b.icon.height,
            "icon artwork scales with its button frame")
    end
    if b.warscapeKeybind then
        assert(b.warscapeKeybind.point[1] == inventoryLabelPoint
            and b.warscapeKeybind.point[2] == b and b.warscapeKeybind.point[3] == inventoryLabelRelativePoint
            and b.warscapeKeybind.point[4] == inventoryLabelX and b.warscapeKeybind.point[5] == inventoryLabelY,
            "all labels use the Inventory label's exact below-button anchor")
        assert(b.point[5] - b.height / 2 - 2 - b.warscapeKeybind.fontSize > 0,
            "keybind label retains bottom padding inside the backing")
    end
    assert((i == 3 and not b.mouseEnabled and not b.warscapeKeybind)
        or (i ~= 3 and b.warscapeKeybind and b.warscapeKeybind.point[1] == "TOP"), "labels sit directly under assigned buttons")
end
assert(WarscapeHUDMenuButton3.icon == nil and WarscapeHUDMenuButton3.scripts.OnClick == nil)
assert(WarscapeHUDHealthBarAnchor.width == WarscapeHUDPrayerBarAnchor.width and WarscapeHUDHealthBarAnchor.height == 22)
assert(WarscapeHUDHealthBarAnchor.point[5] == WarscapeHUDPrayerBarAnchor.point[5]
    and WarscapeHUDHealthBarAnchor.point[5] == 82, "reserved bar layout stays fixed")
assert(WarscapeHUDLeftGryphon.width / WarscapeHUDLeftGryphon.height == 128 / 76)
assert(WarscapeHUDLeftGryphon.texture == WarscapeHUDRightGryphon.texture
    and WarscapeHUDLeftGryphon.texture == "Interface\\AddOns\\WarscapeHUD\\art\\WarscapeGryphonDesign5HD.tga"
    and WarscapeHUDLeftGryphon.width == 160 and WarscapeHUDRightGryphon.width == 160
    and WarscapeHUDLeftGryphon.height == WarscapeHUDRightGryphon.height,
    "both gryphons share the higher-resolution same-design texture at their original dimensions")
assert(WarscapeHUDLeftGryphon.point[1] == "BOTTOMLEFT" and WarscapeHUDLeftGryphon.point[2] == WarscapeHUDArt
    and WarscapeHUDLeftGryphon.point[3] == "BOTTOMLEFT" and WarscapeHUDLeftGryphon.point[4] == -8
    and WarscapeHUDRightGryphon.point[1] == "BOTTOMRIGHT" and WarscapeHUDRightGryphon.point[2] == WarscapeHUDArt
    and WarscapeHUDRightGryphon.point[3] == "BOTTOMRIGHT" and WarscapeHUDRightGryphon.point[4] == 8,
    "gryphon anchors and positions remain unchanged")
assert(WarscapeHUDLeftGryphon.point[5] == 0 and WarscapeHUDRightGryphon.point[5] == 0
    and WarscapeHUDLeftGryphon.texcoord[1] == 0 and WarscapeHUDLeftGryphon.texcoord[2] == 1
    and WarscapeHUDLeftGryphon.texcoord[3] == 52 / 128 and WarscapeHUDLeftGryphon.texcoord[4] == 1)
assert(WarscapeHUDRightGryphon.texcoord[1] == 1 and WarscapeHUDRightGryphon.texcoord[2] == 0)
assert(WarscapeHUDArt.level > WarscapeHUDMenuButton1.level, "gryphon claws draw above the adjoining slots")
local tileEnd = 0
for _, w in ipairs(widgets) do
    if w.parent == WarscapeHUDRail and w.kind == "Texture" and w.layer == "BACKGROUND" then
        assert(math.abs(w.point[4] - tileEnd) < 0.001, "no backing gaps or overlaps")
        local sourceWidth = (w.texcoord[2] - w.texcoord[1]) * 256
        local sourceHeight = (w.texcoord[4] - w.texcoord[3]) * 64
        assert(math.abs(w.width / sourceWidth - w.height / sourceHeight) < 0.001, "native rail is never stretched")
        tileEnd = tileEnd + w.width
    end
end
assert(math.abs(tileEnd - WarscapeHUDRail.width) < 0.001)
local first, last = WarscapeHUDMenuButton1, WarscapeHUDMenuButton10
assert(first.point[4] == -WarscapeHUDRail.width / 2 + 22
    and last.point[4] == WarscapeHUDRail.width / 2 - 22,
    "outer button centres retain their original grid positions")
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
assert(WarscapeInventoryFrame:IsShown() and WarscapeHUDMenuButton5.highlightLocked)
assert(WarscapeSkillsFrame:IsShown() and WarscapeHUDMenuButton6.highlightLocked)
WarscapeHUDMenuButton8.scripts.OnClick(WarscapeHUDMenuButton8)
assert(WarscapeAttackStylesFrame:IsShown() and WarscapeInventoryFrame:IsShown() and not WarscapeSkillsFrame:IsShown())
WarscapeHUDMenuButton9.scripts.OnClick(WarscapeHUDMenuButton9)
assert(WarscapePrayerFrame:IsShown() and WarscapeInventoryFrame:IsShown() and not WarscapeAttackStylesFrame:IsShown())
WarscapeHUDMenuButton10.scripts.OnClick(WarscapeHUDMenuButton10)
assert(WarscapeSpellbookFrame:IsShown() and WarscapeInventoryFrame:IsShown() and not WarscapePrayerFrame:IsShown())
WarscapeHUDMenuButton4.scripts.OnClick(WarscapeHUDMenuButton4)
assert(QuestLogFrame:IsShown() and not WarscapeInventoryFrame:IsShown() and WarscapeSpellbookFrame:IsShown())
WarscapeHUDMenuButton2.scripts.OnClick(WarscapeHUDMenuButton2)
assert(FriendsFrame:IsShown() and not QuestLogFrame:IsShown() and WarscapeSpellbookFrame:IsShown())
WarscapeHUDMenuButton7.scripts.OnClick(WarscapeHUDMenuButton7)
assert(CharacterFrame:IsShown() and not WarscapeSpellbookFrame:IsShown() and FriendsFrame:IsShown())
WarscapeHUDMenuButton1.scripts.OnClick(WarscapeHUDMenuButton1)
assert(GameMenuFrame:IsShown() and not FriendsFrame:IsShown() and CharacterFrame:IsShown())
WarscapeHUDMenuButton1.scripts.OnClick(WarscapeHUDMenuButton1)
assert(not GameMenuFrame:IsShown() and WarscapeHUDMenuButton1.alpha == 1)
WarscapeHUDMenuButton7.scripts.OnClick(WarscapeHUDMenuButton7)
assert(not CharacterFrame:IsShown() and not FriendsFrame:IsShown())
-- Native O key path is synchronized by the native window hook.
ToggleFriendsFrame()
assert(FriendsFrame:IsShown() and WarscapeHUDMenuButton2.highlightLocked)
ToggleFriendsFrame()
assert(not FriendsFrame:IsShown() and not WarscapeHUDMenuButton2.highlightLocked)
WarscapeSkills_Toggle()

ctrl = true
WarscapeHUDFrame.over = true
scaler.scripts.OnUpdate(scaler, 0)
assert(scaler.wheel and scaler.scripts.OnMouseWheel)
scaler.scripts.OnMouseWheel(scaler, 1)
assert(WarscapeHUDFrame.scale > 1 and WarscapePanels:GetScale("skills") == 1 and WarscapeInventoryFrame.scale == WarscapeSkillsFrame.scale)
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
assert(WarscapePanels:GetScale("skills") > 1 and WarscapeHUDFrame.scale == hudBeforeSkillsScale)
for i = 1, 30 do scaler.scripts.OnMouseWheel(scaler, 1) end
assert(WarscapePanels:GetScale("skills") == 1.5, "Skills maximum is 150% at this resolution")
for i = 1, 40 do scaler.scripts.OnMouseWheel(scaler, -1) end
assert(WarscapePanels:GetScale("skills") == 0.5, "Skills minimum is 50%")
assert(WarscapeHUDScales.hud == WarscapeHUDFrame.scale and WarscapeWindowLayouts.right.scale == WarscapePanels:GetScale("skills") and WarscapePanels:GetScale("inventory")==1)

ctrl = false
scaler.scripts.OnUpdate(scaler, 0)
assert(not scaler.wheel)
WarscapeHUDScales = {hud=1.2, skills=0.9}
WarscapePanelScales = nil;WarscapeWindowLayouts=nil -- Upgrade migrates the existing Skills preference once.
dispatch("PLAYER_LOGIN")
assert(WarscapeHUDFrame.scale == 1.2 and WarscapePanels:GetScale("skills") == 0.9 and WarscapeInventoryFrame.scale == WarscapeSkillsFrame.scale)
-- Model UIParent in logical units at different global UI scales. The root's
-- effective pixel width must stay at 52% * saved HUD scale of the viewport.
for _, resolution in ipairs({{1280,720}, {1920,1080}, {2560,1440}, {3440,1440}}) do
    for _, uiScale in ipairs({0.64, 0.8, 1.0}) do
        UIParent:SetScale(uiScale)
        UIParent:SetSize(resolution[1] / uiScale, resolution[2] / uiScale)
        -- SetSize dispatches the registered size hooks.
        for _, userScale in ipairs({0.5, 1.0, 1.5}) do
            WarscapeHUDScales.hud = userScale
            dispatch("PLAYER_LOGIN")
            local width = WarscapeHUDFrame.width * WarscapeHUDFrame:GetEffectiveScale()
            assert(math.abs(width / resolution[1] - math.min(0.90 * userScale,0.98)) < 0.0001)
            local mapScale = Minimap:GetEffectiveScale()
            assert(math.abs(WarscapeHUDTopBorder:GetEffectiveScale() - mapScale) < 0.0001,
                "the border follows the assembly scale at every tested viewport")
            local bottom = MinimapCluster.point[5] * mapScale
            local top = (MinimapCluster.point[5] + MinimapBorder.height) * mapScale
            assert(bottom > 0 and top <= WarscapeHUDFrame.height * WarscapeHUDFrame:GetEffectiveScale() + 0.0001)
assert(WarscapeHUDFrame.point[1] == "BOTTOM" and WarscapeHUDFrame.point[4] == 0 and WarscapeHUDFrame.point[5] == 0)
        end
    end
end
UIParent:SetScale(1)
UIParent:SetSize(800, 640)
WarscapeHUDScales = {hud=1.0, skills=1.5}
WarscapePanels:State("left").scale=1.5;WarscapePanels:State("right").scale=1.5
dispatch("PLAYER_LOGIN")
assert(WarscapeHUDFrame.scale == 1.0 and WarscapeSkillsFrame.scale <= (640 - WarscapeHUDFrame.height - 18) / 514 and WarscapeInventoryFrame.scale == WarscapeSkillsFrame.scale)
''')
print("PASS: Prayer stone HUD backing, trim alpha, harmonised buttons, minimap, gryphons, icon, panel sync, scaling and 36 viewport/scale cases")
