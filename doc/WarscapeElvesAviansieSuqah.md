# Elf, Aviansie, Hobgoblin and Suqah checkpoint

The user confirmed the preceding ordered batch working with drops, then requested
these four families in order and delegated routine decisions. Six new entries
bring the catalogue to **289 entries / 58 families**. All seven existing Hobgoblin
variants are retained: the current complete Wiki page hash is identical to the
reviewed source, and IDs/stats/attack ticks match individually. No duplicate
Hobgoblins or permanent spawns were added. New gameplay/visual acceptance is pending.

## Entries

Reviewed source facts and retrieval hashes (7 November 2026) are in
`contrib/warscape/enemies/elves_aviansie_suqah.json`.

| Entry | Variant | Source HP | Attack ticks | Maximum hit | Slayer XP reference |
| --- | --- | ---: | ---: | --- | ---: |
| 901700 | Elf Warrior (OSRS lletya_1) | 105 | 4 | 10 | 107.5 |
| 901701 | Elf Warrior (OSRS lletya_2) | 105 | 4 | 10 | 107.5 |
| 901702 | Aviansie (OSRS gwd_69) | 70 | 4 | 8 ranged | 70 |
| 901703 | Aviansie (OSRS gwd_148) | 139 | 4 | 16 ranged | 139 |
| 901704 | Suqah (OSRS dual_melee_111) | 105 | 6 | 10 | 107.6 |
| 901705 | Suqah (OSRS shield_hybrid_111) | 105 | 6 | 10 melee / 10 magic | 107.6 |

Existing Hobgoblins: 901236-901242, source NPC IDs 3049, 3050, 3286, 3287, 3288,
3289 and 2241; levels 28/42/28/28/28/28/47. Their accepted stats, loot, models,
cadence and source policies remain unchanged. See `WarscapeMartialFamiliesBatch.md`.

Displayed HP/damage retain Warscape's tenfold scale. Slayer values are reference
metadata only: no skill, gates, tasks or Slayer XP rewards were added.

## Elf Warriors

Two level-108 Lletya forms use the source's matching combat/loot and distinct
Blood Elf appearances: male guard display 15511 and female 15510, equipped with
native polearms. Source Ranged zero is preserved. These are neutral stab-melee
prototypes with source max hit 10 and four-tick cadence. Native WoW reach applies;
exact OSRS halberd tile reach and quest access remain future work. Iorwerth/archer,
Prifddinas and other Elf variants are not implied complete by this release.

They always give Bones. The members main table includes Crystal teleport seed
25/128, one-charge teleport crystal 1/128, herbs 15/128, the source Coin outcomes,
gear, food, ore and gem branch. Teleport items are collectibles, without travel
functionality. Ordinary combat XP retains existing Warscape rules; source XP
bonus percentages and Slayer tasks are not separately activated.

## Aviansie: ranged combat and airborne melee protection

Selected low/high tiers are 69 (NPC 3169, Ranged 71/Defence 70/HP70) and 148
(NPC3176, Ranged151/Defence160/HP139). Both attack with ranged shots every four
ticks and never fall back to melee. Source max hits are 8/16. Native ranged chase
maintains a roughly 20-yard engagement distance; casts require a player target,
30-yard range and line of sight. This is not a God Wars NPC-faction battle system.

One custom shot uses source Ranged stats/attack bonus against the player's
Defence level, stance and Magic-independent Ranged equipment defence. The native
spell is only the animation/projectile carrier: default damage and native accuracy
are replaced by one server-owned source roll. Damage uses the existing scale.
Native damage immunities are retained, while WoW armour/crit/resist layers are
not added over the source calculation. Player ranged/magic attacks continue
the existing native player spell paths; this milestone adds NPC ranged combat,
not a new player ranged XP/formula system.

Ordinary player melee and direct melee-class damage cannot hurt these airborne
entries. Auto-attack rolls and direct melee spell damage are zeroed before their
combat packets; the AI supplies a throttled chat diagnostic and a damage guard.
Blocked damage grants no melee XP. Ranged/magic remain usable. Current functional
weapon definitions have no OSRS halberd/salamander categories, so those source
exceptions await explicit weapon support; no guessed spear exemption was added.
Native AoE/aura edge cases and other WoW class ability interactions are not
exhaustively verified.

Appearance is Skettis Arakkoa display17864, scales1/1.15, with native hover-height
and movement flags. Corpse hover is cleared on death. This is a model stand-in,
not a bespoke flying/flapping Aviansie asset. Hover, pursuit, projectile visuals,
corpse grounding and loot reach require the user's client test. No flight path,
terrain or client executable changes.

Guaranteed Bones plus 1-6 Feathers and the source main table are installed.
Rune dagger(p+), Runite limbs, adamant bars, runes, food, empty and gem outcomes
retain quantities/chances. Collectible stacks do not model bank-note conversion,
poisoned weapon functionality or diary effects. Armadyl gear aggression protection,
GWD affiliation/wars, Wilderness/diary/task/tertiary conditions remain future work.

