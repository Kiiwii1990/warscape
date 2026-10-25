# Warscape — Design Conversation Notes
Updated: 25 October 2026
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
