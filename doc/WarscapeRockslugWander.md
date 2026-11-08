# Rockslug low-health wandering

Closes Rockslug902401 stop-retaliation/wander at1 source HP. Source: [Rockslug](https://oldschool.runescape.wiki/w/Rockslug), reviewed8 November2026. Existing finisher clamp leaves10 displayed HP; normal damage still cannot kill it. Salt902569 still finishes at40 displayed HP or below. Autosalt perk and brine sabre bypass remain separate pending work.

Shared AI detects the1-source-HP floor before UpdateVictim/attacks. It saves native reaction/regeneration state, makes the Rockslug passive, stops its own attack, removes only chase movement and installs native random roaming within3yards of its transition position. Other control movement/CC is not deliberately cleared. AttackStart refuses reacquisition while wandering or already at the floor. Ordinary incoming damage remains subject to existing1HP floor, so it cannot re-trigger combat attacks or kill without salt. Loot ownership is not cleared to initiate wandering.

Native percentage regeneration is locked during the finishing window to prevent immediate heal/retaliation cycling; it is restored on Reset alongside saved reaction and native default movement. Owner pointer is resolved from native loot ownership each AI tick, not retained. If original owner is dead, logged out, on another map/instance or more than30yards away, native evade/reset runs.3yard roam and30yard abandonment are explicit safe prototype distances, not claimed OSRS tile equivalence. Native home reset/loot clearing then applies. Existing WoW combat flags may remain while the owner stands nearby; exact OSRS combat/logout behaviour is not reproduced. No permanent placement/terrain/navigation edits.

Only Rockslug902401 selects this behaviour. Gargoyle/lizard/Zygomite finishers, native regeneration of unrelated creatures and the previous Crawler/Kurask timer remain unchanged. No database migration, client patch, item or spell changes. No client memory-layout-sensitive code changes.

## Manual acceptance

`.gm off`; `.additem 902569 20`; `.npc add temp loot 902401` on open walkable ground. Attack down to10 displayed HP. It should stop hitting/chasing, move locally and remain at the finishing floor. Repeated ordinary attacks must not restart retaliation or kill it. Use salt within5yards: normal death/loot, one salt consumed. Repeat with two players/group if practical to check tap ownership restrictions. Wrong player/blocked LOS/out-of-range/dead target must retain existing salt rejection behaviour.

On a second Rockslug, reach floor then move more than30yards away, die or log out: expect native return/reset rather than an abandoned permanent passive creature. Resummon or wait for native reset/respawn, engage again and verify normal retaliation before floor. Check another finisher at its floor still behaves as before. Movement is native pathfinding and needs user visual acceptance; no client restart needed. No special teleport for temporary summons.

## Verification/deployment

140 Python catalogue tests and focused Debug C++ threshold/owner-range checks passed. Tests cover dead/1/10/11HP, wrong entry and30yard boundary/invalid owner. RelWithDebInfo worldserver build passed. Native random movement reference position, chase removal, passive UpdateVictim handling and reset/default-movement code inspected. Actual wandering, salt ownership and reset acceptance remain manual.

World status56 applied/none pending; zero characters before stopped services. Previous EXE/PDB in C:\WarscapeBackups\RockslugWander-20261108-deploy. Server-only deployment, no database/client writes. Existing world/XP/inventory/wallet preservation hashes checked. Rollback by stopping services and restoring backed-up binary/PDB; no database or character restore.

Post-deployment: EXE/PDB match build; both services ready/listening, no new Rockslug/shared-AI errors in current startup segment. Existing unrelated native warnings remain. All world/character preservation hashes match. Gameplay/pathfinding/reset acceptance remains pending.
