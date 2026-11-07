# Spectral enemies: two-entry checkpoint

The user asked to reduce batches to a few enemies at a time and delegated the
selection. This checkpoint adds Otherworldly being and the Catacombs Shade:
**277 entries / 52 families**. Both new entries await manual acceptance. No
permanent spawns, new client code or custom-client memory-layout changes.

## Source facts and appearance

Reviewed facts are in `contrib/warscape/enemies/spectral.json`, with source NPC
IDs, page hashes and retrieval date 7 November 2026. Sources:
[Otherworldly being](https://oldschool.runescape.wiki/w/Otherworldly_being),
[Shade](https://oldschool.runescape.wiki/w/Shade), and
[Flat armour](https://oldschool.runescape.wiki/w/Flat_armour).

| Entry / family | Source variant | Attack / Strength / Defence / Ranged / Magic / HP | Max hit | Flat armour | Appearance |
| --- | --- | --- | ---: | ---: | --- |
| 901500 / 51 Otherworldly Beings | Zanaris, level 64, NPC 2843 | 56 / 56 / 46 / 1 / 1 / 66 | 7 | -2 | Stock blue Voidwalker, display 1132 |
| 901501 / 52 Shades | Catacombs, level 140, NPC 7258 | 130 / 136 / 100 / 50 / 50 / 115 | 15 | -3 | Stock shadowy Shade, display 4629 |

Both are neutral, crush melee, four-tick (2.4-second) cadence. HP is displayed at
Warscape's existing tenfold scale: 660 and 1,150. Native AggressorAI handles
retaliation/leashing. Native model animation arrays contain standing, movement,
attack and death clips; appearance/audio and targetability need user inspection.
The Voidwalker is a visible silhouette approximation for floating clothing.
Otherworldly being is type 10 (not specified), avoiding an invented undead tag;
the actual undead Shade uses type 6. Source respawns are 20/35 ticks, stored as
metadata; these temporary prototypes have no permanent respawn placement.

## Flat armour behaviour

The reusable catalogue now has signed `flat_armour`, default zero. Only the two
new source-combat entries opt in. All preceding 275 retain zero and the same
runtime data. A successful player melee roll is adjusted in OSRS units before
Warscape display scaling/variation: `max(0, roll - armour)`. Thus -2 adds two OSRS
damage and -3 adds three. A successful zero also gains the bonus. A miss, evade
or immunity does not turn into damage. The calculation uses signed 64-bit
intermediates and saturates at the unsigned damage bound.

The authoritative adjusted roll feeds existing health-capped damage XP; it is
not an extra hit or separate reward. Normal display variation still applies.
Magic damage ignores this hook. This milestone wires existing player melee only;
future ranged combat must explicitly use the same physical-damage rule. No NPC
outgoing damage, older enemy balances, spells, poison, prayer or recoil systems
are changed. The existing player zero-roll distribution remains in place.
`.rs enemy` reports each new target's flat armour and the supported attack path.

The rule was checked against the Wiki's
[PlayerVsNPCCalc source](https://github.com/weirdgloop/osrs-dps-calc/blob/main/src/lib/PlayerVsNPCCalc.ts):
flat armour excludes magic and inaccurate hits. No calculator implementation was
copied into the server. Elemental wind weaknesses (35% / 40%), spectral Prayer
rewards and source flat-armour values on earlier accepted creatures remain future
work. This checkpoint does not silently rebalance older releases.

## Loot

Neither creature guarantees Bones, ashes or any other item.

- Otherworldly being: Coins 15 at 59/128; its six rune outcomes retain their
  individual source chances. Herbs occupy 10/128, gems 3/128, explicit empty main
  outcome 18/128, Ruby ring 2/128, Mithril mace and Mackerel 1/128 each. Existing
  no-ring-of-wealth/pre-Legends gem policy applies, including empty gem rolls and
  replacing the quest-gated spear branch with its talisman slot.
- Catacombs Shade: Shade robe top 1/4, Shade robe bottom 1/4, empty 1/2. Robes use
  the members baseline; Catacombs tertiary drops remain conditional future work.
  This is the Catacombs combat form, without a Mort'ton shadow activation phase.

Four new collectibles: 902357 Ruby ring, 902358 Mackerel, 902359 Shade robe top,
902360 Shade robe. The existing Mithril mace and all other shared items keep their
IDs. These are stack-200 loot collectibles; the fish is not yet edible, robes and
ring do not gain equipment effects. No conditional quest/task rewards, cremation,
Mort'ton keys, Stronghold/random-event Shade or Slayer training is included.

## Verification and deployment - 7 November 2026

```powershell
py -3.13 contrib/warscape/enemies/run_checks.py
.\work\enemies-venv\Scripts\python.exe contrib/warscape/enemies/check_models.py --client 'C:\Wrath of the Lich King'
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

76 Python tests, isolated Debug C++ checks, native model/item checks and full
RelWithDebInfo worldserver build passed. Tests cover exact stats/source IDs/loot,
empty outcomes, signed metadata bounds, additive migration/defaults, new loot CDF
boundaries, successful zero/normal hit adjustments, misses, positive-armour clamp,
extreme arithmetic and adjusted damage XP capped by remaining health. Preceding
275 metadata/pool rows and 8,172 outcome rows match the previous generated header;
only the zero-default field is appended to earlier metadata. Prior SQL/specs
remain unchanged and all nine enemy postconditions pass.

Migration `2026_11_07_08_world.sql`, SHA-1
`2233214813A2C5D900602B389479393148BA1636`, adds one signed INT column with default
zero and two families/profiles/definitions/speeds/variants, four items and exact
native loot rows. It updates only the two new variants. Preconditions check ID
collisions, absence of the new column and existing shared identities. Verification
checks signedness, non-null/default, prior zero defaults, stats and every loot row.
No characters migration, progress edits or permanent spawns.

Runtime is `C:\Warscape\Server`; deployment targets the previously authorized
stock `C:\Wrath of the Lich King` client. The client was closed and zero characters
were online. Both servers were stopped before `db.py apply`, which made a fresh
verified world backup, applied/verified SQL and recorded its hash. Existing rows
across ten affected world tables and all character skill XP matched pre-migration
hashes. Backup (integrity checked; restore not tested):
`C:\WarscapeBackups\world_20261107T163507_866189Z_f88f7d23.sql`
(297,515,742 bytes; 190 tables / 3 views).

Previous binary/PDB, server Item.dbc and client locale patch:
`C:\WarscapeBackups\Spectral-20261107-deploy`.
Prepared assets: `C:\WarscapeBackups\Spectral-20261107-prepared`.
Four installed-file hashes matched build/prepared sources. All earlier DBC
rows/strings and unrelated MPQ contents were retained; all four new client/server
item displays match database values. The build includes the preserved unrelated
`cs_gobject.cpp` worktree edit, excluded from this feature's commit. No client
executable, addons, settings, saved variables or memory layout changed.

Both servers reached ready state and connected to their databases. Startup loaded
280 Warscape profiles / 282 creature definitions / 278 speed overrides. Database
catalogue count is 277 across 52 families. World status: 40 applied, 6,952 archived,
none pending. No startup errors reference new creature/item/loot IDs, models or
flat-armour metadata. Existing Mining script and item-900500 warnings remain.
No in-game combat, visual, damage or loot acceptance is claimed.

## In-game checks

Restart WoW fully to load new item records. Use a clear area on a GM character:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901500
```

Select it and use `.rs enemy`; expect level 64, source HP 66, crush, four ticks,
max hit 7 and flat armour -2. Confirm neutral behaviour until attacked, targeting,
movement, attacks, death and loot names/icons. Kill several: it can drop nothing
and has no guaranteed Bones/ashes. Check that a miss stays zero; successful
physical attacks receive the two-unit bonus before display scaling/variation.

Then spawn separately:

```text
.npc add temp loot 901501
```

Expect level 140, source HP 115, max hit 15, flat armour -3 and a shadowy Shade.
It hits hard. Check the same combat properties and its robe-or-empty table.
Corpses last 30 seconds. Neither temporary spawn is saved permanently.

Check combat XP after successful hits and relog with any new items to verify
inventory/XP persistence. Recheck an earlier enemy: it should have unchanged
combat/loot and no flat-armour diagnostic. Small gameplay samples do not prove
rare odds; exact probability checks are automated. Record only observed results.

## Rollback

If needed, stop spawning these entries and prepare a compatible corrective build
or additive migration. Preserve all items players may own, XP, DBC rows and the
new metadata column. Do not edit applied SQL/history or delete loot records.
The previous binary lacks this armour rule and is not an equivalent gameplay
rollback for these entries. Backup restoration needs separate review and has not
been exercised. No privileges were changed.
