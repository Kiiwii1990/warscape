"""Exercise default-key overrides without changing user bindings or combat state."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
lua = LuaRuntime()
lua.execute(r'''
base, custom, combat = {O="TOGGLESOCIAL", L="TOGGLEQUESTLOG", C="TOGGLECHARACTER0",
    K="TOGGLECHARACTER1", I="TOGGLELFG", P="TOGGLESPELLBOOK"}, {}, false
owners = {}
local methods = {}
function methods:RegisterEvent(event) self.events[event]=true end
function methods:SetScript(name, fn) self.scripts[name]=fn end
function CreateFrame(_, name)
    local f=setmetatable({name=name, events={}, scripts={}}, {__index=methods})
    owners[#owners+1]=f
    return f
end
function InCombatLockdown() return combat end
function ClearOverrideBindings(owner) owner.overrides={};owner.priorities={} end
function GetBindingAction(key) return base[key] or "" end
function GetBindingKey(action) return custom[action] end
function SetOverrideBinding(owner, priority, key, action)
    owner.overrides[key]=action;owner.priorities[key]=priority
end
''')
lua.execute((ROOT / 'Bindings.lua').read_text())
lua.execute(r'''
local owner=owners[1]
owner.scripts.OnEvent(owner,"PLAYER_LOGIN")
assert(owner.overrides.K=="WARSCAPE_TOGGLE_ATTACK_STYLES")
assert(owner.overrides.I=="WARSCAPE_TOGGLE_PRAYER")
assert(owner.overrides.P=="WARSCAPE_TOGGLE_SPELLBOOK")
assert(owner.overrides.O=="WARSCAPE_TOGGLE_FRIENDS")
assert(owner.overrides.L=="WARSCAPE_TOGGLE_QUESTS")
assert(owner.overrides.C=="WARSCAPE_TOGGLE_EQUIPMENT")
custom.WARSCAPE_TOGGLE_SPELLBOOK="ALT-P"
base.I="MY_CUSTOM_ACTION"
owner.scripts.OnEvent(owner,"UPDATE_BINDINGS")
assert(owner.overrides.K=="WARSCAPE_TOGGLE_ATTACK_STYLES")
assert(owner.overrides.O=="WARSCAPE_TOGGLE_FRIENDS" and owner.overrides.L=="WARSCAPE_TOGGLE_QUESTS")
assert(owner.overrides.C=="WARSCAPE_TOGGLE_EQUIPMENT")
assert(owner.overrides.I=="WARSCAPE_TOGGLE_PRAYER" and owner.priorities.I==true,
    "explicit Prayer shortcut overrides conflicting I bindings")
assert(owner.overrides.P==nil)
combat=true
owner.overrides={sentinel="kept"}
owner.scripts.OnEvent(owner,"UPDATE_BINDINGS")
assert(owner.overrides.sentinel=="kept", "combat defers binding updates")
combat=false
owner.scripts.OnEvent(owner,"PLAYER_REGEN_ENABLED")
assert(owner.overrides.K=="WARSCAPE_TOGGLE_ATTACK_STYLES"
    and owner.overrides.I=="WARSCAPE_TOGGLE_PRAYER" and owner.priorities.I==true)
''')
print('PASS: O/L/C/K/I/P defaults, explicit addon binds, unrelated user actions and combat deferral')
