# AGI-004A: Northshire log Agility reward

## Approved behavior

The Northshire log obstacle requires Agility level 1. After validating the
player, route, start location and active-session state, the server performs the
obstacle's success roll. For testing, the prototype has a 50% success chance.
A failed roll displays `Agility Roll Failed`, awards no XP, and does not start
movement. A successful roll awards exactly 8 Agility XP immediately before
movement begins, then starts the existing seven-point spline. Completion only
restores normal movement and clears the session. An interruption after an
accepted attempt does not revoke XP; rejected starts and repeated active-session
commands award none. XP uses the existing curve, character save/load path, and
`WCSkills` UI update.

At Agility level 1, the tooltip's `83 XP to next level` is the level-2
threshold, not the character's earned Agility XP. The tooltip separately labels
`Total XP`. A successful attempt from 0 XP should show `Total XP: 8` and
`XP remaining: 75`.

The seven measured route points and the `.agi start log` command are retained.
Obstacle configuration is separated from the shared traversal/session runner.
Server collision coverage and interruption behavior remain subject to in-game
acceptance; the earlier confirmed traversal covered only the happy path and
movement-button spamming.

AGI-005A supersedes the temporary 50% success setting with 100% and adds the
clickable GameObject entry point. `.agi start log` remains a GM diagnostic;
normal play uses the Northshire log object.

## Prepared character migration

`sql/updates/characters/3.3.5/2026_11_03_00_characters.sql` adds nullable-free,
unsigned `agility_xp` with a default of zero. Existing rows receive zero for the
new skill, while every existing XP value and fractional carry remains intact.
The server must remain stopped while applying this migration. This change has
not been applied.

### Rollback plan

The character updater records applied migration names and hashes. Do not remove
`agility_xp` with an ad hoc `DROP COLUMN`: that would leave the migration marked
applied while making the schema disagree with its verification specification.
For a code rollback, stop the server and restore the prior worldserver/addon
files while leaving this additive column in place. The previous prepared
statements omit `agility_xp`, so the default keeps old code compatible. This
preserves any Agility XP already earned and keeps migration history consistent.

If the column ever must be removed, treat that as a new, separately reviewed
schema migration with explicit progress-preservation handling. Do not rewrite
or unapply the recorded migration, restore a database as routine rollback, or
discard earned Agility XP.

## Acceptance steps after migration and deployment are separately approved

1. Record Agility XP and confirm level 1; travel to the measured approach point
   and run `.agi start log`. On `Agility Roll Succeeded`, confirm +8 XP and the
   UI update immediately, before the character steps onto the log. On
   `Agility Roll Failed`, confirm no movement and no XP.
2. While a successful traversal is active, run `.agi start log` again. Confirm
   it is rejected with no additional XP. Finish the crossing and confirm
   completion adds none.
3. Run another legitimate attempt and confirm another exact +8 XP.
4. Start an accepted attempt, then use `.agi stop`, ordinary movement/replaced
   spline, or logout. Confirm the already-awarded +8 remains, no second reward is
   added, and a later run can start. Also confirm invalid location, combat/death,
   teleport and map/instance-rejected starts give no XP.
5. Relog and confirm XP and level persist and the UI shows the same values.
   Existing Mining fractional XP and Smithing XP/carry should be unchanged.

These are user-run in-game checks. A successful build does not verify them.
