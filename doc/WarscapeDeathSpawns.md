# Owned Nechryael Death spawns

Closes the missing summon feature for regular Nechryael902400. New Death spawn902500 is a native Imp4449 stand-in, source combat46, stats67/7/30/1/1/60, Slash max2 and4-tick cadence, guaranteed existing Fiendish ashes902327. Source/hash in death_spawns.json: [Death spawn](https://oldschool.runescape.wiki/w/Death_spawn), [Nechryael](https://oldschool.runescape.wiki/w/Nechryael), reviewed8 November2026. No client assets changed.

Owned SummonList tracks GUIDs, cap2 including pending corpse lifetime. Parent only advances a chosen12-second summon timer while it has a living player in melee reach and LOS. Source summon interval is unpublished;12seconds is a prototype setting. No safespot summons. Native60-second timed lifetime. Parent Reset/evade or death despawns its own list. Child targets only the original player's GUID, never proximity-acquires other players; resolves parent/target each update rather than retaining raw pointers. Parent removal/death/evade, target logout/death/map leave/invalid hostility or distance above21yards despawns child.21yards represents7OSRS tiles at prototype3yards/tile. No global list or cross-parent cleanup.

Native WoW auto-retaliate, combat/logout, prayer and player-targetability rules remain. Source single-way exceptions, leaving spawns attackable after parent death and OSRS logout/teleport exceptions are not reproduced: parent death deliberately cleans adds for this checkpoint. These limits are tracked in WarscapePendingWork.md. Only regular902400 is bound; greater/superior Nechryael are outside scope.

## Manual acceptance

`.gm off`; `.npc add temp loot 902400` on open ground. Engage in melee and survive at least24seconds: expect an Imp after about12 and a second after24, never more than two belonging to that parent. Misses do not prevent summoning when the parent has reach/LOS. Check max20 displayed damage per spawn hit. Kill a spawn and inspect Fiendish ashes. Kite more than21yards away, die, relog or change map: no abandoned aggressive add. Kill/evade/delete parent: its adds disappear. Repeat with two parents to check ownership cleanup and independent caps. Safespot parent outside melee or behind LOS: no summons. Let an add survive60seconds: it expires. No special teleport needed for temporary summons.

## Verification/operations

139 Python catalogue tests plus Debug C++ cap/reach/cleanup-boundary checks and RelWithDebInfo worldserver build. Shared-only release precondition regression covers empty-item-list SQL; earlier migration04 verification supersession replaces only the parent AI assertion, retaining every other check/hash. No historical SQL/spec changed. Native lifecycle and callbacks inspected; actual summon gameplay acceptance pending. No client memory-layout code changed.

Migration2026_11_08_06_world.sql verified/applied through db.py after stopped writers, zero players and fresh backup C:\WarscapeBackups\world_20261108T120406_155276Z_2da0929f.sql (restore not tested). Only new NPC/profile/loot rows and parent AI binding change. Preservation hashes confirm all other world rows, unchanged parent fields and existing character XP/inventory/wallets. Previous binary/PDB in C:\WarscapeBackups\DeathSpawns-20261108-deploy. No new item or spell DBC deployment. Rollback requires stopped services, coordinated previous binary and reviewed parent-AI rebind migration; leave new rows dormant. Do not restore character data.

Deployed binary/PDB match build. Both services ready/listening, no new summon script/profile/loot errors in current startup segment. Existing unrelated warnings remain. Source/model lifecycle checks are not manual gameplay evidence.
