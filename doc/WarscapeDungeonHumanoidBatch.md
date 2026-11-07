# Dungeon and humanoid checkpoint: 39 variants, eight families

## Scope

The user confirmed the preceding 28-variant coastal batch with correct drops and
requested the next large batch. This checkpoint adds 39 entries across eight
families, for 95 entries across 23 families. There are no permanent world spawns.
The previous 56 accepted entries and all earlier immutable data/SQL/specs remain
unchanged. Dwarves have 13 source variants with distinct source IDs, stats, HP,
melee defence and/or cadence, although they share a stock WoW model. Skeleton
appearance variants with identical stats and loot are grouped under nine
level/loot profiles. Zombie appearance IDs are grouped into three combat tiers.
The registry does not manufacture entries for unused or duplicate animation states.

## Primary sources and policies

Reviewed OSRS Wiki primary pages, retrieval date and raw SHA-256 provenance are
recorded in `contrib/warscape/enemies/dungeon_humanoids.json`:
[Dwarf](https://oldschool.runescape.wiki/w/Dwarf),
[Pirate](https://oldschool.runescape.wiki/w/Pirate),
[Skeleton](https://oldschool.runescape.wiki/w/Skeleton),
[Zombie](https://oldschool.runescape.wiki/w/Zombie),
[Ghost](https://oldschool.runescape.wiki/w/Ghost),
[Ghoul](https://oldschool.runescape.wiki/w/Ghoul),
[Hellhound](https://oldschool.runescape.wiki/w/Hellhound),
[Minotaur](https://oldschool.runescape.wiki/w/Minotaur), and shared Gem drop table,
Module:GemDropLines and Template:HerbDropLines. Raw pages were retrieved on
7 November 2026, rather than using older cached summaries of merged variants.

Members-world ordinary main loot is used for all players, without membership
requirements, Ring of Wealth or quest/faction modifiers. The shared gem-table
policy remains surface Nature talisman and pre-Legends quest state. The mega-rare
branch therefore produces a Nature talisman. Tertiary, clues, champion scrolls,
quest bones, ensouled heads and Wilderness/Catacombs/Slayer tertiary tables remain
deferred. Named collectible equipment still has no gameplay use or stat bonuses.
Noted OSRS items are stackable collectibles here; no bank-note conversion is added.

Specific source decisions:

- Dwarf level 20 is deferred: its variant-specific coin chances are only rounded
  in the reviewed notes. The other 13 variants retain their exact source stats,
  attack intervals (4/5/6 ticks), negative/positive bonuses and standard main loot.
  Missing respawn fields use 25 ticks as metadata; worker level 7 keeps 50.
- Pirates exclude Cabin Fever quest combat. Five remaining location variants use
  the ordinary table, with the source 23/26 levels and 4/5-tick cadences.
- Skeleton Plain profiles drop Bones only. Unarmed and Armed profiles retain
  their separate rune/ammunition/herb/coin/gem tables. The source's armed Air rune
  quantity `12,15` becomes two equally weighted discrete outcomes, not 12-15.
  Equal weighting is an authoring assumption because the source gives no split.
  Source 77 is the armed level-25 profile referenced by the Bronze-bar footnote.
  Level-29 Skeleton has no Slayer-XP field; HP is stored as reference metadata.
- Zombies 13 and 24 use members coin rates 11/128 and 10/128 for ten Coins,
  alongside 25/128 and 30/128 herb branches. Zombie 18 drops only Bones. F2P coin
  substitutions are not stacked on top of members herb drops.
- Ghosts have no ordinary loot. Ghouls always drop Bones. No undead special weapon,
  Prayer, spectral or elemental-weakness mechanics are implied by their visuals.
- Hellhounds always drop Vile ashes, not Bones. Regular 122 has Death rune outcomes
  10 at 6/50, 20 at 3/50 and 50 at 1/50. Smouldering stone is 1/32768 regular,
  absent from GWD 127, and 1/16384 Wilderness Cave 136. The reviewed source does
  not state rune/stone correlation: this pack explicitly assumes independent
  regular rolls. A composed exact table preserves both marginal probabilities
  and allows runes plus stone. Faction protection and weak-burn immunity are not
  implemented; GWD remains hostile under native WoW aggression.
- Minotaurs 12 and 27 retain -21/-10 melee defences and the members 101-slot table.
  F2P-only Rune essence is excluded; Pure essence is the members outcome. The
  listed members rates plus the gem branch account for 100/101 of the roll.
  The remaining 1/101 is explicitly treated as empty, an assumption rather than
  a claimed Wiki fact. Right skull half is a 3/101 collectible without sceptre
  assembly or Diary conversion mechanics. The unused level-19 form is excluded.
- Shades are deferred because flat-armour and unusual XP rules need additional
  support. This batch does not silently treat them as ordinary melee enemies.

## Entries

| Entry | Variant | Combat | Displayed HP | Source max hit | Attack ticks | Loot |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 901100 | Dwarf (OSRS variant_1) | 10 | 160 | 2 | 5 | Bones + main roll |
| 901101 | Dwarf (OSRS variant_3) | 11 | 160 | 2 | 5 | Bones + main roll |
| 901102 | Dwarf (OSRS variant_4) | 11 | 160 | 2 | 5 | Bones + main roll |
| 901103 | Dwarf (OSRS variant_5) | 10 | 120 | 2 | 5 | Bones + main roll |
| 901104 | Dwarf (OSRS variant_6) | 11 | 160 | 2 | 4 | Bones + main roll |
| 901105 | Dwarf (OSRS variant_7) | 11 | 160 | 2 | 4 | Bones + main roll |
| 901106 | Dwarf (OSRS variant_8) | 11 | 160 | 2 | 4 | Bones + main roll |
| 901107 | Dwarf (OSRS variant_9) | 11 | 160 | 2 | 6 | Bones + main roll |
| 901108 | Dwarf (OSRS variant_10) | 10 | 120 | 2 | 6 | Bones + main roll |
| 901109 | Dwarf (OSRS variant_11) | 11 | 180 | 2 | 4 | Bones + main roll |
| 901110 | Dwarf (OSRS variant_12) | 11 | 130 | 2 | 4 | Bones + main roll |
| 901111 | Dwarf (OSRS variant_13) | 7 | 100 | 2 | 4 | Bones + main roll |
| 901112 | Dwarf (OSRS variant_14) | 11 | 180 | 2 | 4 | Bones + main roll |
| 901113 | Pirate (OSRS brimhaven) | 23 | 200 | 3 | 5 | Bones + main roll |
| 901114 | Pirate (OSRS port_sarim) | 23 | 200 | 3 | 4 | Bones + main roll |
| 901115 | Pirate (OSRS pirates_cove) | 23 | 200 | 3 | 4 | Bones + main roll |
| 901116 | Pirate (OSRS ice_dungeon) | 26 | 230 | 4 | 5 | Bones + main roll |
| 901117 | Pirate (OSRS piscarilius) | 23 | 200 | 3 | 4 | Bones + main roll |
| 901118 | Skeleton (OSRS unarmed_21) | 21 | 240 | 3 | 4 | Bones + main roll |
| 901119 | Skeleton (OSRS plain_21) | 21 | 240 | 3 | 4 | Bones |
| 901120 | Skeleton (OSRS unarmed_22) | 22 | 290 | 3 | 4 | Bones + main roll |
| 901121 | Skeleton (OSRS plain_22) | 22 | 290 | 3 | 4 | Bones |
| 901122 | Skeleton (OSRS armed_25) | 25 | 170 | 4 | 4 | Bones + main roll |
| 901123 | Skeleton (OSRS plain_25) | 25 | 170 | 4 | 4 | Bones |
| 901124 | Skeleton (OSRS plain_29) | 29 | 300 | 3 | 4 | Bones |
| 901125 | Skeleton (OSRS armed_45) | 45 | 590 | 5 | 4 | Bones + main roll |
| 901126 | Skeleton (OSRS plain_45) | 45 | 590 | 5 | 4 | Bones |
| 901127 | Zombie (OSRS regular_13) | 13 | 220 | 2 | 4 | Bones + main roll |
| 901128 | Zombie (OSRS regular_18) | 18 | 240 | 2 | 5 | Bones |
| 901129 | Zombie (OSRS regular_24) | 24 | 300 | 3 | 5 | Bones + main roll |
| 901130 | Ghost (OSRS level_1) | 19 | 250 | 2 | 4 | None |
| 901131 | Ghost (OSRS level_2) | 76 | 750 | 7 | 4 | None |
| 901132 | Ghost (OSRS level_3) | 77 | 800 | 7 | 4 | None |
| 901133 | Ghoul (OSRS regular_42) | 42 | 500 | 5 | 4 | Bones |
| 901134 | Hellhound (OSRS level_1) | 122 | 1160 | 11 | 4 | Vile ashes + main roll |
| 901135 | Hellhound (OSRS level_2) | 127 | 1160 | 13 | 4 | Vile ashes |
| 901136 | Hellhound (OSRS level_3) | 136 | 1500 | 13 | 4 | Vile ashes + main roll |
| 901137 | Minotaur (OSRS level_1) | 12 | 100 | 2 | 4 | Bones + main roll |
| 901138 | Minotaur (OSRS level_2) | 27 | 220 | 3 | 4 | Bones + main roll |

## Native models and equipment

The pack follows the supplied model directions: Ironforge dwarf, Defias/Bloodsail
pirates, classic skeletons, Plaguelands zombies, spectral Ghost, classic Scourge
ghoul, felhound and male tauren. Ghost 11649 uses a shrouded spectral silhouette
as a stand-in rather than a custom translucent human from Karazhan. Minotaur uses
Grimtotem tauren displays with stock clothing and an axe; custom OSRS proportions
are not implied. Model paths are asserted against installed client DBCs/M2 files.
All new displays have native stand/walk/run/attack/death sequences. Audio and
actual appearance remain manual acceptance items.

22 native `creature_equip_template` rows add Mining Picks to Dwarves, swords to
Pirates, sword/shield to the two Armed Skeleton profiles, and axes to Minotaurs.
The model checker validates each weapon/shield against Item.dbc and native hand
inventory types. `Creature::InitEntry` already loads default equipment for summons.
Equipment is presentation only: monster combat continues to use the Warscape
profile, source cap, tick speed and directional defence; no WoW weapon stats
replace source values. Existing equipment templates are untouched.

40 new collectibles are 902075-902114. Existing item identities, including Bones,
Coins, ores, herbs and gems, are reused. Client Item.dbc and server Item.dbc append
new records while preserving old rows/strings and unrelated locale-patch payloads.
No client executable, object field, memory-layout or lifetime code changes occur.

## Implementation, checks and deployment

`loot_tables.py` provides exact rational authoring helpers for herb/gem tables,
independent bonuses and integer weights. It has no network access or runtime RNG.
Runtime still selects a single native loot template once per death, then native
loot handles quantities/bundles. New generated headers include the reviewed data.
`family_catalogue.py` adds validated three-slot optional equipment records and
collision-checked additive SQL/postconditions. Runtime denominators must fit
uint32; invalid equipment shapes, probability sums and overflow are rejected.
Earlier SQL/specifications reproduce unchanged.

Run:

```text
py -3.13 contrib/warscape/enemies/run_checks.py
<asset-python> contrib/warscape/enemies/check_models.py --client <game>
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

There are 38 Python tests plus isolated C++ checks. The new cases verify members
coin/herb substitutions, equipment generation/guards, empty Ghost loot, separate
Skeleton tables, discrete rune quantities, Hellhound rune/stone marginals,
Minotaur source gap/negative defence and probability overflow rejection. C++
enumerates every new pool, including all 1,638,400 regular-Hellhound rolls, and
retains prior Goblin/animal source-cap/defence/loot regression checks.

Migration `2026_11_07_04_world.sql` inserts eight families, 39 templates/profiles,
39 speeds, 40 items, 22 equipment rows and native loot outcomes. It makes no schema
or character changes; metadata updates target only newly inserted entries.
Creature entries/profiles are 901100-901138 / 1100-1138; families are 16-23.
Native outcome reservations are 906000-909800, in steps of 100. All ranges are
collision checked against prior releases and the actual database before applying.
Use `db.py` with inspected permissions/status, stopped writers and a fresh verified
backup, then verify all five enemy migrations. Never rewrite an applied hash.

## Manual acceptance

Restart the stock client to load new collectible records, then:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901100
.rs enemy
```

Select the NPC before `.rs enemy`. Spawn one at a time using the table. Temporary
loot-enabled corpses remain 30 seconds. Confirm stats, HP, cadence, aggression,
model/scale, visible weapons/shields, attack/death animations and loot.

- Dwarves 901100/901104/901107: compare 5/4/6-tick attacks and visible pickaxes;
  Bones plus ordinary main roll, which may add no extra item.
- Pirate 901113: sword, Bones and main loot; 901116 is the hostile level-26 tier.
- Skeleton 901119: Bones only; 901118 has Unarmed main loot; 901122/901125 have
  Armed main loot and visible sword/shield. These source profiles differ.
- Zombies 901127/901129 have main loot; 901128 has only Bones.
- Ghosts 901130-901132 have no ordinary loot. Ghoul 901133 has Bones.
- Hellhounds 901134-901136 have Vile ashes. Regular 122 may additionally drop
  10/20/50 Death runes; GWD 127 has ashes only. Stone chances are too rare for a
  small gameplay sample to establish, and are verified mathematically in tests.
- Minotaurs 901137/901138: tauren/axe stand-ins, Bones plus main roll; confirm
  the selected family/stats and negative melee defences in `.rs enemy`.
- Relog with new loot and check inventory/skill persistence. Recheck a previous
  accepted enemy for regression. Some upper tiers can quickly kill low-level PCs.

New gameplay acceptance is pending. Builds, model audits, SQL checks and startup
are not proof of visual quality, audio, collision or combat feel. There are no
permanent populations, Slayer assignments or tertiary systems in this checkpoint.

## Rollback

Keep the verified world and runtime/client backups outside Git. Export integrity
is not a successful restore test. Do not routinely restore a world backup or
remove item records that players can own. Preserve player inventory/XP and all
prior/new client item rows. Stop using the new temporary spawns if needed; no
persistent spawns were installed. Prepare a new corrective migration or reviewed
compatible binary/catalogue; never edit applied SQL/history to reverse a release.

## Deployment record - 7 November 2026

38 Python tests and isolated C++ checks passed. The RelWithDebInfo worldserver
build completed successfully. The model/equipment audit passed for all new
entries. Both servers reached ready state, loading 98 monster profiles,
100 creature definitions and 96 attack speed overrides. The catalogue query
confirmed 95 entries in 23 families and 22 new equipment rows. All five enemy
migrations passed postconditions, with 36 applied/6952 archived and none pending.
No errors referencing new creature, item or loot IDs appeared at startup.
Pre-existing Mining script and item-900500 warnings remain outside this scope.

No characters were online and the stock client was closed before deployment.
The installed worldserver/PDB, server Item.dbc and merged locale patch matched
build/prepared hashes. All 40 new client/server item rows matched SQL displays;
every prior item row/string and unrelated MPQ payload was compared and preserved.
Only the previous 56 entries have user gameplay acceptance; these 39 remain pending.

Fresh verified world backup (integrity checked; restore not tested):
`C:\WarscapeBackups\world_20261107T081052_039324Z_fea3ee06.sql`.
Previous binary/PDB, server DBC and client patch:
`C:\WarscapeBackups\Dungeon-20261107-deploy`.
Prepared new assets: `C:\WarscapeBackups\Dungeon-20261107-prepared`.
