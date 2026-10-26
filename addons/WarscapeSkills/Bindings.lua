-- Supported addon action, visible in the client's Key Bindings menu.
BINDING_HEADER_WARSCAPE_SKILLS = "Warscape"
BINDING_NAME_WARSCAPE_TOGGLE_SKILLS = "Toggle Warscape Skills"

local owner = CreateFrame("Frame", "WarscapeSkillsBindingOwner")
local applying = false
local function applyBindings()
    if applying or InCombatLockdown() then return end
    applying = true
    ClearOverrideBindings(owner)
    -- Replace only the default talent key. Explicit addon bindings and a user's
    -- different action on N take precedence. Never write account/character keys.
    if not GetBindingKey("WARSCAPE_TOGGLE_SKILLS") and GetBindingAction("N") == "TOGGLETALENTS" then
        SetOverrideBinding(owner, false, "N", "WARSCAPE_TOGGLE_SKILLS")
    end
    applying = false
end
owner:RegisterEvent("PLAYER_LOGIN")
owner:RegisterEvent("UPDATE_BINDINGS")
owner:RegisterEvent("PLAYER_REGEN_ENABLED")
owner:SetScript("OnEvent", applyBindings)
