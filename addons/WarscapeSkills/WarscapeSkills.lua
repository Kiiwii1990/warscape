local prefix = "WCSkills"
local metadata = {
    attack = {"Attack", "INV_Sword_04"}, strength = {"Strength", "Ability_Warrior_InnerRage"},
    defence = {"Defence", "Ability_Warrior_DefensiveStance"}, hitpoints = {"Hitpoints", "Spell_Holy_LayOnHands"},
    ranged = {"Ranged", "Ability_Hunter_RunningShot"}, magic = {"Magic", "Spell_Holy_MagicalSentry"},
    prayer = {"Prayer", "Spell_Holy_PrayerOfHealing02"}
}
local panel = CreateFrame("Frame", "WarscapeSkillsFrame", UIParent)
panel:SetSize(390, 390)
panel:SetPoint("CENTER")
panel:SetFrameStrata("DIALOG")
panel:SetClampedToScreen(true)
panel:SetMovable(true)
panel:EnableMouse(true)
panel:RegisterForDrag("LeftButton")
panel:SetBackdrop({bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
    edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border", tile = true, tileSize = 32,
    edgeSize = 32, insets = {left = 10, right = 10, top = 10, bottom = 10}})
panel:SetScript("OnDragStart", function(self) self:StartMoving() end)
panel:SetScript("OnDragStop", function(self)
    self:StopMovingOrSizing()
    local point, _, relative, x, y = self:GetPoint()
    WarscapeSkillsPosition = {point = point, relative = relative, x = x, y = y}
end)
table.insert(UISpecialFrames, "WarscapeSkillsFrame")
local close = CreateFrame("Button", nil, panel, "UIPanelCloseButton")
close:SetPoint("TOPRIGHT", -5, -5)
local title = panel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
title:SetPoint("TOP", 0, -27)
title:SetText("WARSCAPE")
local subtitle = panel:CreateFontString(nil, "OVERLAY", "GameFontNormal")
subtitle:SetPoint("TOP", 0, -51)
subtitle:SetText("Skills")
-- Crop the native elite-target dragon ornament, then mirror it at the other side.
-- These are native decorative pieces, not a flat illustration of the panel.
for side = 1, 2 do
    local dragon = panel:CreateTexture(nil, "OVERLAY")
    dragon:SetTexture("Interface\\TargetingFrame\\UI-TargetingFrame-Elite")
    dragon:SetSize(100, 100)
    dragon:SetPoint(side == 1 and "TOPLEFT" or "TOPRIGHT", panel, side == 1 and "TOPLEFT" or "TOPRIGHT", side == 1 and -25 or 25, 35)
    if side == 1 then dragon:SetTexCoord(1, 0.53, 0, 0.84) else dragon:SetTexCoord(0.53, 1, 0, 0.84) end
