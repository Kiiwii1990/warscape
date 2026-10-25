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
