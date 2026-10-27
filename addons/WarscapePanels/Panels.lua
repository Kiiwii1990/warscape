-- Only explicitly registered Warscape main-menu panels participate. Loot,
-- tooltips, confirmation dialogs and other native transient windows are untouched.
WarscapePanels = {entries = {}, order = {}, buttons = {}}
local P = WarscapePanels
local MIN, MAX, STEP = 0.5, 1.5, 1.05

local function sync()
    for id, attached in pairs(P.buttons) do
        local entry = P.entries[id]
        local open = entry and entry.frame:IsShown() or false
        for _, pair in ipairs(attached) do pair.style(pair.button, open) end
    end
end

local function closeOthers(id)
    for _, other in ipairs(P.order) do
        if other ~= id then
            local entry = P.entries[other]
            if entry.frame:IsShown() then entry.frame:Hide() end
        end
    end
end

function P:Register(id, frame, options)
    assert(type(id) == "string" and frame and not self.entries[id], "Panel must register once with a unique ID")
    local entry = {id = id, frame = frame, options = options or {}}
    self.entries[id] = entry
    self.order[#self.order + 1] = id
    frame:HookScript("OnShow", function()
        closeOthers(id)
        P.active = id
        sync()
        if entry.options.onShow then entry.options.onShow() end
    end)
    frame:HookScript("OnHide", function()
        if P.active == id then P.active = nil end
        sync()
        if entry.options.onHide then entry.options.onHide() end
    end)
    if frame:IsShown() then closeOthers(id); self.active = id end
    if self.loggedIn then self:RestoreScale(id) end
    sync()
end

function P:Open(id)
    local entry = self.entries[id]
    if not entry then return false end
    closeOthers(id) -- Close previous panel before the new panel becomes visible.
    if not entry.frame:IsShown() then entry.frame:Show() end
    self.active = id
    sync()
    return true
end

function P:Close(id)
    local entry = self.entries[id]
    if not entry then return false end
    entry.frame:Hide()
    sync()
    return true
end

function P:Toggle(id)
    local entry = self.entries[id]
    if not entry then return false end
    if entry.frame:IsShown() then return self:Close(id) end
    return self:Open(id)
end

function P:AttachButton(id, button, style)
    self.buttons[id] = self.buttons[id] or {}
    self.buttons[id][#self.buttons[id] + 1] = {button = button, style = style}
    button:SetScript("OnClick", function() P:Toggle(id) end)
    sync()
end

function P:SyncButtons() sync() end
function P:SetHudFrame(frame)
    self.hud = frame
    frame:HookScript("OnSizeChanged", function()
        if P.loggedIn then P:RestoreScales() end
    end)
end

function P:ScaleLimit(id)
    local frame = self.entries[id].frame
    local occupied = self.hud and self.hud:GetHeight() * self.hud:GetScale() or 0
    return math.max(MIN, math.min(MAX, (UIParent:GetHeight() - occupied - 18) / frame:GetHeight(),
        (UIParent:GetWidth() - 16) / frame:GetWidth()))
end

local function validScale(value)
    if type(value) ~= "number" or value ~= value then return 1 end
    return math.max(MIN, math.min(MAX, value))
end

function P:RestoreScale(id)
    WarscapePanelScales = WarscapePanelScales or {}
    local value = WarscapePanelScales[id]
    if value == nil and WarscapeHUDScales then value = WarscapeHUDScales[id] end
    value = validScale(value)
    WarscapePanelScales[id] = value
    self.entries[id].frame:SetScale(math.min(value, self:ScaleLimit(id)))
end

function P:RestoreScales()
    for _, id in ipairs(self.order) do self:RestoreScale(id) end
end

function P:GetScale(id)
    return self.entries[id] and self.entries[id].frame:GetScale() or 1
end

function P:AdjustScale(id, delta)
    local entry = self.entries[id]
    if not entry then return end
    local value = math.max(MIN, math.min(self:ScaleLimit(id), self:GetScale(id) * (delta > 0 and STEP or 1 / STEP)))
    entry.frame:SetScale(value)
    WarscapePanelScales = WarscapePanelScales or {}
    WarscapePanelScales[id] = value
end

function P:HoveredPanel()
    for _, id in ipairs(self.order) do
        local frame = self.entries[id].frame
        if frame:IsShown() and MouseIsOver(frame) then return id end
    end
end

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("DISPLAY_SIZE_CHANGED")
events:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_LOGIN" then P.loggedIn = true end
    if P.loggedIn then P:RestoreScales() end
    sync()
end)
