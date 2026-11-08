# Leaf-bladed spear checkpoint

Adds usable Leaf-bladed spear 902591 to the existing Turoth/Kurask melee gate. Sources reviewed 8 November 2026: [Leaf-bladed spear](https://oldschool.runescape.wiki/w/Leaf-bladed_spear), [Attribute affinities](https://oldschool.runescape.wiki/w/Attribute_affinities), [Attack speed](https://oldschool.runescape.wiki/w/Attack_speed).

Uses existing warscape_item_bonus Spear archetype 9/tier 0: Stab 47, Slash 42, Crush 36, melee Strength 50, Stab/Slash defence 1 each; all other bonuses zero. Five ticks = three seconds. Native two-handed polearm with Pearl-encrusted Spear 1406 appearance/material/sheath; stack one. Native RequiredLevel 1 is separate from the existing permanent 50 OSRS Attack equip guard. Native polearm proficiency also applies. No new damage formula or skill persistence system.

The shared player damage gate now accepts usable, unbroken main-hand spear with no off-hand weapon on Kurask 902304 and Turoths 902404-902407. Existing sword 902590 and dual-leaf-sword route remain supported. Bag-only items, ordinary weapons, below-50 Attack, unusable weapons, spells, DOTs and pet damage remain blocked through the existing gate. Independent NPC/environment damage remains outside this player equipment gate. Other enemy damage and Brine sabre mechanics remain unchanged.

Source Slayer 55 requirement remains pending with Slayer training/gates. Shop acquisition (source 31,000 coins), poisoning restrictions, battleaxe, broad ammunition and Magic Dart remain pending. Existing global four-stance interface does not implement the spear's three selectable Controlled damage lanes: use `.rs controlled` for the current Controlled/Stab path; exact source style/XP fidelity is not claimed. No character XP or stance changed automatically. Original collectible sword 902566 and prior items/loot remain untouched.

## Manual acceptance

Restart the verified Wrath client to load the new item record. On a character with 50+ OSRS Attack, use `.additem 902591 1`, equip the spear and confirm both hands are occupied. If native polearm proficiency is missing, GM test command `.learn 200` grants Polearms; this does not raise OSRS Attack. Use `.rs controlled` for the current Controlled path and `.gm off` before combat.

Spawn one test enemy at a time: `.npc add temp loot 902304` for Kurask; repeat with 902404, 902405, 902406, 902407 for Turoth variants. Confirm spear damages/kills, normal drops/XP, approximately three-second attack interval and equipment bonus UI totals. Ordinary weapon and bag-only spear must do zero damage to these enemies; sword 902590 must still work. Switch weapons during combat. Check ordinary enemies still accept normal weapons and Brine sabre still finishes Rockslug. Relog with spear equipped and confirm equipment/bonuses remain correct. A below-50 test character should fail equip; do not overwrite existing XP to run this test. Shields/lanterns cannot remain equipped with the two-handed spear.

## Verification and operations

140 Python tests, focused Debug C++ gate/equip matrices and RelWithDebInfo worldserver build passed. Matrix covers all five targets, 49/50 Attack, invalid hands, unsupported damage and unusable weapon. Gameplay, native equip/proficiency, cadence, UI and relog acceptance remain manual.

Migration 2026_11_08_13_world.sql adds only one item and one explicit bonus profile. Reviewed hash/precondition/postcondition checks passed through db.py with stopped writers and zero online characters. Fresh verified backup: C:\WarscapeBackups\world_20261108T130513_396217Z_0db4f143.sql (SHA256 73995cf3a5ca55242ccca62598aee4181bf597a9695e33b0544c660af15547c3; restore untested). All 15 preservation hashes matched, including character skills, inventories/wallets and existing world/profile rows.

Runtime backup: C:\WarscapeBackups\LeafSpear-20261108-deploy. Deployed matching EXE/PDB, runtime Item.dbc and verified client's Data/enUS/patch-enUS-Z.MPQ. Exactly one two-handed polearm record appended; existing DBC rows/strings and other MPQ payloads preserved. Server ready and database verification passed. No new spear/profile errors observed; existing unrelated startup warnings remain.

Rollback: stop writers with characters offline; coordinate restoration of backed-up binary/PDB, runtime Item.dbc and client patch only after checking whether any spear instances exist. Leave additive world definitions dormant while items exist; restoring an old client record set while characters possess the spear is unsafe. Prefer retaining the additive Item.dbc record if rolling back code alone. Do not delete player items, restore character data, rewrite applied migration history or restore a whole world backup without separate review. Backup restoration has not been rehearsed.
