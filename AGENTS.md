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

Standing user authorization: when the user requests a Warscape feature or
approves its implementation, that authorizes the routine additive database
migrations, required builds, and client/server installation within that feature's
scope. This includes adding new custom items in reserved, collision-checked ID
ranges. Do not ask for separate approval at each routine step or for each exact
migration. This authorization does not cover destructive changes, loss of player
progress, overwriting existing Blizzard entries, breaking schema changes, or
material work outside the requested scope; ask before those. Stop and report
unexpected ID collisions or failed validation.

For every Warscape database change, follow `doc/WarscapeDatabaseWorkflow.md` and
use `contrib/warscape/db.py`. Inspect migration status and permissions first;
review the exact migration and its verification specification; keep servers and
other updaters stopped; require a fresh verified backup immediately before
execution; and verify and record the result through the tool. Preserve existing
Blizzard entries, player data, and unrelated work. Do not change database
privileges or restore backups without separate user approval. If a higher-priority
instruction prevents an otherwise authorized routine action, explain that exact
restriction instead of repeating an approval request already covered here.

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

# Custom client memory-layout safety

When work touches the custom client under `C:\WoWDev\wowdecomp`, follow its `AGENTS.md` as well as this file. Before modifying gameobjects, creatures or player objects, object fields/update handlers, display IDs/model refresh, network object updates, mirror buffers/field mappings, object creation or destruction, allocators, object structures or their sizes, inspect memory-layout and object-lifetime/deferred-destruction implications.

Mandatory checks:

- Verify every field-index lookup resolves to a valid allocated slot. Unknown mappings must return an explicit invalid result and be rejected before pointer arithmetic, copying or callback reads.
- Check mapping-table storage against declared entry counts and uniqueness wherever slot aliases are not intentional.
- Verify computed offsets and byte ranges fit the actual allocation, including field widths and local/remote object variants.
- Update allocation sizes whenever a mapping or field count grows. Preserve existing field indices and layouts unless a coordinated layout change is required.
- Review allocation, reuse, visibility, deferred destruction and final-free paths when changing object creation or visibility behaviour.
- Run focused mirror-layout checks when relevant object code changes. Compilation alone does not establish memory safety. Do not deploy a change when a relevant check fails.
- Completion reports must state whether memory-layout-sensitive code changed, which relevant checks ran and passed, and any remaining risk needing manual testing.

Keep Release PDB generation and crash diagnostics available. Lifecycle traces must remain bounded and opt-in unless evidence justifies enabling them by default. Never leave PageHeap enabled permanently.

# Default walkable-ground relief for world generation

New landscapes receive biome-appropriate, irregular local relief on walkable ground by default during initial generation. Flat terrain requires an explicit request or a deliberately protected surface.

Use `contrib/warscape/worldgen/terrain_detail.py` and follow `contrib/warscape/worldgen/AGENTS.md` and `doc/WarscapeTerrainGeneration.md`. Apply the shared stage once after broad grading and before final grounding/serialization. Preserve structure, road, liquid, entrance, bridge and NPC masks. Do not erase the detail with later smoothing or accumulate it when rebuilding. Adapt seed, scale, density and biome rather than copying one map's pattern. Explicit flat practice/template maps use `ground_detail.flat: true`. This default applies to future initial generations; it does not authorize altering existing maps.
