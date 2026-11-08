# Waterfiend, Banshee and Revenant checkpoint

Five representative entries add three families, bringing the catalogue to
**301 entries / 66 families**. This follows the user's requested order. These
are playable encounter prototypes with explicit limitations below; other
Revenant variants and a complete Wilderness system remain future work.

## Entries

| Entry | Variant | Combat level | Source HP | Attack ticks |
| --- | --- | ---: | ---: | ---: |
| 901900 | Waterfiend (OSRS regular_115) | 115 | 128 | 4 |
| 901901 | Banshee (OSRS regular_23) | 23 | 22 | 4 |
| 901902 | Twisted Banshee (OSRS twisted_89) | 89 | 100 | 4 |
| 901903 | Revenant imp (OSRS unskulled_offtask_7) | 7 | 10 | 5 |
| 901904 | Revenant knight (OSRS unskulled_offtask_126) | 126 | 143 | 5 |

Displayed HP/damage retain Warscape's tenfold scale. Source facts, NPC IDs,
retrieval dates/hashes, complete weighted outcomes, bonus pools and assumptions
are in `contrib/warscape/enemies/water_banshee_revenants.json`.

Primary sources: [Waterfiend](https://oldschool.runescape.wiki/w/Waterfiend),
[Banshee](https://oldschool.runescape.wiki/w/Banshee),
[Twisted Banshee](https://oldschool.runescape.wiki/w/Twisted_Banshee),
[Revenant imp](https://oldschool.runescape.wiki/w/Revenant_imp),
[Revenant knight](https://oldschool.runescape.wiki/w/Revenant_knight),
[shared loot template](https://oldschool.runescape.wiki/w/Template:Revenants/Drops)
and [Revenant mechanics](https://oldschool.runescape.wiki/w/Revenants/Strategies).

## Waterfiend

Uses Northrend Water Revenant display27391 and its native model/sounds. Both
normal/task-area source NPC IDs2916/2917 share one prototype because their combat
stats and ordinary loot agree. No task-access gate or permanent spawn is added.

It chooses water Magic or magical-Ranged equally, max11, with four-tick cadence.
Both defend against the player's Magic defence, following the magical-Ranged
mechanic; offensive stats use the selected Magic/Ranged lane. It never melees and
resists poison. Published Attack/Strength0 are preserved: native monster profiles
now allow zero offensive stats while Defence/HP still require at least1. Existing
profiles had no zero Attack/Strength rows before deployment, and old nonzero
scaling is unchanged. Player skill minima/XP curves are untouched.

Always drops Fiendish ashes and one Water rune. A150-rune main outcome combines
with that guarantee as151; every other outcome adds the guaranteed rune. The
Mist battlestaff1/3000 pre-roll precedes the conditional main pool. Coins2000-3000
retain their full range. Herbs/seeds/gems and other source quantities are installed.
The source gem template sets both Nature/Chaos talisman flags; this prototype
selects Chaos talisman. Location-specific shards, clue objectives and task drops
are deferred. Missing source respawn data uses15-tick metadata; no spawn timer is
activated without permanent placements.

## Banshees and earmuffs

Regular and Twisted forms use classic Banshee displays8782/8783, scale1/1.3.
Protected attacks use the existing magical-melee path: source melee accuracy
against the player's Magic defence, maximum2/9, four ticks.

Without earmuffs worn in the head slot, a Banshee instead screams for fixed6/7
source damage per eligible melee-range attack. Native spell immunity still
applies. A throttled message explains ear protection. Earmuffs item902428 are
functional cloth headgear, stack1, using a stock goggles display rather than a
bespoke earmuff model. Carrying them in a bag gives no protection. No quest or
Slayer equip gate is invented; the Slayer level15 requirement remains metadata.

**Temporary RS stat drain is not implemented.** The current skill architecture
exposes persistent levels/XP, not temporary drain/restore state. Changing permanent
XP to simulate a scream would damage progression and is explicitly avoided.
Twisted Banshee's on-hit regeneration, superior spawns, Catacombs tertiary drops,
Salve/ectoplasmator effects and elemental weaknesses are also deferred.

Normal Banshee uses the current Energy potion drops, including the August2026
replacement of13 Coins with Energy potion(2). Mystic gloves1/512 are a pre-roll.
Twisted's published rows total125/128; the unlisted3/128 remains empty, without
inflating known chances. Its herb prose says three random herbs while the template
says1-3; this checkpoint follows the established policy of three of one selected
herb. This is an explicit interpretation, not a claim of independent herb choices.
Neither Banshee has invented guaranteed Bones; an empty corpse is legitimate.

## Revenants

Imp7 uses the stock imp4449 silhouette. It is opaque: no unsafe ghost/phasing aura
or custom translucent asset was introduced. Knight126 uses the armoured Northrend
Ice Revenant26177 display (native RevenantEarth model). Both use native sounds.

They open with Magic, then choose among Magic/Ranged and in-reach melee using the
lowest current player defensive roll, with Magic winning ties. Imp melee is Stab,
knight Slash. Magic/Ranged use their own published accuracy bonuses and source
stats. The ranged carrier uses a native zero-minimum30-yard range so close-range
selection can actually cast; the inherited five-yard Shoot dead zone is removed
for this new carrier only. Earlier enemy spells are unchanged.

Source descriptions promise very high accuracy and prayer adaptation but do not
publish the exact hidden modifier/selection algorithm. This prototype uses normal
stats-based source accuracy and a deterministic defensive-roll choice; no arbitrary
accuracy floor or prayer system is invented. These limitations matter for balance.
Positive Magic damage can apply a three-second movement-only freeze with a25%
prototype chance. Exact source freeze odds/duration, same-tile multi-target magic,
freeze-immunity windows and protection-prayer responses remain unimplemented.

When attacking below50% HP, a Revenant heals20 source HP, capped at its maximum.
It can do so every15ticks(9seconds), with a uniformly chosen8-25 heals per reset.
Healing accompanies an attack and does not spend an extra turn. Native recovery
visuals are only a dummy carrier: the AI owns the actual capped heal. Cooldowns
and budget are per creature, reset on evade/respawn and cleared on death. The
stand-in healing animation differs from OSRS's lightning strike.

A charged bracelet's75% damage reduction, charge consumption/recharge and death
loss are **not implemented**. The uncharged bracelet is a collectible drop.
There is no Wilderness PvP toggle, entry fee, skull status, player death-looting,
Maledictus, artifact exchange, avarice noting, weapon charging or blighted consumable
functionality. Do not treat these Northshire prototypes as the Revenant Caves.

## Independent loot pools

Revenants use the Wiki's unskulled/off-task formulas:

- `r=floor(sqrt(combat)); A=floor(2200/r); B=15+floor((combat+60)^2/200)`.
- Ancient table chance1/A; common chance(min(A,B)-1)/A; Coins chance(A-min(A,B))/A.
- Common subtable uses its198 factual slots; Coins range1..1+25*r.
- Ether is guaranteed, uniformly over **even** amounts2..2*(r+1): imp2/4/6,
  knight2/4/.../24. No odd ether counts are generated.
- Independent unique probability uses the literal Wiki constant26.667:
  `1000/(26667*A)`, split2/5 avarice and1/5 each Wilderness weapon. The displayed
  decimal may be rounded; it is not presented as proof of the hidden engine rate.
- Ancient listed weights sum39/40. The40th slot remains empty. The unique table
  is treated independently; this is explicit rather than silently renormalized.
- Independent secondary pool has probability100/(250-combat), with the listed
 100-slot relative weights. Skull/task boosts and tertiary bags/scrolls are excluded.

Main and secondary may both drop the same item. They roll independently and are
kept as separate loot entries, preserving the sum distribution and every item.
They are not replaced with a uniform combined range. The authoring/runtime code
supports up to three bounded bonus pools with exact integer weights and stepped
quantity ranges. This avoids multiplying all combinations into thousands of rows.

All additions occur before native ownership/group processing, preserving loot
rights. A creature outcome can now contain only runtime drops with a zero native-loot
reference, including Twisted
260 Coins or an empty Revenant main roll plus guaranteed ether. No placeholder
item is inserted. Item-container loot retains its old missing-template behaviour.
Compiler checks enforce valid quantities/steps, positive complete distributions,
known item identities, pool limits and the18-slot corpse budget. Native SQL
quantity columns and historical applied migrations remain unchanged. Existing
Coins stack capacity and the separate WoW wallet remain intact.

## Verification and deployment

Run `py -3.13 contrib/warscape/enemies/run_checks.py` for immutable artifact checks,
121 catalogue Python tests and isolated Debug C++ assertions. Coverage includes
source zeros, protected/unprotected damage configuration, current potion drops,
full Coin ranges, all main/bonus boundaries, A/B formulas, even ether, independent
unique/secondary rates, invalid pools, finite heal budgets/cooldowns/caps, adaptive
style choices, native spell range, root and dummy-effect isolation.

Build RelWithDebInfo worldserver. Apply `2026_11_07_13_world.sql` only through
`db.py` after permissions/status/precondition review, stopped writers and a fresh
verified backup. It adds only this batch's world records; no schema or character
migration. Verify all fourteen current enemy/currency contracts. Preservation
hashes cover eleven old world tables, every item instance, skill XP and wallet/
level/XP values. Append46 Item.dbc rows and seven Spell.dbc rows to client/server;
verify every prior row/string offset and unrelated MPQ payload remains intact.
No client executable/object layout or player persistence format changes.

## In-game acceptance

Fully exit and reopen `C:\Wrath of the Lich King\Wow.exe`. Keep GM privileges but
turn GM mode off so NPCs can retaliate:

```text
.gm off
.go xyz -9066.463867 -199.568985 70.600822 0
```

Spawn and finish **one at a time**:

```text
.npc add temp loot 901900
.npc add temp loot 901901
.npc add temp loot 901902
.npc add temp loot 901903
.npc add temp loot 901904
```

Check model/scale, source-scaled HP, retaliation, cast/melee cadence, pursuit,
death and corpse loot reach. Waterfiend should cast both attack visuals, never
melee, and always give ashes plus at least one Water rune. Banshees may leave an
empty corpse. Compare their scream against attacks while wearing head-slot gear:

```text
.additem 902428 1
```

Equip Earmuffs; bag storage is insufficient. Protected attacks should use normal
2/9 maximums instead of fixed6/7 screams. No permanent skill loss should occur.

For each Revenant, lower it below half health while allowing it to attack. Check
heals are capped, nine seconds apart, eventually exhausted, and reset on a new
encounter. Compare near/distant combat and changing defensive equipment. Check
magic freeze ends and ordinary control returns. Logout, teleport, target death,
evade and caster death need manual coverage; no such acceptance is claimed yet.

Every Revenant corpse must contain an even positive ether amount in its tier's
range. Main and secondary supplies can appear together. Check Coin amounts,
full-bag/partial-loot behaviour, group ownership with another tester if available,
and persistence of items/Coins/skill XP after normal relog. Small kill samples do
not prove rare probabilities. Earlier creatures and Agility should remain normal.

## Rollback

Prefer a reviewed forward fix. Keep new item identities and assets while players
may own loot/Earmuffs. Old binaries lack bonus pools and would omit guaranteed
ether; do not spawn these entries under them. Stop writers and take fresh backups
before any rollback. Inspect inventories, bank/mail/auction references and shared
assets, then design a separate preservation plan. Do not delete player items,
restore old character data over progress or rewrite applied migration hashes.


## Completed deployment record (7 November 2026)

Migration13 was applied and verified with a fresh completed world backup:
`C:\WarscapeBackups\world_20261107T200554_399639Z_d2b5a943.sql`
(190 tables, three views; restore not exercised). The five pre-batch runtime/client
files are retained under `C:\WarscapeBackups\SpiritEnemies-20261107-deploy`.
An intermediate executable/PDB is retained under
`C:\WarscapeBackups\SpiritEnemies-20261107-runtime-review`.

The RelWithDebInfo build,121 catalogue Python tests,15 database safety tests and
isolated Debug C++ assertions passed. All fourteen current migration contracts
and preservation hashes passed. Asset checks confirmed46 appended item records,
seven spells, correct display/class/slot/effect/range fields, all prior DBC rows
and string offsets preserved, and unrelated MPQ payloads unchanged. All selected
models resolve to native M2 assets.

Both services restarted successfully and worldserver reports ready. The append-only
error log retains the first startup's two runtime-only loot-reference warnings;
those references were corrected to zero without dummy drops, regression-tested,
rebuilt and redeployed. The latest startup segment has no new item/loot/script/
Warscape-profile errors. Native high-level creature base-stat warnings (including
levels115/126), the pre-existing item900500 and unbound Mining scripts remain;
Warscape uses its own profiles for these enemies. Those warnings are not reported
as fixed. Manual appearance/combat, group loot and interruption acceptance remains
pending. No client executable/object layout or character persistence format changed.


## User acceptance update, 8 November 2026

The user confirmed this batch all working before requesting the next six families.
This records the reported gameplay/drop acceptance, not exhaustive tests of every
rare outcome, aura, interruption, group-loot or balancing edge case.
