# Warscape monster stat foundation

Profiles are custom monster families, independent of WoW creature type. Multiple
creature entries can share a Goblin or Golem profile; bosses can use their own.

Apply `sql/custom/world/2026_10_25_00_warscape_monster_stats.sql` to the world
database before restarting worldserver. The migration only creates two new tables
and seeds missing profiles. Reapplying it preserves edited balance values. It is
also eligible for TrinityCore's custom world SQL updater when configured.
The migration was verified against an isolated temporary MariaDB instance. No working database was modified during implementation.

## Balance data

`warscape_monster_profile` defines all six base stats, independent growth rates,
and attack, strength and defence bonuses for later equipment-like modifiers.
For each skill:

    actual = clamp(base + floor((max(creature_level, 1) - 1) * growth / 100), 1, 1000000)

Growth is hundredths of a skill point per creature level. For example, the seeded
level-50 Goblin has 30 Defence; the Golem has 83. This is a tunable initial balance
formula, not a claim to reproduce Pokemon or OSRS monster stat generation.

`warscape_monster_template.entry` is a creature_template entry. Set `profile_id`
to the desired family. Override columns are final skill values: zero inherits the
scaled profile, while a positive value fixes that skill regardless of level.
Overrides are per template, including bosses, not per spawned GUID.

Profile 0 is the editable fallback for all unmapped creatures. If tables or profile
0 are absent, neutral built-in defaults apply. Invalid rows are logged and ignored:
bases 1..1000000, growth 0..1000000, overrides 0..1000000, bonuses -64..1000000.
Unknown creature entries and profile references are rejected. Empty tables are safe.
All data loads at startup; SQL edits take effect on restart without recompilation.
No SQL is issued during attacks. Do not call the loader concurrently with map threads.

## Combat integration

Player melee auto-attacks use the player's persistent OSRS Attack skill, +3 accurate
or +1 controlled style, and +8 effective level. Monster Defence and defence bonus
come from the cached profile. Standard OSRS attack-roll hit probability is used.
Evade and the earlier physical-immunity checks are preserved. Other melee combat
uses TrinityCore's normal attack table, recovered from the upstream tracked source.

All six monster skills and bonus fields are available to subsequent combat work.
Only monster Defence and defence bonus affect combat in this stage. Hitpoints is
an independent OSRS stat, not applied to live WoW health yet. Damage/health x100,
XP conversion, monster offence, player item bonuses, typed weaknesses, ranged and
magic are subsequent stages. Existing player skill persistence, XP awards and
`.rs` commands are unchanged. No server deployment or live DB mutation is included.

## Verification

`tests/game/WarscapeCombat.cpp` exercises profile scaling and hit-roll boundaries.
The four new Catch2 test cases were compiled and run separately against Catch2 v2.13.9, matching the version pinned by this repository (20,118 assertions passed). Build worldserver in Release|x64
using the existing `build/TrinityCore.sln`.

In-game follow-up: map reviewed creature entries to Goblin/Golem profiles, restart,
check loader counts, compare same-level hit frequencies across the four `.rs`
styles, confirm evade/immunity, and verify skill XP survives logout/login. Check
unmapped creatures as well. These runtime checks require the game and world data.
The SQL migration was applied twice on a fresh temporary MariaDB 11.7 instance.
The second application preserved edited profile values and a creature override.
This validates schema creation and reapplication; live world loading and gameplay
remain to be checked in-game. Existing source backups are excluded from game
compilation by CMake while retained on disk.

The complete worldserver Release|x64 build passed, including the final rebuild.
Build output remains under build/ and was not installed over the running server.
