local skin=WarscapeSkillsSkin
for _, definition in ipairs({
    {id="attackStyles",title="Attack Styles"},
    {id="prayer",title="Prayer"},
    {id="spellbook",title="Spellbook"},
}) do
    local id=definition.id
    local name="Warscape"..id:gsub("^%l",string.upper).."Frame"
    local panel=CreateFrame("Frame",name,UIParent)
    skin.Panel(panel,{title=definition.title,noFooter=true,noStatus=true,closeName=name.."CloseButton"})
    panel:SetFrameStrata("DIALOG");panel:EnableMouse(true);panel:Hide()
    table.insert(UISpecialFrames,name)
    WarscapePanels:Register(id,panel,{group="right",layout=panel.warscapeChrome.resize})
end
function WarscapeMenuPanels_Toggle(id) return WarscapePanels:Toggle(id) end
