local prefix = "WCSkills"
local metadata = {
    attack = {"Attack", "INV_Sword_04"}, strength = {"Strength", "Ability_Warrior_InnerRage"},
    defence = {"Defence", "Ability_Warrior_DefensiveStance"}, hitpoints = {"Hitpoints", "Spell_Holy_LayOnHands"},
    ranged = {"Ranged", "Ability_Hunter_RunningShot"}, magic = {"Magic", "Spell_Holy_MagicalSentry"},
    prayer = {"Prayer", "Spell_Holy_PrayerOfHealing02"}
}
local panel = CreateFrame("Frame", "WarscapeSkillsFrame", UIParent)
local skin = WarscapeSkillsSkin
local total, status, resize = skin.Panel(panel)
if WarscapeHUDFrame then
    panel:SetPoint("BOTTOM", WarscapeHUDFrame, "TOP", 0, 8)
else
    panel:SetPoint("CENTER")
end
panel:SetFrameStrata("DIALOG")
panel:SetClampedToScreen(true)
panel:SetMovable(true)
panel:EnableMouse(true)
panel:RegisterForDrag("LeftButton")
panel:SetScript("OnDragStart", function(self) self:StartMoving() end)
panel:SetScript("OnDragStop", function(self)
    self:StopMovingOrSizing()
    local point, _, relative, x, y = self:GetPoint()
    WarscapeSkillsPosition = {point = point, relative = relative, x = x, y = y}
end)
table.insert(UISpecialFrames, "WarscapeSkillsFrame")
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
    local c = skin.Cell(panel, i)
    c:SetScript("OnEnter", details)
    c:SetScript("OnLeave", function() GameTooltip:Hide() end)
    cells[i] = c
    return c
end
local function render(data)
    -- Match the reference's combat columns; append future stable IDs dynamically.
    local order, included = {}, {}
    for _, id in ipairs({"attack", "hitpoints", "strength", "ranged", "defence", "magic", "prayer"}) do
        if data.rows[id] then order[#order+1] = id; included[id] = true end
    end
    for _, id in ipairs(data.order) do
        if not included[id] then order[#order+1] = id end
    end
    resize(math.ceil(#order / 2))
    local totalLevel = 0
    for i, id in ipairs(order) do
        local c, m, d = cellAt(i), metadata[id], data.rows[id]
        c.data, c.label = d, m and m[1] or id
        c.name:SetText(c.label)
        c.icon:SetTexture("Interface\\Icons\\" .. (m and m[2] or "INV_Misc_QuestionMark"))
        c.level:SetText(number(d.effective or d.base) .. " |cffddd6c6/ " .. number(d.base) .. "|r")
        totalLevel = totalLevel + d.base
        c.bar:SetValue(d.nextXP and (d.xp - d.floor) / (d.nextXP - d.floor) or 1)
        c:Show()
        if MouseIsOver(c) then details(c) end
    end
    for i = #order + 1, #cells do cells[i]:Hide() end
    total.value:SetText("Total level: " .. number(totalLevel))
    status:SetText("")
end
local function request()
    if not protocol or GetTime() - lastRequest < 1 then return end
    lastRequest = GetTime()
    SendAddonMessage(prefix, "HELLO|1|" .. protocol.token, "WHISPER", UnitName("player"))
end
SLASH_WARSCAPESKILLS1 = "/wskills"
function WarscapeSkills_Toggle()
    WarscapePanels:Toggle("skills")
end
SlashCmdList.WARSCAPESKILLS = WarscapeSkills_Toggle
panel:Hide()
WarscapePanels:Register("skills", panel, {onShow = request})
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
