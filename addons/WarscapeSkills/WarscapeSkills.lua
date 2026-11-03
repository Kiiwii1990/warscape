local prefix = "WCSkills"
local metadata = {
    attack = {"Attack", "INV_Sword_04"}, strength = {"Strength", "Ability_Warrior_InnerRage"},
    defence = {"Defence", "Ability_Warrior_DefensiveStance"}, hitpoints = {"Hitpoints", "Spell_Holy_LayOnHands"},
    ranged = {"Ranged", "Ability_Hunter_RunningShot"}, magic = {"Magic", "Spell_Holy_MagicalSentry"},
    prayer = {"Prayer", "Spell_Holy_PrayerOfHealing02"}, mining = {"Mining", "INV_Pick_02"},
    smithing = {"Smithing", "Trade_BlackSmithing"}
}
local panel = CreateFrame("Frame", "WarscapeSkillsFrame", UIParent)
local skin = WarscapeSkillsSkin
local total, status = skin.Panel(panel)
panel:SetFrameStrata("DIALOG")
panel:EnableMouse(true)
table.insert(UISpecialFrames, "WarscapeSkillsFrame")
local cells, protocol, snapshot, lastRequest = {}, nil, nil, -10
local columns, viewportHeight = 3, skin.viewportHeight
local gridWidth, gridLeft = skin.gridWidth, skin.gridLeft
local list = CreateFrame("ScrollFrame", "WarscapeSkillsList", panel)
list:SetPoint("TOPLEFT", panel, "TOPLEFT", gridLeft, -skin.gridTop)
list:SetSize(gridWidth, viewportHeight)
list:EnableMouseWheel(true)
local content = CreateFrame("Frame", nil, list)
content:SetSize(gridWidth, 1)
list:SetScrollChild(content)
local scrollbar = CreateFrame("Slider", "WarscapeSkillsScrollBar", panel, "UIPanelScrollBarTemplate")
scrollbar:SetPoint("TOPRIGHT", panel, "TOPRIGHT", -25, -skin.gridTop)
scrollbar:SetPoint("BOTTOMRIGHT", panel, "BOTTOMRIGHT", -25, skin.height - skin.gridTop - viewportHeight)
scrollbar:SetMinMaxValues(0, 0)
scrollbar:SetValueStep(skin.rowPitch)
scrollbar:SetScript("OnValueChanged", function(_, value) list:SetVerticalScroll(value) end)
list:SetScript("OnMouseWheel", function(_, delta)
    if IsControlKeyDown() then
        -- ScrollFrame receives wheel input before the HUD's full-screen scaler.
        -- Route Ctrl-wheel through the same saved panel scale manager directly.
        WarscapePanels:AdjustScale("skills", delta)
    else
        local _, maxScroll = scrollbar:GetMinMaxValues()
        scrollbar:SetValue(math.max(0, math.min(scrollbar:GetValue() - delta * skin.rowPitch, maxScroll)))
    end
end)
local function number(n) return string.format(n == math.floor(n) and "%.0f" or "%.1f", n) end
local function details(cell)
    local d = cell.data
    if not d then return end
    GameTooltip:SetOwner(cell, "ANCHOR_RIGHT")
    GameTooltip:SetText(cell.label, 1, 0.82, 0)
    local currentLevel = d.effective or d.base
    GameTooltip:AddDoubleLine("Current level", number(currentLevel), 1, 1, 1, 1, 1, 1)
    GameTooltip:AddDoubleLine("Attained level", number(d.base), 1, 1, 1, 1, 1, 1)
    GameTooltip:AddDoubleLine("Total XP", number(d.xp), 1, 1, 1, 1, 1, 1)
    if d.nextXP then
        GameTooltip:AddDoubleLine("XP to next level", number(d.nextXP) .. " XP", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("XP remaining", number(d.nextXP - d.xp), 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("Progress", string.format("%.1f%%", 100 * (d.xp - d.floor) / (d.nextXP - d.floor)), 1, 1, 1, 0.3, 1, 0.3)
    else
        GameTooltip:AddDoubleLine("XP to next level", "Maximum level", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddDoubleLine("XP remaining", "0", 1, 1, 1, 1, 1, 1)
        GameTooltip:AddLine("Maximum level reached (100%)", 0.3, 1, 0.3)
    end
    if d.id == "smithing" then GameTooltip:AddLine("Use a forge for smelting", .3, 1, .3) end
    GameTooltip:Show()
end
local function cellAt(i)
    if cells[i] then return cells[i] end
    local c = skin.Cell(content, i)
    c:SetScript("OnEnter", details)
    c:SetScript("OnLeave", function() GameTooltip:Hide() end)
    cells[i] = c
    return c
end
local function xpProgress(d)
    if not d.nextXP then return 1 end
    local span = d.nextXP - d.floor
    if span <= 0 then return 0 end
    return math.max(0, math.min(1, (d.xp - d.floor) / span))
end
local function render(data)
    -- Match the reference's combat columns; append future stable IDs dynamically.
    local order, included = {}, {}
    for _, id in ipairs({"attack", "hitpoints", "strength", "ranged", "defence", "magic", "prayer", "mining", "smithing"}) do
        if data.rows[id] then order[#order+1] = id; included[id] = true end
    end
    for _, id in ipairs(data.order) do
        if not included[id] then order[#order+1] = id end
    end
    local hasPlaceholder = #order > 0 and #order % columns ~= 0
    local tileCount = #order + (hasPlaceholder and 1 or 0)
    local rows = math.ceil(tileCount / columns)
    local contentHeight = math.max(viewportHeight, (rows - 1) * skin.rowPitch + skin.cellHeight)
    content:SetSize(gridWidth, contentHeight)
    local maxScroll = math.max(0, contentHeight - list:GetHeight())
    scrollbar:SetMinMaxValues(0, maxScroll)
    scrollbar:SetValue(math.min(scrollbar:GetValue(), maxScroll))
    if maxScroll > 0 then scrollbar:Show() else scrollbar:Hide() end
    list:SetVerticalScroll(math.min(list:GetVerticalScroll(), maxScroll))
    local totalLevel = 0
    for i, id in ipairs(order) do
        local c, m, d = cellAt(i), metadata[id], data.rows[id]
        c.data, c.label = d, m and m[1] or id
        c.placeholder = false
        c.icon:SetTexture("Interface\\Icons\\" .. (m and m[2] or "INV_Misc_QuestionMark"))
        c.level:SetText(number(d.effective or d.base) .. "/" .. number(d.base))
        totalLevel = totalLevel + d.base
        c.bar:SetValue(xpProgress(d))
        c:ClearAllPoints();c:SetPoint("TOPLEFT",content,"TOPLEFT",((i-1)%columns)*(skin.cellWidth+skin.columnGap),-math.floor((i-1)/columns)*skin.rowPitch)
        c:Show()
        if MouseIsOver(c) then details(c) end
    end
    if hasPlaceholder then
        local c = cellAt(#order + 1)
        c.data, c.label, c.placeholder = nil, "Next skill", true
        c.icon:SetTexture("Interface\\Icons\\INV_Misc_QuestionMark")
        c.level:SetText("-")
        c.bar:SetValue(0)
        local i=#order+1
        c:ClearAllPoints();c:SetPoint("TOPLEFT",content,"TOPLEFT",((i-1)%columns)*(skin.cellWidth+skin.columnGap),-math.floor((i-1)/columns)*skin.rowPitch)
        c:Show()
    end
    for i = tileCount + 1, #cells do cells[i]:Hide() end
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
local function layout(orientation)
    panel.warscapeChrome.resize(orientation)
    columns=orientation=="portrait" and 3 or 6
    gridWidth=columns*skin.cellWidth+(columns-1)*skin.columnGap
    gridLeft=(panel:GetWidth()-gridWidth)/2
    viewportHeight=panel:GetHeight()-skin.gridTop-84
    list:ClearAllPoints();list:SetPoint("TOPLEFT",panel,"TOPLEFT",gridLeft,-skin.gridTop)
    list:SetSize(gridWidth,viewportHeight)
    scrollbar:ClearAllPoints();scrollbar:SetPoint("TOPRIGHT",panel,"TOPRIGHT",-25,-skin.gridTop)
    scrollbar:SetPoint("BOTTOMRIGHT",panel,"BOTTOMRIGHT",-25,84)
    if snapshot then render(snapshot) else content:SetSize(gridWidth,viewportHeight) end
end
WarscapePanels:Register("skills", panel, {group = "right", onShow = request, layout=layout})
local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("PLAYER_ENTERING_WORLD")
events:RegisterEvent("CHAT_MSG_ADDON")
events:SetScript("OnEvent", function(self, event, ...)
    if event == "PLAYER_LOGIN" then
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
