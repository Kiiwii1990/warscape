# Lizardman, TzHaar, Drake, Wyrm and Wyvern checkpoint

The user confirmed the preceding Elf/Aviansie/Hobgoblin/Suqah batch working with
drops. This next ordered batch adds seven variants in five families, bringing
the catalogue to **296 entries / 63 families**. Manual acceptance of this batch
is pending. No permanent map spawns, player skill changes or Slayer system added.

## Entries and models

| Entry | Variant | Combat level | Source HP | Attack ticks | Slayer XP reference |
| --- | --- | ---: | ---: | ---: | ---: |
| 901800 | Lizardman (OSRS regular_53) | 53 | 60 | 4 | 60.0 |
| 901801 | Lizardman (OSRS regular_62) | 62 | 60 | 4 | 60.0 |
| 901802 | TzHaar-Ket (OSRS ket_149) | 149 | 140 | 4 | 140.0 |
| 901803 | TzHaar-Xil (OSRS xil_ring_133) | 133 | 120 | 4 | 120.0 |
| 901804 | Drake (OSRS regular_192) | 192 | 225 | 4 | 230.6 |
| 901805 | Wyrm (OSRS regular_97) | 97 | 120 | 4 | 123.0 |
| 901806 | Skeletal Wyvern (OSRS skeletal_140) | 140 | 200 | 6 | 210.0 |

Warscape retains tenfold displayed HP/damage. Wiki source hashes, source NPC IDs,
stats, directional melee defences, full drop outcomes and assumptions are in
`contrib/warscape/enemies/draconic_tzhaar.json`. Wyrm is currently level97 with
one flat armour; Drake has two flat armour. Drake Slayer XP230.6 is preserved in
tenths. Slayer requirements84/62/72 are metadata only, matching previous batches.

Following Kieran's model notes: male naga displays6747/18398 stand in for the two
Lizardmen; Flamewaker12030 for Ket; Obsidian Destroyer15343 for Xil; grounded Black
Drake6374; Northrend Jormungar Larva24564; Frost Wyrm16919 for Skeletal Wyvern.
These are stock models/sounds, not new OSRS assets. Naga retain tails and drakes
retain wings. Model paths were resolved through the verified client's display/model
DBC tables. Actual scale, animations, grounding and loot reach require user QA.
Other Lizardmen, TzHaar, superior monsters and Fossil Island Wyverns remain future
variants. No terrain, executable or client object-memory-layout changes.

## Combat

Lizardmen mix source Crush melee and Ranged, apply severity3 poison, and resist
poison. Poison uses the existing 18-second tick/decay system with a new scoped
carrier; unrelated Rogue crit modifiers are removed from that carrier. Applying
poison has a prototype25% chance after positive damage; close-range style choice
is50%. Source level62 Ranged1 is retained even though it gives low accuracy; its
unqualified source max9 is also used for its ranged prototype.

Ket is Crush melee. Ring Xil begins ranged, spends one attack turn switching when
the player enters melee range, then remains melee until reset, following source
prose. Its melee/ranged maximums are11/16. This does not implement TzHaar social
aggro, weapon upgrades, Fight Caves or Tokkul spending.

Drake uses Ranged level140 and source ranged bonus40, maximum15, against the
player's Ranged defence. After seven normal attacks, it targets the player's
position with volcanic breath: move away from that position to avoid damage.
Four pulses deal source6-8 each; an equipped Anti-dragon shield reduces each to
0-4. The prototype uses a1200ms warning,600ms pulse spacing,2.5-yard horizontal
radius and4-yard vertical tolerance; only the intended player is damaged. Those
spatial/timing conversions are explicit WoW choices, not measured OSRS values.
The native Flamestrike carrier supplies visuals only: its direct damage is
suppressed and its persistent damage aura removed. AI owns all four hits.
Timers/target GUID reset on evade/death; missing, dead, invalid or out-of-map
players cannot be hit. No raw player pointer survives between updates. Large
server updates process at most four pulses. Anti-fire potions, protection prayers,
area-floor burns and dragonbane multipliers are not implemented.

