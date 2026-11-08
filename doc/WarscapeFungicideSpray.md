# Refillable Fungicide spray

The user confirmed the seven-family batch working and requested pending mechanics. This is the first independently testable milestone under AGENTS.md. Nechryael summons, equipment restrictions and Wall Beast placement/grab remain queued.

Sources: [Fungicide](https://oldschool.runescape.wiki/w/Fungicide), [Zygomite](https://oldschool.runescape.wiki/w/Zygomite). One refill supplies ten charges.

New spray902585 starts with ten charges in native Item spell-charge slot1. Item creation initializes it from spellcharges_2; existing Item save/load serializes it. Every change marks ITEM_CHANGED. Slot0 stays unlimited so empty bottles remain usable for refill. Chat reports remaining charges; the native use-spell tooltip does not show them. No character schema changes. Original single dose902570 and refill902584 remain unchanged.

Charged use requires a living eligible Zygomite within5yards and LOS, correct map/instance and loot ownership. Invalid targets spend nothing. An accepted attempt spends one charge, including early use; below80 displayed HP it finishes through the existing kill/loot path. Empty bottles cannot kill. Use an empty bottle with Fungicide902584 in bags to consume one refill and restore10; then use again to spray. No partial top-up or auto-refill.

## Acceptance

Restart client; `.gm off`; `.additem 902585 1`; `.additem 902584 2`. Summon `.npc add temp loot 902409` or902410. Early valid use should report9 without killing. Invalid/dead/out-of-range/tapped targets should spend none. Below80 displayed HP it should kill and spend one charge. Relog partly used and empty bottles to verify persistence. Empty use without refill rejects; with refill consumes one and reports10 without attacking. Duplicate requests after death must spend nothing. Recheck old salt/hammer/cooler and XP/Coins/inventory.

## Verification and operations

138 Python tests, isolated Debug C++ charge/refill checks and RelWithDebInfo build passed. Item creation/save/load inspected; live persistence remains unverified. No client memory-layout code changed.

Additive migration2026_11_08_05_world.sql applied and verified through db.py after permissions/status, stopped writers, zero players and fresh backup. Backup: C:\WarscapeBackups\world_20261108T115444_736108Z_c94c4526.sql; restore not tested. Previous runtime files: C:\WarscapeBackups\FungicideSpray-20261108-deploy. Matching EXE/PDB; one additive item/spell row each, old DBC/MPQ content preserved. Both services ready/listening, no new spray startup errors. Existing base-stat/item900500/Mining warnings remain. Existing world rows and character XP/inventory/wallet hashes preserved.

Rollback requires stopped services and coordinated old binary/DBC/patch; leave new item rows dormant. Do not remove definitions while characters hold bottles or restore character data. Full world restore requires separate review.
