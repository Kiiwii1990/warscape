-- Selectively hide the standard WoW 3.3.5a gameplay HUD. Keep UIParent and
-- unrelated UI (chat, menus, tooltips and Warscape addons) fully functional.

local recoveryKey = "CTRL-ALT-F12"
local bindingCommand = "WARSCAPEUI_TOGGLE"

-- These are stock 3.3.5a HUD roots and standalone display frames. MainMenuBar
-- owns the main action bar, XP/reputation bars, micro menu and bag buttons.
-- Its action bindings remain registered while the visuals are hidden.
local hudFrameNames = {
    "PlayerFrame", "TargetFrame", "FocusFrame", "PetFrame",
    "MainMenuBar", "MainMenuExpBar", "ReputationWatchBar", "MainMenuBarArtFrame",
    "MultiBarBottomLeft", "MultiBarBottomRight", "MultiBarRight", "MultiBarLeft",
    -- WarscapeHUD owns the stock Minimap frame and displays it in its own
    -- bottom-centre shell. Do not hide it with the legacy Blizzard cluster.
    "BuffFrame", "TemporaryEnchantFrame",
    "CastingBarFrame", "PetCastingBarFrame", "TargetFrameSpellBar", "FocusFrameSpellBar",
    "PetActionBarFrame", "ShapeshiftBarFrame", "PossessBarFrame", "BonusActionBarFrame",
    "VehicleMenuBar", "VehicleMenuBarActionButtonFrame", "VehicleSeatIndicator", "MultiCastActionBarFrame",
    "ComboFrame", "RuneFrame", "PlayerFrameAlternateManaBar", "PlayerFrameAlternateEnergyBar",
}

local bindingOwner = CreateFrame("Frame", "WarscapeUIHideBindingOwner")
local events = CreateFrame("Frame")
local hookedFrames = {}
local originalVisibility = {}
local inWorld = false
local pending = false

BINDING_HEADER_WARSCAPE_UI = "Warscape UI"
BINDING_NAME_WARSCAPEUI_TOGGLE = "Toggle hidden interface (Ctrl-Alt-F12)"

local function rememberVisibility(name, frame)
    if originalVisibility[name] == nil then
        originalVisibility[name] = frame:IsShown()
    end
end

local function hookFrame(name, frame)
    if hookedFrames[name] == frame then
        return
    end
    hookedFrames[name] = frame
    frame:HookScript("OnShow", function(self)
        if WarscapeUIHidden and inWorld then
            rememberVisibility(name, self)
            if InCombatLockdown() then
                pending = true
            else
                self:Hide()
            end
        end
    end)
end

local function applyHiddenFrames()
    if InCombatLockdown() then
        pending = true
        return
    end
    pending = false
    for _, name in ipairs(hudFrameNames) do
        local frame = _G[name]
        if frame and frame.IsShown and frame.Hide and frame.HookScript then
            hookFrame(name, frame)
            rememberVisibility(name, frame)
            if frame:IsShown() then
                frame:Hide()
            end
        end
    end
end

local function restoreFrameVisibility()
    if InCombatLockdown() then
        pending = true
        return
    end
    pending = false
    -- Restore in list order: containers first, then any standalone child frames.
    for _, name in ipairs(hudFrameNames) do
        local frame, wasShown = _G[name], originalVisibility[name]
        if frame and wasShown ~= nil then
            if wasShown and not frame:IsShown() then
                frame:Show()
            elseif not wasShown and frame:IsShown() then
                frame:Hide()
            end
        end
    end
    originalVisibility = {}
end

local function restoreLegacyCVars()
    -- Older UI Hide builds changed these unrelated presentation CVars. Restore
    -- their saved pre-hide values once when upgrading, then leave them alone.
    if type(WarscapeUIOriginalCVars) == "table" then
        for name, value in pairs(WarscapeUIOriginalCVars) do
            SetCVar(name, value)
        end
        WarscapeUIOriginalCVars = nil
    end
end

local function applyRecoveryBinding()
    if InCombatLockdown() then
        pending = true
        return
    end
    ClearOverrideBindings(bindingOwner)
    -- This session-only binding belongs to this addon. WarscapeSkills' N-key
    -- override has a different owner and is never cleared or changed here.
    SetOverrideBinding(bindingOwner, false, recoveryKey, bindingCommand)
end

local function setHidden(hidden)
    WarscapeUIHidden = hidden
    if not inWorld then
        return
    end
    if hidden then
        applyHiddenFrames()
    else
        restoreFrameVisibility()
    end
end

function WarscapeUI_Toggle()
    setHidden(not WarscapeUIHidden)
end

local function handleSlash(message)
    local command = string.lower(message or "")
    command = string.match(command, "^%s*(.-)%s*$")
    if command == "hide" then
        setHidden(true)
    elseif command == "show" then
        setHidden(false)
    elseif command == "toggle" or command == "" then
        WarscapeUI_Toggle()
    else
        DEFAULT_CHAT_FRAME:AddMessage("Usage: /warscapeui hide|show|toggle")
    end
end

SLASH_WARSCAPEUI1 = "/warscapeui"
SlashCmdList.WARSCAPEUI = handleSlash

events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("PLAYER_LOGOUT")
events:RegisterEvent("UPDATE_BINDINGS")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("UPDATE_BONUS_ACTIONBAR")
events:RegisterEvent("UPDATE_SHAPESHIFT_FORMS")
events:RegisterEvent("PET_BAR_UPDATE")
events:RegisterEvent("UNIT_PET")
events:RegisterEvent("UNIT_ENTERED_VEHICLE")
events:RegisterEvent("UNIT_EXITED_VEHICLE")
events:RegisterEvent("PLAYER_CONTROL_GAINED")

events:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_LOGIN" then
        restoreLegacyCVars()
        applyRecoveryBinding()
        if WarscapeUIHidden == nil then
            WarscapeUIHidden = true
        end
    elseif event == "PLAYER_ENTERING_WORLD" then
        inWorld = true
        if WarscapeUIHidden then
            applyHiddenFrames()
        end
    elseif event == "PLAYER_LOGOUT" then
        inWorld = false
        restoreFrameVisibility()
        restoreLegacyCVars()
    elseif event == "PLAYER_REGEN_ENABLED" then
        applyRecoveryBinding()
        if pending then
            if WarscapeUIHidden then
                applyHiddenFrames()
            else
                restoreFrameVisibility()
            end
        end
    elseif event == "UPDATE_BINDINGS" then
        applyRecoveryBinding()
    elseif inWorld and WarscapeUIHidden then
        -- Reconcile late-created/vehicle HUD frames only on relevant UI events;
        -- there is no per-frame scan or OnUpdate polling.
        applyHiddenFrames()
    end
end)