Wyrm mixes source Slash melee(max10) and magic(max13), using magic at distance
and50% magic selection nearby. It resists poison. There is no custom idle-to-hover
model transformation. Source stats/flat armour are used by the existing combat
system; player ranged/magic still follow their previously implemented paths.

Skeletal Wyvern mixes Slash melee(max13), ranged(max13), and icy breath. Its
melee accuracy rolls against player Stab defence, as specified by the Wiki. Breath
ignores the ordinary armour accuracy roll, with a provisional unprotected maximum60
because the Wiki publishes only50+. An equipped Elemental shield caps breath at10;
an Anti-dragon shield does not protect against this icy breath. Breath choice33%
is a prototype policy. Freeze lasts6.6seconds and includes native root plus pacify
so movement and attacks are blocked. Protected freeze chance is1/7; unprotected
always freezes as an explicit prototype choice. Native immunities/dispels remain;
no ancient-shield exemption, prayer protection or exact OSRS freeze immunity window.
The freeze carrier has no periodic damage, inherited Druid procs or damage-break
flags. Source references: [Wyvern strategies](https://oldschool.runescape.wiki/w/Skeletal_Wyvern/Strategies)
and [icy breath](https://oldschool.runescape.wiki/w/Dragonfire#Icy_breath).

## Loot and source ambiguities

Members/no-wealth/off-task/pre-Legends tables are used. Drake and Wyrm unique
pre-rolls use off-task rates before their conditional main pool. Wyvern rare
armour is a pre-roll and visage1/10000 is independent. Guaranteed Drake/Wyrm/
Wyvern bones are distinct item identities; Lizardmen give normal Bones. TzHaar
do not give invented bones. Herbs, seeds, gems, rare table, gear and empty outcomes
retain exact integer weights and stated quantity ranges. Task/quest/diary/key/
clue conditions, bank-note conversion and most item functionality are deferred.

Specific source gaps are explicit rather than silently renormalized:

- Lizardman lists seeds15/87 or15/78, fangs10/87 or14/78, fabric6/87 or8/78 and
  talisman1/250. Unlisted main-table mass is represented as Nothing. Talisman is
  treated independently, without diary boost; seed subtable's two unlisted slots
  retain its existing empty policy.
- Xil gear totals1/128 while its common rows already total1. Gear is treated as
  an exclusive pre-roll, with the common table conditional on no gear. This
  preserves unique rates; displayed common rates are conditional. Source needs
  future confirmation. Ket149's table sums correctly and is used directly.
- Wyvern prose says exactly three herbs, while its template says1-3. This release
  follows the explicit prose. Drake's shark lure choices8/10/12 are equally likely.

Large quantities are no longer forced through SQL's byte-sized MinCount/MaxCount.
A validated outcome may carry one extra32-bit drop range. Native loot still
creates guaranteed bones; the extra item is rolled once and inserted before
ownership/group processing. Counts can span multiple ordinary item stacks. Coins
use the existing2,147,483,647 stack limit. Drake Coins1000-2000/5000-7000, Wyrm
Coins950-1450/Pure essence200-300, and Wyvern300/RDT3000 Coins are preserved in
full. No changes to native SQL column types, historical migrations or drop chances.
The compiler rejects multiple wide drops, unsupported quantities, missing native
base loot, overlapping IDs and loot outcomes that exceed18 visible slots.

Shields902379(Elemental) and902380(Anti-dragon) are native off-hand shield items,
stack1, with scoped breath protection. They have no invented OSRS armour bonuses
or quest/Defence gates. Obtain them through GM commands for this checkpoint.
Tokkul902387 remains a200-stack collectible; other new items are collectible
identities except these two shields. No spending/conversion economy is added.

## Automated checks and deployment

`py -3.13 contrib/warscape/enemies/run_checks.py` checks immutable releases,
107 Python cases and isolated Debug C++ assertions. New checks cover all outcome
boundaries, exact unique/bonus marginals, full-count ranges, invalid wide drops,
shield records, source stats/armour, poison/root spell isolation and bounded breath
scheduling. `cmake --build build --config RelWithDebInfo --target worldserver -- /m`
builds the runtime. These are source/automated checks, not gameplay acceptance.

Migration `2026_11_07_12_world.sql` is additive, with reviewed pre/postconditions.
Deployment must use `db.py`, stop writers, make a fresh verified world backup,
then check all thirteen current enemy/currency contracts. Before/after hashes
cover eleven existing world tables, every inventory row, all skill XP and wallet/
level/XP values. Client/server Item.dbc and Spell.dbc append49 items/nine spells;
all prior rows/string offsets and unrelated MPQ entries must remain byte-identical.
Runtime executable/PDB and previous assets are backed up outside Git. No client
cache/SavedVariables deletions or automatic test-character edits are needed.

## In-game acceptance

Fully exit/reopen `C:\Wrath of the Lich King\Wow.exe` so the patch loads. Test
one creature at a time on open Northshire ground away from the Agility log:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901800
.npc add temp loot 901801
.npc add temp loot 901802
.npc add temp loot 901803
.npc add temp loot 901804
.npc add temp loot 901805
.npc add temp loot 901806
```

Run each spawn command separately after finishing the preceding fight; the `loot`
argument retains a temporary corpse for30seconds. Check appearance, source-scaled
HP, retaliation, source attack cadence, death and loot reach. Check Lizardman poison
and Xil's one-way style switch. Let Drake perform seven attacks, then compare moving
out of its warned position with standing still for four pulses. Let Wyrm attack
nearby and from range. Compare Wyvern breath/freeze with and without its shield.
Breath damage uses the tenfold Warscape scale and can kill the test character.

```text
.additem 902379 1
.additem 902380 1
```

Equip the appropriate shield in the off hand; carrying it in a bag gives no
protection. Elemental protects Wyvern; Anti-dragon protects Drake. Check native
control returns after freeze and encounter effects stop/reset on evade, death,
logout and teleport. These interruption paths are not claimed manually tested.

Confirm guaranteed bones (none for TzHaar), occasional main drops, correct item
names, Coins piling above200, large stack quantities, loot with nearly full bags,
and unchanged earlier enemy loot. Relog and verify collected loot, Coins and skill
XP persist. A small manual sample cannot prove rare drop rates. Ordinary creature
loot and previous Agility/skill UI should remain normal.

## Rollback

Prefer a reviewed forward fix. Do not spawn these entries under an old binary
that lacks extra-drop selection or special mechanics. Keep installed item identities
while characters may own loot or shields; never remove character inventory to undo
this batch. Restoring old assets/binaries while items remain can break displays or
protection. Stop writers, take fresh backups, inspect inventory/bank/mail/auction
references, and design a separate rollback before removing any world definitions.
Never restore old character data over subsequent progress or rewrite applied SQL.


## Completed deployment record (7 November 2026)

Migration12 applied and verified through `db.py`. Fresh verified backup:
`C:\WarscapeBackups\world_20261107T193351_904850Z_455c2319.sql`
(190 tables, three views, completed export; restore not exercised).
Runtime/client rollback files are in
`C:\WarscapeBackups\Draconic-20261107-deploy`.

RelWithDebInfo worldserver build,107 Python catalogue tests, isolated Debug C++
checks, all thirteen current enemy/currency migration contracts, preservation
hashes and staged diff checks passed. Both servers restarted and report ready
with auth3724/world8085 listening. No new batch database/script errors appeared;
pre-existing unrelated item/Mining/GameObject warnings remain. Asset checks prove
49 added item records/nine spells, correct classes/displays/shield slots and
spell effects, preserved previous DBC rows/string offsets and unrelated MPQ
payloads. All selected model assets resolve to native M2 files.

No user visual/combat/loot or interruption acceptance is claimed for this batch.
No client executable/object layout or player persistence schema was changed.

Final review builds also guard against the Drake target dying during a pulse and
match Wyvern melee to player Stab defence. Intermediate executable/PDB backups
are retained in `C:\WarscapeBackups\Draconic-20261107-reviewfix` and
`C:\WarscapeBackups\Draconic-20261107-release`; the pre-batch full rollback set
remains in `Draconic-20261107-deploy`.


## Lizardman acceptance update, 7 November 2026

The user confirmed Lizardman retaliation works after disabling GM mode. Saved GM
mode had prevented NPC attacks. This does not establish exhaustive acceptance of
every other entry, drop or special mechanic in that checkpoint.
