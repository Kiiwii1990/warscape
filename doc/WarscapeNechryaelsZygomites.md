# Nechryael through Zygomite checkpoint

The user confirmed the prior five-family checkpoint working. This batch adds eleven entries in seven families: **343 entries / 94 families**. New in-game acceptance remains pending.

| Entry | Variant | Combat level |
|---|---|---:|
|902400|Nechryael|115|
|902401|Rockslug, adult|29|
|902402|Smoke Devil|160|
|902403|Sourhog|37|
|902404|Turoth, baby|83|
|902405|Turoth, child|85|
|902406|Turoth, mum|87|
|902407|Turoth, dad|89|
|902408|Wall Beast|49|
|902409|Zygomite|74|
|902410|Zygomite|86|

## Sources and policies

Raw OSRS Wiki pages reviewed 8 November 2026; source IDs, hashes and weighted outcomes are in nechryaels_zygomites.json:
[Nechryael](https://oldschool.runescape.wiki/w/Nechryael), [Rockslug](https://oldschool.runescape.wiki/w/Rockslug), [Smoke Devil](https://oldschool.runescape.wiki/w/Smoke_devil), [Sourhog](https://oldschool.runescape.wiki/w/Sourhog), [Turoth](https://oldschool.runescape.wiki/w/Turoth), [Wall Beast](https://oldschool.runescape.wiki/w/Wall_beast), [Zygomite](https://oldschool.runescape.wiki/w/Zygomite).

Members/no wealth/pre-Legends loot, no quest/task/area tertiary or clues. Explicit residual Nothing remains empty. Source cadence, melee directional defences and tenfold HP/damage retained. Precise Slayer XP/required levels are metadata, without training/tasks/gates. No bosses, superior forms, Greater Nechryael or Ancient Zygomites. Uniques are conditional mutually exclusive prerolls before ordinary loot. Nechryael decimal coin weights10.5/116 and2.5/116 are represented exactly.

Nechryael guarantees Malicious ashes; Smoke Devil and both Zygomites Ashes; Sourhog Big bones; Turoth Bones. Rockslug and Wall Beast have no invented guaranteed bones. Nechryael double rare-seed outcome doubles the chosen seed quantity, with Snape grass simplified to6 instead of3-6; independent seed identities are deferred. Smoke Devil herbs retain quantity mixture1 at2/3 and2 at1/3; Turoth herbs1/2/3 at15/31,10/31,6/31. Multiple herbs select the same herb type; independent identities remain deferred. Source locations without published respawn use prototype15ticks. Most loot items remain collectibles.

Models: FelGuard5047 demon, Worm7549 small Rockslug, AirElemental10315 smoky stand-in, Boar193, Silithid157 at four scales, BogBeast168 as free-standing Wall Beast humanoid (no native wall-hand mesh), FungalMonster16109 at two scales. Native M2 assets resolved and native animation/sounds retained. No new client executable or memory-layout-sensitive code.

## Finishing interactions

Both finisher families retain one source HP through existing damage clamp. Bag of salt902569 finishes Rockslug at4 source HP or lower (40 displayed HP). Fungicide spray dose902570 is a **single-consumable prototype**, finishing a Zygomite below8 source HP (below80 displayed HP). It is not the OSRS ten-charge refillable spray. Fungicide902584 dropped by Zygomites remains a refill collectible with no refill action yet.

Select the living creature, right-click the item in the bag and target it within5yards. Requires valid hostile target, correct configured item, LOS, native same-map/instance distance, not evading and eligible loot ownership. Wrong/dead/out-of-range/other-player tapped targets reject without consumption. Each valid accepted attempt consumes one item, including early attempts above the health threshold. A successful attempt uses normal kill/loot credit. Existing reusable Gargoyle hammer and consumable Ice cooler remain separate and unchanged.

Rockslug autosalt, brine sabre bypass and stop-retaliation/wandering at1HP remain deferred. Zygomite pick-fungi transformation, ten-charge spray/refills and autospray perk are deferred. No auto-finishing is implied by carrying the items.

## Other explicit encounter gaps

Nechryael death-spawn summons are deferred. Smoke Devil uses source Ranged195/max20 against player Magic defence via existing magical-Ranged carrier; poison immunity retained. Facemask/task protection requirements are deferred. Sourhog uses Crush plus existing mixed ranged projectile(max6, ranged bonus20); goggles, unprotected20-30 damage and temporary stat drains are deferred. Turoth leaf-bladed/broad/Magic Dart restrictions, rapid regeneration and cannon/thrall immunity are deferred consistently with current Kurask. Ordinary weapons work. Wall Beast is a free-standing combat prototype: wall holes, trigger/grab/Spiny helmet and linked respawn need a separate placement/interaction checkpoint. Zygomites use existing magical melee lane plus magical-Ranged projectile(max6/10); exact hybrid melee accuracy remains prototype. Permanent player XP is never drained as a substitute for temporary stats.

## Manual acceptance

Restart the verified Wrath client for new item/spell records. Use `.gm off`, then `.npc add temp loot 902400` through902410 one at a time on open walkable ground. No special teleport is needed for temporary summons. Check appearance, name, HP, retaliation, cadence and drops. Smoke Devil should cast; Sourhog/Zygomite can use projectile and melee paths. Wall Beast should fight as a normal free-standing creature, not a wall ambush.

Get `.additem 902569 20` and `.additem 902570 20`. For Rockslug reduce health to40 displayed HP or less; for Zygomite below80. Use the matching item, verify kill/normal loot and one consumed. Test early use on a valid target: one consumed, creature lives. Wrong target, dead target, out-of-range, blocked LOS and other-player tapped target should consume none. Repeated successful use after death must not kill/reward twice. Check both Zygomite tiers and existing Ice cooler/Gargoyle hammer. Rare drops are not guaranteed by a small sample. Relog to check XP/Coins/inventory persistence.

## Deployment and rollback

Additive world migration2026_11_08_04_world.sql through db.py with reviewed specification/preconditions, stopped writers, zero online characters and fresh verified world backup. No character migration/writes. Preserve world rows outside new IDs, all character skill XP/inventory/wallets. Back up matching previous EXE/PDB, Item/Spell.dbc and client patch outside Git. Check deployed hashes, old DBC records/string offsets and unrelated MPQ payloads; inspect only new startup log bytes. Existing native high-level base-stat, item900500 and Mining warnings remain separate.

Rollback requires stopped services and previous coordinated binary/DBC/patch. Keep additive rows dormant; never delete item definitions while characters hold them. Full world restore needs separate review and can overwrite later world edits. Character restore is unnecessary. Backup restore has not been tested.

Deployment 8 November 2026: migration applied/verified;138 Python tests, isolated Debug C++ checks and RelWithDebInfo build passed. Backup C:\WarscapeBackups\world_20261108T010141_622704Z_35011620.sql, SHA2565efc8600270004391aeb2773487968041068c162dd0f73fdbdf1df2bff99c482; restore not tested. Previous runtime files: C:\WarscapeBackups\Nechryaels-20261108-deploy. Binary hashes match build;16 item/five spell records append correctly, old DBC rows/string offsets and unrelated MPQ content preserved. Eleven M2 assets resolve. Both services listening, world ready, no new batch ID/script errors. Existing native high-level base-stat/item900500/Mining warnings remain. Existing world records, XP, inventory and wallets preserved. Gameplay acceptance remains pending.
