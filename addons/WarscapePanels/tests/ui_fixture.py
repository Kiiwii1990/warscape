"""Real Lua 5.1 addons + native item scripts; mock geometry, not live rendering."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

ADDONS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ADDONS / 'WarscapeHUD/tools'))
from client_assets import ClientAssets

assets = ClientAssets(Path(r'C:\WoWDev\wowdecomp\bin\Win'))


def load(saved=None):
    lua = LuaRuntime()
    lua.execute((ADDONS / 'WarscapePanels/tests/ui_harness.lua').read_text())
    if saved:
        def table(value):
            return lua.table_from({k: table(v) for k, v in value.items()}) if isinstance(value, dict) else value
        for key, value in saved.items():
            lua.globals()[key] = table(value)
    for name in ['ItemButtonTemplate.lua', 'ContainerFrame.lua']:
        data, _ = assets.get('Interface\\FrameXML\\' + name)
        lua.execute(data.decode('utf-8-sig'))
    data, _ = assets.get('Interface\\FrameXML\\ContainerFrame.xml')
    scripts = ET.fromstring(data).find("{*}Button[@name='ContainerFrameItemButtonTemplate']/{*}Scripts")
    lua.globals().nativeTemplateScripts = lua.table_from({
        e.tag.rsplit('}', 1)[-1]: lua.eval('function(self, button, motion)\n' + (e.text or '') + '\nend')
        for e in scripts})
    lua.execute('''
        nativeControl=CreateFrame("Button","NativeSocialTest",FriendsFrame)
        nativeControl:SetScript("OnClick",function() socialClicks=(socialClicks or 0)+1 end)
        nativeControl:SetScript("OnMouseWheel",function() socialWheels=(socialWheels or 0)+1 end)
    ''')
    for folder, names in [
        ('WarscapePanels', ['Panels.lua']),
        ('WarscapeSkills', ['Protocol.lua', 'Skin.lua', 'WarscapeSkills.lua', 'Bindings.lua']),
        ('WarscapeInventory', ['Inventory.lua', 'Bindings.lua']),
        ('WarscapeMenuPanels', ['MainPanels.lua', 'NativePanels.lua', 'Bindings.lua']),
        ('WarscapeHUD', ['WarscapeHUD.lua']),
    ]:
        for name in names:
            lua.execute((ADDONS / folder / name).read_text())
    lua.execute('dispatch("PLAYER_LOGIN")')
    return lua

\n