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
base tier and the API no longer accepts a WoW level. Stage 1B scales player and
creature live health by 100 from OSRS Hitpoints; HP level-ups increase max health
by 100 per level.

For this temporary stage, WoW weapon damage/DPS, attack power, hit/avoidance stats,
glancing/crushing outcomes, armour reduction, resilience, absorbs/resists, WoW
stamina and WoW level-based creature offence/health are excluded from melee
auto-attacks. Equipment bonuses are deliberately zero until item bonuses are
mapped. WoW weapon attack timers,
animations, targeting, damage/death events, loot and OSRS XP awards remain on the
existing paths. Spells and ranged attacks are outside this Stage 1 melee change.

These are testable starter defaults, not final balance. Profiles remain editable
in SQL; later equipment and combat stages can replace the zero-bonus defaults.
Existing character XP persistence and `.rs` attack-style commands remain active.

## Stage 1A skill visibility and progression

Use `.rs stats` to display Attack, Strength, Defence, Hitpoints, Ranged, Magic
and Prayer levels, total XP, and XP remaining to the next level. Level 99 is
reported as the maximum; OSRS combat level is explicitly marked as not yet
implemented. The existing `.rs accurate`, `.rs aggressive`, `.rs defensive` and
`.rs controlled` commands are unchanged.

OSRS XP thresholds use the standard integer-rounded formula (for example,
83/174/276/388 XP gives levels 2/3/4/5). Level-up messages identify the skill
and new level. Skill XP is saved to the character database and levels are
reconstructed from saved XP at login. Player melee accuracy uses the persistent
OSRS Attack level and the existing attack-style bonus; WoW level is not an input.
The test suite covers threshold boundaries, level changes, XP serialize/restore,
and improved accuracy from a higher OSRS Attack level. Runtime persistence and
combat checks still require in-game playtesting.

## Stage 1B health scaling and GM test commands

Player maximum health is OSRS Hitpoints level × 100 (fresh characters start at
level 10 with 1,000 health). Saved OSRS XP remains the source of skill levels;
older saved Hitpoints below level 10 retain their XP while using the mandatory
level-10 health floor. Creature Hitpoints use the configured Warscape profile
or per-creature `hitpoints_override`, then scale by 100. The fallback profile
remains safe at 10 OSRS HP (1,000 displayed HP). Increasing a Hitpoints level
updates player max health and grants the scaled level-up heal; reducing it safely
clamps current health. WoW level and stamina are not used for these values.

Warscape melee positive damage rolls are multiplied by 100 for both player and
monster auto-attacks; misses and zero rolls remain zero. WoW resilience and
absorb/resist modifiers do not change the OSRS damage result. Flat player and
controlled-creature health regeneration and spell healing are scaled by 100;
percentage-based regeneration remains proportional to the scaled maximum health. XP is derived
from the unscaled OSRS-equivalent damage, preserving the existing attack-style
split and Hitpoints XP rates. Damage variation is not included.

The GM-only commands `.rs setlevel <skill> <1-99>` and
`.rs setxp <skill> <0-200000000>` support all seven OSRS skills. Hitpoints
cannot be set below level 10 or its corresponding XP threshold. Skill names are case-insensitive.
Successful adjustments update Hitpoints health immediately when relevant and
save the character. Internal WoW levels are untouched. The command uses the
existing `RBAC_PERM_COMMAND_SETSKILL` permission; `.rs stats` remains available
under the existing `.rs` permission.

## Stage 1C damage variation

Positive OSRS melee damage rolls use a uniform integer multiplier around 100%.
The default `Warscape.DamageVariationPercent = 20` gives a range of 80% through
120%; set it to zero for strict 100× damage. Values outside 0..99 are clamped
when the server loads configuration. The multiplier is rolled only after a hit
has succeeded and only when the OSRS damage roll is positive. Player and monster
melee use the same helper. Spell damage, environmental damage and scripted
encounters are unchanged.

