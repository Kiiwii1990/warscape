BINDING_HEADER_WARSCAPE_INVENTORY = "Warscape"
BINDING_NAME_WARSCAPE_TOGGLE_INVENTORY = "Toggle Warscape Inventory"
local owner = CreateFrame("Frame", "WarscapeInventoryBindingOwner")
local applying = false
local function apply()
    if applying or InCombatLockdown() then return end
    applying = true
    ClearOverrideBindings(owner)
    local current = GetBindingAction("B")
    if not GetBindingKey("WARSCAPE_TOGGLE_INVENTORY") and (current == "TOGGLEBACKPACK" or current == "OPENALLBAGS") then
        SetOverrideBinding(owner, false, "B", "WARSCAPE_TOGGLE_INVENTORY")
    end
    applying = false
end
owner:RegisterEvent("PLAYER_LOGIN")
owner:RegisterEvent("UPDATE_BINDINGS")
owner:RegisterEvent("PLAYER_REGEN_ENABLED")
owner:SetScript("OnEvent", apply)
