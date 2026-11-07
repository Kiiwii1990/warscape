# Ordered enemy checkpoint: Lizard, Scarab, Druid and Dwarf

The user confirmed both spectral enemies working with drops, then asked for the
remaining families in the supplied list order. This checkpoint follows the four
requested families. Dwarf already had 13 entries: these remain intact and its
missing level-20 variant is added. Total: **283 entries / 55 families**.
The six new entries await in-game acceptance; no permanent populations added.

## Entries and source facts

Stats, exact loot weights, source IDs, retrieval date 7 November 2026 and page
SHA-256 are in `contrib/warscape/enemies/ordered_desert_druids.json`.

| Entry | Source variant | Source HP | Max melee hit | Attack ticks | Guaranteed loot |
| --- | --- | ---: | ---: | ---: | --- |
| 901600 | Small Lizard (OSRS desert_12) | 15 | 2 | 4 | Bones |
| 901601 | Desert Lizard (OSRS desert_24) | 25 | 3 | 4 | Bones |
| 901602 | Lizard (OSRS desert_42) | 40 | 5 | 4 | Big bones |
| 901603 | Scarab Swarm (OSRS normal_98) | 25 | 1 | 1 | Bones |
| 901604 | Druid (OSRS taverley_33) | 30 | 4 | 4 | Bones |
| 901605 | Dwarf (OSRS standard_20) | 26 | 3 | 6 | Bones |

Native displays: thunder lizard 1532 at scale 0.3/0.45/0.65 for the three tiers;
Ahn'Qiraj scarab 7470 at 0.65 for the swarm; robed Night Elf Cenarion druid 4249;
and the previously validated Ironforge Dwarf 1598 with its native equipment.
The Scarab uses one beetle as a swarm stand-in. Source-specific appearance
variants beyond these entries remain future work. Native model checks confirmed
movement/death/attack sequences, not in-game appearance or audio.

## Lizard: functional finishing item

All three desert tiers require an Ice cooler, item **902361**. Ordinary damage is
capped at one OSRS Hitpoint (10 displayed HP). The remaining reserved point is
excluded from ordinary melee XP, including oversized final blows; attacks doing
no damage grant no XP. The item kills through the native kill/loot path exactly
once, without inventing a second melee-damage XP award.

Use the item from the bag and target the lizard. The server checks a living,
attackable, non-evading desert lizard, range/line of sight, and loot ownership
(including its party). Invalid targets consume nothing. A valid attempt consumes
one cooler: below 5 source HP (below 50 displayed HP) it finishes the lizard;
at 5 or more HP it is wasted, with a system message. Reuse on a corpse cannot
consume another cooler or reward again. There is no automatic Reptile Freezer
perk or functional Slayer master/vendor yet; the GM test acquisition is below.
Source Slayer 22 remains diagnostic metadata, as Warscape has no Slayer skill.

The existing herb/fire-rune and seed/potion pairs are preserved. Herbs also give
42 Fire runes, seeds also give Energy potion(3). Standalone portions retain the
published marginals. The gem branch is one roll at 4/128 and two independent rolls
at 2/128: repeated identical items are combined by quantity rather than discarded.
Mystic gloves 1/512 are composed as an independent bonus, an explicit assumption
where correlation is unspecified. Every quantity/chance remains exact under that
policy. Quest/tertiary rewards and functional potions/gear are separate work.

## Scarab: fast attacks and poison

One normal Scarab Swarm entry covers the selected source's level-98 stats, Bones
and one-tick melee (600 ms). A separate monster interval helper admits one tick;
player weapon validation still starts at two ticks. Earlier monster intervals
are unchanged. This is a generic combat prototype; original pyramid trap/chest
spawning, target-owner-only aggression and encounter despawn rules are deferred.
The Giant Scarab boss/ranged encounter is outside this batch.

On a damaging melee hit, a chosen **25% proc chance** applies poison. The page
calls poisoning very likely without specifying a number; this is a documented
prototype decision, not a verified Jagex proc rate. The native poison aura deals
3 OSRS damage every 18 seconds, then 2 and 1 after successive groups of five
occurrences, unless re-poisoned. Refresh restores severity/duration while keeping
the next periodic tick in place. Normal native Poison dispels and death cleanup
apply. This does not reproduce interface-open poison pausing or original minigame
rules. Offline time/persistence follows native saved-aura handling.

The aura stores no raw creature pointer. Its source GUID identifies the behaviour
after the source despawns; when no caster object remains, tick damage uses the
owner safely. Saved max/remaining duration drives decay after relog. This uses
existing character aura persistence with no character schema changes. Actual
long-duration, source-despawn, relog and cleanse behaviour remains manual testing;
pure timing tests and startup checks do not prove those paths.

## Druid: mixed melee and magic

