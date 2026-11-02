BINDING_HEADER_WARSCAPE_MENUS = "Warscape Menus"
BINDING_NAME_WARSCAPE_TOGGLE_FRIENDS = "Toggle Friends / Social"
BINDING_NAME_WARSCAPE_TOGGLE_QUESTS = "Toggle Quest Journal"
BINDING_NAME_WARSCAPE_TOGGLE_EQUIPMENT = "Toggle Character Equipment"
BINDING_NAME_WARSCAPE_TOGGLE_ATTACK_STYLES = "Toggle Warscape Attack Styles"
BINDING_NAME_WARSCAPE_TOGGLE_PRAYER = "Toggle Warscape Prayer"
BINDING_NAME_WARSCAPE_TOGGLE_SPELLBOOK = "Toggle Warscape Spellbook"

local owner = CreateFrame("Frame", "WarscapeMenuPanelsBindingOwner")
local applying = false
local keys = {
    {key="O", action="WARSCAPE_TOGGLE_FRIENDS", defaults={TOGGLESOCIAL=true}},
    {key="L", action="WARSCAPE_TOGGLE_QUESTS", defaults={TOGGLEQUESTLOG=true}},
    {key="C", action="WARSCAPE_TOGGLE_EQUIPMENT", defaults={TOGGLECHARACTER0=true}},
    {key="K", action="WARSCAPE_TOGGLE_ATTACK_STYLES", defaults={TOGGLECHARACTER1=true, TOGGLESKILLS=true}},
    -- I is an explicit Warscape assignment; override any competing Blizzard
    -- action while retaining the client's normal key handling in text fields.
    {key="I", action="WARSCAPE_TOGGLE_PRAYER", priority=true},
    {key="P", action="WARSCAPE_TOGGLE_SPELLBOOK", defaults={TOGGLESPELLBOOK=true}},
}
local function apply()
    if applying or InCombatLockdown() then return end
    applying = true
    ClearOverrideBindings(owner)
    for _, binding in ipairs(keys) do
        local current = GetBindingAction(binding.key)
        if binding.priority then
            SetOverrideBinding(owner, true, binding.key, binding.action)
        elseif not GetBindingKey(binding.action) and (current == "" or binding.defaults[current]) then
            SetOverrideBinding(owner, false, binding.key, binding.action)
        end
    end
    applying = false
end
owner:RegisterEvent("PLAYER_LOGIN")
owner:RegisterEvent("UPDATE_BINDINGS")
owner:RegisterEvent("PLAYER_REGEN_ENABLED")
owner:SetScript("OnEvent", apply)
