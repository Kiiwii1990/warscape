-- Keep native 3.3.5 widgets, scripts, tabs, selections and item actions intact.
-- Complex native pages live in a scrollable viewport instead of being squeezed
-- to tiny text or having their lower controls clipped by the landscape shell.
local skin, manager = WarscapeSkillsSkin, WarscapePanels

function WarscapeMenuPanels_RegisterNative(definition, native)
    if InCombatLockdown() then return end -- Never reparent native UI during combat.
    local id = definition.id
    local name = "Warscape" .. id:gsub("^%l", string.upper) .. "MenuFrame"
    local shell = CreateFrame("Frame", name, UIParent)
    local titles = {settings="Settings", friends="Friends / Social", quests="Quest Journal", equipment="Equipment"}
    skin.Panel(shell, {title=titles[id], noFooter=true, noStatus=true, closeName=name.."CloseButton"})
    shell:SetFrameStrata("DIALOG"); shell:EnableMouse(true); shell:Hide()
    table.insert(UISpecialFrames, name)
    local viewport = CreateFrame("ScrollFrame", name.."Viewport", shell)
    local content = CreateFrame("Frame", nil, viewport)
    viewport:SetScrollChild(content)
    viewport:EnableMouseWheel(true)
    local vertical = CreateFrame("Slider", name.."ScrollBar", shell, "UIPanelScrollBarTemplate")
    vertical:SetValueStep(24)
    vertical:SetScript("OnValueChanged", function(_, value) viewport:SetVerticalScroll(value) end)
    local horizontal = CreateFrame("Slider", name.."HorizontalScrollBar", shell)
    horizontal:SetOrientation("HORIZONTAL")
    horizontal:SetThumbTexture("Interface\\Buttons\\UI-SliderBar-Button-Horizontal")
    horizontal:SetBackdrop({bgFile="Interface\\AddOns\\WarscapeSkills\\art\\Stone",
        edgeFile="Interface\\Tooltips\\UI-Tooltip-Border",tile=true,tileSize=100,edgeSize=8})
    horizontal:SetValueStep(24)
    horizontal:SetScript("OnValueChanged", function(_, value) viewport:SetHorizontalScroll(value) end)
    viewport:SetScript("OnMouseWheel", function(_, delta)
        if IsControlKeyDown() then manager:AdjustScale(id,delta)
        else
            local slider = IsShiftKeyDown() and horizontal or vertical
            local _, maximum = slider:GetMinMaxValues()
            slider:SetValue(math.max(0,math.min(maximum,slider:GetValue()-delta*24)))
        end
    end)
    -- Disable only the old automatic top-level placement, not its native scripts.
    -- GetUIPanelWindowInfo in the installed 3.3.5 UI honours these attributes.
    native:SetAttribute("UIPanelLayout-defined", true)
    native:SetAttribute("UIPanelLayout-enabled", false)
    native:SetParent(content)
    native:SetFrameStrata("DIALOG")
    native:SetFrameLevel(content:GetFrameLevel()+1)
    if id=="settings" then native:SetBackdrop(nil) end
    native:SetScale(1)
    native:SetClampedToScreen(false)
    native:SetMovable(false)
    native:RegisterForDrag()
    native:SetScript("OnDragStart", nil); native:SetScript("OnDragStop", nil)
    local nativeWidth = native:GetWidth()
    local nativeHeight = native:GetHeight()
    local close = _G[definition.name.."CloseButton"]
    if close then close:Hide(); close:HookScript("OnShow",function(self) self:Hide() end) end

    -- Ctrl-wheel must also reach the shared scale manager over native scrolling
    -- children. Ordinary wheel input retains the child's existing callback.
    local function routeWheel(frame)
        if frame.warscapeWheelRouted then return end
        frame.warscapeWheelRouted = true
        local wheel = frame:GetScript("OnMouseWheel")
        if wheel then
            frame:SetScript("OnMouseWheel",function(self,delta,...)
                if IsControlKeyDown() then manager:AdjustScale(id,delta)
                else wheel(self,delta,...) end
            end)
        end
        for _,child in ipairs({frame:GetChildren()}) do routeWheel(child) end
    end
    local function updateContent()
        if id == "settings" then
            local visible = {}
            for _,suffix in ipairs({"Options","SoundOptions","UIOptions","MacOptions","Keybindings",
                "Macros","Ratings","Logout","Quit","Continue"}) do
                local button = _G["GameMenuButton"..suffix]
                if button and button:IsShown() then visible[#visible+1]=button end
            end
            local landscape = manager:State(id).orientation == "landscape"
            local columns = landscape and 2 or 1
            local width = math.min(220,(viewport:GetWidth()-24)/columns)
            for i,button in ipairs(visible) do
                button:ClearAllPoints();button:SetWidth(width-12)
                local col,row=(i-1)%columns,math.floor((i-1)/columns)
                button:SetPoint("TOPLEFT",native,"TOPLEFT",12+col*width,-12-row*30)
            end
            nativeWidth=columns*width+24
            nativeHeight=math.ceil(#visible/columns)*30+24
            native:SetSize(nativeWidth,nativeHeight)
        else
            -- Native dimensions are meaningful (e.g. quest list + details).
            -- Keep their readable widgets and both axes reachable in either shape.
            nativeHeight=math.max(nativeHeight,native:GetHeight())
        end
        local w,h=math.max(viewport:GetWidth(),nativeWidth),nativeHeight+32 -- native tab clearance
        content:SetSize(w,h)
        native:ClearAllPoints();native:SetPoint("TOPLEFT",content,"TOPLEFT",(w-nativeWidth)/2,0)
        local maxY,maxX=math.max(0,h-viewport:GetHeight()),math.max(0,w-viewport:GetWidth())
        vertical:SetMinMaxValues(0,maxY);horizontal:SetMinMaxValues(0,maxX)
        vertical:SetValue(math.min(vertical:GetValue(),maxY))
        horizontal:SetValue(math.min(horizontal:GetValue(),maxX))
        if maxY>0 then vertical:Show() else vertical:Hide() end
        if maxX>0 then horizontal:Show() else horizontal:Hide() end
        routeWheel(native)
    end
    local function layout(orientation)
        -- Match every other menu's outer profile. Native pages retain readable
        -- widgets inside the existing two-axis viewport in either orientation.
        shell.warscapeChrome.resize(orientation)
        viewport:ClearAllPoints();viewport:SetPoint("TOPLEFT",shell,"TOPLEFT",48,-92)
        viewport:SetSize(shell:GetWidth()-96,shell:GetHeight()-130)
        vertical:ClearAllPoints();vertical:SetPoint("TOPRIGHT",shell,"TOPRIGHT",-26,-108)
        vertical:SetPoint("BOTTOMRIGHT",shell,"BOTTOMRIGHT",-26,54)
        horizontal:ClearAllPoints();horizontal:SetPoint("BOTTOMLEFT",shell,"BOTTOMLEFT",60,22)
        horizontal:SetSize(shell:GetWidth()-120,14)
        updateContent()
    end
    local changing = false
    native:HookScript("OnShow",function()
        if changing then return end
        changing=true
        shell:Show(); manager:Open(id);updateContent()
        changing=false
    end)
    native:HookScript("OnHide",function()
        if not changing then shell:Hide() end
    end)
    shell:HookScript("OnHide",function()
        if native:IsShown() then native:Hide() end
    end)
    manager:Register(id,shell,{group=definition.group,layout=layout,
        combatSensitive=native.IsProtected and native:IsProtected(),
        show=function()
            definition.toggle()
            if native:IsShown() then shell:Show() end
        end,
        hide=function()
            if native:IsShown() then definition.toggle() end
            shell:Hide()
        end})
    if native:IsShown() then shell:Show() end
end
