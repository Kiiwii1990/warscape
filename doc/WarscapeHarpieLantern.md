# Harpie Bug Swarm equipped-lantern requirement

Next pending-work milestone: Harpie902301 now requires Lit bug lantern902586 equipped in the native off-hand slot to take player-owned damage. Source: [Harpie Bug Swarm](https://oldschool.runescape.wiki/w/Harpie_Bug_Swarm), [Slayer equipment](https://oldschool.runescape.wiki/w/Slayer_equipment), reviewed8 November2026. A bag item or different off-hand does not qualify. The new item is already lit for testing; lighting/unlighting, Firemaking33, vendor placement and Kraken interaction remain future work. No player skill system is invented for those requirements.

Configuration is separate in WarscapeEnemyRequirements.h; generic DamageTaken code resolves the attacking player or player owner and checks current off-hand entry. Missing/wrong item zeroes damage before attacker DamageDealt and health loss. It applies to direct damage and periodic damage flowing through native DealDamage, including player-owned pet/summon damage with a resolvable native owner. Free environmental/NPC damage is not restricted by a player equipment check. Three-second creature-local warning throttle prevents chat spam; damage is still rejected every time. No raw item pointer survives the call. Harpie keeps its original source stats, loot and native melee behaviour via shared AI. Other enemies without a rule remain unaffected.

Item902586 is new, stack1, class4/subclass0/InventoryType23; no WoW armour or RS combat bonuses invented. Uses native Everglow Lantern5323 display only, no inherited stats. Original stored player items remain unchanged. Existing Lit bug lantern functionality is not claimed for unrelated items with similar names.

## Manual acceptance

Restart the verified Wrath client. `.gm off`; `.npc add temp loot 902301`.

1. Attack without lantern: Harpie health must not fall from your attacks; chat explains requirement. Check no damage-based XP from rejected attacks.
2. `.additem 902586 1`; keep in bag and repeat: still blocked. Another shield/off-hand also fails.
3. Equip the lantern off-hand, using `.additem 2131 1` Shortsword if replacing a two-handed weapon. Attacks should damage normally and yield unchanged loot on kill.
4. Remove/swap lantern mid-fight: subsequent damage blocked. Reequip: damage resumes. If practical test spell/DOT and pet attacks, including removal after applying a DOT. Those paths are source-reviewed, not live-tested.
5. Relog with lantern equipped and repeat. Confirm another enemy still takes ordinary damage and previous Death spawns/spray work.

No special teleport required for temporary summon; use ordinary open walkable ground. Native lantern model/hold animation is a stand-in; appearance needs user confirmation. No client executable/memory-layout code changed.

## Validation and rollout

139 Python catalogue tests and focused Debug C++ checks passed. C++ cases cover no item, wrong item, correct item and unrelated enemy. RelWithDebInfo worldserver build passed. Unit::DealDamage calls victim DamageTaken before attacker DamageDealt; full player XP acceptance remains manual.

Migration2026_11_08_07_world.sql adds one item and updates only Harpie AI binding. Historical03 verification is superseded for that binding alone; all other assertions retained and old migration files unchanged. Apply through db.py with inspected permissions/status, zero online players, stopped writers, fresh verified backup and matching pre/postconditions. Preserve all existing world rows, Harpie fields except AI, character XP/inventory/wallets. Deploy matching EXE/PDB and one appended Item.dbc row/client patch; no Spell.dbc change.

Rollback requires stopped services and coordinated previous binary/DBC/patch plus reviewed Harpie AI rebind migration. Leave new item definition dormant while players hold lanterns. No character restore. Full world restore needs separate review and backup restore is not tested.

Deployment8 November2026: all checks above passed. Fresh verified backup C:\WarscapeBackups\world_20261108T120919_307435Z_fae9b7b6.sql, restore not tested. Previous runtime files in C:\WarscapeBackups\HarpieLantern-20261108-deploy. Binary/PDB hashes match build; new off-hand DBC row and previous records/MPQ payloads preserved. Both services listening/ready, no new lantern/Harpie script errors. Existing unrelated native warnings remain. Preservation hashes passed. Gameplay, pet/DOT and XP acceptance remain pending.
