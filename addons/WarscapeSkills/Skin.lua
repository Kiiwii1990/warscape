-- Reference-derived artwork is split into independent stretchable pieces.
-- All skill text, values, native icons and status bars are real UI regions.
WarscapeSkillsSkin = {}
local S = WarscapeSkillsSkin
local art = "Interface\\AddOns\\WarscapeSkills\\art\\"
S.width, S.gridTop, S.rowPitch, S.cellWidth, S.cellHeight = 500, 102, 82, 206, 76
local gold = {1, 0.82, 0.25}

local function texture(parent, file, layer, width, height, point, x, y, mirror)
    local t = parent:CreateTexture(nil, layer or "BORDER")
    t:SetTexture(art .. file)
    t:SetSize(width, height)
    t:SetPoint(point or "TOPLEFT", parent, point or "TOPLEFT", x or 0, y or 0)
    if mirror then t:SetTexCoord(1, 0, 0, 1) end
    return t
end

function S.Font(parent, size, point, x, y)
    local f = parent:CreateFontString(nil, "OVERLAY")
    f:SetFont("Fonts\\FRIZQT__.TTF", size, "")
    f:SetTextColor(unpack(gold))
    f:SetShadowColor(0, 0, 0, 1)
    f:SetShadowOffset(1, -1)
    f:SetPoint(point, parent, point, x, y)
    return f
end

-- A true nine-slice frame: corners retain their bevels as the layout grows.
function S.NineSlice(parent, file, sw, sh, tw, th, inset, edge, layer)
    local xsrc, ysrc = {0, inset, sw-inset, sw}, {0, inset, sh-inset, sh}
    local parts = {}
    for row = 1, 3 do
        for col = 1, 3 do
            local t = parent:CreateTexture(nil, layer or "BORDER")
            t:SetTexture(art .. file)
            t:SetTexCoord(xsrc[col]/tw, xsrc[col+1]/tw, ysrc[row]/th, ysrc[row+1]/th)
            parts[#parts+1] = {region=t, row=row, col=col}
        end
    end
    return function(width, height)
        local xs, ys = {0, edge, width-edge}, {0, edge, height-edge}
        local ws, hs = {edge, width-2*edge, edge}, {edge, height-2*edge, edge}
        for _, p in ipairs(parts) do
            p.region:ClearAllPoints()
            p.region:SetPoint("TOPLEFT", parent, "TOPLEFT", xs[p.col], -ys[p.row])
            p.region:SetSize(ws[p.col], hs[p.row])
        end
    end
end

function S.Panel(panel, options)
    options = options or {}
    panel:SetSize(S.width, 514)
    -- Unlike the old native dialog backdrop, this stone texture has full alpha.
    panel:SetBackdrop({bgFile=art.."Stone", tile=true, tileSize=100,
        insets={left=17, right=17, top=28, bottom=20}})
    panel:SetBackdropColor(1, 1, 1, 1)
    texture(panel, "TopRail", "BORDER", 300, 14, "TOP", 0, -24)
    texture(panel, "HeaderRail", "BORDER", 366, 12, "TOP", 0, -78)
    local left = texture(panel, "Side", "BORDER", 35, 300, "TOPLEFT", 12, -117)
    local right = texture(panel, "Side", "BORDER", 35, 300, "TOPRIGHT", -12, -117, true)
    texture(panel, "Dragon", "OVERLAY", 141, 175, "TOPLEFT", -6, 0)
    texture(panel, "Dragon", "OVERLAY", 141, 175, "TOPRIGHT", 6, 0, true)
    texture(panel, "Foot", "OVERLAY", 112, 111, "BOTTOMLEFT", 5, -1)
    texture(panel, "Foot", "OVERLAY", 112, 111, "BOTTOMRIGHT", -5, -1, true)
    texture(panel, "BottomRail", "BORDER", 330, 32, "BOTTOM", 0, 0)
    S.Font(panel, 28, "TOP", 0, -38):SetText(options.title or "Skills")

    local close = CreateFrame("Button", options.closeName or "WarscapeSkillsCloseButton", panel)
    close:SetSize(30, 34)
    close:SetPoint("TOPRIGHT", -20, -33)
    close:SetNormalTexture(art.."Close")
    close:SetPushedTexture(art.."Close")
    close:GetPushedTexture():SetVertexColor(0.7, 0.7, 0.7)
    close:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    close:SetScript("OnClick", function() panel:Hide() end)

    local total = CreateFrame("Frame", options.totalName or "WarscapeSkillsTotal", panel)
    total:SetSize(420, 48)
    total:SetPoint("BOTTOM", 0, 38)
    S.NineSlice(total, "Total", 831, 102, 1024, 128, 20, 10)(420, 48)
    total.value = S.Font(total, 23, "CENTER", 0, 0)
    total.value:SetText("Total level: --")
    local status = panel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    status:SetPoint("BOTTOM", 0, 24)
    status:SetTextColor(0.72, 0.68, 0.56)
    status:SetText("Waiting for server data...")
    return total, status, function(rows)
        local h = S.gridTop + rows * S.rowPitch + 84
        panel:SetHeight(h)
        left:SetHeight(h-189)
        right:SetHeight(h-189)
    end
end

function S.Cell(panel, i)
    local c = CreateFrame("Frame", nil, panel)
    c:SetSize(S.cellWidth, S.cellHeight)
    c:SetPoint("TOPLEFT", panel, "TOPLEFT", 40 + ((i-1)%2)*214, -S.gridTop-math.floor((i-1)/2)*S.rowPitch)
    S.NineSlice(c, "Cell", 406, 155, 512, 256, 16, 8)(S.cellWidth, S.cellHeight)
    c:EnableMouse(true)
    local socket = CreateFrame("Frame", nil, c)
    socket:SetSize(58, 58)
    socket:SetPoint("TOPLEFT", 8, -9)
    c.icon = socket:CreateTexture(nil, "ARTWORK")
    c.icon:SetPoint("TOPLEFT", 4, -4)
    c.icon:SetSize(50, 50)
    c.icon:SetTexCoord(0.06, 0.94, 0.06, 0.94)
    texture(socket, "Icon", "OVERLAY", 58, 58)
    c.name = S.Font(c, 16, "TOPLEFT", 74, -10)
    c.level = S.Font(c, 21, "TOPLEFT", 74, -30)
    local track = CreateFrame("Frame", nil, c)
    track:SetSize(124, 13)
    track:SetPoint("BOTTOMRIGHT", -9, 10)
    texture(track, "Track", "BACKGROUND", 124, 13)
    c.bar = CreateFrame("StatusBar", nil, track)
    c.bar:SetPoint("TOPLEFT", 2, -2)
    c.bar:SetSize(120, 9)
    c.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    c.bar:SetStatusBarColor(0.12, 0.9, 0.025)
    c.bar:SetMinMaxValues(0, 1)
    return c
end
