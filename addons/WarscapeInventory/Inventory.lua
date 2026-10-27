local prefix = "WCInventory"
local panel = CreateFrame("Frame", "WarscapeInventoryFrame", UIParent)
local total, status = WarscapeSkillsSkin.Panel(panel, {title = "Inventory", closeName = "WarscapeInventoryCloseButton", totalName = "WarscapeInventoryTotal"})
panel:SetPoint("CENTER")
panel:SetFrameStrata("DIALOG")
panel:SetClampedToScreen(true)
panel:SetMovable(true)
panel:EnableMouse(true)
panel:RegisterForDrag("LeftButton")
panel:SetScript("OnDragStart", function(self) self:StartMoving() end)
panel:SetScript("OnDragStop", function(self)
    self:StopMovingOrSizing()
    local point, _, relative, x, y = self:GetPoint()
    WarscapeInventoryPosition = {point = point, relative = relative, x = x, y = y}
end)
table.insert(UISpecialFrames, "WarscapeInventoryFrame")

local slots, containers = {}, {}
local token, revision, usable, state, lastRequest = nil, 0, 0, "PENDING", -10
local observedExtensionSlots = -1
for bag = 0, 1 do
    local container = CreateFrame("Frame", "WarscapeInventoryContainer" .. bag, panel)
    container:SetAllPoints(panel)
    container:SetID(bag)
    containers[bag] = container
end

local function allowed(button)
    return state == "READY" and button.logical <= usable
        and button:GetID() <= GetContainerNumSlots(button:GetParent():GetID())
end

local function lockedTooltip(button)
    GameTooltip:SetOwner(button, "ANCHOR_RIGHT")
    if state ~= "READY" then
        GameTooltip:SetText(state == "PENDING" and "Loading inventory..." or "Inventory unavailable")
    else
        GameTooltip:SetText("Locked inventory slot")
        GameTooltip:AddLine("Complete the beginner questline to unlock four additional inventory slots.", 1, 0.82, 0.25, true)
    end
    GameTooltip:Show()
end

for i = 1, 28 do
    local bag, slot = i <= 16 and 0 or 1, i <= 16 and i or i - 16
    local button = CreateFrame("Button", "WarscapeInventorySlot" .. i, containers[bag], "ContainerFrameItemButtonTemplate")
    button:SetID(slot)
    button.logical = i
    button:ClearAllPoints()
    button:SetSize(44, 44)
    button:SetPoint("TOPLEFT", panel, "TOPLEFT", 78 + ((i - 1) % 4) * 100, -102 - math.floor((i - 1) / 4) * 46)
    local icon = _G[button:GetName() .. "IconTexture"]
    icon:ClearAllPoints()
    icon:SetPoint("CENTER", button, "CENTER", 0, 0)
    icon:SetSize(40, 40)
    icon:SetTexCoord(0.06, 0.94, 0.06, 0.94)
    local normal = button:GetNormalTexture()
    normal:ClearAllPoints()
    normal:SetPoint("CENTER", button, "CENTER", 0, -1)
    normal:SetSize(44 * 64 / 37, 44 * 64 / 37)
    _G[button:GetName() .. "Cooldown"]:SetAllPoints(button)
    button.padlock = button:CreateTexture(nil, "OVERLAY")
    button.padlock:SetTexture("Interface\\LFGFrame\\UI-LFG-ICON-LOCK")
    button.padlock:SetSize(24, 24)
    button.padlock:SetPoint("CENTER", button, "CENTER", 0, 0)
    -- Keep the original template's complete item actions: use/equip, spell
    -- targeting, merchant confirmations, split stacks, modified clicks and drag.
    for _, script in ipairs({"OnClick", "OnDragStart", "OnReceiveDrag"}) do
        local native = button:GetScript(script)
        button:SetScript(script, function(self, ...)
            if allowed(self) and native then native(self, ...) end
        end)
    end
    local nativeEnter = button:GetScript("OnEnter")
    button:SetScript("OnEnter", function(self, ...)
        if not allowed(self) then lockedTooltip(self)
        elseif nativeEnter then nativeEnter(self, ...) end
    end)
    button.UpdateTooltip = button:GetScript("OnEnter")
    button:Show()
    slots[i] = button
end

