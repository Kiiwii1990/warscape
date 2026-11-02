-- Self-whisper protocol: recipe/cost/XP/inventory mutations belong to the server.
local S=WarscapeSkillsSkin
local art="Interface\\AddOns\\WarscapeSkills\\art\\"
local frame=CreateFrame("Frame","WarscapeSmeltingFrame",UIParent)
local _,status=S.Panel(frame,{title="Smelting",closeName="WarscapeSmeltingClose",noFooter=true,noDragons=true,background=art.."SmeltingStone"})
frame.status=status
frame:SetFrameStrata("DIALOG");frame:EnableMouse(true)
frame:ClearAllPoints();frame:SetPoint("CENTER",UIParent,"CENTER",0,0)
frame.warscapeChrome.lock:Hide();frame.warscapeChrome.rotate:Hide()
for _,side in ipairs({"LEFT","RIGHT"}) do
 local hammer=frame:CreateTexture(nil,"OVERLAY")
 hammer:SetTexture(art.."SmeltingHammer")
 hammer:SetSize(116,112);hammer:SetPoint("TOP"..side,frame,"TOP"..side,side=="LEFT" and -2 or 2,0)
 if side=="RIGHT" then hammer:SetTexCoord(1,0,0,1) end
end
local ids={"bronze","iron","steel","silver","gold","mithril","adamant","rune"}
local names={"Bronze","Iron","Steel","Silver","Gold","Mithril","Adamant","Rune"}
local icons={"INV_Ingot_Bronze","INV_Ingot_Iron","INV_Ingot_Steel","INV_Ingot_01","INV_Ingot_03","INV_Ingot_06","INV_Ingot_10","INV_Ingot_07"}
local token,sequence,quantity=nil,0,1
local pendingSequence,serverError=nil,nil
local suppressCloseOnHide=false
local cells,quantities={},{}
local state={level=0,copper=0,tin=0,space=false,busy=false}
local function send(operation,tail)
 if not token then return end
 sequence=sequence+1
 SendAddonMessage("WCSmelt",operation.."|"..token.."|"..sequence..(tail or ""),"WHISPER",UnitName("player"))
 return sequence
end
local function reason(i)
 if i~=1 then return "Recipe not implemented" end
 if state.level<1 then return "Requires attained Smithing level 1" end
 if state.copper<1 or state.tin<1 then return "Missing ingredients: 1 Copper Ore and 1 Tin Ore" end
 if not state.space then return "No usable inventory space or materials unavailable" end
 if state.busy then return "Smelting in progress" end
end
local function refresh()
 for i,c in ipairs(cells) do
  c.unavailable=reason(i)
  c.icon:SetDesaturated(c.unavailable~=nil)
  local brightness=c.unavailable and .35 or 1
  c.icon:SetVertexColor(brightness,brightness,brightness)
  c.name:SetTextColor(c.unavailable and .45 or 1,c.unavailable and .42 or .82,c.unavailable and .35 or .25)
 end
 status:SetText(serverError or (state.busy and "Smelting..." or "Select quantity, then a bar"))
end
for i,id in ipairs(ids) do
 local c=CreateFrame("Button","WarscapeSmeltBar"..i,frame)
 c:SetSize(128,128);c:SetPoint("TOPLEFT",frame,"TOPLEFT",73+((i-1)%4)*142,-103-math.floor((i-1)/4)*140)
 S.NineSlice(c,"Cell",406,155,512,256,16,8)(128,128)
 c.icon=c:CreateTexture(nil,"ARTWORK");c.icon:SetTexture("Interface\\Icons\\"..icons[i]);c.icon:SetSize(80,80);c.icon:SetPoint("TOP",0,-9)
 c.name=S.Font(c,20,"BOTTOM",0,12);c.name:SetText(names[i])
 c:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square","ADD")
 c:SetScript("OnClick",function() if not reason(i) then pendingSequence=send("START","|"..id.."|"..quantity) end end)
 c:SetScript("OnEnter",function(self)
  GameTooltip:SetOwner(self,"ANCHOR_RIGHT");GameTooltip:SetText(names[i].." Bar",1,.82,.25)
  if i==1 then
   GameTooltip:AddLine("1 Copper Ore + 1 Tin Ore",1,1,1)
   GameTooltip:AddLine("Smithing 1 | 6.2 XP | 3 seconds",1,1,1)
   GameTooltip:AddLine("Carried: "..state.copper.." Copper, "..state.tin.." Tin",1,1,1)
  end
  GameTooltip:AddLine(reason(i) or "Click to smelt selected quantity",1,.82,.25,true);GameTooltip:Show()
 end)
 c:SetScript("OnLeave",function() GameTooltip:Hide() end)
 cells[i]=c
