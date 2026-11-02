-- Main Warscape panels use two independent groups. Native transient windows
-- (loot, tooltips and confirmations) are deliberately never registered here.
WarscapePanels = {entries = {}, order = {}, buttons = {}, activeGroups = {},
    windows = {left={group="left"}, right={group="right"}}}
local P = WarscapePanels
local MIN, MAX, STEP = 0.5, 1.5, 1.05

local function sync()
    for id, attached in pairs(P.buttons) do
        local entry = P.entries[id]
        local open = entry and entry.frame:IsShown() or false
        for _, pair in ipairs(attached) do pair.style(pair.button, open) end
    end
end

local function groupFor(id)
    local entry = P.entries[id]
    return entry and entry.group
end

local function hideEntry(entry)
    if not entry.frame:IsShown() then return end
    if entry.options.hide then entry.options.hide(entry.frame)
    else entry.frame:Hide() end
end

local function closeGroupPeers(id)
    local group = groupFor(id)
    if not group then return end
    for _, otherId in ipairs(P.order) do
        local other = P.entries[otherId]
        if otherId ~= id and other.group == group and other.frame:IsShown() then
            hideEntry(other)
        end
    end
end

local function legacyScale()
    local old = type(WarscapePanelScales)=="table" and WarscapePanelScales or {}
    local value = old.universal
    -- Upgrade older per-panel preferences once. Skills was the established
    -- scale control before the universal setting was introduced.
    if value == nil then value = old.skills end
    if value == nil then value = old.inventory end
    if value == nil and type(WarscapeHUDScales)=="table" then value = WarscapeHUDScales.skills end
    if type(value) ~= "number" or value ~= value then value = 1 end
    return math.max(MIN, math.min(MAX, value))
end

local function validGroup(group)
    assert(group == "left" or group == "right", "Warscape panels must register in the left or right group")
    return group
end

