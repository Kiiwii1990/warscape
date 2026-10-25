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
