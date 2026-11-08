# Killerwatt through Basilisk checkpoint

The user confirmed the preceding Waterfiend/Banshee/Revenant batch working, then
requested Killerwatt, Nagua, Aberrant Spectre, Aquanite, Araxyte and Basilisk.
Ten representative variants add six families: **311 entries / 72 families**.
This is an encounter/loot checkpoint, not completion of every family variant or
all OSRS mechanics. New in-game acceptance is pending.

## Entries

| Entry | Variant | Combat level | Source HP | Attack ticks |
| --- | --- | ---: | ---: | ---: |
| 902000 | Killerwatt (OSRS regular_55) | 55 | 51 | 2 |
| 902001 | Sulphur Nagua (OSRS sulphur_98) | 98 | 100 | 4 |
| 902002 | Frost Nagua (OSRS frost_104) | 104 | 120 | 5 |
| 902003 | Earthen Nagua (OSRS earthen_128) | 128 | 160 | 4 |
| 902004 | Aberrant spectre (OSRS regular_96) | 96 | 90 | 4 |
| 902005 | Deviant spectre (OSRS regular_169) | 169 | 190 | 4 |
| 902006 | Aquanite (OSRS lure_145) | 145 | 180 | 5 |
| 902007 | Araxyte (OSRS regular_96) | 96 | 60 | 4 |
| 902008 | Araxyte (OSRS regular_146) | 146 | 100 | 4 |
| 902009 | Basilisk (OSRS regular_61) | 61 | 75 | 4 |

Warscape retains tenfold HP/damage display. Source IDs, stats, directional defence,
precise Slayer XP, hashes and complete weighted outcomes are in
`contrib/warscape/enemies/slayer_elementals.json`. Source pages were read on
8 November2026; four shared loot-template snapshots match previously reviewed
weights byte for byte. Slayer levels/XP remain reference metadata, without a new
Slayer skill, gates, tasks, reward unlocks or training system.

