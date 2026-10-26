# Warscape — Design Conversation Notes
Updated: 26 October 2026
Status: Discussion notes; proposals are not approved implementations unless marked decided.

## Core direction — decided
- Rebuild a game that feels approximately 95% Old School RuneScape using WoW 3.3.5a engine, models, monsters, animations and movement.
- Retain OSRS-style formulas, XP pacing and skills, while fixing progression issues that do not make sense (for example, 99 Smithing to make equipment requiring only 40 Defence).
- Use Azeroth initially; explore a custom world much later.
- Replace most WoW fetch quests with longer, meaningful OSRS-style quest chains and milestones.

## Interconnected progression — design goal
- Skills should interact: combat or quests may unlock mines; Mining yields ore; Smithing turns it into gear; gear enables harder encounters.
- Unlocks may also involve Agility, gathering, quests, or combinations, not only combat.
- Players should be able to specialise in a few skills and trade, with mid-tier progression viable; mastering more skills should offer earned, meaningful advantages.
- Avoid a single activity, such as Slayer, effortlessly funding all other progression through sellable drops and coins. Exact economic balancing is unresolved.
- Preserve the value of Smithing and crafting without forcing Ironman rules.

## Skill Mastery Perks — proposed, not yet scheduled
- Herblore/Alchemy: small incremental increases to potion effectiveness at skill milestones.
- Smithing: expert smiths gain modest weight reductions for armour they know how to make or refine.
- Mining: chance for additional mineral resources from earthen/golem-type creatures.
- Perks should reward long-term investment, including very high skill levels; cumulative effects must be considered.
- OSRS-like carried weight and run energy mechanics need a separate future discussion.

## Equipment and economy — unresolved
- Materials and tier names are secondary to the gather/craft/fight progression loop.
- Need to decide balance between crafted equipment and monster/boss drops, and how WoW's many item models are used.
- Stage 1G proposal: deterministic weapon archetype base stats and tier scaling on a limited test set.
- Stage 1H proposal: permanent, item-definition-level random stat rolls, identical for all copies of the same item; revisit before implementation.

## Ground items — deferred
- Keep standard WoW lootable corpses for monster drops.
- Consider reusable, respawning clickable ground items using WoW GameObjects.
- Player-dropped ground items and drop parties can wait; WoW's existing trade window is sufficient for now.

## Development checkpoint — confirmed by user's test report
- Stage 1F passed in-game: OSRS tick-based weapon and monster attack speeds, weapon switching and related checks.
- Migration applied; Release x64 build and automated tests passed; branch `feature/osrs-monster-stats`, reported commit `f4fc5e3b22`.
- Stage 1G has not been approved or started in this discussion.

## Note-taking rule proposed by user
- Maintain a version-controlled, append-or-update design journal in the TrinityCore repository after substantive design conversations.
- Distinguish decided rules from ideas and open questions; do not treat brainstorming as authorisation to implement.
- Preserve previous notes and avoid committing credentials, backups or server data.

## Stage 1G authorization and decisions — 25 October 2026
- The user approved Stage 1G as a combined batch: deterministic weapon archetype
  statistics, conservative equipment-tier progression, and health/damage display
  scaling from ×100 to ×10. This supersedes the earlier checkpoint stating that
  Stage 1G had not been approved; that checkpoint remains historical context.
- Use established OSRS equipment statistics as the baseline. Prefer existing WoW
  item classification and explicit exceptions; do not equate WoW item level with
  OSRS tier or overwrite existing custom Warscape profiles.
- Preserve Stage 1E bonus aggregation and Stage 1F attack speeds, existing OSRS
  combat/accuracy calculations, and unrelated XP progression. Preserve approximate
  damage-to-health ratios when changing the display scale.
- When tier evidence is unreliable, use a conservative default with configurable
  overrides. The implementation uses Bronze fallback, explicit metal tiers and a
  small reviewed QA mapping; details and references are in
  [Stage 1G](WarscapeStage1G.md).
- Stage 1H randomized item statistics remain future possibilities and are not
  authorized or implemented by this batch. In-game Stage 1G acceptance is pending.

## Development training utility — approved, 25 October 2026
- Before Stage 1G acceptance, the user requested a permanent reusable testing
  tool: Warscape Training Dummy, with GM spawn/removal, optional persistent
  spawns, no retaliation or movement, and damage-path immortality.
- Preserve real calculated damage, normal hit/miss rolls, equipment bonuses,
  attack intervals and combat logs. Exclude combat XP, loot, money and quest
  credit. Configurable Defence is a testing control, not a monster balance change.