function P:Register(id, frame, options)
    options = options or {}
    assert(type(id) == "string" and frame and not self.entries[id], "Panel must register once with a unique ID")
    local entry = {id = id, frame = frame, group = validGroup(options.group or "left"), options = options}
    entry.window = self.windows[entry.group]
    self.entries[id] = entry
    self.order[#self.order + 1] = id
    frame:HookScript("OnShow", function()
        P:PrepareShow(entry)
        closeGroupPeers(id)
        P.activeGroups[entry.group] = id
        P.active = id -- Most recently opened content; layout belongs to its side.
        P:State(id).lastMenu = id
        sync()
        if entry.options.onShow then entry.options.onShow() end
    end)
    frame:HookScript("OnHide", function()
        if P.activeGroups[entry.group] == id then P.activeGroups[entry.group] = nil end
        if P.active == id then P.active = nil end
        sync()
        if entry.options.onHide then entry.options.onHide() end
    end)
    if frame:IsShown() then
        self:PrepareShow(entry)
        closeGroupPeers(id)
        self.activeGroups[entry.group] = id
        self.active = id
    end
    self:Configure(entry)
    if self.loggedIn then self:RestoreScales() end
    sync()
end

function P:Open(id)
    local entry = self.entries[id]
    if not entry then return false end
    self:PrepareShow(entry) -- Complete layout before Show, including native toggles.
    closeGroupPeers(id) -- Other groups are not affected.
    if not entry.frame:IsShown() then
        if entry.options.show then entry.options.show(entry.frame)
        else entry.frame:Show() end
    else
        self.activeGroups[entry.group] = id
        self.active = id
        sync()
    end
    return true
end

function P:Close(id)
    local entry = self.entries[id]
    if not entry then return false end
    self:Capture(entry)
    hideEntry(entry)
    sync()
    return true
end

function P:Toggle(id)
    local entry = self.entries[id]
    if not entry then return false end
    if entry.frame:IsShown() then return self:Close(id) end
    return self:Open(id)
end

function P:AttachButton(id, button, style, click)
    assert(self.entries[id], "Register a panel before attaching its HUD button")
    self.buttons[id] = self.buttons[id] or {}
    self.buttons[id][#self.buttons[id] + 1] = {button = button, style = style}
    button:SetScript("OnClick", function()
        if click then click() else P:Toggle(id) end
    end)
    sync()
end

function P:SyncButtons() sync() end

-- Exactly two layout owners. Menu frames remain reusable content views.
-- Old per-menu tables are read once for migration and never rewritten here.
local function finite(n) return type(n)=="number" and n==n and math.abs(n)<100000 end
local function validPosition(p) return type(p)=="table" and finite(p.x) and finite(p.y) end
local legacyOrder={left={"inventory","friends","quests","settings"},
    right={"skills","attackStyles","equipment","prayer","spellbook"}}

function P:Group(id)
    if id=="left" or id=="right" then return id end
    local entry=self.entries[id or self.active or "inventory"]
    return entry and entry.group or "left"
end

local function migrate(group)
    local old=type(WarscapePanelLayouts)=="table" and WarscapePanelLayouts or {}
    local selected,source
    -- A detached position is more intentional than the default records written
    -- for every menu. Ties use Inventory/Skills first; all originals survive.
    for pass=1,3 do
        for _,id in ipairs(legacyOrder[group]) do
            local candidate=old[id]
            if type(candidate)=="table" and
                ((pass==1 and candidate.locked==false and validPosition(candidate.position)) or
                 (pass==2 and candidate.locked==false) or
                 (pass==3 and candidate.orientation=="portrait")) then
                selected,source=candidate,id;break
            end
        end
        if selected then break end
    end
    selected=selected or old[legacyOrder[group][1]] or {}
    if type(selected)~="table" then selected={} end
    local result={locked=selected.locked~=false,
        orientation=selected.orientation=="portrait" and "portrait" or "landscape",
        migratedFrom=source or legacyOrder[group][1]}
    if not result.locked and validPosition(selected.position) then
        result.position={x=selected.position.x,y=selected.position.y}
    end
    return result
end

function P:WindowState(group)
    group=self:Group(group)
    if type(WarscapeWindowLayouts)~="table" then WarscapeWindowLayouts={version=1} end
    local state=WarscapeWindowLayouts[group]
    if type(state)~="table" then state=migrate(group);WarscapeWindowLayouts[group]=state end
    state.locked=state.locked~=false
    state.orientation=state.orientation=="portrait" and "portrait" or "landscape"
    if not validPosition(state.position) then state.position=nil end
    if finite(state.scale) then state.scale=math.max(MIN,math.min(MAX,state.scale))
    elseif self.loggedIn then state.scale=legacyScale() end
    -- Delay fallback scale persistence until all addons' SavedVariables loaded.
    self.windows[group].state=state
    return state
end

function P:State(id) return self:WindowState(self:Group(id)) end

local function scaleOf(frame)
    return frame:GetEffectiveScale() / UIParent:GetEffectiveScale()
end
local function location(frame)
    local x = frame:GetCenter()
    local y = frame:GetBottom()
    if not x or not y then return end
    local scale = scaleOf(frame)
    return {x = x * scale / UIParent:GetWidth(), y = y * scale / UIParent:GetHeight()}
end

local function canChange(entry)
    return not (entry.options.combatSensitive and InCombatLockdown())
end

function P:Capture(entry, force)
    if not entry or not canChange(entry) then return end
    local state=self:State(entry.id)
    if state.locked or (not force and not entry.frame:IsShown()) then return end
    if entry.dragging then entry.frame:StopMovingOrSizing();entry.dragging=nil;force=true end
    local current=location(entry.frame)
    local resolved=self.windows[entry.group].position
    -- Don't replace an off-screen preferred anchor with its viewport-clamped
    -- rendering merely because the user switched contents or closed a window.
    if current and (force or not resolved or math.abs(current.x-resolved.x)>1e-7 or math.abs(current.y-resolved.y)>1e-7) then
        state.position=current
    end
end

function P:Envelope(group)
    local width,height=1,1
    for _,entry in pairs(self.entries) do
        if entry.group==group and entry.options.scalable~=false then
            width=math.max(width,entry.frame:GetWidth())
            height=math.max(height,entry.frame:GetHeight())
        end
    end
    return width,height
end

function P:ResolvePosition(group)
    local window,state=self.windows[group],self:WindowState(group)
    local position=state.position or {x=.5,y=.3}
    local width,height=self:Envelope(group)
    local scale=window.scale or self:DockFit()
    width,height=width*scale,height*scale
    local sw,sh=UIParent:GetWidth(),UIParent:GetHeight()
    local x=math.max(width/2+8,math.min(sw-width/2-8,position.x*sw))
    local y=math.max(8,math.min(sh-height-8,position.y*sh))
    window.position={x=x/sw,y=y/sh}
end

function P:PlaceDetached(entry, position)
    if position then self:State(entry.id).position={x=position.x,y=position.y};self:ResolvePosition(entry.group) end
    local resolved=self.windows[entry.group].position
    if not resolved then self:ResolvePosition(entry.group);resolved=self.windows[entry.group].position end
    local scale=scaleOf(entry.frame)
    entry.frame:ClearAllPoints()
    entry.frame:SetPoint("BOTTOM",UIParent,"BOTTOMLEFT",resolved.x*UIParent:GetWidth()/scale,resolved.y*UIParent:GetHeight()/scale)
end

function P:Position(entry)
    if not canChange(entry) then return end
    local frame,state=entry.frame,self:State(entry.id)
    if state.locked then
        local anchor=self.windows[entry.group].anchor
        local point=entry.group=="left" and "BOTTOMRIGHT" or "BOTTOMLEFT"
        frame:ClearAllPoints()
        if anchor then frame:SetPoint(point,anchor,point,0,0)
        else frame:SetPoint("BOTTOM",UIParent,"BOTTOM",0,80/scaleOf(frame)) end
    else self:PlaceDetached(entry) end
end

function P:PrepareShow(entry)
    local previous=self.entries[self.activeGroups[entry.group]]
    if previous and previous~=entry then self:Capture(previous) end
    self:RefreshWindow(entry.group)
end

function P:Configure(entry)
    local frame, state = entry.frame, self:State(entry.id)
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    -- Only an explicit header hit area initiates moving. Contents never do.
    local header = CreateFrame("Frame", nil, frame)
    entry.header = header
    header:SetPoint("TOPLEFT", frame, "TOPLEFT", 92, -12)
    header:SetPoint("BOTTOMRIGHT", frame, "TOPRIGHT", -128, -68)
    header:EnableMouse(true)
    header:RegisterForDrag("LeftButton")
    header:SetScript("OnDragStart", function()
        if not P:State(entry.id).locked and canChange(entry) then frame:StartMoving(); entry.dragging = true end
    end)
    header:SetScript("OnDragStop", function()
        if not entry.dragging then return end
        frame:StopMovingOrSizing(); entry.dragging = nil
        P:Capture(entry,true)
        P:RefreshWindow(entry.group)
    end)
    frame:HookScript("OnHide", function()
        if entry.dragging then header:GetScript("OnDragStop")(header) end
    end)
    if frame.warscapeChrome then
        local chrome = frame.warscapeChrome
        chrome.lock:SetScript("OnClick", function() P:SetLocked(entry.id, not P:State(entry.id).locked) end)
        chrome.rotate:SetScript("OnClick", function() P:ToggleOrientation(entry.id) end)
    end
    self:Layout(entry)
end

function P:Layout(entry)
    if entry.options.combatSensitive and InCombatLockdown() then entry.pendingLayout=true;return end
    entry.pendingLayout=nil
    local state = self:State(entry.id)
    if entry.options.layout then entry.options.layout(state.orientation) end
    if entry.frame.warscapeChrome then entry.frame.warscapeChrome.setLocked(state.locked) end
end

function P:SetLocked(id, locked)
    local entry = self.entries[id]
    if not entry then return end
    local state = self:State(id)
    if state.locked == locked then return end
    if entry.dragging then entry.frame:StopMovingOrSizing(); entry.dragging = nil end
    if not locked then
        local current=self.entries[self.activeGroups[entry.group]] or entry
        state.position=location(current.frame)
    end
    state.locked = locked
    if locked then state.position=nil;self.windows[entry.group].position=nil end
    self:RefreshWindow(entry.group)
end

function P:ToggleOrientation(id)
    local entry = self.entries[id]
    if not entry then return end
    local state = self:State(id)
    local current=self.entries[self.activeGroups[entry.group]] or entry
    self:Capture(current)
    state.orientation = state.orientation == "landscape" and "portrait" or "landscape"
    self:RefreshWindow(entry.group)
end

function P:SetHudFrame(frame, bottomOffset)
    self.hud, self.hudBottomOffset = frame, bottomOffset or 0
    frame:HookScript("OnSizeChanged", function() if P.loggedIn then P:RestoreScales() end end)
end

function P:SetDocks(left, right, width, referenceWidth)
    self.docks, self.dockWidth = {left = left, right = right}, width
    self.dockReferenceWidth = referenceWidth or 700
    self.windows.left.anchor,self.windows.right.anchor=left,right
    if self.loggedIn then self:RestoreScales() end
end

function P:DockFit()
    if not self.docks then return 1 end
    return self.dockWidth * scaleOf(self.docks.left) / self.dockReferenceWidth
end

function P:ScaleLimit(id)
    local group=self:Group(id)
    local fit=self:DockFit()
    local width,height=self:Envelope(group)
    local state=self:WindowState(group)
    local occupied,availableWidth=16,UIParent:GetWidth()-24
    if state.locked and self.docks then
        local dock=self.windows[group].anchor
        occupied=(dock:GetBottom() or 0)*scaleOf(dock)+16
        local x=(dock:GetCenter() or UIParent:GetWidth()/2)*scaleOf(dock)
        availableWidth=group=="left" and x-8 or UIParent:GetWidth()-x-8
    end
    return math.max(.05,math.min(MAX,(UIParent:GetHeight()-occupied)/(height*fit),availableWidth/(width*fit)))
end

function P:RefreshWindow(group)
    group=self:Group(group)
    local window=self.windows[group]
    if window.refreshing then return end
    window.refreshing=true
    -- Reserve the largest registered content area on this side. Switching to a
    -- larger page cannot recalculate the common scale or clamp a different anchor.
    for _,entry in pairs(self.entries) do if entry.group==group then self:Layout(entry) end end
    window.scale=math.min(self:GetScale(group),self:ScaleLimit(group))*self:DockFit()
    for _,entry in pairs(self.entries) do
        if entry.group==group and entry.options.scalable~=false and canChange(entry) then entry.frame:SetScale(window.scale) end
    end
    if not self:WindowState(group).locked then self:ResolvePosition(group) end
    for _,entry in pairs(self.entries) do if entry.group==group then self:Position(entry) end end
    window.refreshing=nil
end

function P:RestoreScale(id)
    if id then self:RefreshWindow(self:Group(id)) else self:RestoreScales() end
end
function P:RestoreScales()
    self:RefreshWindow("left");self:RefreshWindow("right")
end
function P:GetScale(id)
    local value=self:State(id).scale
    return finite(value) and value or legacyScale()
end
function P:AdjustScale(id, delta)
    local group=self:Group(id)
    self:Capture(self.entries[self.activeGroups[group]])
    self:WindowState(group).scale=math.max(MIN,math.min(MAX,self:GetScale(group)*(delta>0 and STEP or 1/STEP)))
    self:RefreshWindow(group)
end

function P:HoveredPanel()
    for i = #self.order, 1, -1 do
        local id = self.order[i]
        local frame = self.entries[id].frame
        if self.entries[id].options.scalable ~= false and frame:IsShown() and MouseIsOver(frame) then return id end
    end
end

-- Read-only, physical-screen-pixel diagnostics. No settings or positions change.
-- Retain the full snapshot in memory for a developer inspecting /wgeometry.
function P:GeometrySnapshot()
    local function bounds(frame)
        if not frame then return end
        local x,y=frame:GetLeft(),frame:GetBottom()
        if not x or not y then return end
        local owner=frame.GetEffectiveScale and frame or frame:GetParent()
        local s=owner:GetEffectiveScale()
        return {left=x*s,bottom=y*s,width=frame:GetWidth()*s,height=frame:GetHeight()*s,
            scale=s,shown=frame:IsShown()}
    end
    local snapshot={panels={},buttons={},minimap=bounds(Minimap),
        leftGryphon=bounds(WarscapeHUDLeftGryphon),rightGryphon=bounds(WarscapeHUDRightGryphon)}
    for _,id in ipairs(self.order) do
        local entry=self.entries[id]
        local b=bounds(entry.frame)
        if b then
            local state=self:State(id)
            b.group,b.locked,b.orientation=entry.group,state.locked,state.orientation
            snapshot.panels[id]=b
        end
    end
    for i=1,10 do snapshot.buttons[i]=bounds(_G["WarscapeHUDMenuButton"..i]) end
    local left=self.activeGroups.left or "inventory"
    local right=self.activeGroups.right or "skills"
    local a,b=snapshot.panels[left],snapshot.panels[right]
    if a and b and snapshot.minimap then
        local center=snapshot.minimap.left+snapshot.minimap.width/2
        snapshot.comparison={left=left,right=right,
            comparable=a.locked and b.locked and a.orientation==b.orientation and math.abs(a.scale-b.scale)<.000001,
            widthError=math.abs(a.width-b.width),heightError=math.abs(a.height-b.height),
            bottomError=math.abs(a.bottom-b.bottom),
            topError=math.abs(a.bottom+a.height-b.bottom-b.height),
            mirrorError=math.abs((center-a.left-a.width)-(b.left-center))}
    end
    self.geometrySnapshot=snapshot
    return snapshot
end

SLASH_WARSCAPEGEOMETRY1="/wgeometry"
SlashCmdList.WARSCAPEGEOMETRY=function()
    local snapshot=P:GeometrySnapshot()
    if not DEFAULT_CHAT_FRAME then return end
    local function line(text) DEFAULT_CHAT_FRAME:AddMessage("Warscape geometry: "..text) end
    for _,id in ipairs(P.order) do
        local b=snapshot.panels[id]
        if b and b.shown then
            line(string.format("%s %s %s: x %.2f y %.2f, %.2f x %.2f pixels",id,
                b.locked and "locked" or "unlocked",b.orientation,b.left,b.bottom,b.width,b.height))
        end
    end
    local c=snapshot.comparison
    if c and c.comparable then
        line(string.format("pair errors: width %.3f height %.3f top %.3f bottom %.3f mirror %.3f px",
            c.widthError,c.heightError,c.topError,c.bottomError,c.mirrorError))
    else line("Pair comparison needs two locked menus with matching orientation and scale.") end
end

local events = CreateFrame("Frame")
events:RegisterEvent("PLAYER_LOGIN")
events:RegisterEvent("DISPLAY_SIZE_CHANGED")
events:RegisterEvent("UI_SCALE_CHANGED")
events:RegisterEvent("PLAYER_REGEN_ENABLED")
events:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_LOGIN" then P.loggedIn = true end
    if P.loggedIn then P:RestoreScales() end
    sync()
end)

-- Forge/interaction windows never join the two saved HUD-side containers.
function P:RegisterInteraction(id, frame)
    self.interactions = self.interactions or {}
    assert(not self.interactions[id], "Interaction panel must register once")
    self.interactions[id] = frame
    frame:SetClampedToScreen(true)
    frame:EnableMouseWheel(true)
    local function restore()
        local old=type(WarscapePanelScales)=="table" and WarscapePanelScales or {}
        local scales=type(old.interactions)=="table" and old.interactions or {}
        frame:SetScale(math.max(MIN,math.min(MAX,tonumber(scales[id]) or 1)))
    end
    frame:HookScript("OnShow",restore)
    frame:SetScript("OnMouseWheel",function(_,delta)
        if not IsControlKeyDown() then return end
        WarscapePanelScales=type(WarscapePanelScales)=="table" and WarscapePanelScales or {}
        WarscapePanelScales.interactions=type(WarscapePanelScales.interactions)=="table" and WarscapePanelScales.interactions or {}
        local scale=math.max(MIN,math.min(MAX,frame:GetScale()*(delta>0 and STEP or 1/STEP)))
        WarscapePanelScales.interactions[id]=scale
        frame:SetScale(scale)
    end)
    restore()
end
