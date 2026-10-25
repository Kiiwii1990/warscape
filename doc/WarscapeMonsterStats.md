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
Overrides are per template, including bosses, not per spawned GUID. The migration maps Harvest Golem (36) and Rusty Harvest Golem (480) to the defensive Golem profile, and Goblin Engineer (622), Goblin Mercenary (638) and Goblin Woodcarver (641) to the Goblin profile. Reapplying the seed leaves existing creature mappings intact. These entry identities were checked against the world dump shipped with the server.

Profile 0 is the editable fallback for all unmapped creatures. If tables or profile
0 are absent, neutral built-in defaults apply. Invalid rows are logged and ignored:
bases 1..1000000, growth 0..1000000, overrides 0..1000000, bonuses -64..1000000.
Unknown creature entries and profile references are rejected. Empty tables are safe.
All data loads at startup; SQL edits take effect on restart without recompilation.
No SQL is issued during attacks. Do not call the loader concurrently with map threads.

## Stage 1 combat defaults

The first combat pass replaced player-to-monster hit chance but still passed hits
through WoW weapon DPS, attack power, armour mitigation and creature health. It
also used WoW's level-based attack table for monster-to-player attacks. These
remaining paths explain why raising a WoW level did not make an OSRS level 1
character fight like a level 10 character, and why WoW monsters could take far too
long to defeat.

Player-versus-creature and creature-versus-player melee auto-attacks now use OSRS
Attack/Defence roll probability. Player damage uses the OSRS max-hit formula from
the persistent Strength level and an explicitly temporary zero equipment Strength
bonus; damage is rolled uniformly from 0 through max hit. Monster attack and
Strength rolls use the monster profile. All combat stat lookups use the profile's
base tier and the API no longer accepts a WoW level. Player live health uses the
persistent OSRS Hitpoints level; creature live health uses the profile's Hitpoints
at base tier. A Hitpoints level-up raises live max health by one and heals one.

For this temporary stage, WoW weapon damage/DPS, attack power, hit/avoidance stats,
glancing/crushing outcomes, armour reduction, WoW stamina and WoW level-based
creature offence/health are excluded from melee auto-attacks. Equipment bonuses
are deliberately zero until item bonuses are mapped. WoW weapon attack timers,
animations, targeting, damage/death events, loot and OSRS XP awards remain on the
existing paths. Spells and ranged attacks are outside this Stage 1 melee change.

These are testable starter defaults, not final balance. Profiles remain editable
in SQL; later equipment and combat stages can replace the zero-bonus defaults.
Existing character XP persistence and `.rs` attack-style commands remain active.

## Verification

`tests/game/WarscapeCombat.cpp` exercises profile scaling, hit-roll boundaries and
the temporary OSRS max-hit calculation. Build worldserver in Release|x64
using the existing `build/TrinityCore.sln`.

In-game follow-up: use a fresh character and starter equipment against a level 1
creature and the mapped Golem. Compare representative WoW levels while keeping
OSRS skills/equipment fixed, observe incoming damage, and verify skill XP survives
logout/login. These runtime checks require the game and world data.
The SQL migration was applied twice on a fresh temporary MariaDB 11.7 instance.
The second application preserved edited profile values and a creature override.
This validates schema creation, seed mappings and reapplication; live world loading and gameplay
remain to be checked in-game. Existing source backups are excluded from game
compilation by CMake while retained on disk.

The complete worldserver Release|x64 build passed, including the final rebuild.
Build output remains under build/ and was not installed over the running server.

