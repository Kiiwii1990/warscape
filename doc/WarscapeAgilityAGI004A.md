# AGI-004A: Northshire log Agility reward

## Approved behavior

The Northshire log obstacle requires Agility level 1 and awards exactly 8 Agility
XP after a successful crossing. It uses the existing skill XP curve, character
save/load path, and `WCSkills` UI update. No reward is given when starting or
when a traversal is interrupted, replaced, times out, or ends outside the final
landing tolerance. Each active session is removed before its reward is applied.

The seven measured route points and the `.agi start log` command are retained.
Obstacle configuration is separated from the shared traversal/session runner.
Server collision coverage and interruption behavior remain subject to in-game
acceptance; the earlier confirmed traversal covered only the happy path and
movement-button spamming.

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
   and run `.agi start log`.
2. Confirm there is no XP award at start. Complete the seven-point crossing and
   confirm the XP total increased by exactly 8 and the skills UI refreshes.
3. Complete another legitimate crossing and confirm another exact 8 XP.
4. Separately test `.agi stop`, ordinary movement/replaced spline, timeout,
   combat/death, logout, teleport, and map/instance departure where practical;
   confirm each failed attempt gives 0 XP and a later run can start.
5. Relog and confirm Agility XP and level persist and the UI shows the same
   values. Existing Mining fractional XP and Smithing XP/carry should be
   unchanged.

These are user-run in-game checks. A successful build does not verify them.
