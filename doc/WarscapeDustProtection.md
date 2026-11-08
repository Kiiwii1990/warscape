# Dust Devil facemask and ranged-melee damage

Both current Dust Devils902204(level93) and902205(level110) now use the existing Facemask902587 in the head slot. Sources: [Dust devil](https://oldschool.runescape.wiki/w/Dust_devil), [Ranged melee](https://oldschool.runescape.wiki/w/Ranged_melee), reviewed8 November2026. This closes damage mitigation and ranged-defence accuracy, not temporary skill drains, Slayer/task gates, dungeon smoke or Slayer helmet alternatives. Existing stored skill XP is never reduced.

Separate EnemyRangedMeleeProtections records specify source entry, carrier900790, head item, protected max8/10 and unprotected hit16. Dedicated creature AI uses native melee chase, attack timer and reach plus LOS; it emits only this carrier, never an extra ordinary melee attack. Carrier clones existing900771 with native hit-result bypass; native damage immunity is still checked. On hit, the currently equipped mask selects protected source Attack-level/profile-bonus accuracy against player Defence level and ranged equipment defence. Damage is then uniform0..8/10 if accurate, otherwise0. Without mask, each accepted attack is16 source damage without the custom accuracy roll. Range/LOS/living-player guards run again in the spell. No attacks from a distance or through walls. Existing four-tick cadence retained.

Warscape display remains tenfold: unprotected160 damage; protected maximum80(level93) or100(level110), and protected attacks may miss. Bag-only or Reinforced goggles/Nose peg do not count. Player outgoing damage is not blocked: unlike the Smoke Devil requirement, this is an incoming-damage penalty. Native spell damage/death/immunity lifecycle retained. Full OSRS prayer semantics are still wider combat work; this carrier is not proof of Protect from Melee support. Native spell visuals remain stand-ins/manual QA. No new client memory-layout code.

## Manual acceptance

Restart the verified Wrath client for the new spell record. `.gm off`; `.additem 902587 1`; wear mask on head. Summon one at a time with `.npc add temp loot 902204` then902205 on open walkable ground. Both should approach melee; protected hits must not exceed80/100 displayed respectively and can miss. Check roughly2.4-second cadence and no doubled swings. At distance/blocked LOS there should be no attack until it reaches you.

With sufficient HP, remove mask: each attack should deal160 displayed damage and warn. Bag-only or goggles does not protect. Reequip: protected rolls resume immediately. Relog wearing mask; repeat. Kill each and check unchanged loot/XP. Recheck Smoke Devil mask gate, Harpie lantern and Sourhog goggles. These temporary summons need no special teleport.

## Checks and deployment

140 Python tests, focused Debug C++ mask/tier/entry matrix and RelWithDebInfo build passed. Historical02 supersession test restores the two AI predicates and compares the entire previous verification string. No original migration/spec/profile/loot record changed. New900790 school-damage carrier and two AI bindings only; no new item/character migration. Existing new client Item.dbc should be byte-identical, Spell.dbc appends one record.

Use db.py permissions/status, zero players, stopped writers, fresh verified backup and reviewed preconditions/postconditions. Preservation hashes cover all preexisting world rows except exactly two AI bindings, all remaining fields of those NPCs, all character XP/inventory/wallets. Back up EXE/PDB, runtime Spell.dbc and client patch. Verify matching binary hashes, preserved DBC/MPQ records, startup ready and no new binding errors. Existing native base-stat/item900500/Mining warnings are separate. Manual gameplay/visual acceptance is pending.

Rollback requires stopped services, coordinated previous binary/Spell.dbc/patch and reviewed rebind migration for the two NPCs. Keep additive spell binding dormant; do not restore character data. Any full world restore requires separate review; backup restore untested.

Deployment8 November2026: fresh verified backup C:\WarscapeBackups\world_20261108T122545_274741Z_2b594fe6.sql; restore untested. Previous runtime files C:\WarscapeBackups\DustProtection-20261108-deploy. Both current and superseded02 verification pass. EXE/PDB match build; one school-damage carrier appended with native hit bypass, previous Spell.dbc rows and unrelated MPQ data preserved; Item.dbc unchanged. Both services listening/ready; no new Dust Devil script/carrier errors. Existing unrelated native warnings remain. Preservation hashes passed. Gameplay/visual acceptance remains pending.