The standard Taverley Druid is neutral and uses four-tick attacks, source melee
max 4 and magic max 5. At melee range it chooses magic half the time; at range it
uses magic within 30 yards and line of sight. Source selection odds are not
published, so 50% is a prototype decision. Native cast timing and green Wrath
visuals are retained. The custom effect prevents native default damage and uses
one OSRS accuracy/damage roll, avoiding a second WoW hit/critical/resistance roll.

NPC magic accuracy uses `(Magic + 9) * (magic attack bonus + 64)`. Player defence
uses separately truncated 70% Magic / 30% Defence, the +8 offset, current defensive
or controlled stance bonus and Magic equipment defence. Native immunity/range/LOS
checks remain. Damage uses the existing tenfold scale. The non-damaging Entangle-
like animation on the Wiki is represented by Wrath here; no unsupported exact
root duration or debuff is invented. Chaos, elder and undead Druids remain future
entries. Guaranteed Bones and the standard herb/rune/coin/robe table are installed.

## Dwarf: fill the missing variant

The existing family 16 and all 13 earlier variants are unchanged. The new level-20
Dwarf uses source NPC 292. The Wiki gives its changed Coin odds only rounded:
1/5.57 for 4 Coins and 1/10.7 for 10 Coins. This release infers 23/128 and 12/128
on the existing 128-slot table: these round correctly and preserve the combined
35 slots. They are a declared assumption, not proof of exact hidden weights.
All other listed main outcomes and the existing no-wealth/pre-Legends gem policy
are retained. This resolves the previously documented deferred variant without
rewriting an applied release or changing earlier Dwarves.

## Native integration and client data

`EnemyBehaviours` is generated from canonical per-entry configuration, separate
from the shared creature AI, item script and spell/aura runners. Five entries use
`npc_warscape_enemy`; the Dwarf retains AggressorAI. The cooler uses
`item_warscape_ice_cooler`. Only the new rows are bound to these scripts.

Three new stock-format Spell.dbc records:

- 900700 Ice cooler: cloned native Ice Lance targeting data, with a dedicated
  item label/description. The item script owns its action; no native Ice Lance
  damage is executed.
- 900701 Druid nature bolt: cloned Wrath visuals/cast timing, dedicated scripted
  accuracy/damage. Its native hit-result suppression prevents duplicate accuracy.
- 900702 Scarab poison: cloned native Deadly Poison aura/dispellability, with
  dedicated periodic damage and timing. Existing Rogue poisons are untouched.

Eight new items 902361-902368 include the functional cooler and seven collectibles.
New robes/potions/gloves are not functional equipment/consumables. Existing shared
items keep their identities. The DBC builder copies 234-field records within the
native layout, adds strings safely and refuses ID collisions/invalid layouts.
All earlier rows/string offsets and unrelated MPQ payloads were checked intact.
No client executable, object fields, allocator, memory layout, addon, settings or
saved variables changed. Custom-client code was not touched.

## Automated checks and deployment

```powershell
py -3.13 contrib/warscape/enemies/run_checks.py
.\work\enemies-venv\Scripts\python.exe contrib/warscape/enemies/check_models.py --client 'C:\Wrath of the Lich King'
cmake --build build --config RelWithDebInfo --target worldserver -- /m
```

86 Python tests and isolated Debug C++ assertions passed. Coverage includes loot
marginals/double-gem quantities, behaviour bindings and invalid definitions, Dwarf
inference, native DBC bounds/collision/preservation, finishing threshold and XP cap,
poison decay boundaries, monster/player speed separation, magic defence stance
and CDF edges. All earlier 277 metadata/pool rows and 8,206 outcomes match the
preceding header. Full RelWithDebInfo worldserver build/model checks passed.
No in-game encounter or UI acceptance is claimed by these results.

Migration `2026_11_07_09_world.sql`, SHA-1
`B2537630809BA2E64617D2BAADB703C8E1AC1F3D`, is additive: three families, six
profiles/definitions/speeds/variants, eight items, loot and new script bindings.
It updates only its new entries; no ALTER/DELETE/DROP or character SQL. Reviewed
preconditions detect ID/binding collisions and postconditions verify exact rows,
quantities, source data and script links. All ten enemy migration checks pass.
World status: 41 applied / 6,952 archived / none pending.

With zero online characters and the client closed, both servers were stopped;
`db.py apply` created a fresh verified backup, applied SQL, checked postconditions
and recorded its hash. Existing data across eleven affected world tables and
all character skill XP match pre-migration hashes. Fresh backup:
`C:\WarscapeBackups\world_20261107T165923_409497Z_b9ac5b57.sql`
(297,521,647 bytes, 190 tables / 3 views; integrity checked, restore not tested).

