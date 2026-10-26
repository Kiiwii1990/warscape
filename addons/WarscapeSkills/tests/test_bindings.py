"""Lua 5.1 binding policy tests; no running client required."""
from pathlib import Path
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]
xml = ET.parse(root / 'Bindings.xml').getroot()
binding = xml.find('Binding')
assert binding.attrib['name'] == 'WARSCAPE_TOGGLE_SKILLS'
assert 'WarscapeSkills_Toggle();' in binding.text
lua = LuaRuntime()
lua.execute('''
baseAction, addonKey, combat = "TOGGLETALENTS", nil, false
override, clears = nil, 0
function CreateFrame()
    owner = {RegisterEvent = function() end}
    function owner:SetScript(_, callback) self.callback = callback end
    return owner
end
function InCombatLockdown() return combat end
function GetBindingKey(action) assert(action == "WARSCAPE_TOGGLE_SKILLS"); return addonKey end
function GetBindingAction(key) assert(key == "N"); return baseAction end
function ClearOverrideBindings(w) assert(w == owner); override = nil; clears = clears + 1 end
function SetOverrideBinding(w, priority, key, action)
    assert(w == owner and priority == false and key == "N")
    override = action
end
''')
lua.execute((root / 'Bindings.lua').read_text())
lua.execute('''
owner.callback(owner, "PLAYER_LOGIN")
assert(override == "WARSCAPE_TOGGLE_SKILLS")
owner.callback(owner, "UPDATE_BINDINGS")
assert(override == "WARSCAPE_TOGGLE_SKILLS")
baseAction = "TOGGLEWORLDMAP"
owner.callback(owner, "UPDATE_BINDINGS")
assert(override == nil) -- preserve a custom N
baseAction = ""; owner.callback(owner, "UPDATE_BINDINGS")
assert(override == nil) -- preserve an intentionally unbound N
baseAction = "TOGGLETALENTS"; addonKey = "CTRL-N"
owner.callback(owner, "UPDATE_BINDINGS")
assert(override == nil) -- explicit addon binding takes priority over default
addonKey = nil; combat = true
local before = clears
owner.callback(owner, "PLAYER_LOGIN")
assert(clears == before and override == nil) -- /reload in combat defers safely
combat = false; owner.callback(owner, "PLAYER_REGEN_ENABLED")
assert(override == "WARSCAPE_TOGGLE_SKILLS")
''')
print('PASS: Lua 5.1 default N override, custom bindings, XML action and combat deferral')
