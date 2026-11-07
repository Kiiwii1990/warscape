# Wildlife batch: 21 variants across five families

## Scope and source decisions

The user confirmed the Cow/Rat release and authorized larger batches on
7 November 2026. This release adds 21 variants across Bats, Bears, Wolves,
Spiders and Scorpions, following Kieran's model list. The catalogue now has
28 entries across eight families. The other 88 family directions remain planned.
No permanent world populations are installed by this release.

Reviewed source snapshots and SHA-256 provenance are in `wildlife.json`:
[Bat](https://oldschool.runescape.wiki/w/Bat),
[Giant bat](https://oldschool.runescape.wiki/w/Giant_bat),
[Black bear](https://oldschool.runescape.wiki/w/Black_bear),
[Grizzly bear](https://oldschool.runescape.wiki/w/Grizzly_bear),
[Wolf](https://oldschool.runescape.wiki/w/Wolf),
[Spider](https://oldschool.runescape.wiki/w/Spider),
[Giant spider](https://oldschool.runescape.wiki/w/Giant_spider), and
[Scorpion](https://oldschool.runescape.wiki/w/Scorpion), retrieved 7 November 2026.

Loot follows ordinary unconditional drops. Wolves use the Wiki's members-world
Wolf bones drop for every Warscape player; there is no account membership gating.
This is explicit policy, not a claim that F2P OSRS wolves drop bones. Bats and
Bears retain their unconditional source drops. Spiders and non-poisonous Scorpions
have no ordinary unconditional loot. Quest items, wilderness bags, clues and
ensouled heads remain conditional/tertiary work and are not granted unconditionally.
The poisonous level-38 Scorpion is deferred until poison mechanics are supported.
The Wiki omits the Arceuus Giant bat respawn value; 35 ticks is recorded as a
judgment call matching the normal Giant bat. It is metadata, not a live spawn timer.

| Entry | Family / subcategory | Combat level | Displayed HP | Source max hit | Guaranteed loot |
| --- | --- | ---: | ---: | ---: | --- |
| 901030 | Bats / regular_6 | 6 | 80 | 1 | Bat bones |
| 901031 | Bats / giant_27 | 27 | 320 | 3 | Bat bones |
| 901032 | Bats / arceuus_27 | 27 | 320 | 3 | Bat bones |
| 901033 | Bears / black_19 | 19 | 250 | 3 | Bones, Bear fur, Raw bear meat |
| 901034 | Bears / grizzly_21 | 21 | 270 | 3 | Bones, Bear fur, Raw bear meat |
| 901035 | Bears / grizzly_42 | 42 | 350 | 5 | Bones, Bear fur, Raw bear meat |
| 901036 | Wolves / stronghold_11 | 11 | 100 | 2 | Wolf bones |
| 901037 | Wolves / stronghold_14 | 14 | 150 | 2 | Wolf bones |
| 901038 | Wolves / regular_25 | 25 | 340 | 3 | Wolf bones |
| 901039 | Wolves / regular_64 | 64 | 690 | 6 | Wolf bones |
| 901040 | Wolves / rellekka_64 | 64 | 690 | 6 | Wolf bones |
| 901041 | Spiders / common_1 | 1 | 20 | 0 | None |
| 901042 | Spiders / underground_pass_1 | 1 | 20 | 1 | None |
| 901043 | Spiders / stronghold_24 | 24 | 220 | 6 | None |
| 901044 | Spiders / giant_2 | 2 | 50 | 1 | None |
| 901045 | Spiders / giant_27 | 27 | 320 | 3 | None |
| 901046 | Spiders / giant_50 | 50 | 500 | 7 | None |
| 901047 | Scorpions / sailing_1 | 1 | 20 | 0 | None |
| 901048 | Scorpions / regular_14 | 14 | 170 | 2 | None |
| 901049 | Scorpions / stronghold_37 | 37 | 370 | 4 | None |
| 901050 | Scorpions / stronghold_59 | 59 | 550 | 6 | None |

## Combat support

Some NPCs have unequal stab/slash/crush defences. The source maximum hit also
sometimes differs from the existing shared Strength formula: Black bear is 3,
level-42 Grizzly is 5, and the Underground Pass Spider is 1 despite its weak
Strength bonus. This release preserves both the published stats and maximum hit.

The combined generated registry adds explicit maximum-hit and directional melee
defence fields, enabled only for these 21 new entries. Player melee accuracy
selects the source defence lane from the player's existing Warscape weapon style.
Their incoming melee attacks also select the player's configured OSRS equipment
defence lane from the source attack style. Explicit zero maximum hits remain zero.
Existing stance calculations, tenfold display scale, configured damage variation,
combat XP/persistence and native attack scheduling remain in use. Unprofiled WoW
armour does not acquire OSRS bonuses automatically.

The seven accepted Goblin/Cow/Rat entries retain their prior formula and equipment
behaviour. The new schema fills their directional source metadata for contributors
but leaves `use_source_combat=0`. Unregistered creatures retain the original path.
Source-cap metadata, like the loot pools, is compiled from reviewed release data;
manual database edits to these new metadata columns are not a runtime reload API.
New source changes require a new migration release and matching build. Other
Warscape monster-profile tuning continues through its existing loader.

`warscape_enemy_variant` now has additive `defence_stab`, `defence_slash`,
`defence_crush` and `use_source_combat` columns. Every prior migration/hash is
preserved. New release inserts explicitly name columns, so future additive columns
do not break their positional layout. `.rs enemy` reports the new source caps and
lanes for these entries, alongside family identity and current loaded stats.

## Appearance

The batch uses native Duskbat 4732, Black bear 719, Grizzly Hills bear 21635,
unsaddled forest/dire wolves 380 and 11415, Duskwood widow 955 and Durotar scorpid
2485. Tier-specific scales and two wolf models distinguish variants. The database
entry called Timber Wolf resolved to a riding model, so unsaddled 380 was selected
instead. All selected model files have native stand/walk/run/attack/death sequences,
verified through the installed client assets. Sounds come from the existing displays;
audio and visual presentation still require in-game acceptance. Bats retain native
flying-looking animations with the current ground-navigation melee AI.

No client executable or memory-layout code changed. Four new collectible Item.dbc
records use existing artwork: 902018 Bat bones, 902019 Bear fur, 902020 Raw bear meat,
902021 Wolf bones. Bones reuses 902000. Collectibles still have no food, Prayer,
crafting or currency functionality. The existing Cow's missing native attack clip
remains a known, accepted-prototype limitation; it was not changed in this batch.

## Data, tooling and verification

`releases.json` lists immutable data packs in order. The compiler validates every
release against the earlier catalogue, checks every frozen SQL/spec artifact, and
builds one combined runtime header. `expansion_release.py` emits additive releases
against the existing family schema, with cross-release entry/profile/item/loot and
family-key collision checks. This avoids rewriting prior applied releases when the
catalogue expands. Future releases add a manifest entry and fresh migration name.

Run:

```text
py contrib/warscape/enemies/run_checks.py
<asset-python> contrib/warscape/enemies/check_models.py --client <game>
```

The source suite has 18 tests plus isolated C++ checks for all prior Goblin rolls,
family membership, explicit zero/non-formula caps, Scorpion defence lanes, empty
loot and safe fallback for accepted/unregistered entries. Native model audits cover
all release packs, retaining the explicit Cow exception. Build the existing
RelWithDebInfo worldserver target for the integrated code.

The additive migration is `2026_11_07_02_world.sql`, with a generated verification
specification under `contrib/warscape/verifications`. Check status/permissions, stop
servers/updaters, and use `db.py apply` with a fresh verified backup. Verify all
three enemy migrations afterward. Templates/profile IDs are 901030-901050 / 1030-1050;
new native outcome IDs reserve 901200 through 901400 in steps of ten. Empty outcomes
have no native loot rows and are deliberately skipped by the loader validation.
Family IDs are 4 Bats, 5 Bears, 6 Wolves, 7 Spiders and 8 Scorpions.

Prepare the four item records with `build_assets.py --catalogue
contrib/warscape/enemies/wildlife.json --client <game> --server-data <runtime-data>
--output <new-staging-directory>`. Back up and deploy matching binary/PDB,
server Item.dbc and merged client locale patch with the client stopped. The active
local targets remain `C:\Warscape\Server` and `C:\Wrath of the Lich King`.
The asset builder preserves every prior row/string and unrelated MPQ payload.
Rollback must preserve inventories and all previously deployed item records;
never rewrite migration history or restore a world backup as routine rollback.

## In-game acceptance

Restart the game to load the four item records. Use one temporary spawn at a time:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901030
.rs enemy
```

Select the NPC before `.rs enemy`. Substitute entries from the table. The `loot`
argument retains eligible temporary corpses for 30 seconds. Confirm family,
source stats, HP, attack cadence, animations/death and the stated loot. Spiders and
Scorpions are intentionally not lootable under the unconditional-drop policy.
Upper-tier Wolves, Spiders and Scorpions can quickly kill a low-level character.

For combat regression, the common level-1 Spider must hit zero; the Underground
Pass Spider may hit 1. Scorpion 37 has stab defence 35 versus slash/crush 15;
compare configured weapon lanes without assuming a small sample proves a hit rate.
Test inventory and skill XP after relog, and recheck accepted Goblin/Cow/Rat entries.
The native WoW aggression/leash rules still apply; OSRS tolerance timers, ranged/
magic attacks, elemental weaknesses, poison, Slayer tasks and conditional tertiary
loot are separate milestones. The batch does not add permanent world spawns.

## Deployment record - 7 November 2026

The RelWithDebInfo build passed. Eighteen Python validation/regression tests and
isolated C++ checks passed, including old Goblin outcomes, old-family fallbacks,
new explicit zero and non-formula caps, Scorpion defence lanes and family/loot
boundaries. Every selected new model has native attack and death clips; the
existing Cow exception remains explicit. The additive migration applied and all
three enemy migration verifications passed with no pending updates.

Both servers reached ready state. Startup loaded 31 Warscape monster profiles,
33 creature definitions and 29 speed overrides. No new enemy/item/loot errors
appeared; existing Mining and item-900500 warnings remain. The four installed
client/server item records matched SQL displays. All previous client/server DBC
rows/strings and unrelated locale-patch payloads were preserved and compared.
Only the earlier Goblin/Cow/Rat entries have user gameplay acceptance; these 21
new entries still need the manual checks above.

Verified world backup:
`C:\WarscapeBackups\world_20261107T073840_558106Z_fddc91ab.sql`.
Binary/PDB, server DBC and client-patch backups:
`C:\WarscapeBackups\Wildlife-20261107-deploy`.