## Suqah: melee and hybrid forms

The Wiki images identify version4/NPC790 as dual-weapon melee and version1/NPC787
as shield hybrid. Both source forms use level111, six-tick cadence and source
Attack/Strength/Defence95, Ranged/Magic1, HP105; those published low caster stats
are retained. Models are Ice Thistle Yeti10579 and Patriarch10946 with different
sizes. They follow Kieran's bulky-yeti direction, without reproducing the exact
hairless body, weapons or shield. Both are hostile stab attackers, max hit10.

The hybrid chooses magic only while in native melee range and line of sight.
The hit handler repeats the melee-range check, so it does not damage a distant
safespot target through an already-started cast. The prototype chooses magic on
half its ready melee-range attacks and splits magic equally between water/ice;
the Wiki does not publish selection odds. Water damage rolls0-10. An accurate
ice attack deals a fixed10 source damage (100 displayed), matching the stated
unprotected behaviour. Accurate ice also applies a three-second native root.
That duration is an explicit prototype choice pending exact source evidence.
Native root dispels/diminishing-return/interrupt behaviour is retained; this does
not claim full OSRS freeze-immunity timing or Protect from Magic support.

Magic accuracy uses published Magic1 +9 against separately truncated 70% player
Magic /30% Defence, +8 and stance, and Magic equipment defence. Native spell
immunities apply. Damage is applied once, without an extra native spell roll.
The old Druid, Scarab and lizard behaviours retain zero-default new options.

Both Suqah forms always give Big bones and Suqah hide. The main roll uses the
source129-slot table: tooth69, guam30, marrentill25 and gem5. The quest-dependent
special-tiara pre-roll and tertiary drops are excluded. Hide/tooth are collectibles,
without Lunar Diplomacy quest progression. Source elemental weaknesses and quest
access remain separate work.

## Fractional Slayer reference and reusable configuration

The additive unsigned `source_slayer_xp_tenths` column preserves 107.5/107.6
exactly. The existing integer `slayer_xp` column keeps the whole part for new
fractional entries; the new precise field is authoritative. Every earlier row's
new field defaults to0 and falls back to its unchanged legacy reference. No
existing integer value, character XP, XP curve or persistence schema is changed.
`.rs enemy` displays the fractional reference and ranged/hybrid diagnostics.

Generated per-entry behaviours now carry ranged maximum, airborne flag, primary
and alternate spell IDs, and melee-only magic flag alongside the existing
finisher/poison options. Shared script execution remains separate from the data.
Source profile/loot ownership and the existing registry are reused.

Four dedicated stock-format Spell.dbc entries are appended:

- 900710 Aviansie shot: native Shoot6660, scripted ranged hit/damage.
- 900711 Suqah water wave: native Waterbolt31707, scripted magic hit/damage.
- 900712 Suqah ice barrage: native Ice Lance30455 visuals, fixed accurate hit.
- 900713 Suqah freeze: native Entangling Roots339 with every secondary effect
  cleared, preventing its original periodic damage. Only the root remains.

Ten new item IDs902369-902378 are collectibles. All earlier Item.dbc/Spell.dbc rows,
string offsets and unrelated locale MPQ payloads are preserved. The new spell
records retain the native234-field layout; selected-effect clearing is bounded
and tested. Native hover APIs are used; no custom-client object fields, allocator,
memory layout, executable, addons, saved variables or settings changed.

## Verification and deployment - 7 November 2026

