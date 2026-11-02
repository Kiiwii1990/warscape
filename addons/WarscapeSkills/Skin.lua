-- Reference-derived artwork is split into independent stretchable pieces.
-- All skill text, values, native icons and status bars are real UI regions.
WarscapeSkillsSkin = {}
local S = WarscapeSkillsSkin
local art = "Interface\\AddOns\\WarscapeSkills\\art\\"
-- One shared exterior configuration for all custom Warscape menu panels.
S.width, S.height = 700, 460
S.profiles = {landscape={width=S.width,height=S.height}, portrait={width=430,height=756}}
S.metrics = {hudGrid=44,hudGap=24,hudButton=34,inventorySlot=76,inventoryGap=6,utility=30}
S.columns = 3
S.gridLeft, S.gridTop = 48, 108
S.rowPitch, S.cellWidth, S.cellHeight = 112, 80, 104
S.columnGap, S.gridWidth, S.viewportHeight = 7, 254, S.profiles.portrait.height-S.gridTop-84
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
    panel:SetSize(S.width, S.height)
    panel:SetBackdrop({bgFile=options.background or art.."Stone", tile=true, tileSize=100,
        insets={left=17, right=17, top=28, bottom=20}})
    panel:SetBackdropColor(1, 1, 1, 1)
    local top = texture(panel, "TopRail", "BORDER", S.width-80, 14, "TOP", 0, -24)
    local divider = texture(panel, "HeaderRail", "BORDER", S.width-64, 12, "TOP", 0, -78)
    local left = texture(panel, "Side", "BORDER", 35, 300, "TOPLEFT", 12, -117)
    local right = texture(panel, "Side", "BORDER", 35, 300, "TOPRIGHT", -12, -117, true)
    -- Ornaments retain their original dimensions; only plain frame segments resize.
    if not options.noDragons then
    texture(panel, "Dragon", "OVERLAY", 141, 175, "TOPLEFT", -6, 0)
    texture(panel, "Dragon", "OVERLAY", 141, 175, "TOPRIGHT", 6, 0, true)
    end
    texture(panel, "Foot", "OVERLAY", 112, 111, "BOTTOMLEFT", 5, -1)
    texture(panel, "Foot", "OVERLAY", 112, 111, "BOTTOMRIGHT", -5, -1, true)
    local bottom = texture(panel, "BottomRail", "BORDER", S.width-40, 32, "BOTTOM", 0, 0)
    local title = S.Font(panel, 28, "TOP", 0, -38)
    title:SetText(options.title or "Skills")
    local close = CreateFrame("Button", options.closeName or "WarscapeSkillsCloseButton", panel)
    close:SetSize(S.metrics.utility, S.metrics.utility+4); close:SetPoint("TOPRIGHT", -20, -33)
    close:SetNormalTexture(art.."Close"); close:SetPushedTexture(art.."Close")
    close:GetPushedTexture():SetVertexColor(0.7, 0.7, 0.7)
    close:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
    close:SetScript("OnClick", function() panel:Hide() end)

    local chrome = {close=close}
    panel.warscapeChrome = chrome
    local function control(suffix, x)
        local b = CreateFrame("Button", panel:GetName()..suffix, panel)
        b:SetSize(S.metrics.utility, S.metrics.utility); b:SetPoint("TOPLEFT", panel, "TOPLEFT", x, -35)
        S.NineSlice(b, "Cell", 406, 155, 512, 256, 16, 5)(S.metrics.utility,S.metrics.utility)
        b:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")
        b:SetScript("OnLeave", function() GameTooltip:Hide() end)
        return b
    end
    chrome.lock = control("LockButton", 20)
    chrome.rotate = control("OrientationButton", 58)
    local function icon(parent, path, width, height, u1,u2,v1,v2)
        local t=parent:CreateTexture(nil,"ARTWORK"); t:SetTexture(path)
        t:SetSize(width,height);t:SetPoint("CENTER",parent,"CENTER",0,0)
        if u1 then t:SetTexCoord(u1,u2,v1,v2) end
        return t
    end
    local lockPath="Interface\\LFGFrame\\UI-LFG-ICON-LOCK"
    local closed=icon(chrome.lock,lockPath,24,24)
    -- Open shackle uses two UV regions of the SAME approved native lock icon.
    local body=icon(chrome.lock,lockPath,24,13,0,1,.46,1)
    body:ClearAllPoints();body:SetPoint("CENTER",chrome.lock,"CENTER",0,-5)
    local shackle=icon(chrome.lock,lockPath,24,11,0,1,0,.46)
    shackle:ClearAllPoints();shackle:SetPoint("CENTER",chrome.lock,"CENTER",5,8)
    function chrome.setLocked(locked)
        chrome.locked=locked
        if locked then closed:Show();body:Hide();shackle:Hide()
        else closed:Hide();body:Show();shackle:Show() end
    end
    icon(chrome.rotate,"Interface\\Buttons\\UI-RotationLeft-Button-Up",28,28)
    chrome.lock:SetScript("OnEnter",function(self)
        GameTooltip:SetOwner(self,"ANCHOR_RIGHT")
        GameTooltip:SetText(chrome.locked and "Locked to HUD" or "Unlocked",1,.82,.25)
        GameTooltip:AddLine(chrome.locked and "Click to unlock. Drag using the title bar." or "Click to lock and return to the HUD anchor.",1,1,1,true)
        GameTooltip:Show()
    end)
    chrome.rotate:SetScript("OnEnter",function(self)
        GameTooltip:SetOwner(self,"ANCHOR_RIGHT")
        GameTooltip:SetText("Change orientation",1,.82,.25)
        GameTooltip:AddLine(chrome.orientation=="portrait" and "Switch to landscape. Lock and scale are retained." or "Switch to portrait. Lock and scale are retained.",1,1,1,true)
        GameTooltip:Show()
    end)
    local total, resizeTotal
    if not options.noFooter then
        total = CreateFrame("Frame", options.totalName or "WarscapeSkillsTotal", panel)
        total:SetPoint("BOTTOM", 0, 38)
        resizeTotal=S.NineSlice(total,"Total",831,102,1024,128,20,8)
        total.value=S.Font(total,18,"CENTER",0,0)
        total.value:SetText(options.footerText or "Total level: --")
    end
    local status
    if not options.noStatus then
        status=panel:CreateFontString(nil,"OVERLAY","GameFontHighlightSmall")
        status:SetPoint("BOTTOM",0,18);status:SetTextColor(.72,.68,.56)
        status:SetText(options.statusText or "Waiting for server data...")
    end
    function chrome.resize(orientation, override)
        chrome.orientation=orientation
        local profile=override or S.profiles[orientation] or S.profiles.landscape
        local w,h=profile.width,profile.height
        panel:SetSize(w,h)
        top:SetWidth(w-80);divider:SetWidth(w-64);bottom:SetWidth(w-40)
        left:SetHeight(h-189);right:SetHeight(h-189)
        title:SetWidth(w-190);title:SetFont("Fonts\\FRIZQT__.TTF",orientation=="portrait" and 20 or 28,"")
        if total then
            local compact=orientation=="landscape"
            local height=compact and 26 or 38
            total:ClearAllPoints();total:SetPoint("BOTTOM",panel,"BOTTOM",0,compact and 22 or 38)
            total:SetSize(w-48,height);resizeTotal(w-48,height)
            total.value:SetFont("Fonts\\FRIZQT__.TTF",compact and 16 or 18,"")
        end
        if status then
            status:SetWidth(w-80);status:ClearAllPoints()
            status:SetPoint("BOTTOM",panel,"BOTTOM",0,orientation=="landscape" and 5 or 18)
        end
    end
    chrome.resize("landscape");chrome.setLocked(true)
    return total,status,chrome.resize
