# Warscape standard WotLK ore expansion — Stage A plan

Status: Stage A plan with Stage B implementation prepared, 31 October 2026.
Database rows and live client/server deployment remain unchanged. Stage B source,
validated assets and pending migration artifacts are described below.

## Scope and existing behavior

Extend `src/server/scripts/Custom/warscape_copper_mining.cpp` into a shared,
configuration-driven Mining implementation. Preserve Copper entry 900101,
depleted counterpart 900103/display 900102, existing XP accumulator,
Mining Pick 2901, attempt cadence, tool visual, animation, 9-second timer,
counterpart lifecycle, scale 0.5, and interruption/inventory handling. New
nodes use the same pairing model and award one item only after safe inventory
capacity validation. Each active node owns its own depleted counterpart and
timer. All 14 new ores temporarily require skill level 1.

No client object layout, allocator, mirror buffer, or object lifetime code is
part of this feature. If asset/client model work ever touches those systems,
the memory-layout requirements in both applicable `AGENTS.md` files apply.

## Standard client models and vanilla item templates

The live world templates and server `GameObjectDisplayInfo.dbc` were inspected.
Warscape uses custom-path copies of the existing WotLK models and display rows,
without changing Blizzard data. `Small Thorium Vein` (entry 324/display 3951) supplies
the standard Thorium appearance; rich veins remain excluded. Titanium shares
the Adamantite model/display 6798, matching the standard DBC record. Model paths:

| Ore | Existing node/display | Existing display ID | Existing model path | Vanilla ore item |
|---|---:|---:|---|---:|
| Tin | 1732 | 315 | `World\\SkillActivated\\TradeskillNodes\\tin_Miningnode_01.mdx` | 2771 |
| Silver | 1733 | 314 | `World\\SkillActivated\\TradeskillNodes\\TrueSilver_Miningnode_01.mdx` | 2775 |
| Iron | 1735 | 312 | `World\\SkillActivated\\TradeskillNodes\\Iron_Miningnode_01.mdx` | 2772 |
| Gold | 1734 | 311 | `World\\SkillActivated\\TradeskillNodes\\gold_Miningnode_01.mdx` | 2776 |
| Mithril | 2040 | 313 | `World\\SkillActivated\\TradeskillNodes\\mithril_Miningnode_01.mdx` | 3858 |
| Truesilver | 2047 | 314 | `World\\SkillActivated\\TradeskillNodes\\TrueSilver_Miningnode_01.mdx` | 7911 |
| Dark Iron | 165658 | 2571 | `World\\Azeroth\\BurningSteppes\\ActiveDoodads\\DarkIronNode\\DarkIronNode.mdx` | 11370 |
| Thorium | 324 | 3951 | `World\\SkillActivated\\TradeskillNodes\\Thorium_Miningnode_01.mdx` | 10620 |
| Fel Iron | 181555 | 6799 | `World\\SkillActivated\\TradeskillNodes\\FelIron_Miningnode_01.mdx` | 23424 |
| Adamantite | 181556 | 6798 | `World\\SkillActivated\\TradeskillNodes\\Adamantium_Miningnode_01.mdx` | 23425 |
| Khorium | 181557 | 6800 | `World\\SkillActivated\\TradeskillNodes\\Khorium_Miningnode_01.mdx` | 23426 |
| Cobalt | 189978 | 7881 | `World\\SkillActivated\\TradeskillNodes\\Cobalt_Miningnode_01.mdx` | 36909 |
| Saronite | 189980 | 7804 | `World\\SkillActivated\\TradeskillNodes\\Yoggthorite_Miningnode_01.mdx` | 36912 |
| Titanium | 191133 | 6798 | `World\\SkillActivated\\TradeskillNodes\\Adamantium_Miningnode_01.mdx` | 36910 |

The existing world item templates supply the standard icons and fields. Custom
Warscape item rows should be copied from their matching vanilla ore templates,
then set to the custom name, unique entry, and `stackable=1`; all other columns
should remain cloned. Copper's existing 2770 template remains unchanged.
Migration SQL must explicitly insert custom rows only and have a read-only
precondition/postcondition specification. It must not alter loot tables,
vanilla templates, or character inventory.

## Proposed custom IDs

Existing Copper IDs are retained. Each new active/depleted pair occupies two
gameobject entries; grayscale display IDs and ore item IDs use their separate
namespaces.

| Ore | Active GO | Depleted GO | Active display | Depleted display | Ore item ID/name |
|---|---:|---:|---:|---:|---|
| Tin | 900110 | 900111 | 900118 | 900104 | 900201 — Warscape Tin Ore |
| Silver | 900112 | 900113 | 900119 | 900105 | 900202 — Warscape Silver Ore |
| Iron | 900114 | 900115 | 900120 | 900106 | 900203 — Warscape Iron Ore |
| Gold | 900116 | 900117 | 900121 | 900107 | 900204 — Warscape Gold Ore |
| Mithril | 900118 | 900119 | 900122 | 900108 | 900205 — Warscape Mithril Ore |
| Truesilver | 900120 | 900121 | 900123 | 900109 | 900206 — Warscape Truesilver Ore |
| Dark Iron | 900122 | 900123 | 900124 | 900110 | 900207 — Warscape Dark Iron Ore |
| Thorium | 900124 | 900125 | 900125 | 900111 | 900208 — Warscape Thorium Ore |
| Fel Iron | 900126 | 900127 | 900126 | 900112 | 900209 — Warscape Fel Iron Ore |
| Adamantite | 900128 | 900129 | 900127 | 900113 | 900210 — Warscape Adamantite Ore |
| Khorium | 900130 | 900131 | 900128 | 900114 | 900211 — Warscape Khorium Ore |
| Cobalt | 900132 | 900133 | 900129 | 900115 | 900212 — Warscape Cobalt Ore |
| Saronite | 900134 | 900135 | 900130 | 900116 | 900213 — Warscape Saronite Ore |
| Titanium | 900136 | 900137 | 900131 | 900117 | 900214 — Warscape Titanium Ore |