- [Training dummy usage and safeguards](WarscapeTrainingDummy.md) documents the
  temporary/permanent command modes and session-only Defence setting.
- This utility is separate from Stage 1G balance. Stage 1H remains unauthorized;
  live dummy acceptance and Stage 1G testing await the user's confirmation.

## Automated combat testing utility — approved, 25 October 2026
- The user requested GM-only `.rs attacktest <1-30 minutes>`, with stop, cancel
  and status controls, against a selected Warscape Training Dummy.
- Observe real melee auto-attack events, count successful zero-damage rolls
  consistently, use actual elapsed time for DPS, report interruptions, and check
  XP changes across all seven combat skills. Do not simulate swings or modify
  attack timing, combat balance, dummy reward suppression or Stage 1G formulas.
- Keep at most one session per player; cancel safely on lifecycle changes and
  retain no stale target pointers or background timer work. Live acceptance
  awaits the user's confirmation. [Usage and measurement definitions](WarscapeAttackTest.md).
- This remains a testing utility. Stage 1H and other gameplay work are not
  authorized by this request.

## Stage 2A skills interface — approved, 25–26 October 2026
- The user approved a standalone 3.3.5a `WarscapeSkills` addon for the seven
  existing combat skills, with actual server values, XP bars/tooltips, a movable
  saved-position panel and `/wskills` toggle.
- Preserve the approved ornate frame, two dragons, compact grid, gold labels and
  green bars. Use native WoW icons and UI assets; a close native dragon ornament
  equivalent is permitted when the exact illustrated dragons are unavailable.
- Use structured read-only addon communication, ordinary-player access and
  automatic login/XP/level updates. Do not invent temporary boosts.
- On 26 October the user authorized restarting from this specification in the
  Windows checkout if the interrupted Linux draft could not be recovered. That
  draft is not a dependency of the Windows implementation.
- Build, test, safely deploy, commit and push Stage 2A, then await the user's
  in-game acceptance. Stage 2B, Stage 1H, Mining and Smithing remain outside scope.
- [Implementation and acceptance checklist](WarscapeStage2A.md).

## Stage 2A UI correction — approved, 26 October 2026
- The user reports that the functional first panel differs significantly from
  the approved reference. This is a correction within Stage 2A, not a new stage.
- The earlier permission to use native dragon ornaments did not establish visual
  acceptance. The user now requires the approved ornate dragon-frame appearance:
  nearly opaque dark stone, thick metal/gold frame, integrated corner dragons,
  compact two-column recessed gold-trimmed cells, larger gold labels, green XP
  bars, `current / base` levels, an integrated close button and a total-level panel.
- Native textures remain preferred where suitable; separate custom addon textures
  are authorized when needed for visual fidelity. Interactive elements stay live.
- Replace the default N/Talents shortcut through supported addon bindings while
  respecting custom bindings and preserving the underlying talent system,
  `/wskills`, Escape, drag position, live values, tooltips and automatic updates.
- Work and deployment remain exclusively on local Windows. Preserve combat,
  progression and persistence; rebuild the server only if server code changes.
  Commit/push the correction, verify the remote, then await user acceptance.
- Stage 2B and Stage 1H remain outside scope.
- The user subsequently supplied both screenshots and explicitly retained the
  original addon icons and clean layout while requiring the reference's borders,
  backgrounds and dragons. The correction uses local reference-derived texture
  pieces; sample tab buttons and Slayer remain unimplemented.

## Primary development client — user correction, 26 October 2026
- The custom-built wowdecomp client under `C:\WoWDev\wowdecomp` is the primary
  Warscape client. This explicitly supersedes the earlier ChromieCraft target
  assumption; the previous deployment remains historical context, not permission
  to change ChromieCraft again.
- Locate the real `WowClient64.exe` process and effective game/interface directory
  before deploying addons, including any `datadir` override. Initial inspection
  found the executable at `bin\Win\WowClient64.exe` and no running client.
  Source verification establishes `bin\Win` as its default game directory and
  `bin\Win\Interface\AddOns` as its default addon directory.
- Deploy and validate Stage 2A's approved visual correction and N binding against
  wowdecomp. Keep source in TrinityCore, use Windows only, preserve existing work
  and do not modify ChromieCraft unless explicitly requested.
- This changes the client configuration, not stage scope, combat or persistence.
  Stage 2B and Stage 1H remain outside scope.