Runtime is `C:\Warscape\Server`; client is the authorized stock
`C:\Wrath of the Lich King`. Previous binary/PDB, Item.dbc, Spell.dbc and patch:
`C:\WarscapeBackups\Ordered-20261107-deploy`.
Prepared assets: `C:\WarscapeBackups\Ordered-20261107-prepared`.
All five installed files match final build/prepared hashes. Earlier intermediate
builds were retained in backup subdirectories during final poison-refresh/XP-cap
corrections. The binary includes the pre-existing unrelated `cs_gobject.cpp` edit,
which is excluded from this feature's commit. No unrelated worktree files staged.

Both servers reached ready state with database connectivity. Startup loaded 286
Warscape profiles, 288 creature definitions and 284 speed overrides. New spell
scripts validated; no new encounter/item/spell/loot errors. Existing Mining and
item-900500 warnings remain. The unrelated GameObject entry 900700 quaternion
warning is also pre-existing; GameObject and spell ID namespaces are separate.
Neither that object nor its placement was changed.

## Exact in-game checklist

Close/reopen WoW fully so it loads the new Item.dbc and Spell.dbc records. On a GM
character, use a clear area and spawn one NPC at a time:

```text
.go xyz -9066.463867 -199.568985 70.600822 0
.additem 902361 20
.npc add temp loot 901600
```

1. Select each NPC and run `.rs enemy`. Compare source stats/HP, model, attack/death
   animations, cadence, aggression, targeting, loot icons/names and combat XP.
2. Small Lizard 901600: attack until it stays at 10 displayed HP. Further ordinary
   attacks must not kill it or grant damage XP. Right-click a cooler in the bag,
   then click the lizard. One cooler should vanish; the lizard dies and drops Bones
   plus its normal roll. Repeat with Desert Lizard 901601 and Lizard 901602;
   the level-42 tier guarantees Big bones instead.
3. At full health, use a cooler: it is consumed, gives the below-5-HP message and
   does not kill. Wrong target/out of range/another player's tap/dead target should
   reject without consumption. Validate below 50 displayed HP versus 50 or more;
   the threshold is source HP, not the larger displayed health number.
4. Scarab 901603: expect 600 ms melee, max 1 source damage and Bones. Let it poison
   you; watch 18-second ticks, including while it keeps attacking. After killing
   it, verify poison continues and decays (3 then 2 then 1); test relog and native
   Poison cleanse. Emergency GM cure: select yourself, `.unaura 900702`.
5. Druid 901604: neutral until attacked; observe both melee and green nature casts,
   also from 10-20 yards with LOS. Max source damage is 4/5 respectively. Check
   for double hits, excessive WoW damage, range/LOS and death/evade cleanup.
6. Dwarf 901605: Bones plus its ordinary table. Recheck an existing Dwarf such as
   901100 to confirm its original stats, attack speed and loot remain intact.
7. Relog with drops and check inventory/XP. Test both previously accepted spectral
   enemies if desired. Loot-enabled temporary corpses remain 30 seconds; no
   permanent spawns were created. A short sample cannot prove rare probabilities.

## Recovery and remaining scope

Preserve backup files privately. Do not restore/delete player items or edit
applied SQL/history as routine rollback. Stop using new temporary spawns if a
problem appears; deploy a compatible corrective build/additive migration. Older
binaries lack required item/spell scripts and are not equivalent rollback for
these records. Keep new DBC records and items players may own. Restore requires
separate review and is not tested. No database privileges changed.

Slayer gates/training, functional dropped gear/potions, original minigame/quest
conditions and additional family variants remain future work. Next unimplemented
family in the supplied order is Elf; do not start another checkpoint before user
feedback. Record only the user's observed acceptance results.

## Sources

- [Small Lizard](https://oldschool.runescape.wiki/w/Small_Lizard)
- [Desert Lizard](https://oldschool.runescape.wiki/w/Desert_Lizard)
- [Lizard](https://oldschool.runescape.wiki/w/Lizard)
- [Scarab Swarm](https://oldschool.runescape.wiki/w/Scarab_Swarm)
- [Druid](https://oldschool.runescape.wiki/w/Druid)
- [Dwarf](https://oldschool.runescape.wiki/w/Dwarf)
- [Ice cooler](https://oldschool.runescape.wiki/w/Ice_cooler)
- [Poison](https://oldschool.runescape.wiki/w/Poison)
- [Template:HerbDropLines](https://oldschool.runescape.wiki/w/Template:HerbDropLines)
- [Module:GeneralSeedDropLines](https://oldschool.runescape.wiki/w/Module:GeneralSeedDropLines)
- [Module:GemDropLines](https://oldschool.runescape.wiki/w/Module:GemDropLines)
- [Gem drop table](https://oldschool.runescape.wiki/w/Gem_drop_table)
- [Wiki NPC combat calculator](https://github.com/weirdgloop/osrs-dps-calc/blob/main/src/lib/NPCVsPlayerCalc.ts)
