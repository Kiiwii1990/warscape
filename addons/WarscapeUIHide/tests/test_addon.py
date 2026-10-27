"""Lua 5.1 tests for selective WoW HUD hiding and Warscape UI preservation."""
from pathlib import Path
import xml.etree.ElementTree as ET
import unittest

from lupa.lua51 import LuaRuntime


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parents[0] / "WarscapeSkills"


class WarscapeUIHideTests(unittest.TestCase):
    def test_binding_manifest_and_toc(self):
        binding = ET.parse(ROOT / "Bindings.xml").getroot().find("Binding")
        self.assertIsNotNone(binding)
        self.assertEqual(binding.attrib["name"], "WARSCAPEUI_TOGGLE")
        self.assertEqual(binding.attrib["header"], "WARSCAPE_UI")
        self.assertEqual(binding.text.strip(), "WarscapeUI_Toggle()")
        toc = (ROOT / "WarscapeUIHide.toc").read_text()
        self.assertIn("## Interface: 30300", toc)
        self.assertIn("SavedVariablesPerCharacter: WarscapeUIHidden, WarscapeUIOriginalCVars", toc)

    def test_selective_hide_chat_skills_menus_and_recovery(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(r'''
            widgets, SlashCmdList, overrides = {}, {}, {}
            combat, baseN, addonN = false, "TOGGLETALENTS", nil
            cvars = {UnitNameNPC="1", nameplateShowEnemies="1", enableCombatText="1"}
            function GetCVar(name) return cvars[name] end
            function SetCVar(name, value) cvars[name] = tostring(value) end
            function InCombatLockdown() return combat end
            function CreateFrame(kind, name)
                local frame = {kind=kind, name=name, scripts={}, shown=true, hideCalls=0, showCalls=0}
                function frame:RegisterEvent(event) end
                function frame:SetScript(script, fn) self.scripts[script] = fn end
                function frame:HookScript(script, fn) self.hooks = self.hooks or {}; self.hooks[script] = fn end
                function frame:IsShown() return self.shown end
                function frame:Hide()
                    self.hideCalls = self.hideCalls + 1
                    local changed = self.shown
                    self.shown = false
                    if changed and self.hooks and self.hooks.OnHide then self.hooks.OnHide(self) end
                end
                function frame:Show()
                    local changed = not self.shown
                    self.shown = true
                    if changed and self.hooks and self.hooks.OnShow then self.hooks.OnShow(self) end
                end
                widgets[#widgets+1] = frame
                if name then _G[name] = frame end
                return frame
            end
            function ClearOverrideBindings(owner) overrides[owner] = {} end
            function SetOverrideBinding(owner, priority, key, command)
                overrides[owner] = overrides[owner] or {}
                overrides[owner][key] = command
            end
            function GetBindingKey(action) assert(action == "WARSCAPE_TOGGLE_SKILLS"); return addonN end
            function GetBindingAction(key) assert(key == "N"); return baseN end
            UIParent = CreateFrame("Frame", "UIParent")
            local hud = {
                "PlayerFrame", "TargetFrame", "FocusFrame", "PetFrame", "MainMenuBar",
                "MainMenuExpBar", "ReputationWatchBar", "MainMenuBarArtFrame",
                "MultiBarBottomLeft", "MultiBarBottomRight", "MultiBarRight", "MultiBarLeft",
                "BuffFrame", "TemporaryEnchantFrame",
                "CastingBarFrame", "PetCastingBarFrame", "TargetFrameSpellBar", "FocusFrameSpellBar",
                "PetActionBarFrame", "ShapeshiftBarFrame", "PossessBarFrame", "BonusActionBarFrame",
                "VehicleMenuBar", "VehicleMenuBarActionButtonFrame", "VehicleSeatIndicator", "MultiCastActionBarFrame",
                "ComboFrame", "RuneFrame", "PlayerFrameAlternateManaBar", "PlayerFrameAlternateEnergyBar"
            }
            for _, name in ipairs(hud) do _G[name] = CreateFrame("Frame", name) end
            MinimapCluster = CreateFrame("Frame", "MinimapCluster")
            Minimap = CreateFrame("Frame", "Minimap")
            VehicleMenuBar:Hide() -- retain pre-hide hidden state on restore
            vehicleHideCountBeforeAddon = VehicleMenuBar.hideCalls
            ChatFrame1 = CreateFrame("Frame", "ChatFrame1")
            ChatFrame1EditBox = CreateFrame("EditBox", "ChatFrame1EditBox")
            WarscapeSkillsFrame = CreateFrame("Frame", "WarscapeSkillsFrame")
            WarscapeSkillsFrame:Hide()
            GameMenuFrame = CreateFrame("Frame", "GameMenuFrame")
            GameTooltip = CreateFrame("Frame", "GameTooltip")
            UIErrorsFrame = CreateFrame("Frame", "UIErrorsFrame")
            CharacterFrame = CreateFrame("Frame", "CharacterFrame")
            ContainerFrame1 = CreateFrame("Frame", "ContainerFrame1")
            SpellBookFrame = CreateFrame("Frame", "SpellBookFrame")
            QuestLogFrame = CreateFrame("Frame", "QuestLogFrame")
            WorldMapFrame = CreateFrame("Frame", "WorldMapFrame")
            DEFAULT_CHAT_FRAME = {AddMessage=function(self, msg) self.last=msg end}
            WarscapeUIHidden = true -- preference from the old addon build
            WarscapeUIOriginalCVars = {UnitNameNPC="1", nameplateShowEnemies="1", enableCombatText="1"}
        ''')

        # Load the real N-key override first, then load the selective HUD addon.
        lua.execute((SKILLS / "Bindings.lua").read_text())
        lua.execute((ROOT / "WarscapeUIHide.lua").read_text())
        lua.execute(r'''
            local handlers = {}
            for _, frame in ipairs(widgets) do
                if frame.scripts.OnEvent then handlers[#handlers+1] = frame end
            end
            assert(#handlers == 2)
            local skillsOwner = WarscapeSkillsBindingOwner
            local hudHandler
            for _, frame in ipairs(handlers) do
                if frame ~= skillsOwner then hudHandler = frame end
            end
            assert(hudHandler)
            local function event(name, ...) hudHandler.scripts.OnEvent(hudHandler, name, ...) end

            event("PLAYER_LOGIN")
            assert(WarscapeUIOriginalCVars == nil)
            assert(cvars.UnitNameNPC == "1" and cvars.nameplateShowEnemies == "1" and cvars.enableCombatText == "1")
            skillsOwner.scripts.OnEvent(skillsOwner, "PLAYER_LOGIN")
            assert(overrides[skillsOwner].N == "WARSCAPE_TOGGLE_SKILLS")
            event("PLAYER_ENTERING_WORLD")

            assert(UIParent:IsShown() and UIParent.hideCalls == 0, "UIParent must never be hidden")
            for _, name in ipairs({
                "PlayerFrame", "TargetFrame", "FocusFrame", "PetFrame", "MainMenuBar",
                "MainMenuExpBar", "ReputationWatchBar", "MainMenuBarArtFrame",
                "MultiBarBottomLeft", "MultiBarBottomRight", "MultiBarRight", "MultiBarLeft",
                "BuffFrame", "TemporaryEnchantFrame",
                "CastingBarFrame", "PetCastingBarFrame", "TargetFrameSpellBar", "FocusFrameSpellBar",
                "PetActionBarFrame", "ShapeshiftBarFrame", "PossessBarFrame", "BonusActionBarFrame",
                "VehicleMenuBarActionButtonFrame", "VehicleSeatIndicator", "MultiCastActionBarFrame", "ComboFrame", "RuneFrame",
                "PlayerFrameAlternateManaBar", "PlayerFrameAlternateEnergyBar"
            }) do assert(not _G[name]:IsShown(), name .. " should be hidden") end
            assert(VehicleMenuBar.hideCalls == vehicleHideCountBeforeAddon, "already-hidden frames should not be needlessly changed")
            assert(ChatFrame1:IsShown() and ChatFrame1EditBox:IsShown())
            assert(not WarscapeSkillsFrame:IsShown())
            assert(GameMenuFrame:IsShown() and GameTooltip:IsShown() and UIErrorsFrame:IsShown())
            assert(CharacterFrame:IsShown() and ContainerFrame1:IsShown() and SpellBookFrame:IsShown())
            assert(QuestLogFrame:IsShown() and WorldMapFrame:IsShown())
            assert(overrides[skillsOwner].N == "WARSCAPE_TOGGLE_SKILLS", "N binding must remain owned by Skills")
            assert(overrides[WarscapeUIHideBindingOwner]["CTRL-ALT-F12"] == "WARSCAPEUI_TOGGLE")

            -- HUD frames shown later (for example during vehicle transitions) are hidden selectively.
            VehicleMenuBar:Show()
            event("UNIT_ENTERED_VEHICLE", "player")
            assert(not VehicleMenuBar:IsShown())

            -- Chat slash commands remain callable; show restores the original frame states.
            SlashCmdList.WARSCAPEUI("show")
            assert(not WarscapeUIHidden and UIParent:IsShown())
            assert(MinimapCluster:IsShown() and Minimap:IsShown(), "Warscape minimap remains available")
            for _, name in ipairs({"PlayerFrame", "MainMenuBar", "BuffFrame", "CastingBarFrame"}) do
                assert(_G[name]:IsShown(), name .. " should be restored")
            end
            assert(not VehicleMenuBar:IsShown(), "pre-hidden frame state should be restored")
            assert(ChatFrame1:IsShown() and ChatFrame1EditBox:IsShown() and GameMenuFrame:IsShown())
            assert(CharacterFrame:IsShown() and ContainerFrame1:IsShown() and SpellBookFrame:IsShown())
            assert(QuestLogFrame:IsShown() and WorldMapFrame:IsShown())
            assert(overrides[skillsOwner].N == "WARSCAPE_TOGGLE_SKILLS")

            -- N continues to invoke the Skills toggle; the hidden-mode list never targets its frame.
            function WarscapeSkills_Toggle()
                if WarscapeSkillsFrame:IsShown() then WarscapeSkillsFrame:Hide() else WarscapeSkillsFrame:Show() end
            end
            WarscapeSkills_Toggle(); assert(WarscapeSkillsFrame:IsShown())
            WarscapeSkills_Toggle(); assert(not WarscapeSkillsFrame:IsShown())

            SlashCmdList.WARSCAPEUI("hide")
            WarscapeSkills_Toggle()
            assert(WarscapeUIHidden and WarscapeSkillsFrame:IsShown() and ChatFrame1:IsShown() and UIParent:IsShown())
            event("UPDATE_BINDINGS")
            assert(overrides[skillsOwner].N == "WARSCAPE_TOGGLE_SKILLS")
            GameMenuFrame:Hide(); GameMenuFrame:Show(); assert(GameMenuFrame:IsShown()) -- Escape menu is not suppressed
            combat = true
            local before = MainMenuBar.hideCalls
            SlashCmdList.WARSCAPEUI("show")
            assert(not WarscapeUIHidden and MainMenuBar.hideCalls == before)
            combat = false
            event("PLAYER_REGEN_ENABLED")
            assert(MainMenuBar:IsShown() and MinimapCluster:IsShown())
            assert(overrides[skillsOwner].N == "WARSCAPE_TOGGLE_SKILLS")
            SlashCmdList.WARSCAPEUI("toggle")
            assert(WarscapeUIHidden and not MainMenuBar:IsShown())
            SlashCmdList.WARSCAPEUI("show")
            assert(MainMenuBar:IsShown())
        ''')


if __name__ == "__main__":
    unittest.main()