end
local status = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
status:SetPoint("BOTTOM", 0, 22)
status:SetText("Waiting for Warscape server data...")
local cells, protocol, snapshot, lastRequest = {}, nil, nil, -10
local function number(n) return string.format("%.0f", n) end
local function details(cell)
    local d = cell.data
    if not d then return end
    GameTooltip:SetOwner(cell, "ANCHOR_RIGHT")
    GameTooltip:SetText(cell.label, 1, 0.82, 0)
    GameTooltip:AddDoubleLine("Base level", number(d.base), 1, 1, 1, 1, 1, 1)
    if d.effective then GameTooltip:AddDoubleLine("Current level", number(d.effective), 1, 1, 1, 1, 1, 1) end
    GameTooltip:AddDoubleLine("Total XP", number(d.xp), 1, 1, 1, 1, 1, 1)
    if d.nextXP then
        GameTooltip:AddDoubleLine("Next level at", number(d.nextXP) .. " XP", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("XP remaining", number(d.nextXP - d.xp), 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("Progress", string.format("%.1f%%", 100 * (d.xp - d.floor) / (d.nextXP - d.floor)), 1, 1, 1, 0.3, 1, 0.3)
    else
        GameTooltip:AddDoubleLine("Next level at", "Maximum level", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("XP remaining", "0", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddLine("Maximum level reached (100%)", 0.3, 1, 0.3)
    end
    GameTooltip:Show()
end
local function cellAt(i)
    if cells[i] then return cells[i] end
    local c = CreateFrame("Frame", nil, panel)
    c:SetSize(168, 59)
    c:SetPoint("TOPLEFT", 25 + ((i - 1) % 2) * 172, -85 - math.floor((i - 1) / 2) * 64)
    c:SetBackdrop({bgFile = "Interface\\Tooltips\\UI-Tooltip-Background", edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border", tile = true, tileSize = 16, edgeSize = 12, insets = {left = 3, right = 3, top = 3, bottom = 3}})
    c:SetBackdropColor(0.12, 0.12, 0.12, 0.95)
    c:SetBackdropBorderColor(0.65, 0.53, 0.3)
    c:EnableMouse(true)
    c.icon = c:CreateTexture(nil, "ARTWORK")
    c.icon:SetSize(32, 32)
    c.icon:SetPoint("TOPLEFT", 8, -8)
    c.name = c:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    c.name:SetPoint("TOPLEFT", 47, -9)
    c.level = c:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    c.level:SetPoint("TOPLEFT", 47, -24)
    c.bar = CreateFrame("StatusBar", nil, c)
    c.bar:SetPoint("BOTTOMLEFT", 8, 7)
    c.bar:SetSize(152, 7)
    c.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    c.bar:SetStatusBarColor(0.12, 0.8, 0.2)
    c.bar:SetMinMaxValues(0, 1)
    local bg = c.bar:CreateTexture(nil, "BACKGROUND")
    bg:SetAllPoints()
    bg:SetTexture(0.03, 0.08, 0.03, 1)
    c:SetScript("OnEnter", details)
    c:SetScript("OnLeave", function() GameTooltip:Hide() end)
    cells[i] = c
    return c
end
local function render(data)
    panel:SetHeight(125 + math.ceil(#data.order / 2) * 64)
    for i, id in ipairs(data.order) do
        local c, m, d = cellAt(i), metadata[id], data.rows[id]
        c.data, c.label = d, m and m[1] or id
        c.name:SetText(c.label)
        c.icon:SetTexture("Interface\\Icons\\" .. (m and m[2] or "INV_Misc_QuestionMark"))
        c.level:SetText(d.effective and d.effective ~= d.base and (d.effective .. "/" .. d.base) or d.base)
        c.bar:SetValue(d.nextXP and (d.xp - d.floor) / (d.nextXP - d.floor) or 1)
        c:Show()
        if MouseIsOver(c) then details(c) end
    end
    for i = #data.order + 1, #cells do cells[i]:Hide() end
    status:SetText("Live skills  |  Drag frame to move  |  /wskills")
end
local function request()
    if not protocol or GetTime() - lastRequest < 1 then return end
    lastRequest = GetTime()
    SendAddonMessage(prefix, "HELLO|1|" .. protocol.token, "WHISPER", UnitName("player"))
end
SLASH_WARSCAPESKILLS1 = "/wskills"
SlashCmdList.WARSCAPESKILLS = function()
    if panel:IsShown() then panel:Hide() else panel:Show(); request() end
end
panel:Hide()
local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("CHAT_MSG_ADDON")
events:SetScript("OnEvent", function(self, event, ...)
    if event == "PLAYER_LOGIN" then
        local pos = WarscapeSkillsPosition
        if type(pos) == "table" and type(pos.point) == "string" and type(pos.relative) == "string" and type(pos.x) == "number" and type(pos.y) == "number" then
            local valid = {CENTER=true,TOP=true,BOTTOM=true,LEFT=true,RIGHT=true,TOPLEFT=true,TOPRIGHT=true,BOTTOMLEFT=true,BOTTOMRIGHT=true}
            if valid[pos.point] and valid[pos.relative] then panel:ClearAllPoints(); panel:SetPoint(pos.point, UIParent, pos.relative, pos.x, pos.y) end
        end
        protocol = WarscapeSkillsProtocol.New(tostring(math.floor(GetTime() * 1000) % 1000000000) .. tostring(math.random(100000, 999999)))
        request()
    elseif event == "PLAYER_ENTERING_WORLD" then
        request()
    else
        local p, message, distribution, sender = ...
        if p ~= prefix or distribution ~= "WHISPER" or sender ~= UnitName("player") or not protocol then return end
        local received = WarscapeSkillsProtocol.Receive(protocol, message, GetTime())
        if received then snapshot = received; render(received) end
    end
end)
local elapsed = 0
events:SetScript("OnUpdate", function(self, dt)
    elapsed = elapsed + dt
    if elapsed < 2 then return end
    elapsed = 0
    if protocol and not snapshot then
        status:SetText("Waiting for server... check addon channel / server version")
        request()
    elseif protocol and protocol.pending and GetTime() - protocol.pending.started > 5 then
        protocol.pending = nil
        request()
    end
end)
