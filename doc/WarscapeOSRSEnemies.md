# OSRS enemy catalogue: first Goblin milestone

## Implemented scope

The approved catalogue direction is OSRS Wiki enemy variants, stats and drop
weights with appropriate WoW presentation. This first milestone enables the
ordinary level-2 Goblin (entry **901000**). Other regular Goblin variants are
recorded as facts but disabled. No existing WoW creatures or world spawns are
replaced. Use the temporary QA spawn below to test the new enemy.

Source: [OSRS Wiki Goblin](https://oldschool.runescape.wiki/w/Goblin), raw page
retrieved 7 November 2026 with a research User-Agent. `goblins.json` records the
source URL, date and SHA-256, variant NPC IDs, combat facts and published main
loot-table weights. The Wiki describes its drop rates as sample estimates;
Warscape reproduces the published weights, not a claim of independent measurement.

## Combat and presentation

The first Goblin uses stats Attack/Strength/Defence/Ranged/Magic/HP =
1/1/1/1/1/5, attack bonus -21, Strength bonus -15, melee defence -15,
and four 600ms ticks per attack. Its source maximum hit is 1, matching the
existing Warscape max-hit formula. The existing tenfold display scale gives
50 displayed HP. Configured Warscape damage variation remains active. Displayed
creature level is 2. Existing damage-based skill XP, persistence and UI are reused.

The new creature uses existing Goblin Engineer display 7109, including its native
WoW animations and sounds. It is a neutral humanoid using AggressorAI: it reacts
to attacks without the old engineer's SmartAI spells. No custom client executable,
object layout or model assets changed. Visual suitability still needs user review.

`compile.py` generates the SQL, migration verification and C++ loot registry from
reviewed JSON. The normal monster profile/template and attack-speed tables remain
the combat architecture. The compiler rejects invalid probabilities, duplicate
IDs, unsupported stats and variants requiring directional defence it cannot yet
represent. No source request or SQL query is made during combat. Generated release SQL is
immutable: the compiler checks existing artifacts by default and refuses changed
release artifacts even with `--write`. New catalogue releases need new migration
filenames/specifications; never regenerate an already-applied migration in place.

## Loot semantics

The ordinary Goblin's free-to-play main drop table is one integer draw from 128
slots, plus guaranteed Bones. The empty main outcome occupies 44 slots, including
the members-only spear/book replacements. The three coin outcomes remain separate:
15 at 28/128, 20 at 2/128, and 1 at 1/128. Other quantities and weights are in the
reviewed JSON. Coins are collectible items, not converted to WoW money.

The registry selects one native loot template per corpse. Native loot generation
still handles ownership, party distribution and inventory delivery. Guaranteed
outcome items have 100% native chances; the OSRS pool is selected once before
corpse looting, so clicking the corpse cannot reroll it. Existing creatures retain
their native loot path. All registered outcome templates are validated at startup.

The 15 new item entries 902000-902014 are explicitly described as collectibles.
Their names and quantities represent the OSRS drops, and existing WoW item displays
supply icons. They currently have no equipment bonuses, potion effects, rune
casting, tool functionality, currency spending or quest use. This avoids silently
assigning unrelated WoW item powers. Tertiary clues/heads/champion scrolls,
quest-conditioned bones/skulls and members-only tables are **not enabled**.
The first milestone therefore implements the main F2P pool, not the complete
OSRS Goblin drop catalogue. There are no automatic world populations yet.

## Verification and deployment

Run `py contrib/warscape/enemies/run_checks.py` for validation and isolated C++
checks. It exhaustively counts all 128 roll outcomes, checks exact coin/empty
weights, rejects invalid source data and verifies fallback plus combat formulas.
It does not modify the existing worldserver CMake configuration.

Build the normal RelWithDebInfo worldserver target. Apply
`2026_11_07_00_world.sql` only through `contrib/warscape/db.py`, with its generated
verification specification, stopped servers and fresh verified backup. It adds
only custom creature/profile/speed/loot/item rows. No character data or existing
skill XP is modified. Entry 901000, profile 1000, loot IDs 901000-901016 and item
IDs 902000-902014 were collision-checked before the migration.

`build_assets.py --client <game> --server-data <data> --output <new staging dir>`
prepares additive Item.dbc records for both installations and merges the locale
patch while preserving prior MPQ payloads. Asset tooling requires `requirements.txt`.
Deploy the server DBC and client patch together with the updated binary/PDB, with
the client stopped. The installed client is the previously verified
`C:\Wrath of the Lich King`; runtime is `C:\Warscape\Server`.

7 November deployment: migration applied and verified, RelWithDebInfo build passed,
source guard tests and exhaustive C++ checks passed, and all 15 installed
client/server DBC records matched SQL displays. Original server Item.dbc rows and
strings were compared byte-for-byte and preserved. Both servers reached ready state.
Existing item-900500/Mining reference warnings remain; no new catalogue warnings
appeared. No manual combat or visual acceptance has been performed.

Verified world backup: `C:\WarscapeBackups\world_20261107T003547_837084Z_5f3e0d47.sql`.
Deployment backup: `C:\WarscapeBackups\OSRSEnemies-20261107-deploy`.
Do not remove deployed item records while inventories may contain collectibles.
A rollback needs a reviewed forward migration and inventory preservation; never
restore the world backup over current player data. Old binaries lack weighted
pool selection, so do not spawn catalogue creatures under an older binary.

## In-game acceptance

Fully restart the verified WoW client to load the item patch. Log in as a GM and
stand on open Northshire ground, away from the Agility log:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901000
```

The `loot` argument is required to keep the temporary corpse available for 30
seconds. Confirm a neutral Goblin appears with 50 displayed HP. Attack it and
observe retaliation, a roughly 2.4-second swing interval, appropriate animations,
normal death and a lootable corpse. Record skill XP before/after and after relog.
Each corpse should contain Bones and at most one main-table drop (possibly none).
Repeatedly spawn/kill a sample to inspect item names and quantities; a small
manual sample cannot establish rare drop probabilities. Collectibles should
persist after relog. Confirm a normal WoW creature retains its existing loot.

## Extending the catalogue

Next: accept this Goblin in-game, then implement item functionality/economy and
conditional tertiary drops before presenting it as a fully faithful OSRS enemy.
Add armed, level-5 and level-13 Goblins through distinct reviewed definitions,
model choices and loot pools. Level 13 requires per-style defence support rather
than collapsing its different stab/slash/crush bonuses to one value. Reconcile
source infobox/prose loot-table differences before enabling that variant.

Wider families require researched variant identities, reusable herb/gem/rare
subtables, independent tertiary rolls, quest/achievement conditions, membership,
Slayer requirements/XP, poison/immunities, ranged/magic and special attacks.
Those mechanics are not inferred from monster names. Expand the compiler and
focused tests as each mechanic is supported; preserve provenance and reject
unsupported definitions rather than silently approximating them.