The unscaled OSRS damage roll travels with the melee event and remains the basis
for combat and Hitpoints XP. Displayed damage variation therefore does not change
XP awards. Tests cover the min/max boundaries, a million-sample mean, preserved
zero rolls, OSRS-based XP and existing accuracy/health behavior.

## Legacy WoW weapon and Defence skill investigation

Combat skill-up checks are triggered in `Unit::ProcSkillsAndReactives` for melee
auto-attack outcomes. That path calls `Player::UpdateCombatSkills`, which calls
`UpdateWeaponSkill` for weapon proficiencies and `UpdateDefense` for Defence.
Warscape player-versus-creature and creature-versus-player accuracy returns from
the OSRS roll branches in `Unit::RollMeleeOutcomeAgainst` before reading WoW
weapon or Defence skills. Those skills still affect the legacy non-Warscape
attack table, WoW-derived dodge/parry/crit calculations, and fallback combat.

The item template maps weapon subclasses to skill IDs, and equipped weapon skill
values are still used for proficiency/equipment compatibility. The same skill
data is sent to the client and can be visible in its skill UI; hiding it would
require filtering skill initialization/update packets and could break item
requirements. Stage 1D removes the combat proc callback and player helper methods
that advanced legacy weapon and Defence skills. It retains skill records,
weapon proficiency checks, level-based skill setup, client skill fields, and all
non-combat skill progression. The callback still handles unrelated reactive
aura behavior. WoW skill-based combat calculations remain in legacy PvP, ranged
and other non-Warscape attack paths; the implemented Warscape melee paths return
through OSRS calculations before consulting them.

## Long-term attribute replacement objective

Replace WoW combat attributes incrementally with OSRS equipment attack/defence
bonuses, Strength/Ranged Strength/Magic bonuses, Prayer bonuses and OSRS weapon
attack speed. Keep engine-required WoW values until each dependency has a tested
replacement. This objective is tracked for later isolated stages; Stage 1C does
not change the attribute system.

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

## Stage 1E weapon archetypes and equipment bonuses

`WarscapeEquipment.h` defines OSRS-style weapon archetypes and signed attack,
defence, Strength, Ranged Strength, Magic Damage and Prayer bonuses. WoW
subclasses infer broad categories; sword items default to Longsword, two-handed
swords to TwoHandedSword, and polearms to Spear. Item IDs in
`warscape_item_bonus` can override those categories, which is required to
distinguish scimitars, short swords and halberds. Additional ranged archetypes
are represented now for later use.

The repeatable world migration `2026_10_25_00_world.sql` creates one row per
item template, including future tier, attack speed and generation metadata.
Its four initial fixed QA profiles are item 2494 Stiletto (Dagger), 2488
Gladius (Longsword), 2489 Two-handed Sword, and 2493 Wooden Mallet (Warhammer).
The values are deliberately distinct test values, not balance targets. No
random rolls or per-instance records are created. `INSERT IGNORE` preserves
existing server-side custom profiles if the migration is replayed.

ObjectMgr loads the table once after item templates. Missing rows contribute
zero bonuses; invalid rows are skipped. Player equipment totals are recalculated
from all equipped slots on demand, so equip, removal and weapon switching do
not depend on mutable accumulated state. Current styles still provide the same
OSRS level bonuses. Damage type is selected from the weapon archetype: Accurate,
Aggressive and Controlled use its archetype default; Defensive prefers stab
except for blunt weapons, which use crush. The current style buttons do not
otherwise encode OSRS attack types. Melee accuracy uses
the selected attack bonus; melee max hit uses the summed melee Strength bonus.
WoW Strength, Attack Power, item level and WoW item combat modifiers remain
outside these OSRS calculations. Other WoW stat infrastructure and ranged/magic
combat remain intact.

The `.rs bonuses` diagnostic prints the total of all fourteen bonus channels
and the selected melee damage type. It is read-only. Automated coverage includes
archetype inference/overrides, slot aggregation and recalculation, signed bonus
lanes, style/type selection, OSRS accuracy and max-hit effects. Live database
loading and the in-game checks remain part of Stage 1E player testing.