```powershell
py -3.13 contrib/warscape/enemies/run_checks.py
.\work\enemies-venv\Scripts\python.exe contrib/warscape/enemies/check_models.py --client 'C:\Wrath of the Lich King'
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

96 Python tests, isolated Debug C++ assertions, model/equipment checks and full
RelWithDebInfo worldserver build passed. Coverage includes exact loot marginals,
feather ranges, no duplicate Hobgoblins, precise XP bounds/round-trip metadata,
ranged/airborne rules, melee-only magic, stance defence, native DBC preservation,
root-without-DOT and new CDF boundaries. Previous 283 pool/metadata and8,989 outcome
rows are unchanged, apart from the new zero-default reference field. Prior
behaviour fields retain zero defaults. These are automated/source checks, not
in-game packet, root, projectile or gameplay acceptance.

Migration `2026_11_07_10_world.sql`, SHA-1
`BEAE6A28EB9FD087F6DA8D5C8AAD6178491A0FA6`, adds one metadata column, three families,
six creature/profile/speed/variant rows, four equipment rows, ten items,432 native
loot rows and three new spell-script bindings. Only new creature/variant rows
are updated; no character migration, DELETE/DROP or earlier balance edits.
Preconditions catch collisions/partial application; postconditions verify schema,
legacy zero defaults, source facts, quantities and script ownership. All eleven
enemy migrations pass. World status:42 applied /6,952 archived /none pending.

With zero online characters and the stock client closed, both servers were
stopped; `db.py apply` made a fresh verified backup, applied SQL, checked its
postconditions and recorded its immutable hash. Existing rows across eleven
affected world tables and all character skill XP matched pre-migration hashes.
Backup (integrity checked, restore not tested):
`C:\WarscapeBackups\world_20261107T183747_804247Z_d315ae48.sql`
(297,710,424 bytes,190 tables /3 views).

Runtime: `C:\Warscape\Server`; client: the previously authorized stock
`C:\Wrath of the Lich King`. Previous binary/PDB, Item.dbc, Spell.dbc and patch:
`C:\WarscapeBackups\Elves-20261107-deploy`.
Prepared assets: `C:\WarscapeBackups\Elves-20261107-prepared`.
Five installed files matched final build/prepared hashes. All ten item displays
and four new spell records matched their reviewed data; previous records/strings
and unrelated patch payloads were checked intact. The binary includes the
pre-existing unrelated `cs_gobject.cpp` edit; it is excluded from this commit.

Both servers reached ready state with database connectivity. Startup loaded292
Warscape profiles,294 creature definitions and290 speed overrides. New spell
scripts validated without new encounter/item/loot/metadata errors. Existing
Mining, item900500 and unrelated GameObject900700 quaternion warnings remain.
No manual WoW session was launched or operated by the agent.

## Exact user acceptance steps

Close/reopen WoW fully to load the new client data. Use a clear GM testing area,
one temporary spawn at a time:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.npc add temp loot 901700
```

Select it, use `.rs enemy` and check stats, polearm/model, retaliation, cadence,
attack/death animations and Bones/main loot. Repeat901701; the Slayer reference
should show107.5. The new values remain references, not actual Slayer awards.

For Aviansie901702 then901703, confirm ordinary melee causes no damage or XP and
produces the diagnostic. Engage at range with a working ranged/magic ability.
For a GM-only loot check without configuring a weapon/spellbook, select it and
use `.cast 42833 triggered` (native high-rank Fireball); this checks magic access
and loot, not player OSRS spell formulas. Observe incoming ranged shots from a
distance, LOS/range handling and no melee fallback when close. Check hover and
corpse/loot reach. Bones and1-6 Feathers must appear alongside the main roll.
These enemies can kill low-stat characters; high tier max16 is160 displayed.

Recheck existing Hobgoblins901236/901237/901242 for unarmed/armed models, source
stats, cadence and their accepted Bones/main tables. No new Hobgoblin IDs.

Spawn Suqah901704 then901705. Both give Big bones and hide plus main loot. Confirm
melee-only versus hybrid, no hybrid spell damage out of melee range, water rolls,
accurate ice100 displayed and brief root expiry/restored control. Check the107.6
reference, targeting, death/evade/cast cleanup and quest tiara exclusion. Native
root interactions and precise source timing remain unverified until observed.

Relog with new drops and check inventory/XP. Recheck the preceding lizard cooler,
Scarab poison and Druid if practical. Temporary corpses remain30 seconds. Small
samples do not prove rare odds; record only observed results. No permanent
populations were created.

## Recovery and remaining scope

If needed, stop new temporary spawns and prepare a compatible corrective binary
or additive migration. Keep all item/DBC records and character XP, especially
items players own. Do not edit applied SQL/history or restore/delete data as
routine rollback. Older binaries lack the new ranged/hybrid guards and precise
reference field and are not equivalent gameplay rollback. Restore needs separate
review and has not been tested. No privileges changed.

Source exceptions, additional variants, GWD affiliations, exact OSRS spell/prayer
systems and functional gear remain separate work. Do not begin another checkpoint
before user feedback. Next supplied families should continue the user's list order.

## Sources

- [Elf Warrior](https://oldschool.runescape.wiki/w/Elf_Warrior)
- [Aviansie](https://oldschool.runescape.wiki/w/Aviansie)
- [Suqah](https://oldschool.runescape.wiki/w/Suqah)
- [Hobgoblin](https://oldschool.runescape.wiki/w/Hobgoblin)
- [Template:HerbDropLines](https://oldschool.runescape.wiki/w/Template:HerbDropLines)
- [Module:GemDropLines](https://oldschool.runescape.wiki/w/Module:GemDropLines)
- [Gem drop table](https://oldschool.runescape.wiki/w/Gem_drop_table)
- [Bestiary](https://oldschool.runescape.wiki/w/Bestiary)
- [Wiki NPC combat calculator](https://github.com/weirdgloop/osrs-dps-calc/blob/main/src/lib/NPCVsPlayerCalc.ts)
