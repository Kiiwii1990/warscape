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