The proposed gameobject IDs occupy 900110–900137 (28 IDs). To provide
Warscape-specific model paths for both active and depleted variants, display
IDs 900104–900117 are for depleted models and 900118–900131 are for active
models. No custom `ItemDisplayInfo.dbc` records are needed because the cloned
item rows reuse their matching vanilla ore item display. No creatures, spells,
quests, or spawn GUIDs are needed.

## XP and success configuration

Copper remains 17.5 XP via the existing alternating 17/18 accumulator. The
shared engine stores XP as half-points and uses `MiningSuccessOutOf256` with
per-ore `low`/`high` parameters. Temporary required Mining level is 1 for every
node; all configured low values are positive so all nodes can succeed at level
1. Attempt timing stays at 8 OSRS ticks / 4.8 seconds.

| Ore | XP per success | Success low/high | Status |
|---|---:|---:|---|
| Tin | 17.5 | 100 / 350 | OSRS chart |
| Silver | 40 | 25 / 200 | OSRS chart |
| Iron | 35 | 96 / 350 | OSRS chart and Mod Ash level-1/99 values |
| Gold | 65 | 7 / 75 | OSRS chart |
| Mithril | 80 | 4 / 50 | OSRS chart |
| Adamantite | 95 | 3 / 25 | OSRS chart; level-1 access is Warscape test policy |
| Truesilver | 40 | 18 / 180 | Provisional WotLK ore balance |
| Dark Iron | 90 | 24 / 200 | Provisional WotLK ore balance |
| Thorium | 100 | 20 / 190 | Provisional WotLK ore balance |
| Fel Iron | 90 | 28 / 220 | Provisional WotLK ore balance |
| Khorium | 120 | 30 / 230 | Provisional WotLK ore balance |
| Cobalt | 80 | 32 / 220 | Provisional WotLK ore balance |
| Saronite | 100 | 24 / 200 | Provisional WotLK ore balance |
| Titanium | 125 | 15 / 170 | Provisional WotLK ore balance |

The comparable OSRS XP/success references are the [Mining experience
table](https://oldschool.runescape.wiki/w/Mining/Experience_table), per-rock
pages for Tin, Silver, Iron, Gold, Mithril and Adamantite, and the [Skilling
success rate](https://oldschool.runescape.wiki/w/Skilling_success_rate)
formula. WotLK-only values above are explicitly provisional, not official OSRS
values. No secondary loot is included in the Warscape configuration.
The per-ore configuration is implemented in
`src/server/scripts/Custom/warscape_copper_mining.cpp`; provisional WotLK rates
are explicitly flagged there for later balancing.

## Asset and collision pipeline

For each source model, create a Warscape-path copy with the matching original
00.skin. Preserve geometry, bounds, orientation, material/render settings and
model structure. Reuse its original textures for the colored model. Create
grayscale texture variants for depleted models, including emissive/glow inputs;
verify decoded pixels and mipmaps. Do not change shared Blizzard MPQ assets.
Append the custom client display rows, and make server collision DBC / VMap
display aliases refer to each original model's existing collision geometry.
The current `copper_depletion_assets.py` has the proven copper DBC, SKIN,
texture, MPQ preservation, collision alias, backup and deployment checks; Stage
B should generalize these checked operations rather than replace them with
unchecked scripts. Asset coverage and paths must be validated against the
actual client archives before Stage C.

## Required reviewed migrations

One world migration is expected to:

1. Insert 14 active mining templates with their corresponding standard display
   IDs and the shared Mining script.
2. Insert 14 depleted, non-selectable templates and addon flags, each using its
   unique grayscale display ID.
3. Insert 14 custom ore item templates cloned from standard matching ore item
   templates, renamed and `stackable=1`.

It must not edit existing Copper rows, character data, loot tables, or standard
items. A matching verification JSON must assert all expected rows, intended
fields, and absence of partial preexisting custom entries. Before application,
the live migration status/permissions and database state must be checked again;
then stop for explicit approval of the exact migration. Application needs a
fresh verified backup immediately before execution through `contrib/warscape/db.py`.

## Stage gates

- Stage A: audit, conflict-check IDs and document the design.
- Stage B: shared engine and custom model/texture/DBC/collision package are
  prepared and validated without database changes. Builder:
  `contrib/warscape/mining/build_standard_ore_assets.py`; focused checks:
  `contrib/warscape/mining/test_standard_ore_assets.py`.
- Stage C: the reviewed migration is stored outside TrinityCore updater paths at
  `contrib/warscape/migrations/pending/2026_10_31_00_world.sql`; its matching
  read-only verification spec remains under `contrib/warscape/verifications/`.
  It has not been applied and awaits explicit approval.
- Stage D: after approval, apply with safeguards, build/deploy the server and
  paired client/server asset files. The user performs in-game confirmation.
