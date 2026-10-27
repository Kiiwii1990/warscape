# Warscape development efficiency rules

Our priority is completing Warscape efficiently while preserving correctness
and existing functionality.

For all future development:

- Begin by reading `AGENTS.md` and the relevant Warscape documentation.
- Work from the existing project at `C:\WoWDev\TrinityCore`, custom client at
  `C:\WoWDev\wowdecomp`, and server at `C:\WoWDev\TrinityServer`.
- Continue existing implementations where present. Create new systems only when
  explicitly requested or genuinely necessary.
- Keep changes focused on the requested feature.
- Reuse existing TrinityCore, WoW client and Warscape functionality wherever
  practical.
- Avoid exhaustive repository searches when relevant files are already known.
- Run targeted tests during development.
- Perform full builds and deployment only when necessary for a meaningful
  testing milestone.
- Do not launch the game for manual visual testing; the user handles this.
- Avoid repeated speculative fixes when the underlying problem is unknown.
- If a blocker requires substantial additional investigation, stop and report
  the problem and available options.
- Use concise completion reports rather than lengthy technical explanations.
- Preserve backups, uncommitted work and unrelated project changes.
- Do not reduce essential validation, data integrity or deployment safety to
  save time.

**Aim to deliver one independently testable improvement per development session.**

If a request is too large, divide it into practical milestones and implement
only the first one unless the user explicitly authorises the rest.

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

# Warscape testing workflow

For Warscape world-generation and client/server tests, use local Windows execution only. The user performs in-game visual inspection and manual gameplay tests; Codex handles development, automated validation, builds, deployment and technical troubleshooting. Do not launch or operate WoW for manual QA unless the user explicitly requests it or approves direct diagnosis of a specific technical issue. Never claim a manual visual or gameplay test passed until the user confirms it. After successful automated checks and safe deployment, provide exact teleport instructions and a short checklist, then stop for user feedback before further checkpoint work. See `doc/Warscape_Design_Notes.md` for the approved workflow history.
