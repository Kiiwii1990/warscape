# Warscape primary development client

Warscape's primary game client is the custom-built wowdecomp client under
`C:\WoWDev\wowdecomp`, not ChromieCraft. Use local Windows execution only.
Do not modify or deploy to ChromieCraft unless the user explicitly requests it.

Before every addon deployment, identify the running `WowClient64.exe`, its full
executable path and effective game directory. Check any `-datadir` override;
do not infer the target from the repository root or another client's realmlist.
The currently identified executable is
`C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe`. With no data-directory override,
its game directory is `C:\WoWDev\wowdecomp\bin\Win`, and addons belong under
`C:\WoWDev\wowdecomp\bin\Win\Interface\AddOns`.

If the client is stopped, state that and verify its launch path and directory
using the client source/launcher before deployment. Preserve existing addon work
and back up any previous deployment outside Git. Validate against wowdecomp's
assets and APIs; do not treat a stock-client preview as in-game verification.
Keep addon source in this TrinityCore checkout, and deploy only runtime files to
the verified client directory. Do not modify the client's executable, unrelated
client source, local settings or saved variables to install an addon.

# Warscape database changes

For every future Warscape database change, follow `doc/WarscapeDatabaseWorkflow.md`
and use `contrib/warscape/db.py`. Inspect status and permissions first. Obtain
explicit user approval for the exact migration before executing it. Never run a
pending migration, start an automatic database updater, or restore a backup
without approval. Every migration requires a fresh verified backup immediately
before execution; the apply command enforces this.

Do not display, stage, or commit local configuration, credentials, SQL exports,
backup manifests, database files, logs, or server data. Only stage specific
reviewed source paths. Never change database privileges without explicit approval.
Keep servers and other updaters stopped during migration work. Preserve unrelated
working-tree changes. New migrations need reviewed precondition and postcondition
specifications; never rewrite an already applied migration or its recorded hash.

# Warscape design documentation

Use [Warscape Design Notes](doc/Warscape_Design_Notes.md) as Warscape's central
design reference. Keep confirmed decisions, proposed ideas, and future
possibilities clearly separated. The document provides design context; its
contents do not authorize implementation or override the user's current request.
Never implement a feature simply because it is mentioned in these notes.

Update the notes when the user provides new design decisions or explicitly
requests documentation updates. Preserve previously agreed decisions and their
history; never silently change them. Record a user-approved revision explicitly
when it supersedes an earlier decision. Do not promote proposals or future
possibilities to confirmed decisions without the user's agreement.