Sources: [Killerwatt](https://oldschool.runescape.wiki/w/Killerwatt),
[Nagua](https://oldschool.runescape.wiki/w/Nagua),
[Sulphur](https://oldschool.runescape.wiki/w/Sulphur_Nagua),
[Frost](https://oldschool.runescape.wiki/w/Frost_Nagua),
[Earthen](https://oldschool.runescape.wiki/w/Earthen_Nagua),
[Aberrant](https://oldschool.runescape.wiki/w/Aberrant_spectre),
[Deviant](https://oldschool.runescape.wiki/w/Deviant_spectre),
[Aquanite](https://oldschool.runescape.wiki/w/Aquanite),
[Araxyte](https://oldschool.runescape.wiki/w/Araxyte),
[Basilisk](https://oldschool.runescape.wiki/w/Basilisk).

## Combat and model choices

Killerwatt uses Storm Revenant26382, approaches melee, and launches magical-Ranged
lightning when out of melee reach. Two-tick cadence; protected melee/ranged caps
6/8, rising to15 without Insulated boots worn on the feet. Ranged uses Ranged67,
zero ranged bonus and player Magic defence; melee uses Attack50/bonus30. Separate
bonus fields preserve that distinction. Neutral until engaged. The stock model
has no passive orb-to-limbs click transformation; exact source mode-switch exploit,
13-tile reach and protection prayers are deferred (prototype range30 yards).

Lesser Nagua use Flame Revenant25680, Ice Revenant26177 and Earthbound27392.
They retain flat armour-4 through the existing player melee damage pipeline.
Sulphur and Earthen perform two source-melee components6+5 and7+6; Frost performs
two Magic components6+6 using Magic90/bonus70. Each component has its own accuracy
and damage roll, emitted in one server attack event, stopping if target/caster
dies. Source correlation and per-component timing are not published and are not
claimed exact. The native spell's ordinary damage is suppressed; it is a carrier.

Earthen reinforces on a positive non-periodic hit while already below60% HP.
Its melee defences change30/50/50 to50/70/10, with a one-time message, and reset
on evade/respawn. Crush-special weakening, burn clearing and Prayer restoration
are deferred. Frost's ground icicle/Prayer-drain special is deferred. Moons of
Peril, Amoxliatl, quest forms and other bosses are not part of this release.
Nagua/Killerwatt use native elemental type; no undead-tag benefit is invented.

Regular/Deviant Spectres use Tainted Arcane Wraith15406/Doom Wraith14703 at distinct
scales. They cast source Magic at range, max8 with a Nose peg in the head slot.
Without it their special always passes the custom accuracy roll and rolls0-14;
native damage immunity still applies. Temporary skill drains are not implemented,
and persistent XP/levels are never reduced as a substitute. No Slayer helmet or
Salve effects, quest access or superior variants are added.

Aquanite uses Zangarmarsh Sporebat17751, casts Magic170/bonus50, max18, and stays
ranged. A player Slash auto-attack severs its lure before accuracy is rolled, even
if the hit misses, and reduces Stab defence60 to10. Slash/Crush defence remains80.
One message is emitted; state clears on reset. This uses Warscape's existing
weapon damage-lane classification; there is no new independent OSRS weapon-option
selector or special-attack system. The stock Sporebat has no removable lure model.
Sailing access, cannon immunity, superior encounters and weaknesses are deferred.

Araxytes use dark Dreadfang Lurker8271 at two scales, with source Crush melee,
maximum13/17. Positive melee damage has a prototype25% chance to apply venom.
Venom ticks every18seconds, starts6, increases2 per tick to20, and remains until
native poison dispel/death. Severity is stored in the existing aura amount with
recalculation disabled. Native `Aura::SetLoadedState` restores saved amounts before
recalculation; no separate player table or raw creature pointer is used. Severity
advances before damage so death/removal cannot leave a post-damage aura access.
Loaded caster GUID/entry identifies the configured source even after despawn.
Reapplications do not reset/escalate a running venom aura. Native poison dispels
cure it fully; OSRS antipoison-to-poison conversion and antivenom items are not
implemented. Relog/timer phase and cleanse interactions still need user QA.

Basilisk uses classic Crystal Spine Basilisk601, neutral Slash melee max5.
**Its stat-draining ranged gaze and mirror requirement remain unfinished.** Mirror
shield is available as native off-hand equipment for future mechanics, but has
no scripted gaze benefit in this checkpoint. No substitute stun or artificial
attack lock is invented. Basilisk Knights/superiors are outside this release.

Stock models retain native animations/sounds; paths resolved through the verified
client's display/model DBCs and native M2 headers. Colour, scale, movement,
projectiles, hover, death and loot reach require user inspection. There are no
client executable/object-memory-layout or terrain changes.

## Loot and deliberate policies

Members/no-wealth/pre-Legends tables with off-task unique rates. Main pools after
pre-rolls retain full conditional probabilities, quantities and explicit empty
mass. No independent rolls are collapsed into a uniform combined count. Native
byte-sized SQL quantity columns are unchanged; the existing wide-drop/bonus-pool
paths supply full quantities before group/ownership processing.

- Killerwatt guarantees Ashes, uses Mystic fire staff1/512 pre-roll, current
  Energy potion drops and an independent Air diamond1/64 (September2026 update).
- Sulphur blades1/450 is a pre-roll. Sulphur's gem prose says once or twice but
  gives no selection odds; one gem subroll is the explicit checkpoint policy.
- Frost main rates are source-labelled approximations, not proven exact values.
  Frozen tears5-10 at1/10, pendant1/100 and glacial temotli1/500 use independent
  bonus pools. Moon-key tooth and quest/task-only tertiary drops are deferred.
- Earthen includes independent Earthbound tecpatl1/400. No Prayer/crafting use.
- Aberrant herbs use quantity weights1:11/26,2:11/26,3:4/26. Deviant uses
 2:29/46,3:17/46. Each is one selected herb type at that quantity, not independent
  herb identities. Their seed/gem/main pools retain the source probabilities;
  dual Nature/Chaos talisman flags select Chaos for the regular Spectre.
- Aquanite guarantees Big bones; off-task tendon1/3500 pre-roll, complete seed/
  coral-frag table and Water rune150-350 range. Items are collectible identities,
  without Sailing/Smithing hopper functionality or long/curved bone tertiaries.
- Araxytes guarantee one venom sac. Main sac2/4 therefore totals3/5. Higher-tier
  common quantities are doubled as listed, including rune ranges240-280; boots
  off-task1/4000 versus1/2000 and head1/2000 are independent bonus drops. No quest
  eggs, superiors or Araxxor boss. Venom-sac consumable use is deferred.
- Basilisk guarantees Bones; Mystic hat(light)1/512 pre-roll, full440-Coin fixed
  outcome and independent head1/2000. Quest basilisk bones/clues/keys are excluded.

Most loot remains collectible, matching earlier checkpoints. Any missing published
main-table mass stays Nothing and is not redistributed. Native regen and existing
player ranged/magic paths remain; source XP bonuses are not new training rewards.

## Equipment

| Item | ID | Slot | Implemented role |
| --- | ---: | --- | --- |
| Insulated boots | 902474 | Feet | Killerwatt damage caps |
| Nose peg | 902475 | Head | Spectre damage/accuracy protection |
| Mirror shield | 902476 | Off hand | Equipable; gaze/drain mechanic deferred |

Native cloth boots/goggles and shield displays are stand-ins, no invented OSRS
armour bonuses or equip-level gates. Carrying boots/peg in a bag gives no protection.
This does not add permanent skill drains, XP changes or an equipment economy.

## Validation and safe deployment

`py -3.13 contrib/warscape/enemies/run_checks.py`: immutable release generation,
131 Python cases, isolated Debug C++ assertions. Coverage includes every new
outcome boundary, exact herb quantity weights, full ranges, guaranteed sac sums,
unique rates, protection slots, double-hit sums, negative flat armour, lure/
reinforced defence states, venom progression/cap and isolated DBC carrier effects.
Build RelWithDebInfo worldserver. Automated checks do not prove live gameplay.

Migration `2026_11_08_00_world.sql` adds only reserved batch records; no schema or
character migration. Use `db.py`, stop writers, require a new verified world backup,
verify all fifteen current enemy/currency contracts and preserve old world/player
hashes. Client/server append33 item and six spell records, keeping old rows/string
offsets and unrelated MPQ payloads intact. Preserve executable/PDB and asset backups
outside Git. Do not overwrite unrelated working-tree changes or existing player XP.

## User acceptance

Fully exit/reopen `C:\Wrath of the Lich King\Wow.exe`, then use:

```text
.gm off
.go xyz -9066.463867 -199.568985 70.600822 0
```

Spawn/finish one creature at a time, substituting the table ID:

```text
.npc add temp loot 902000
```

Inspect all ten models, source-scaled HP, retaliation, attack cadence, approach,
spell visuals, death and corpse reach. Compare protected/unprotected Killerwatt and
Spectres with equipment actually worn in the correct slots:

```text
.additem 902474 1
.additem 902475 1
.additem 902476 1
```

Check Nagua's two damage packets, Earthen reinforcement below60% and reset, Aquanite
lure message from a Slash-classified auto-attack (including miss), then Stab damage/
accuracy with reduced defence. Check Araxyte venom progression and cap, persistence
after normal relog, no reset on another application, and native cleanse/death
removal. Select yourself and use `.unaura 900745` to clear venom after testing if
needed. Venom is not cosmetic and can kill the test character.

Check guaranteed Ashes/Bones/sacs, large Coin/rune amounts, legitimate empty
Spectre/Nagua outcomes, both Araxyte tiers, full-bag and partial/group looting and
relogged item/Coins/XP persistence. A small kill sample does not establish rare
probabilities. Evade, death, logout, teleport and aura-dispel edges need manual
coverage; none are claimed exhaustively tested. Previous mobs/Agility/UI should
remain normal. Stop for this acceptance before expanding further.

## Rollback

Prefer a reviewed forward fix. Do not remove loot identities/DBC records while
characters may own them. An old binary lacks this venom/state/double-hit behaviour;
do not spawn these entries under it. Stop writers, make verified backups, inspect
inventory/bank/mail/auction/aura references and design a separate preservation plan.
Do not delete player items/XP, restore stale character data or rewrite applied SQL.


## Completed deployment record (8 November 2026)

Migration `2026_11_08_00_world.sql` applied/verified through `db.py`. Fresh completed
world backup: `C:\WarscapeBackups\world_20261108T001538_246955Z_1210c235.sql`
(190 tables, three views; restore not exercised). Five previous runtime/client
files retained at `C:\WarscapeBackups\SlayerElementals-20261108-deploy`.

RelWithDebInfo worldserver build,131 catalogue Python tests,15 database safety
tests and isolated Debug C++ checks passed. All fifteen current enemy/currency
contracts and preservation hashes passed. Both services restarted and report
ready, auth3724/world8085 listening. New startup bytes were checked separately
from historical append-only logs: no batch item/loot/script/Warscape-profile errors.
Existing native high-level base-stat, item900500 and Mining warnings remain.

Client/server33 item and six spell records match world classes/displays/slots.
All previous DBC rows/string offsets and unrelated MPQ entries were preserved;
all ten models resolve to native M2 assets. No character persistence, client
executable/object-layout or terrain changes. New manual gameplay/drop/aura/
interruption acceptance is pending; only prior user-reported acceptance is recorded.

User acceptance8 November2026: all six families confirmed working with drops. This does not establish every rare drop, venom persistence or deferred mechanic.
