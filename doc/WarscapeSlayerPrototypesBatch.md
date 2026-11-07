# Slayer and melee enemy prototypes: 70-variant checkpoint

The user confirmed the preceding 205 catalogue entries working with drops and
requested a larger batch. This release adds 70 entries across 14 new families
and extends Giants and Demons: **275 entries / 50 families** in total.
The new entries are pending manual acceptance. No permanent spawns were added.

## Source and implementation policy

The [OSRS Wiki Bestiary](https://oldschool.runescape.wiki/w/Bestiary) and individual
pages below are the factual sources. Reviewed JSON contains source NPC IDs,
retrieval date (7 November 2026), raw-page SHA-256, combat levels, six stats,
bonuses, source maximum hits, attack ticks, exact loot weights and provenance.
Models follow Kieran's directions where stock assets permit; the table gives
actual display IDs. Native WoW animations/audio are inherited; gameplay and
appearance are manual checks, not established by asset inspection.

These are baseline melee prototypes. Warscape has **no Slayer skill**. Source
requirements are stored in the new unsigned `source_slayer_level` metadata column
and shown by `.rs enemy`; no Slayer gates, training or task rewards are invented.
The field defaults to zero for every preceding entry. Existing character XP,
item identities, equipment effects and accepted combat policies are preserved.
New loot items remain stack-200 collectibles; weapons, keys, seeds and quest
pieces do not gain functional gameplay merely by becoming loot.

Magical melee (`m_melee`, fitting the existing eight-character SQL field) uses
melee cadence/accuracy and the player's Magic equipment defence. Its effective
defence level is `floor(0.7 * Magic) + floor(0.3 * Defence)`, before the existing
+8 offset. See [Magical melee](https://oldschool.runescape.wiki/w/Magical_melee)
and the Wiki calculator's [NPCVsPlayerCalc implementation](https://github.com/weirdgloop/osrs-dps-calc/blob/main/src/lib/NPCVsPlayerCalc.ts).
This adds no spell-casting AI or prayer mechanics; earlier melee styles retain
their defence lanes. The existing Warscape attack/HP/damage scale remains.

Exact nested probabilities can exceed 32-bit totals. Runtime weights, totals and
selection rolls now use unsigned 64-bit integers. Existing small pools retain
their previous RNG path. Large pools combine two native 32-bit draws and reject
the incomplete remainder range before modulo, avoiding biased/clamped chances.
The authoring helper refuses probabilities beyond the 64-bit bound. Full general
seed tiers and the 1090-weight rare seed table use exact module weights rather
than rounded displayed odds. Existing release SQL/specifications remain frozen.

## Entries

Use one temporary NPC at a time. HP is displayed at the existing tenfold scale.
Slayer levels below are source references, not enforced requirements.

| Entry | Family / source variant | Combat level | Slayer reference | Display | Guaranteed loot |
| --- | --- | ---: | ---: | ---: | --- |
| 901400 | Ankou / stronghold_75 | 75 | 0 | 3942 | 1 Bones |
| 901401 | Ankou / stronghold_82 | 82 | 0 | 3942 | 1 Bones |
| 901402 | Ankou / stronghold_86 | 86 | 0 | 3942 | 1 Bones |
| 901403 | Ankou / catacombs_95 | 95 | 0 | 3942 | 1 Bones |
| 901404 | Ankou / cemetery_86 | 86 | 0 | 3942 | 1 Bones |
| 901405 | Tortoises / unridden_79 | 79 | 0 | 1244 | 1 Bones |
| 901406 | Dagannoth / melee_2 | 92 | 0 | 1246 | 1 Bones |
| 901407 | Dagannoth / melee_3 | 74 | 0 | 1246 | 1 Bones |
| 901408 | Dagannoth / melee_4 | 92 | 0 | 1246 | 1 Bones |
| 901409 | Abyssal Demons / regular_1 | 124 | 85 | 14255 | 1 Abyssal ashes |
| 901410 | Abyssal Demons / regular_2 | 124 | 85 | 14255 | 1 Abyssal ashes |
| 901411 | Abyssal Demons / regular_3 | 124 | 85 | 14255 | 1 Abyssal ashes |
| 901412 | Terror Dogs / level_100 | 100 | 40 | 1913 | 1 Bones |
| 901413 | Terror Dogs / level_110 | 110 | 40 | 1913 | 1 Big bones |
| 901414 | Cave Bugs / level_6 | 6 | 7 | 7470 | None |
| 901415 | Cave Bugs / level_96 | 96 | 7 | 7470 | None |
| 901416 | Jellies / regular_1 | 78 | 52 | 681 | None |
| 901417 | Jellies / regular_2 | 78 | 52 | 767 | None |
| 901418 | Jellies / regular_3 | 78 | 52 | 11138 | None |
| 901419 | Jellies / regular_4 | 78 | 52 | 1145 | None |
| 901420 | Jellies / regular_5 | 78 | 52 | 767 | None |
| 901421 | Jellies / regular_6 | 78 | 52 | 1145 | None |
| 901422 | Jellies / warped_112 | 112 | 52 | 767 | None |
| 901423 | Bloodvelds / normal_1 | 76 | 50 | 1913 | 1 Vile ashes |
| 901424 | Bloodvelds / normal_2 | 81 | 50 | 1913 | 1 Vile ashes |
| 901425 | Bloodvelds / mutated_123 | 123 | 50 | 1913 | 1 Vile ashes |
| 901426 | Icefiends / level_13 | 13 | 0 | 5561 | None |
| 901427 | Icefiends / level_18 | 18 | 0 | 5561 | None |
| 901428 | Pyrefiends / pyrefiend_1 | 43 | 30 | 4449 | 1 Fiendish ashes |
| 901429 | Pyrefiends / pyrefiend_2 | 48 | 30 | 4449 | 1 Fiendish ashes |
| 901430 | Pyrefiends / pyrelord_1 | 60 | 30 | 1405 | 1 Fiendish ashes |
| 901431 | Pyrefiends / pyrelord_2 | 60 | 30 | 1405 | 1 Fiendish ashes |
| 901432 | Kalphites / worker_28 | 28 | 0 | 7470 | None |
| 901433 | Molanisks / active_51 | 51 | 39 | 7898 | 1 Bones |
| 901434 | Vampyres / feral_1 | 61 | 0 | 31025 | 1 Vampyre dust |
| 901435 | Vampyres / feral_2 | 64 | 0 | 31026 | 1 Vampyre dust |
| 901436 | Vampyres / feral_3 | 64 | 0 | 31025 | 1 Vampyre dust |
| 901437 | Vampyres / feral_4 | 70 | 0 | 31026 | 1 Vampyre dust |
| 901438 | Vampyres / feral_5 | 72 | 0 | 955 | 1 Vampyre dust |
| 901439 | Vampyres / feral_6 | 77 | 0 | 31026 | 1 Vampyre dust |
| 901440 | Vampyres / feral_7 | 100 | 0 | 31025 | 1 Vampyre dust |
| 901441 | Vampyres / feral_8 | 130 | 0 | 31026 | 1 Vampyre dust |
| 901442 | Dragons / baby_green_dragon_0_1 | 48 | 0 | 6291 | 1 Baby dragon bones |
| 901443 | Dragons / baby_green_dragon_0_2 | 48 | 0 | 6291 | 1 Baby dragon bones |
| 901444 | Dragons / baby_green_dragon_0_3 | 48 | 0 | 6291 | 1 Baby dragon bones |
| 901445 | Dragons / baby_blue_dragon_0_1 | 48 | 0 | 6293 | 1 Baby dragon bones |
| 901446 | Dragons / baby_blue_dragon_0_2 | 48 | 0 | 6293 | 1 Baby dragon bones |
| 901447 | Dragons / baby_blue_dragon_0_3 | 48 | 0 | 6293 | 1 Baby dragon bones |
| 901448 | Dragons / baby_blue_dragon_1_1 | 48 | 0 | 6293 | 1 Baby dragon bones |
| 901449 | Dragons / baby_blue_dragon_1_2 | 48 | 0 | 6293 | 1 Baby dragon bones |
| 901450 | Dragons / baby_red_dragon_0_1 | 48 | 0 | 6290 | 1 Baby dragon bones |
| 901451 | Dragons / baby_red_dragon_0_2 | 48 | 0 | 6290 | 1 Baby dragon bones |
| 901452 | Dragons / baby_red_dragon_0_3 | 48 | 0 | 6290 | 1 Baby dragon bones |
| 901453 | Dragons / baby_black_dragon_0_1 | 83 | 0 | 6288 | 1 Baby dragon bones |
| 901454 | Dragons / baby_black_dragon_0_2 | 83 | 0 | 6288 | 1 Baby dragon bones |
| 901455 | Giants / hill_0_1 | 28 | 0 | 12813 | 1 Big bones |
| 901456 | Giants / hill_0_2 | 28 | 0 | 12813 | 1 Big bones |
| 901457 | Giants / hill_0_3 | 28 | 0 | 12813 | 1 Big bones |
| 901458 | Giants / hill_0_4 | 28 | 0 | 12813 | 1 Big bones |
| 901459 | Giants / hill_0_5 | 28 | 0 | 12813 | 1 Big bones |
| 901460 | Giants / hill_0_6 | 28 | 0 | 12813 | 1 Big bones |
| 901461 | Giants / hill_1_1 | 28 | 0 | 12813 | 1 Big bones |
| 901462 | Giants / hill_2_1 | 28 | 0 | 12813 | 1 Big bones |
| 901463 | Giants / hill_2_2 | 28 | 0 | 12813 | 1 Big bones |
| 901464 | Giants / hill_2_3 | 28 | 0 | 12813 | 1 Big bones |
| 901465 | Giants / hill_3_1 | 28 | 0 | 12813 | 1 Big bones |
| 901466 | Giants / hill_3_2 | 28 | 0 | 12813 | 1 Big bones |
| 901467 | Giants / hill_3_3 | 28 | 0 | 12813 | 1 Big bones |
| 901468 | Demons / imp_1 | 2 | 0 | 1185 | 1 Fiendish ashes |
| 901469 | Demons / imp_2 | 7 | 0 | 1185 | 1 Fiendish ashes |

## Reviewed source choices and limits

- Ankou: separate Stronghold 75/82/86, Catacombs 95 and Forgotten Cemetery 86
  tables. Stronghold includes the left skull half; Catacombs does not. Cemetery
  uses Dark fishing bait and its own Law rune/coin/robe distribution. Level-98
  Wilderness Slayer Cave is deferred where source rates/quantity ranges differ.
- Tortoise: unridden melee form only. Preserve paired loot: general seeds also
  give 12-23 Steel arrows, herbs also give 20-59 Cabbages. Standalone arrows and
  cabbage retain the remaining half of each published marginal. A separate direct
  Cabbage seed outcome remains independent of the general-seed paired branch.
- Dagannoth: three melee forms; ranged level-74 form is deferred.
- Abyssal demons: standard, Catacombs and Wilderness loot forms. Whip 1/512 and
  dagger 1/32000 are modeled as independent bonus rolls composed with the normal
  table. Their mutual correlation is an explicit assumption where the page gives
  separate marginals. Both marginals are exact; they may occur together. Largest
  denominator is 17,179,869,184,000. Teleport AI and source Slayer-85 gating are
  deferred. Abyssal ashes are guaranteed.
- Terror dogs: levels 100/110; Cave bugs: 6/96. Source Slayer levels are metadata.
- Jellies: six regular appearances and Warped Jelly. Wilderness variants deferred.
  Jellies/Bloodvelds/Icefiends/Pyrefiends/Pyrelords use magical melee.
- Bloodvelds: regular, GWD and Mutated. The footnoted Big bones outcomes also
  contain normal Bones: preserve those pairs and remove the separately displayed
  10/128 normal-Bones marginal from the main-slot accounting. Vile ashes remain
  guaranteed. No superior spawning or task-only bonuses.
- Kalphite: non-poisonous Worker only. Listed main slots total 127/128; the missing
  1/128 is explicit empty loot, rather than renormalizing the listed odds.
- Molanisk: pre-activated combat prototype, without Slayer-bell activation AI.
  Its source Nothing 1/128 is already included and is not added a second time.
- Feral Vampyres: eight source stat variants. The two converted forms give only
  Vampyre dust; other forms use the normal table. The level-130 source omits
  Ranged, so zero is used, matching the level-100 Temple Trekking form. Bite-heal
  and trek encounter AI are deferred; no special weapon gate is needed for Feral
  Vampyres. Blood Elf displays are humanoid stand-ins, not custom vampire models.
- Baby dragons: 3 green, 5 blue, 3 red and 2 black source variants. Source attacks
  are melee; no adult dragonfire/poison is introduced. Baby dragon bones only.
  Baby-blue source respawn prose is recorded as the first 30-tick baseline;
  location-specific 15-tick Taverley timers need placement-specific handling.
- Hill Giants: 13 source variants in existing family 31, preserving Plateau
  equipment/loot differences. Use the ordinary non-Wilderness 1/128 Giant key
  policy, completing the listed 127/128 table. No Wilderness key multiplier,
  Obor access, or conditional F2P loot rules. Big bones are guaranteed.
- Imps: level 2 and GWD 7, in existing family 32. Fiendish ashes guaranteed;
  escape/teleport AI is deferred.
- Native hostile/neutral factions and AggressorAI remain. OSRS aggression level
  cutoffs/tolerance, original quests, tertiary clues, task-only drops and encounter
  conditions are not implemented. N/A source respawns retain prototype metadata
  defaults; no permanent spawn timers are claimed.
- Nechryaels remain deferred: 5,000 Coins exceed the current native 18-slot capacity
  at the preserved 200 stack size. Gryphon paired-feather handling and Cyclops
  defender progression also remain separate work. No drop quantity is clamped.

The new native Coin reference 970100 produces fixed 200-stacks. Existing 970000
is unchanged. The worst Abyssal 3,000-Coin outcome plus ash, whip and dagger uses
exactly 18 slots. Quantity ranges stay native; reference use is restricted to
fixed large quantities, and the compiler rejects slot overflow.

## Automated verification and deployment

```powershell
py -3.13 contrib/warscape/enemies/run_checks.py
.\work\enemies-venv\Scripts\python.exe contrib/warscape/enemies/check_models.py --client 'C:\Wrath of the Lich King'
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

69 Python tests and isolated Debug C++ assertions passed. Coverage includes new
and preceding releases, exact rare marginals and paired loot, 64-bit bounds and
rejection sampling, first/last CDF boundary for every new outcome, separate Magic
level truncation, family reference collision guards, additive schema/defaults,
slot budgets, and unchanged immutable release generation. Native model/equipment
checks and full RelWithDebInfo worldserver build passed. No custom-client memory
layout, object allocations or executable code changed.

Migration `2026_11_07_07_world.sql` SHA-1
`D01D84B96CD352AD4FE3B4EBCE6917EA55D4C5A7` adds one metadata column, 14 families,
70 profiles/definitions/speeds/variants, 13 equipment rows, 85 collectible items,
one native reference and 6,225 native loot rows. Reviewed preconditions detect ID
collisions/partial application and require existing family identity; postconditions
verify schema attributes and the exact generated records/quantities. Only new
variant rows are updated. No character migration or permanent population changes.

Deployment on 7 November 2026 used `C:\Warscape` and runtime `C:\Warscape\Server`;
the stock `C:\Wrath of the Lich King` client was closed and zero characters were
online. Both servers were stopped. `db.py apply` made a fresh verified backup,
applied the migration, verified its postconditions and recorded the unchanged
hash in native history. Pre/post hashes matched for all earlier records across
ten affected world tables and all character skill XP. No character data was edited.
The verified world backup is:
`C:\WarscapeBackups\world_20261107T125534_744757Z_57946770.sql`
(296,964,655 bytes, 190 tables / 3 views; integrity checked, restore not tested).

Previous binary/PDB, server Item.dbc and merged locale patch:
`C:\WarscapeBackups\SlayerPrototypes-20261107-deploy`.
Prepared assets: `C:\WarscapeBackups\SlayerPrototypes-20261107-prepared`.
All four installed files matched their build/prepared hashes. Every preceding
DBC row/string and unrelated MPQ payload was preserved; all 85 new client/server
item displays matched database values. The client executable/addons/settings
were unchanged. The installed binary includes the pre-existing unrelated
`cs_gobject.cpp` worktree change; that source change is excluded from this commit.

Both servers reached ready state with database connectivity. Startup loaded 278
Warscape profiles, 280 creature definitions and 276 speed overrides. The catalogue
contains 275 entries / 50 families. All eight enemy migration postconditions pass;
world status has 39 applied, 6,952 archived and no pending migrations. Database
outcome 1009131 expands to exactly 18 slots: 3,000 Coins, ash, whip and dagger;
this was SQL/source verification rather than an observed in-game roll. Startup has
no errors referencing the new enemy/item/loot/reference IDs or Slayer column.
Existing Mining script and item-900500 warnings remain unrelated.

## In-game acceptance

Completely close/reopen the stock client to load the new item records. On a GM
character in a clear test area, use:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901416
.rs enemy
```

Select the NPC before `.rs enemy`. Substitute an entry from the table. The command
creates a loot-enabled temporary NPC; corpses remain 30 seconds. Strong enemies
can kill low-level characters. Check model/size, equipment, targeting, aggression,
HP, melee cadence, attack/death animations, stats, combat XP and loot.

1. Ankou 901400 vs 901403/901404: normal Bones and differing source loot tables.
2. Tortoise 901405: Bones and ordinary loot; observe paired arrows/seeds or
   cabbage/herbs if rolled. Dagannoth 901406: Bones and melee attack.
3. Abyssal 901409, Terror dog 901412, Cave bug 901414: ash/Bones/ordinary loot
   respectively. Verify Slayer diagnostics explicitly say reference only.
4. Jelly 901416/Warped 901422, Bloodveld 901423/Mutated 901425, Icefiend 901426
   and Pyrefiend 901428/Pyrelord 901430: magical-melee diagnostic and attacking.
   With otherwise equal stats/gear, Magic resistance should reduce their accuracy;
   hit chance is statistical, so a few hits cannot establish its formula.
5. Worker 901432 (no poison), Molanisk 901433 (pre-activated), Feral 901434 vs
   converted 901435 (dust only). Ensure loot names/icons display properly.
6. Baby green 901442, blue 901445, red 901450 and black 901453: Baby dragon bones.
7. Hill Giant 901455 (Big bones) and Imp 901468 (Fiendish ashes); check Hill Giant
   visible weapon variants and both regular/GWD Imp stats.
8. Relog with new drops and check inventory and skill XP persistence. Recheck one
   earlier accepted enemy. Rare drops and full 3,000-Coin/18-slot outcomes were
   source/math/SQL checked, not forced or observed in-game. User acceptance will
   not by itself establish every rare probability, special AI or interruption path.

## Rollback and recovery

Keep backups private, outside Git. Do not restore or delete loot items players own
as routine rollback. If a regression appears, stop new temporary spawns and use a
reviewed compatible binary or additive corrective migration. Preserve all items,
XP, inventories, metadata and DBC rows. Do not edit applied SQL or its history hash.
An older binary lacks magical-melee/64-bit support and is not a fully compatible
rollback for these entries. Backup restoration requires separate review; it has
not been tested. Existing server restart/configuration practices remain unchanged.

## Wiki page sources

- [Ankou](https://oldschool.runescape.wiki/w/Ankou)
- [Tortoise](https://oldschool.runescape.wiki/w/Tortoise)
- [Dagannoth](https://oldschool.runescape.wiki/w/Dagannoth)
- [Abyssal demon](https://oldschool.runescape.wiki/w/Abyssal_demon)
- [Terror dog](https://oldschool.runescape.wiki/w/Terror_dog)
- [Cave bug](https://oldschool.runescape.wiki/w/Cave_bug)
- [Jelly](https://oldschool.runescape.wiki/w/Jelly)
- [Warped Jelly](https://oldschool.runescape.wiki/w/Warped_Jelly)
- [Bloodveld](https://oldschool.runescape.wiki/w/Bloodveld)
- [Mutated Bloodveld](https://oldschool.runescape.wiki/w/Mutated_Bloodveld)
- [Icefiend](https://oldschool.runescape.wiki/w/Icefiend)
- [Pyrefiend](https://oldschool.runescape.wiki/w/Pyrefiend)
- [Pyrelord](https://oldschool.runescape.wiki/w/Pyrelord)
- [Kalphite Worker](https://oldschool.runescape.wiki/w/Kalphite_Worker)
- [Molanisk](https://oldschool.runescape.wiki/w/Molanisk)
- [Feral Vampyre](https://oldschool.runescape.wiki/w/Feral_Vampyre)
- [Baby green dragon](https://oldschool.runescape.wiki/w/Baby_green_dragon)
- [Baby blue dragon](https://oldschool.runescape.wiki/w/Baby_blue_dragon)
- [Baby red dragon](https://oldschool.runescape.wiki/w/Baby_red_dragon)
- [Baby black dragon](https://oldschool.runescape.wiki/w/Baby_black_dragon)
- [Hill Giant](https://oldschool.runescape.wiki/w/Hill_Giant)
- [Imp](https://oldschool.runescape.wiki/w/Imp)
- [Module:GemDropLines](https://oldschool.runescape.wiki/w/Module:GemDropLines)
- [Gem drop table](https://oldschool.runescape.wiki/w/Gem_drop_table)
- [Module:RareDropLines](https://oldschool.runescape.wiki/w/Module:RareDropLines)
- [Template:HerbDropLines](https://oldschool.runescape.wiki/w/Template:HerbDropLines)
- [Template:UncommonSeedDropLines](https://oldschool.runescape.wiki/w/Template:UncommonSeedDropLines)
- [Module:GeneralSeedDropLines](https://oldschool.runescape.wiki/w/Module:GeneralSeedDropLines)
- [Template:RareSeedDropLines](https://oldschool.runescape.wiki/w/Template:RareSeedDropLines)
- [Drop table](https://oldschool.runescape.wiki/w/Drop_table)
- [Magical melee](https://oldschool.runescape.wiki/w/Magical_melee)
