widgets, messages, calls, UISpecialFrames, SlashCmdList = {}, {}, {}, {}, {}
clock, ctrl, combat, modified, cursorItem = 10, false, false, nil, false
bagSizes = {[0]=16, [1]=8}
items = {["0:1"]={"Interface\\Icons\\INV_Misc_Bone_01",10}}
baseBindings, customBindings = {B="TOGGLEBACKPACK",N="TOGGLETALENTS",O="TOGGLESOCIAL",L="TOGGLEQUESTLOG",
    C="TOGGLECHARACTER0",K="TOGGLECHARACTER1",I="TOGGLELFG",P="TOGGLESPELLBOOK"}, {}
local function record(name, ...) calls[#calls+1] = {name,...} end
function GetTime() return clock end
function UnitName() return "Tester" end
function SendAddonMessage(...) messages[#messages+1]={...} end
function GetContainerNumSlots(bag) return bagSizes[bag] or 0 end
function GetContainerItemInfo(bag,slot)
    assert(slot>=1 and slot<=GetContainerNumSlots(bag), "native container read outside real capacity")
    local item=items[bag..":"..slot]
    if item then return item[1],item[2],false,1,false,false,"item:1" end
end
function GetContainerItemLink() return "item:1" end
function GetContainerItemQuestInfo() return nil,nil,false end
function GetContainerItemCooldown() return 0,0,1 end
function PickupContainerItem(...) record("pickup",...); cursorItem=not cursorItem end
function UseContainerItem(...) record("use",...) end
function SplitContainerItem(...) record("split",...) end
function SocketContainerItem(...) record("socket",...) end
function IsControlKeyDown() return ctrl end
function GetCursorPosition() return 100,100 end
function GetScreenWidth() return UIParent:GetWidth() end
function MouseIsOver(w) return w.over==true end
function InCombatLockdown() return combat end
function GetBindingAction(k) return baseBindings[k] or "" end
function GetBindingKey(action) return customBindings[action] end
function ClearOverrideBindings(owner) owner.overrides={} end
function SetOverrideBinding(owner,priority,key,action) owner.overrides[key]=action end
function IsModifiedClick(kind) return kind and modified==kind or (not kind and modified~=nil) end
function GetCursorInfo() return cursorItem and "item" or nil end
function CursorHasItem() return cursorItem end
function SpellCanTargetItem() return false end
function InRepairMode() return false end
function HandleModifiedItemClick() return false end
function OpenStackSplitFrame(count,owner) StackSplitFrame.owner=owner; record("split-dialog",count) end
function CooldownFrame_SetTimer() end
function MerchantFrame_ResetRefundItem() end
function MerchantFrame_SetRefundItem() end
function ResetCursor() end
local methods={}
function methods:SetScript(k,v) self.scripts[k]=v end
function methods:GetScript(k) return self.scripts[k] end
function methods:HookScript(k,v) self.hooks[k]=self.hooks[k] or {}; table.insert(self.hooks[k],v) end
function methods:RegisterEvent(event) self.events[event]=true end
function methods:GetName() return self.name end
function methods:SetID(id) self.id=id end
function methods:GetID() return self.id end
function methods:GetParent() return self.parent end
function methods:SetParent(p) self.parent=p end
function methods:SetSize(w,h)
    local changed=self.width~=w or self.height~=h
    self.width,self.height=w,h
    if changed then
        if self.scripts.OnSizeChanged then self.scripts.OnSizeChanged(self,w,h) end
        for _,f in ipairs(self.hooks.OnSizeChanged or {}) do f(self,w,h) end
    end
end
function methods:SetHeight(h) self.height=h end
function methods:GetHeight() return self.height end
function methods:GetWidth() return self.width end

function methods:SetScale(v) self.scale=v end
function methods:GetScale() return self.scale end
function methods:GetEffectiveScale() return self.scale*(self.parent and self.parent:GetEffectiveScale() or 1) end
function methods:SetPoint(a,b,c,d,e)
    if not b then b,c,d,e=self.parent or UIParent,a,0,0
    elseif type(b)=="number" then b,c,d,e=self.parent or UIParent,a,b,c end
    self.point={a,b,c,d or 0,e or 0}
    self.points=self.points or {}
    self.points[a]=self.point
end
function methods:GetPoint() return unpack(self.point) end
function methods:ClearAllPoints() self.point=nil;self.points={};self.allPoints=nil end
function methods:SetAllPoints(w) self.allPoints=w or self.parent end
function methods:SetTexture(v) self.texture=v end
function methods:SetTexCoord(...) self.uv={...};self.texcoord=self.uv end
function methods:SetVertexColor(...) self.color={...} end
function methods:SetBlendMode(v) self.blendMode=v end
function methods:SetDesaturated(v) self.desaturated=v; return true end
function methods:SetText(v) self.text=v;if self.kind=="Tooltip" then self.lines={} end end
function methods:SetValue(v) self.value=v;if self.scripts.OnValueChanged then self.scripts.OnValueChanged(self,v) end end
function methods:SetAlpha(v) self.alpha=v end
function methods:SetValueStep(v) self.valueStep=v end
function methods:SetBackdrop(v) self.backdrop=v end
function methods:SetBackdropColor(...) self.bg={...} end
function methods:LockHighlight() self.highlight=true;self.highlightLocked=true end
function methods:UnlockHighlight() self.highlight=false;self.highlightLocked=false end
function methods:SetOwner(v) self.owner=v end
function methods:GetOwner() return self.owner end
function methods:SetBagItem(bag,slot) record("tooltip",bag,slot); self:Show(); return false,0 end
function methods:Show()
    if self.shown then return end
    self.shown=true
    if self.scripts.OnShow then self.scripts.OnShow(self) end
    for _,f in ipairs(self.hooks.OnShow or {}) do f(self) end
end
function methods:Hide()
    if not self.shown then return end
    self.shown=false
    if self.scripts.OnHide then self.scripts.OnHide(self) end
    for _,f in ipairs(self.hooks.OnHide or {}) do f(self) end
end
function methods:IsShown() return self.shown end
function methods:IsVisible()
    return self.shown and (not self.parent or self.parent:IsVisible())
end
function methods:CreateTexture(name,layer) local w=CreateFrame("Texture",name,self); w.layer=layer; return w end
function methods:CreateFontString(name,layer) local w=self:CreateTexture(name,layer);w.kind="FontString";return w end
function methods:SetNormalTexture(path) self.normal=self:CreateTexture(); self.normal:SetTexture(path) end
function methods:GetNormalTexture() return self.normal end
function methods:SetPushedTexture(path) self.pushed=self:CreateTexture(); self.pushed:SetTexture(path) end
function methods:GetPushedTexture() return self.pushed end
function methods:SetFrameLevel(v) self.level=v end
function methods:GetFrameLevel() return self.level or 1 end
function methods:EnableMouseWheel(v) self.wheel=v end
function methods:SetScrollChild(child) self.scrollChild=child end
function methods:EnableMouse(v) self.mouseEnabled=v end
for _,m in ipairs({"SetFrameStrata","SetClampedToScreen","EnableMouse","EnableKeyboard","SetMovable",
    "RegisterForClicks","RegisterForDrag","SetHighlightTexture","SetBackdropBorderColor","SetFont",
    "SetTextColor","SetShadowColor","SetShadowOffset","StartMoving","StopMovingOrSizing",
    "SetStatusBarTexture","SetStatusBarColor"}) do methods[m]=function() end end
function methods:SetFont(path,size,flags) self.font=path;self.fontSize=size;self.fontFlags=flags end
function methods:SetTextColor(...) self.color={...} end
function methods:SetMinMaxValues(low,high) self.minValue,self.maxValue=low,high end
function methods:GetMinMaxValues() return self.minValue or 0,self.maxValue or 0 end
function methods:GetValue() return self.value or 0 end
function methods:SetVerticalScroll(v) self.verticalScroll=v end
function methods:GetVerticalScroll() return self.verticalScroll or 0 end
function methods:SetHorizontalScroll(v) self.horizontalScroll=v end
function methods:GetHorizontalScroll() return self.horizontalScroll or 0 end
function methods:SetOrientation(v) self.orientation=v end
function methods:SetThumbTexture(v) self.thumb=v end
function methods:SetWidth(v) self.width=v end
function methods:SetJustifyH(v) self.justifyH=v end
function methods:AddLine(...) self.lines=self.lines or {};table.insert(self.lines,{...}) end
function methods:AddDoubleLine(...) self:AddLine(...) end
function methods:SetAttribute(k,v) self.attributes=self.attributes or {};self.attributes[k]=v end
function methods:GetAttribute(k) return self.attributes and self.attributes[k] end
function methods:GetChildren()
    local children={}
    for _,child in ipairs(widgets) do if child.parent==self and child.kind~="Texture" and child.kind~="FontString" then children[#children+1]=child end end
    return unpack(children)
end
function methods:SetMovable(v) self.movable=v end
function methods:StartMoving() assert(self.movable);self.moving=true end
function methods:StopMovingOrSizing() self.moving=false end
local factors={TOPLEFT={0,1},TOP={.5,1},TOPRIGHT={1,1},LEFT={0,.5},CENTER={.5,.5},RIGHT={1,.5},BOTTOMLEFT={0,0},BOTTOM={.5,0},BOTTOMRIGHT={1,0}}
local function scale(frame) return frame:GetEffectiveScale()/UIParent:GetEffectiveScale() end
function methods:Rect()
    if self==UIParent then return 0,0,self.width,self.height end
    if self.allPoints then return self.allPoints:Rect() end
    local positions={}
    for _,p in pairs(self.points or {}) do positions[#positions+1]=p end
    if #positions==0 then positions[1]={"BOTTOMLEFT",self.parent or UIParent,"BOTTOMLEFT",0,0} end
    local function target(p)
        local reference=type(p[2])=="string" and _G[p[2]] or p[2]
        local x,y,w,h=reference:Rect();local f=factors[p[3]]
        return x+w*f[1]+p[4]*scale(self),y+h*f[2]+p[5]*scale(self)
    end
    local p=positions[1];local x,y=target(p);local f=factors[p[1]]
    local w,h=self.width*scale(self),self.height*scale(self)
    for i=2,#positions do
        local q=positions[i];local xx,yy=target(q);local ff=factors[q[1]]
        if ff[1]~=f[1] then w=(xx-x)/(ff[1]-f[1]) end
        if ff[2]~=f[2] then h=(yy-y)/(ff[2]-f[2]) end
    end
    return x-w*f[1],y-h*f[2],w,h
end
function methods:GetLeft() local x=self:Rect();return x/scale(self) end
function methods:GetBottom() local _,y=self:Rect();return y/scale(self) end
function methods:GetRight() local x,_,w=self:Rect();return (x+w)/scale(self) end
function methods:GetTop() local _,y,_,h=self:Rect();return (y+h)/scale(self) end
function methods:GetCenter() local x,y,w,h=self:Rect();return (x+w/2)/scale(self),(y+h/2)/scale(self) end
function IsShiftKeyDown() return false end
function CreateFrame(kind,name,parent,template)
    local w=setmetatable({kind=kind,name=name,parent=parent,scripts={},hooks={},events={},shown=true,scale=1,width=0,height=0}, {__index=methods})
    if name then _G[name]=w end
    widgets[#widgets+1]=w
    if template=="ContainerFrameItemButtonTemplate" then
        w.shown=false
        for _,suffix in ipairs({"IconTexture","IconQuestTexture","Count","Stock","Cooldown","NormalTexture"}) do
            local child=CreateFrame("Texture",name..suffix,w)
            if suffix=="NormalTexture" then w.normal=child end
        end
        for k,f in pairs(nativeTemplateScripts) do w.scripts[k]=f end
        w.scripts.OnLoad(w)
    end
    return w
end
UIParent=CreateFrame("Frame","UIParent");UIParent:SetSize(1920,1080)
GameTooltip=CreateFrame("Tooltip","GameTooltip")
MerchantFrame=CreateFrame("Frame","MerchantFrame");MerchantFrame:Hide()
StackSplitFrame=CreateFrame("Frame","StackSplitFrame");StackSplitFrame:Hide()
LootFrame=CreateFrame("Frame","LootFrame")
Confirmation=CreateFrame("Frame","Confirmation")
GameMenuFrame=CreateFrame("Frame","GameMenuFrame",UIParent);GameMenuFrame:SetSize(195,240);GameMenuFrame:Hide()
for _,suffix in ipairs({"Options","SoundOptions","UIOptions","MacOptions","Keybindings","Macros","Ratings","Logout","Quit","Continue"}) do CreateFrame("Button","GameMenuButton"..suffix,GameMenuFrame):SetSize(160,22) end
FriendsFrame=CreateFrame("Frame","FriendsFrame",UIParent);FriendsFrame:SetSize(384,512);FriendsFrame:Hide()
QuestLogFrame=CreateFrame("Frame","QuestLogFrame",UIParent);QuestLogFrame:SetSize(682,447);QuestLogFrame:Hide()
CharacterFrame=CreateFrame("Frame","CharacterFrame",UIParent);CharacterFrame:SetSize(384,512);CharacterFrame:Hide()
function ToggleGameMenu()
    menuToggleCount=(menuToggleCount or 0)+1
    if GameMenuFrame:IsShown() then GameMenuFrame:Hide() else GameMenuFrame:Show() end
end
secureHooks={}
function hooksecurefunc(name, callback)
    local original=_G[name]
    assert(type(original)=="function", "missing function for secure hook: "..name)
    secureHooks[name]=(secureHooks[name] or 0)+1
    _G[name]=function(...)
        local results={original(...)}
        callback(...)
        return unpack(results)
    end
end
function ToggleFriendsFrame() if FriendsFrame:IsShown() then FriendsFrame:Hide() else FriendsFrame:Show() end end
function ToggleFrame(frame) if frame:IsShown() then frame:Hide() else frame:Show() end end
function ToggleCharacter() if CharacterFrame:IsShown() then CharacterFrame:Hide() else CharacterFrame:Show() end end
MinimapCluster=CreateFrame("Frame","MinimapCluster",UIParent)
Minimap=CreateFrame("Frame","Minimap",MinimapCluster)
for _,name in ipairs({"MinimapBackdrop","MinimapBorder","MinimapBorderTop","MinimapNorthTag","MinimapCompassTexture","MinimapZoomIn","MinimapZoomOut","MiniMapWorldMapButton","MiniMapTracking","MinimapZoneTextButton","MinimapToggleButton","GameTimeFrame","MinimapCalendarButton","TimeManagerClockButton"}) do
    local w=CreateFrame("Frame",name,Minimap);w:SetSize(32,32)
end
ContainerFrame1=CreateFrame("Frame","ContainerFrame1",UIParent);ContainerFrame1:SetID(0);ContainerFrame1:Hide()
ContainerFrame2=CreateFrame("Frame","ContainerFrame2",UIParent);ContainerFrame2:SetID(5);ContainerFrame2:Hide()
function dispatch(event,...)
    for _,w in ipairs(widgets) do
        if w.events[event] and w.scripts.OnEvent then w.scripts.OnEvent(w,event,...) end
    end
end
