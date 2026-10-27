"""Inventory B override policy, using a separate owner from the Skills N override."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]
binding = ET.parse(root / 'Bindings.xml').getroot().find('Binding')
assert binding.attrib['name'] == 'WARSCAPE_TOGGLE_INVENTORY'
assert 'WarscapeInventory_Toggle();' in binding.text
lua = LuaRuntime()
lua.execute('''
combat, base, explicit, count = false, "TOGGLEBACKPACK", nil, 0
function CreateFrame()
    owner={RegisterEvent=function() end}
    function owner:SetScript(_,callback) self.callback=callback end
    return owner
end
function InCombatLockdown() return combat end
function GetBindingAction(key) assert(key=="B");return base end
function GetBindingKey(action) assert(action=="WARSCAPE_TOGGLE_INVENTORY");return explicit end
function ClearOverrideBindings(frame) assert(frame==owner);override=nil;count=count+1 end
function SetOverrideBinding(frame,priority,key,action)
    assert(frame==owner and key=="B" and priority==false);override=action
end
''')
lua.execute((root / 'Bindings.lua').read_text())
lua.execute('''
owner.callback();assert(override=="WARSCAPE_TOGGLE_INVENTORY")
base="OPENALLBAGS";owner.callback();assert(override=="WARSCAPE_TOGGLE_INVENTORY")
base="TOGGLEWORLDMAP";owner.callback();assert(override==nil)
base="";owner.callback();assert(override==nil)
base="TOGGLEBACKPACK";explicit="CTRL-B";owner.callback();assert(override==nil)
explicit=nil;combat=true;local before=count;owner.callback();assert(count==before)
combat=false;owner.callback();assert(override=="WARSCAPE_TOGGLE_INVENTORY")
''')
print('PASS: default B override, custom bindings, distinct owner and combat deferral')
