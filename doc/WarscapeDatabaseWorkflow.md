# Warscape database workflow

Use this workflow for every future Warscape development stage. Python 3 and the
local MariaDB client tools are required. Run commands from `C:\WoWDev\TrinityCore`.
Configuration is read from the ignored `worldserver.conf`. Passwords are passed
only through the child process environment, never command arguments or generated
files. Raw client errors and SQL result rows are suppressed. Do not enable shell
tracing or dump process environments. The script never changes database grants.

## Inspect and back up

```powershell
py contrib/warscape/db.py permissions --database world
py contrib/warscape/db.py status --database world
py contrib/warscape/db.py backup --database world
```

`--database` accepts `world`, `characters`, or `auth`. `--config`, `--client-dir`,
and `--backup-dir` support other installations without editing source. Backups
must stay outside the repository; the default is `C:\WoWDev\Backups`. Keep that
directory private: the script restricts its Windows ACL to the current user,
SYSTEM and Administrators before each export (Unix: mode 0700). Backups contain server
data and must never be displayed or committed. Do not stage directory trees or
use `git add .` when local server files are present.

Each backup has a UTC timestamp and random suffix, uses exclusive creation,
and is published as `.sql` only after the dump exits successfully, its completion
marker is present, and table/view definition counts match database metadata.
A `.sql.json` manifest records byte length, table/view counts, INSERT statement
count, and SHA-256. Failed exports remain `.sql.partial` and are never accepted
as completed backups. Existing backups are never overwritten.

The export includes structure, data, views, triggers, events, and routines when
present. It uses `--single-transaction --skip-lock-tables --hex-blob`: every base
table must be InnoDB, otherwise the script refuses. No concurrent schema changes
are allowed during the dump. Ordinary InnoDB data writes are snapshot consistent.
Stop worldserver/authserver and all other schema writers before migration work.
An account that cannot see every database object cannot certify a complete
backup. Database-wide grants are checked without printing SHOW GRANTS (which can
contain authentication material). Actual dump success verifies export access.

The current account has database-wide schema/data privileges, SHOW VIEW, TRIGGER,
EVENT and LOCK TABLES. Global RELOAD and SELECT on `mysql.proc` are unavailable.
The inspected world database has no routines, events or triggers, and all 186
base tables are InnoDB, with three additional views. Thus no privilege changes
are needed for the tested world backup or the pending Stage 1F migration.
If routines are added, the script requests their export and fails safely when
routine-definition access is insufficient. Mixed storage engines require a
separately reviewed locked backup with appropriate privileges. Role-derived or
table-specific grants are conservatively unverified by this grant parser.

## Review and apply migrations under standing authorization

TrinityCore uses `updates_include` to locate SQL and `updates` to record filename,
SHA-1, state and application time. The tool reads those tables without modifying
them. Windows text-mode newline normalization matches TrinityCore's updater.
Archived rows are recognized using the native default of skipping archived hash
checks; released migrations must match their recorded hashes. Custom SQL is also
checked even if its directory is missing from `updates_include`.

Only a genuinely pending migration can run. Applied files, changed hashes,
renamed/duplicate contents and duplicate filenames cause refusal. Earlier pending
files must be resolved first. Never rewrite an already applied migration; add a
new file. Never rehash a changed file to bypass this guard.

Every executable migration must have a reviewed specification in
`contrib/warscape/verifications/<filename-without-.sql>.json`, containing the migration SHA-1,
`precondition_sql` and `verify_sql`. Each query must return exactly `1` on success.
Use metadata to check expected column types, defaults, nullability, placement,
indexes and table engines, plus targeted assertions for intended data changes.
Preconditions must detect partial/manual application. Both queries are executed
in read-only transactions. The current specification covers Stage 1F.

The user's standing authorization in `AGENTS.md` covers routine additive
migrations, builds, and client/server installation required by a requested or
approved Warscape feature. It includes new custom items in reserved,
collision-checked ID ranges. Do not request separate approval for every migration
or deployment step within that scope. Before applying, inspect the exact SQL and
hash, review its precondition and postcondition specification, and confirm its
changes are additive and within the request. Stop and ask first for destructive
changes, possible player-progress loss, overwriting Blizzard entries, breaking
schema changes, or material work outside scope. Stop and report unexpected ID
collisions or any failed validation. If a higher-priority instruction blocks an
authorized action, identify that specific restriction rather than relying on the
superseded per-migration approval rule.

The user explicitly included migration `2026_11_01_00_world.sql` (SHA-1
`37214478DF0AFA8A5FDA90344B889F30DA719FFF`) and the associated Bronze, Iron,
and Steel Pickaxe deployment in this authorization. Both were applied and
verified on 1 November 2026; this is a completion record, not pending work.

Once the migration is confirmed to be within the user's standing authorization,
stop servers and all other updaters, then apply it through `db.py`:

```powershell
py contrib/warscape/db.py apply --database world --migration 2026_10_25_01_world.sql --approved --servers-stopped
py contrib/warscape/db.py verify --database world --migration 2026_10_25_01_world.sql
py contrib/warscape/db.py status --database world
```

`apply` acquires an exclusive local lock, makes a **new verified backup**, rechecks
history and preconditions, executes one migration, verifies its postconditions,
and inserts its filename/hash into TrinityCore's existing history. It confirms
that ledger entry before releasing the lock. There is no automatic batch apply.
The preexisting backup from workflow setup is never reused for an application.

The lock coordinates this workflow on this machine and backup directory only;
it cannot stop a different host, a manual SQL client, or TrinityCore's updater.
Keep those stopped. The inspected local configuration enables automatic updates
(`Updates.EnableDatabases = 7`, `Updates.AutoSetup = 1`), so **do not start servers
while an authorized migration is pending application or a failed migration is
under investigation**. No configuration was changed during workflow setup. A
permanent change to automatic updater policy should be reviewed separately before
restarting servers.

## Recovery and verification limits

MariaDB DDL can commit implicitly; an interrupted migration can leave partial
changes. Any apply failure retains `<database>.migration.lock`. Do not delete it
and retry automatically. Inspect history/schema privately, compare preconditions,
and plan recovery. Restore requires separate user approval and stopped writers;
never restore over the working database merely to test a backup. The export uses
`--databases`, so it contains database-selection statements; review/remap those
privately before any isolated restore.

When an apply has already executed its SQL but failed only at postcondition or
ledger recording, `db.py recover` can record the existing migration without
rerunning its SQL. It requires the retained lock, a still-pending matching
migration, failed preconditions, passing postconditions, sufficient permissions,
and stopped servers/updaters. It removes the lock only after the recorded hash
is confirmed in TrinityCore's update history. Do not use recovery to bypass a
failed postcondition or unresolved migration state.

Completion checks and checksums verify an export, not a successful restoration.
An isolated restore and row-by-row comparison have not been performed. SHA-256
detects accidental corruption; it is not an authenticity signature. Files are
local plaintext and need normal private storage/retention management.

Offline guard tests (no database operations):

```powershell
py -m unittest discover -s contrib/warscape -p test_db.py -v
```

Setup inspection on 25 October 2026 found one pending world migration:
`sql/updates/world/3.3.5/2026_10_25_01_world.sql`. It adds
`warscape_item_bonus.attack_speed_ticks`, assigns three starter weapon speeds,
and creates/seeds `warscape_monster_attack_speed`. The new column and new table
are both absent. Auth and characters have no pending migrations. This is a
point-in-time record; always rerun `status` and make a fresh backup.
