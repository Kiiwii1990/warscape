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

Do not run a rollback after characters have earned Agility XP: dropping the
column would permanently delete that progress. If rollback is required before
Agility XP has been awarded, stop the server, take and verify a fresh character
database backup, then run:

```sql
ALTER TABLE `warscape_skills` DROP COLUMN `agility_xp`;
```

Rollback also requires reverting the server code that reads/writes the column.
After any Agility XP has been earned, preserve the column and XP data; rollback
must instead retain compatible persistence or first export and separately
preserve every value. Never use a database restore as a routine rollback.

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