local function refresh()
    observedExtensionSlots = GetContainerNumSlots(1)
    for _, button in ipairs(slots) do
        local enabled = allowed(button)
        button.warscapeLocked = not enabled
        local texture, count, locked, _, readable
        if enabled then
            texture, count, locked, _, readable = GetContainerItemInfo(button:GetParent():GetID(), button:GetID())
        end
        SetItemButtonTexture(button, texture or "Interface\\PaperDoll\\UI-Backpack-EmptySlot")
        SetItemButtonCount(button, count or 0)
        SetItemButtonDesaturated(button, not enabled or locked, 0.4, 0.4, 0.4)
        button:GetNormalTexture():SetVertexColor(enabled and 1 or 0.4, enabled and 1 or 0.4, enabled and 1 or 0.4)
        button.hasItem, button.readable = texture and 1 or nil, readable
        if texture then ContainerFrame_UpdateCooldown(button:GetParent():GetID(), button)
        else _G[button:GetName() .. "Cooldown"]:Hide() end
        if button.logical > 24 and not enabled then button.padlock:Show() else button.padlock:Hide() end
        local questTexture = _G[button:GetName() .. "IconQuestTexture"]
        if enabled then
            local isQuestItem, questId, active = GetContainerItemQuestInfo(button:GetParent():GetID(), button:GetID())
            if questId and not active then questTexture:SetTexture(TEXTURE_ITEM_QUEST_BANG); questTexture:Show()
            elseif questId or isQuestItem then questTexture:SetTexture(TEXTURE_ITEM_QUEST_BORDER); questTexture:Show()
            else questTexture:Hide() end
        else questTexture:Hide() end
        if GameTooltip:GetOwner() == button then button.UpdateTooltip(button) end
    end
    if state == "READY" then
        total.value:SetText("Inventory slots: " .. usable .. " / 28")
        status:SetText(usable == 24 and "Four slots unlock after the beginner questline." or "")
    elseif state == "PENDING" then
        total.value:SetText("Inventory")
        status:SetText("Waiting for inventory...")
    else
        total.value:SetText("Inventory unavailable")
        status:SetText("Please contact support. Your existing items are preserved.")
    end
end

local function request()
    if not token or GetTime() - lastRequest < 1 then return end
    lastRequest = GetTime()
    SendAddonMessage(prefix, "HELLO|1|" .. token, "WHISPER", UnitName("player"))
end

panel:Hide()
WarscapePanels:Register("inventory", panel, {onShow = function() refresh(); request() end})
function WarscapeInventory_Toggle() WarscapePanels:Toggle("inventory") end
SLASH_WARSCAPEINVENTORY1 = "/winventory"
SlashCmdList.WARSCAPEINVENTORY = WarscapeInventory_Toggle

local function suppressNativeBags()
    for i = 1, (NUM_CONTAINER_FRAMES or 13) do
        local frame = _G["ContainerFrame" .. i]
        if frame then
            if not frame.warscapeInventoryHook then
                frame.warscapeInventoryHook = true
                frame:HookScript("OnShow", function(self)
                    local bag = self:GetID()
                    if bag and bag >= 0 and bag <= 4 then
                        self:Hide()
                        WarscapePanels:Open("inventory")
                    end
                end)
            end
            local bag = frame:GetID()
            if bag and bag >= 0 and bag <= 4 then frame:Hide() end
        end
    end
end

local events = CreateFrame("Frame")
for _, event in ipairs({"PLAYER_LOGIN", "PLAYER_ENTERING_WORLD", "CHAT_MSG_ADDON", "BAG_UPDATE",
    "ITEM_LOCK_CHANGED", "BAG_UPDATE_COOLDOWN", "PLAYER_EQUIPMENT_CHANGED", "ADDON_LOADED"}) do
    events:RegisterEvent(event)
end
events:SetScript("OnEvent", function(_, event, ...)
    if event == "PLAYER_LOGIN" then
        token = tostring(math.floor(GetTime() * 1000) % 1000000000) .. tostring(math.random(100000, 999999))
        local p = WarscapeInventoryPosition
        local anchors = {CENTER=true,TOP=true,BOTTOM=true,LEFT=true,RIGHT=true,TOPLEFT=true,TOPRIGHT=true,BOTTOMLEFT=true,BOTTOMRIGHT=true}
        if type(p) == "table" and anchors[p.point] and anchors[p.relative] and type(p.x) == "number" and type(p.y) == "number" then
            panel:ClearAllPoints(); panel:SetPoint(p.point, UIParent, p.relative, p.x, p.y)
        end
        suppressNativeBags()
        request()
    elseif event == "CHAT_MSG_ADDON" then
        local p, message, distribution, sender = ...
        if p ~= prefix or distribution ~= "WHISPER" or sender ~= UnitName("player") or not token then return end
        local receivedToken, rev, receivedState, count, bag = message:match("^STATE|1|([^|]+)|(%d+)|([A-Z_]+)|(%d+)|(%d+)$")
        rev, count, bag = tonumber(rev), tonumber(count), tonumber(bag)
        if receivedToken ~= token or not rev or rev <= revision or rev > 4294967295 or bag ~= 1 then return end
        if not ((receivedState == "READY" and (count == 24 or count == 28))
            or (receivedState == "CONVERSION_REQUIRED" and count == 0)) then return end
        revision, state, usable = rev, receivedState, count
    elseif event == "PLAYER_ENTERING_WORLD" then request()
    elseif event == "ADDON_LOADED" then suppressNativeBags() end
    refresh()
end)
local elapsed = 0
events:SetScript("OnUpdate", function(_, dt)
    elapsed = elapsed + dt
    if elapsed < 3 then return end
    elapsed = 0
    if state == "PENDING" then request()
    elseif state == "READY" and observedExtensionSlots ~= GetContainerNumSlots(1) then refresh() end
end)
refresh()
