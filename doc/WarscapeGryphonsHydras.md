# Gryphon through Kurask checkpoint

User confirmed the preceding Stalker/Dark Beast/Dust Devil/Ent/Gargoyle checkpoint working. This batch adds five regular entries/families: **332 entries / 87 families**. New gameplay acceptance is pending.

| Entry | Enemy | Level | Source HP | Cadence |
|---|---|---:|---:|---:|
|902300|Gryphon|95|110|5 ticks|
|902301|Harpie Bug Swarm|46|25|4 ticks|
|902302|Hydra|194|300|6 ticks|
|902303|Infernal Mage|66|60|4 ticks|
|902304|Kurask|106|97|4 ticks|

## Sources and scope

Raw OSRS Wiki pages reviewed 8 November 2026, hashes/source IDs in gryphons_hydras.json:
[Gryphon](https://oldschool.runescape.wiki/w/Gryphon), [Harpie Bug Swarm](https://oldschool.runescape.wiki/w/Harpie_Bug_Swarm), [Hydra](https://oldschool.runescape.wiki/w/Hydra), [Infernal Mage](https://oldschool.runescape.wiki/w/Infernal_Mage), [Kurask](https://oldschool.runescape.wiki/w/Kurask).

Regular representatives only; no boss, superior, quest forms, Slayer training or task gates. Existing source combat profiles, attack cadence and tenfold HP/damage display retained. Poison immunity uses existing behaviour for Kurask. No character migration, permanent player skill drain or new XP system.

Models: native Gryphon935, Silithid Wasp482 as single-insect swarm stand-in, three-headed Hydra62, Defias Pillager2338 as humanoid caster stand-in, FelBeast10193 as horned quadruped Kurask stand-in. M2 assets resolved, native animations/sounds retained. This is not a custom OSRS mesh or visual acceptance result. No client memory-layout code changed.

Hydra starts in a randomly selected Magic/Ranged style and switches after each three emitted attacks, including misses. Cycle state is local to the creature, cleared on Reset; it does not count target damage or carry between respawns. Existing shared spells calculate source Magic/Ranged accuracy and max22. Both spells use a 30-yard carrier without Shoot's minimum-range dead zone. Infernal Mage uses ranged source Magic75 and max8, with no ordinary melee attack.

## Explicit encounter gaps

Gryphon equipped-weight knockback, self-stun/counterattack and Tortugan shields remain deferred. Harpie lit/equipped bug-lantern damage requirement and Firemaking gating remain deferred. Hydra poison ground pools and ordered eye/fang/heart collection are deferred; ring pieces are excluded instead of dropped randomly. Kurask leaf-bladed/broad ammunition/Magic Dart restrictions, rapid regeneration, cannon/thrall immunity and burn handling remain deferred. Normal weapons can hurt Harpies and Kurask in this prototype. Full player ranged/magic/prayer and elemental-weakness support remain existing wider-system limitations.

## Loot policies

Members/no wealth/pre-Legends main tables, explicit residual Nothing probability. Gryphon guarantees Bones and 1-3 feathers; extra10-25 feather roll adds to that guarantee. Three equiprobable guaranteed quantities are expanded separately, retaining the sum distribution rather than replacing it with a uniform11-28 range. Off-task Horn of Plenty1/2500 is independent. Harpies have no invented guaranteed bones. Hydra guarantees one Hydra bones, not the boss's two. Off-task tail1/5001, thrownaxe200-400 at1/10000 and knife200-400 at1/10001 are independent bonus pools; exact source correlation between these prerolls is not established. Task rates excluded. Hydra noted herb and bolt-tip expressions use exact base weights rather than rounded displayed denominators; ordinary herb quantity1-3 is uniform as a documented prototype choice.

Infernal Lava battlestaff1/1000 and dark Mystic boots/hat1/512 each are mutually exclusive prerolls before the ordinary table; Fire ruby1/64 is an independent bonus. Kurask triples one selected herb type rather than choosing independent identities. Leaf sword1/384, light Mystic top1/512 and leaf battleaxe1/1026 use independent bonus pools; exact source correlation is not established. Kurask head is deferred because the current bonus registry has three pools; no random substitute is added. Quest/task/area tertiary, clues and ensouled heads excluded. Most items remain collectibles, including leaf weapons and horns; existing stacked item definitions are not silently changed to equipment.

## In-game acceptance

Restart the verified Wrath client for new item/spell records. Use `.gm off`, then `.npc add temp loot 902300` through902304, one at a time on ordinary open walkable ground. No special teleport is required for these temporary summons. Check appearance, retaliation, HP, cadence and loot. Gryphon/Harpie/Kurask have source melee; Hydra should cast three Magic attacks then three Ranged, with either opening style; Infernal should cast fire bolts without melee. Check Hydra from close and distant positions, evade/reengage and respawn. It has no poison pool in this checkpoint.

Defeat multiple enemies: Gryphon always Bones plus feathers, Hydra one Hydra bones, Infernal/Kurask Bones. Harpie has no guaranteed Bones. Rare items are not guaranteed by a small sample. Relog to check existing XP, inventory and Coins. Kurask/Harpie currently accept ordinary weapons. Previous Gargoyle hammer and Ice cooler tests should continue to work. Use `.additem 2131 1` for a verified one-handed testing weapon.

## Operations and rollback

Additive migration2026_11_08_03_world.sql and generated verification specification, through db.py after permissions/status, zero characters, stopped writers and a fresh verified backup. Preserve preexisting world rows, all character skills, inventory and wallets with before/after hashes. Back up previous EXE/PDB, runtime Item/Spell.dbc and client patch outside Git. Require matching build hashes, previous DBC rows/string offsets and unrelated MPQ payloads unchanged; check current startup log bytes only. No configuration/credential or generated runtime assets in Git.

Rollback requires stopped services and coordinated previous binary/DBC/patch. Leave new additive world rows dormant; never remove item definitions while players hold new loot. Full world restore requires separate review and can overwrite subsequent changes; no character restore is needed. Backup restore has not been tested.

Deployment 8 November 2026: migration applied/verified;136 Python tests, isolated Debug C++ checks and RelWithDebInfo build passed. Backup C:\WarscapeBackups\world_20261108T005430_088146Z_b26efaf5.sql, SHA256 d8440a3c3b99d5d3f2644ee25d96cca475823813809e60e928be0594668295e2; restore not tested. Previous runtime files: C:\WarscapeBackups\Gryphons-20261108-deploy. Deployed EXE/PDB match build;34 item and three spell records append correctly, old DBC rows and unrelated MPQ content preserved. Five native M2 assets resolve. Both services listening and world ready without new batch ID errors; existing native base-stat/item900500/Mining warnings remain. Existing world records, XP, inventory and wallets preserved. User gameplay acceptance remains pending.

User acceptance 8 November 2026: all five families confirmed working. Deferred requirements, pools, ring pieces and weight mechanics are not inferred tested.
