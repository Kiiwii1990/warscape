# Stalker through Gargoyle checkpoint

User confirmed the preceding five cave families working. This batch adds nine representative entries/five families:327 entries/82 families. Gameplay acceptance pending.

|Entry|Variant|Level|Source HP|
|---|---|---:|---:|
|902200|Juvenile custodian stalker|93|135|
|902201|Mature custodian stalker|117|190|
|902202|Elder custodian stalker|142|250|
|902203|Dark beast|182|220|
|902204|Dust devil, Smoke Dungeon|93|105|
|902205|Dust devil, Catacombs|110|130|
|902206|Ent, Guild|86|75|
|902207|Ent, Wilderness|101|105|
|902208|Gargoyle, upstairs|111|105|

## Sources and loot

Raw pages reviewed8 November2026, with hashes and source IDs in stalkers_gargoyles.json:
[Custodian](https://oldschool.runescape.wiki/w/Custodian_stalker), [Juvenile](https://oldschool.runescape.wiki/w/Juvenile_custodian_stalker), [Mature](https://oldschool.runescape.wiki/w/Mature_custodian_stalker), [Elder](https://oldschool.runescape.wiki/w/Elder_custodian_stalker), [Dark beast](https://oldschool.runescape.wiki/w/Dark_beast), [Dust devil](https://oldschool.runescape.wiki/w/Dust_devil), [Ent](https://oldschool.runescape.wiki/w/Ent), [Gargoyle](https://oldschool.runescape.wiki/w/Gargoyle).

Members/no wealth/pre-Legends main tables. Explicit residual probability stays Nothing. Stalkers guarantee Big bones; broken antlers remain main-table drops. Mature/Elder Antler guard is independent1/800 and1/650. Elder signet is main2/124. Dark bow1/512, Granite maul1/256 and Mystic robe top dark1/512 are conditional prerolls. Dust battlestaff1/4000 is treated as independent: Wiki lists it in addition to a complete128-slot table; source correlation is not established. Dragon chainbody1/32768 shares the source residual slot. Dark beast double herb outcome selects one herb type at quantity2; independent herb identities remain deferred. Task/quest/area-dependent tertiary, clues, ensouled heads and long bones excluded. Most loot remains collectible without gameplay use.

## Combat and explicit limits

Existing tenfold HP/damage display, source attack cadences, directional melee defences, Gargoyle flat armour-2 and poison-immunity behaviour retained. Source Slayer levels/XP are reference metadata; no task gates/training or new XP system. No superior, boss or quest variants.

Custodian models use native Wendigo927 at tiered scales. Bleed is deferred; the Wiki explicitly identifies its listed damage as uncertain. Dark beast uses native horned FelBeast10193 and existing melee-only magic carrier (max8) alongside Crush(max17); exact source attack switching remains prototype. Dust devils use AirElemental5187 and ordinary melee(max8/10); ranged-based melee defence, facemask protection and temporary stat drains are deferred. These are incomplete encounters, not exact OSRS ports. Player permanent XP is never drained to simulate temporary stats.

Ent uses native Ent864, both source combat profiles and poison immunity. **Ent has no combat loot.** OSRS logs/nests require chopping the defeated trunk with Woodcutting-dependent rolls. That harvesting interaction is a separate pending checkpoint; no invented log drop table is substituted.

Gargoyle uses native Gargoyle7533. Existing finisher damage clamp retains one source HP. Reusable Rock hammer902531 uses separate item script: living valid hostile target, range5yards, same map/instance through native distance validation, LOS, not evading and eligible loot ownership; health must be1-8 source HP inclusive. It sets loot credit and executes the normal kill path. Failure does not consume the hammer; duplicate/dead targets are rejected. The existing consumable Ice cooler behaviour is unchanged. Auto-smash perk, thrown/granite hammers and golembane effects deferred. No client memory-layout code changed; native model animations/sounds are stand-ins, with visual QA pending.

## Acceptance steps

Restart the verified Wrath client to load new item/spell records. Use `.gm off`, then `.npc add temp loot 902200` through902208, one at a time on open walkable ground. Check name, appearance, retaliation, attack cadence and drops. Expect Big bones for Stalkers/Dark beast, Bones for Dust devils, no Ent combat loot and no guaranteed Gargoyle bones.

Get `.additem 902531 1`. Reduce Gargoyle to80 displayed HP or lower (8 source HP), right-click the hammer in the bag and target the Gargoyle. Check normal corpse loot and that hammer remains. Test early use above80, dead target, wrong creature, out-of-range and another player's tapped target: no kill, no item loss. Kill another Gargoyle with the same hammer. Verify old Ice coolers still consume normally. For a one-handed weapon use `.additem 2131 1`. No facemask or hammer auto-smash is required elsewhere in this prototype.

## Deployment and rollback

Only additive world migration2026_11_08_02_world.sql; no character schema/data writes. Use db.py permissions/status, stopped writers, zero online characters, fresh verified backup, reviewed preconditions/spec, apply and verify. Deployment backs up executable/PDB, runtime Item/Spell.dbc and client patch before copying matching build/assets. Confirm startup ready and current error-log bytes; historical/native base-stat, item900500 and Mining warnings are separate. Backups are outside Git and restore has not been tested.

Rollback requires stopped services and coordinated previous binary/DBC/client patch; leave additive world rows dormant. Never delete item definitions while players hold new loot. Full world restore needs separate review and could erase subsequent world changes; character restore is unnecessary.

Deployment8 November2026: migration verified/recorded,134 Python tests plus isolated Debug C++ checks and RelWithDebInfo worldserver build passed. Fresh backup C:\WarscapeBackups\world_20261108T004755_507026Z_65b283e1.sql, SHA256463a55e287efa5505da695f82063e6e95ec5ca1ccf62ffc9797423d509be8ea3 (restore not tested). Previous runtime files in C:\WarscapeBackups\Stalkers-20261108-deploy. Deployment hashes match build,17 item/one spell records append correctly, previous DBC/MPQ content preserved. Both servers listening, world ready; no new batch ID/script errors in current startup bytes. Existing native high-level base-stat, item900500 and Mining warnings remain. All preexisting world records/character XP/inventories/wallets match preservation snapshots. No live gameplay checks claimed.
