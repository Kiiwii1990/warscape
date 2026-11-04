# Warscape Skill ID Allocations

Updated: 1 November 2026

This document reserves IDs for Warscape skill content. Reservations do not
create database rows. Before using a value, add it to the in-use register below
and check the relevant client/server data files again. Each database/DBC
category is its own namespace: the same number may be used in two different
categories without a collision.

## Allocation rule

Each skill receives a 200-ID block per applicable entity category. Blocks start
at 900100 and advance by 200. The current reservations are:

| Skill | First ID | Last ID | Reservation state |
| --- | ---: | ---: | --- |
| Mining | 900100 | 900299 | Reserved |
| Woodcutting | 900300 | 900499 | Reserved |
| Smithing | 900500 | 900699 | Reserved, approved 1 November 2026 |
| Agility | 900700 | 900899 | Reserved, approved 4 November 2026 |

The former proposal for 900500-900699 is superseded by the user's approved
Bronze smelting task on 1 November 2026: it is now reserved for Smithing.
The Agility block 900700-900899 is assigned to Agility obstacles.

## Per-category reservations and current use

| Entity category / key | Mining: 900100-900299 | Woodcutting: 900300-900499 | Agility: 900700-900899 |
| --- | --- | --- | --- |
| `gameobject_template.entry` | Reserved. In use: 900101 active copper rock; 900103 grayscale depletion counterpart. Assigned in the pending implementation (not yet database rows): active even entries 900110-900136 and depleted odd entries 900111-900137. | Reserved; no IDs in use. | In use: 900700 Northshire Agility Log clickable proxy. |
| `item_template.entry` | Reserved; 900201-900214 are the ore items listed in `WarscapeMiningExpansionPlan.md` (live presence rechecked 1 November). 900220 Bronze, 900221 Iron and 900222 Steel Pickaxes are allocated to the pending pickaxe migration. Copper Ore 2770 and Mining Pick 2901 remain unchanged. | Reserved; no IDs in use. | Reserved; no IDs in use. |
| `Item.dbc` ID | 900201-900214 ore entries; 900220-900222 allocated to the staged pickaxe package. | Reserved; no IDs in use. | Reserved; no IDs in use. |
| `creature_template.entry` | Reserved; no Mining creature IDs in use. Training Dummy 900001 is an existing Warscape utility outside this block. | Reserved; no IDs in use. | Reserved; no IDs in use. |
| Spell ID (`Spell.dbc`, mirrored by world `spell_dbc`) | Reserved; no custom Mining spell IDs in use. | Reserved; no IDs in use. | Reserved; no Agility spells in use. |
| `GameObjectDisplayInfo.dbc` ID | Reserved. In use: 900102, the grayscale copper display referenced by entry 900103. Assigned in the pending implementation: depleted displays 900104-900117 and active displays 900118-900131. | Reserved; no IDs in use. | Uses existing Blizzard display 8028; no custom display allocated. |
| `CreatureDisplayInfo.dbc` ID | Reserved; no Mining creature display IDs in use. | Reserved; no IDs in use. | Reserved; no Agility creature displays in use. |
| `ItemDisplayInfo.dbc` ID | 900220 Bronze, 900221 Iron and 900222 Steel Pickaxes allocated to the staged pickaxe package. Each clones the original pick display 6568 with its own icon and replaceable metal texture. | Reserved; no IDs in use. | Reserved; no Agility item displays in use. |
| `quest_template.ID` | Reserved; no Mining quest IDs in use. | Reserved; no IDs in use. | Reserved; no Agility quest IDs in use. |

`gameobject_template_addon.entry` is a foreign key into
`gameobject_template.entry`, not a separate allocation namespace; addon rows
use their parent gameobject's entry. Persisted gameobject and creature spawn
GUIDs are allocated by TrinityCore and must not be selected from these entry
ranges manually. Map IDs are also a separate, non-skill namespace.

## Existing Warscape IDs outside the reservations

| Category | ID | Existing use |
| --- | ---: | --- |
| `creature_template.entry` | 900001 | Warscape Training Dummy |
| Map ID | 905 | Briarbrook development environment |

## Range validation and updates

Historical snapshot, 31 October 2026: the allocation was checked against the Warscape world database and server
DBC files on 31 October 2026. No world rows occupy candidate Mining gameobject
IDs 900110â€“900137 or ore item IDs 900201â€“900214; no server display DBC rows
occupy candidate display IDs 900104â€“900131. The world database contains the listed
custom gameobject and creature entries, no custom item or quest entries at or
above 900000, and no custom spell IDs at or above 900000. Server DBC inspection
found only the listed custom gameobject display ID in the 900000 range;
`CreatureDisplayInfo.dbc`, `ItemDisplayInfo.dbc`, and `Spell.dbc` contain no
records at or above 900000. The largest inspected standard IDs were 68,742 for
item displays and 200,000 for spells. The item-template range is above the
current database's highest item entry (56,806).

1 November pickaxe audit: world item IDs 900220â€“900222, installed client and
server `Item.dbc`/`ItemDisplayInfo.dbc` IDs 900220â€“900222, and source/pending
migrations were checked for conflicts; all were unused. The live database now
contains the 14 custom ore items. The pickaxe reservations remain **staged,
not applied or deployed**. See [pickaxe progression](WarscapePickaxeProgression.md).

Recheck client MPQs, server DBCs, world tables, pending migrations, and this
register before adding a new custom record. Proposed ranges are not active
allocations until their migration and asset package are reviewed; recheck them
again immediately before preparation/deployment. Keep existing IDs stable. If an
external update claims a reserved value, stop and revise the allocation with
review rather than silently renumbering deployed content.

## Custom skill identifiers — 1 November 2026

The independent Warscape skill namespace uses enum slots 0–8 and wire IDs
attack, strength, defence, hitpoints, ranged, magic, prayer, mining, smithing.
Smithing appends slot 8 / wire ID `smithing`; prior slots 0–7 stay stable.
Source enum, name lookup, snapshot IDs and addon metadata were checked before
allocation. This allocates no Blizzard SkillLine, spell, item or entity IDs.

## Smithing content allocation - Bronze prototype, 1 November 2026

- Item template and Item.dbc entry 900500: non-stackable Warscape Bronze Bar.
- World item range 900500-900699, server Item.dbc range and current effective
  client Item.dbc entry were checked before allocation. Source SQL/asset code
  was checked for existing 900500 allocations; none existed.
- Reuses Blizzard Bronze Bar 2841's display 7390 and existing icon, through an
  additive Item.dbc row. No Blizzard item/display is overwritten. No new spell,
  gameobject, display, creature or spawn IDs are allocated.
- World migration 2026_11_01_01_world.sql is applied and verified. Source and
  asset preparation: contrib/warscape/smithing. The Smithing plan records QA.