end

function S.Cell(panel, i)
    local c = CreateFrame("Frame", nil, panel)
    c:SetSize(S.cellWidth, S.cellHeight)
    local offset = i - 1
    local column, row = offset % S.columns, math.floor(offset / S.columns)
    c:SetPoint("TOPLEFT", panel, "TOPLEFT", column * (S.cellWidth + S.columnGap), -row * S.rowPitch)
    S.NineSlice(c, "Cell", 406, 155, 512, 256, 16, 8)(S.cellWidth, S.cellHeight)
    c:EnableMouse(true)
    local socket = CreateFrame("Frame", nil, c)
    socket:SetSize(68, 68)
    socket:SetPoint("TOP", c, "TOP", 0, -1)
    c.icon = socket:CreateTexture(nil, "ARTWORK")
    c.icon:SetPoint("CENTER", socket, "CENTER", 0, 0)
    c.icon:SetSize(64, 64)
    c.icon:SetTexCoord(0.06, 0.94, 0.06, 0.94)
    texture(socket, "Icon", "OVERLAY", 68, 68)
    c.level = S.Font(c, 18, "TOP", 0, -72)
    c.level:SetWidth(S.cellWidth - 8)
    c.level:SetJustifyH("CENTER")
    local track = CreateFrame("Frame", nil, c)
    track:SetSize(S.cellWidth - 12, 8)
    track:SetPoint("BOTTOMLEFT", c, "BOTTOMLEFT", 6, 4)
    texture(track, "Track", "BACKGROUND", S.cellWidth - 12, 8)
    c.bar = CreateFrame("StatusBar", nil, track)
    c.bar:SetPoint("TOPLEFT", 2, -2)
    c.bar:SetSize(S.cellWidth - 16, 4)
    c.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
    c.bar:SetStatusBarColor(0.12, 0.9, 0.025)
    c.bar:SetMinMaxValues(0, 1)
    return c
end
