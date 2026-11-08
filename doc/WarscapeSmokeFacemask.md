# Smoke Devil facemask requirement

Smoke Devil902402 now requires Facemask902587 in the native head slot to take player-owned damage. Source: [Smoke devil](https://oldschool.runescape.wiki/w/Smoke_devil), [Facemask](https://oldschool.runescape.wiki/w/Facemask), reviewed8 November2026. This closes the equipped-mask combat requirement only. Dungeon smoke hazards, temporary stat drains, Slayer task/level gates and Slayer helmet alternatives remain pending. Dust Devil protection is separate and not implemented by this change.

The existing equipment-rule registry now identifies head/off-hand slots. Harpie902301 still requires lantern902586 off-hand. DamageTaken resolves the player or native player owner and reads current head/off-hand each time. Mask in bag, wrong head item or mask passed as off-hand fails the pure rule. Damage is zeroed before attacker DamageDealt/health loss; warnings are creature-local throttled3seconds. Removing/replacing gear during combat takes effect on the next damage event. Direct/DOT and resolvable player-owned pet damage use this same hook; independent NPC/environment damage is outside player equipment checks. Actual pet/DOT/XP behaviour remains manual acceptance, not established by the build.

New mask is class4,cloth/subclass1,InventoryType1,stack1,all classes/races,using native10504 head display only. No inherited WoW stats, source equipment bonuses or existing item changes. The goggles-style head appearance is a native stand-in. No client executable/memory-layout-sensitive code changed. Existing Smoke Devil source stats, loot, spell cadence and AI database binding remain unchanged.

## Manual acceptance

Restart the verified Wrath client. `.gm off`; `.npc add temp loot 902402`. Without mask, damage should be blocked with a message. `.additem 902587 1`; bag-only still blocks. Equip on head: damage should work. Swap to Nose peg or another helmet: damage blocked again. Reequip: damage resumes. Test relog with mask equipped; ordinary enemies still take damage. Test player spell/DOT/pet attacks and no damage-based XP from blocked attacks if practical. Smoke Devil can hit hard; use a suitable test character.

Regression: `.npc add temp loot 902301`, lantern902586 must still be off-hand; facemask alone must not unlock Harpie damage. User confirmed the previous Harpie checkpoint working; no extra individual path is inferred tested. Temporary summons need no special teleport, just open walkable ground.

## Automated checks and operations

139 Python catalogue tests, focused Debug C++ slot/item matrix and RelWithDebInfo build passed. C++ tests include missing/wrong item, wrong-slot mask, correct mask, mask plus unrelated off-hand, existing lantern and unrelated enemy. Migration2026_11_08_08_world.sql adds one item only; historical SQL/specs unchanged. db.py permissions/status, zero online players, stopped writers, fresh verified backup and pre/postconditions required. Preserve all existing world rows, character XP/inventory/wallets and old DBC/MPQ data. No NPC/character schema/data migration.

Rollback: stop services, restore coordinated previous binary/Item.dbc/client patch; leave additive mask definition dormant while characters hold it. No character restore. Full world restore requires separate review; backup restore is untested. Manual gameplay/appearance acceptance is pending.

Deployment8 November2026: fresh verified backup C:\WarscapeBackups\world_20261108T121352_340586Z_a8ad88bd.sql; restore untested. Previous runtime files C:\WarscapeBackups\SmokeFacemask-20261108-deploy. Deployed EXE/PDB match build; Item.dbc appends one correct head-slot row and old DBC/MPQ content is preserved. Both services listening/ready; no new mask/Smoke Devil errors. Existing unrelated native warnings remain. Existing world/XP/inventory/wallet hashes match. Manual acceptance remains pending.