end
for i,q in ipairs({1,5,10,0}) do
 local b=CreateFrame("Button","WarscapeSmeltQuantity"..i,frame)
 b:SetSize(116,42);b:SetPoint("BOTTOMLEFT",frame,"BOTTOMLEFT",95+(i-1)*132,27)
 S.NineSlice(b,"Cell",406,155,512,256,16,7)(116,42)
 b.text=S.Font(b,24,"CENTER",0,0);b.text:SetText(q==0 and "All" or tostring(q))
 b.selected=b:CreateTexture(nil,"ARTWORK");b.selected:SetTexture("Interface\\Buttons\\ButtonHilight-Square");b.selected:SetAllPoints(b);b.selected:SetBlendMode("ADD");b.selected:SetVertexColor(1,.72,.12,.5)
 b:SetScript("OnClick",function()
  quantity=q
  for j,other in ipairs(quantities) do if j==i then other.selected:Show() else other.selected:Hide() end end
 end)
 if i~=1 then b.selected:Hide() end
 quantities[i]=b
end
frame:SetScript("OnHide",function() if token and not suppressCloseOnHide then send("CLOSE") end;token=nil;pendingSequence=nil end)
table.insert(UISpecialFrames,"WarscapeSmeltingFrame")
frame:Hide();WarscapePanels:RegisterInteraction("smelting",frame)
local events=CreateFrame("Frame")
events:RegisterEvent("CHAT_MSG_ADDON");events:RegisterEvent("PLAYER_LEAVING_WORLD")
events:SetScript("OnEvent",function(_,event,p,message,distribution,sender)
 if event=="PLAYER_LEAVING_WORLD" then frame:Hide();return end
 if p~="WCSmelt" or distribution~="WHISPER" or sender~=UnitName("player") or #message>180 then return end
 local f={};for value in string.gmatch(message.."|","([^|]*)|") do f[#f+1]=value end
 if f[1]=="OPEN" and #f==2 and tonumber(f[2]) then
  token=f[2];sequence=0;pendingSequence=nil;serverError=nil;state={level=0,copper=0,tin=0,space=false,busy=false};refresh();frame:Show()
 elseif f[2]==token and f[1]=="CLOSE" then token=nil;frame:Hide()
 elseif f[2]==token and f[1]=="ACCEPT" and tonumber(f[3])==pendingSequence then
  token=nil;pendingSequence=nil;serverError=nil;suppressCloseOnHide=true;frame:Hide();suppressCloseOnHide=false
 elseif f[2]==token and f[1]=="REJECT" and tonumber(f[3])==pendingSequence then
  pendingSequence=nil;serverError="Request rejected. Check range, level, materials and inventory space.";refresh()
 elseif f[2]==token and f[1]=="STATE" and #f==7 then
  local level,copper,tin=tonumber(f[3]),tonumber(f[4]),tonumber(f[5])
  if not level or not copper or not tin then return end
  serverError=nil;state={level=level,copper=copper,tin=tin,space=f[6]=="1",busy=f[7]=="1"};refresh()
 end
end)
refresh()
