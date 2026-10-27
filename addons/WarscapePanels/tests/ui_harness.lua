widgets, messages, calls, UISpecialFrames, SlashCmdList = {}, {}, {}, {}, {}
clock, ctrl, combat, modified, cursorItem = 10, false, false, nil, false
bagSizes = {[0]=16, [1]=8}
items = {["0:1"]={"Interface\\Icons\\INV_Misc_Bone_01",10}}
baseBindings, customBindings = {B="TOGGLEBACKPACK",N="TOGGLETALENTS"}, {}
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
function methods:SetSize(w,h) self.width,self.height=w,h end
function methods:SetHeight(h) self.height=h end
function methods:GetHeight() return self.height end
function methods:GetWidth() return self.width end
function methods:GetRight() return UIParent.width end
function methods:SetScale(v) self.scale=v end
function methods:GetScale() return self.scale end
function methods:GetEffectiveScale() return self.scale*(self.parent and self.parent:GetEffectiveScale() or 1) end
function methods:SetPoint(a,b,c,d,e)
    if not b then b,c,d,e=self.parent or UIParent,a,0,0
    elseif type(b)=="number" then b,c,d,e=self.parent or UIParent,a,b,c end
    self.point={a,b,c,d or 0,e or 0}
end
function methods:GetPoint() return unpack(self.point) end
function methods:ClearAllPoints() self.point=nil end
function methods:SetAllPoints(w) self.allPoints=w or self.parent end
function methods:SetTexture(v) self.texture=v end
function methods:SetTexCoord(...) self.uv={...} end
function methods:SetVertexColor(...) self.color={...} end
function methods:SetDesaturated(v) self.desaturated=v; return true end
function methods:SetText(v) self.text=v end
function methods:SetValue(v) self.value=v end
function methods:SetAlpha(v) self.alpha=v end
function methods:SetBackdrop(v) self.backdrop=v end
function methods:SetBackdropColor(...) self.bg={...} end
function methods:LockHighlight() self.highlight=true end
function methods:UnlockHighlight() self.highlight=false end
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
function methods:CreateTexture(name,layer) local w=CreateFrame("Texture",name,self); w.layer=layer; return w end
function methods:CreateFontString(name,layer) return self:CreateTexture(name,layer) end
function methods:SetNormalTexture(path) self.normal=self:CreateTexture(); self.normal:SetTexture(path) end
function methods:GetNormalTexture() return self.normal end
function methods:SetPushedTexture(path) self.pushed=self:CreateTexture(); self.pushed:SetTexture(path) end
function methods:GetPushedTexture() return self.pushed end
function methods:SetFrameLevel(v) self.level=v end
function methods:GetFrameLevel() return self.level or 1 end
function methods:EnableMouseWheel(v) self.wheel=v end
for _,m in ipairs({"SetFrameStrata","SetClampedToScreen","EnableMouse","EnableKeyboard","SetMovable",
    "RegisterForClicks","RegisterForDrag","SetHighlightTexture","SetBackdropBorderColor","SetFont",
    "SetTextColor","SetShadowColor","SetShadowOffset","StartMoving","StopMovingOrSizing",
    "SetStatusBarTexture","SetStatusBarColor","SetMinMaxValues","AddLine","AddDoubleLine"}) do methods[m]=function() end end
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
MinimapCluster=CreateFrame("Frame","MinimapCluster",UIParent)
Minimap=CreateFrame("Frame","Minimap",MinimapCluster)
ContainerFrame1=CreateFrame("Frame","ContainerFrame1",UIParent);ContainerFrame1:SetID(0);ContainerFrame1:Hide()
ContainerFrame2=CreateFrame("Frame","ContainerFrame2",UIParent);ContainerFrame2:SetID(5);ContainerFrame2:Hide()
function dispatch(event,...)
    for _,w in ipairs(widgets) do
        if w.events[event] and w.scripts.OnEvent then w.scripts.OnEvent(w,event,...) end
    end
end
