# Cave family checkpoint

The user confirmed Killerwatt, Nagua, Aberrant Spectre, Aquanite, Araxyte and Basilisk working with drops. This batch adds seven entries and five families, giving318 entries/77 families. New gameplay acceptance remains pending.

| Entry | Enemy | Level | Source HP |
|---|---|---:|---:|
|902100|Catablepon|49|40|
|902101|Catablepon|64|70|
|902102|Catablepon|68|50|
|902103|Cave crawler|23|22|
|902104|Cave horror worker|80|55|
|902105|Cave slime|23|25|
|902106|Cockatrice|37|37|

## Sources and scope

Reviewed raw OSRS Wiki pages8 November2026: [Catablepon](https://oldschool.runescape.wiki/w/Catablepon), [Cave crawler](https://oldschool.runescape.wiki/w/Cave_crawler), [Cave horror](https://oldschool.runescape.wiki/w/Cave_horror), [Cave slime](https://oldschool.runescape.wiki/w/Cave_slime), [Cockatrice](https://oldschool.runescape.wiki/w/Cockatrice). Stats, source IDs, hashes and exact weighted tables live in cave_families.json. Members main loot; no wealth ring, pre-Legends gem policy. Catablepon F2P-only alternatives excluded. Allotment seeds use Wiki template weights64/32/16/8/4/2/1/1 over128. Missing probability stays Nothing. Guaranteed Bones/Big bones and slime tar1-6 retained; crawler has no guaranteed bones. Black mask main probability1/512; Mystic boots light preroll1/512; Cockatrice head independent1/1000. Clue/quest/ensouled/long-bone tertiary excluded. Loot items are collectibles unless existing functionality already supports them.

Models: Catablepon Kodo1230 scaled.65 (cow/reptile silhouette); crawler Crab979 scaled.6; horror Gorilla3186 scaled.85; slime Lesser Slime12349 scaled.65; Cockatrice Basilisk601 scaled.7. These are stand-ins, including missing Cockatrice wings. Native animations/sounds retained, no custom mesh. Client M2 paths validated; appearance remains manual QA.

## Explicit encounter limits

Source HP/damage use existing tenfold display. Attack cadences and directional melee defences retained. Slayer levels/XP are metadata only; no Slayer gates/training/tasks added. Cave crawler/slime reuse existing25-percent poison after positive melee damage, severity8/3. Slime adjacency/zero-damage application and crawler fast regeneration are deferred. Catablepon temporary Strength drain is deferred. Cave Horror uses existing magic melee lane prototype; exact magical-melee accuracy/scream/AoE, witchwood-icon/prayer protection and attack alternation remain deferred. Cockatrice gaze/temporary drains/mirror enforcement remain deferred, as for current Basilisk. No permanent character XP is reduced to simulate temporary drains. Superior/icy/boss variants are outside this checkpoint.

## Acceptance

Close/reopen the verified Wrath client for new Item.dbc records. Use `.gm off`, then summon one at a time with `.npc add temp loot 902100` through902106. Stay on ordinary open walkable ground. Check name/model, retaliation, cadence, HP and loot. Defeat several of each; rare drops are not guaranteed. Slime should always supply1-6 tar, Catablepon/Cockatrice Bones, horror Big bones. Crawler/slime poison can outlast combat; native dispel/death clears it. Verify existing XP/Coins/inventory after relog.

For a verified one-handed testing weapon use `.additem 2131 1` (native Shortsword, InventoryType13, required level1), unequip the two-handed weapon and equip it with mirror shield902476. Previous suggested900001 was unverified and should be ignored. Native weapon use may require its ordinary proficiency. Mirror shield does not yet enforce gaze protection.

## Operations and rollback

Apply only2026_11_08_01_world.sql with its generated verification spec and db.py after permissions/status, zero players, stopped writers and fresh verified world backup. No character migration. Preserve old executable/PDB, runtime Item.dbc and client patch before deployment. Rollback requires stopped services and a coordinated previous binary/DBC/patch; leave new additive world rows dormant. Do not remove item definitions while characters may hold new items. Restoring the entire world backup requires separate review and could overwrite later world edits; never restore character data for this feature.

Automated validation:132 Python catalogue tests and isolated Debug C++ checks; RelWithDebInfo worldserver build. These establish source/data consistency, not in-game acceptance. No memory-layout-sensitive client code changed.

Deployment8 November2026: migration applied/verified via db.py. Fresh verified backup C:\WarscapeBackups\world_20261108T004021_899491Z_1511ef46.sql (SHA256105574746ca2f5b91e0676c759f234c30c54981e03cdeb647e5095d30411c278; restore not tested). Previous deployment saved under C:\WarscapeBackups\CaveFamilies-20261108-deploy. All existing world rows outside new IDs, character skills, inventory and wallets matched preservation hashes. Runtime EXE/PDB match build; previous Item.dbc records and unrelated MPQ payloads unchanged. Startup ready, ports3724/8085 listening, no new batch ID errors. Existing high-level native base-stat, item900500 and unbound Mining warnings remain. No character database writes or client memory-layout changes.

User acceptance8 November2026: all five families confirmed working. No additional rare-drop, poison or deferred-mechanic acceptance is inferred.
