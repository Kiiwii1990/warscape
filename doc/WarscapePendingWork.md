# Warscape pending-work register

Reviewed supplied conversation history and current enemy checkpoint documentation on8 November2026. User acceptance means the observed checkpoint worked; it does not prove mechanics explicitly omitted by that checkpoint. This is an implementation backlog, not an instruction to introduce every future catalogue variant.

## Confirmed completed

- Agility Northshire movement and attempt-time rewards; clickable proxy implemented and user accepted. Exact distant-click OSRS approach remains separate below.
- Coins stacking change accepted; do not replace with WoW wallet conversion.
- Enemy combat/loot batches through Nechryael-Zygomite accepted.
- Refillable ten-charge Fungicide spray902585 accepted, including user confirmation after deployment. Original dose902570 and refill902584 preserved.
- Gargoyle manual reusable hammer, salt finisher, source poison, ranged/magic carriers, Hydra three-attack cycle, Aquanite lure cut, Nagua double-hit and Earthen reinforcement already implemented. Do not redo these as if absent.

## Current milestones

- Smoke Devil equipped facemask: implemented, see WarscapeSmokeFacemask.md; manual acceptance pending. Dust Devil mitigation, dungeon smoke and temporary drains remain queued.

- Harpie equipped lit lantern: user confirmed working; deployment/acceptance recorded in WarscapeHarpieLantern.md. Lighting/Firemaking remains future work.
- Nechryael owned Death spawns: implemented/deployed; manual acceptance pending. See WarscapeDeathSpawns.md. Two active GUIDs at most,60-second native lifetime, target binding and cleanup. Native WoW auto-retaliate/logout/prayer exceptions remain unlike exact OSRS behaviour.

## Queued enemy mechanics

| Area | Remaining work | Reference |
|---|---|---|
| Protection gear | Dust Devil facemask mitigation; Smoke Devil dungeon smoke/stat-drain effects; Sourhog goggles; Turoth/Kurask leaf/broad/Magic Dart gates; Harpie lantern lighting/Firemaking | NechryaelsZygomites, StalkersGargoyles, GryphonsHydras |
| Temporary stats/gaze | Basilisk/Cockatrice mirror protection and gaze; Spectre/other temporary drains; implement temporary combat stats without changing stored XP | SlayerElementals, CaveFamilies |
| Wall Beast | Wall-hole placement/trigger, grab/Spiny helmet, linked respawn; free-standing model currently a stand-in | NechryaelsZygomites |
| Ent | Defeated trunk/chopping, Woodcutting-dependent logs and nests; no kill loot substitute | StalkersGargoyles |
| Hydra | Poison ground pools; ordered eye/fang/heart and task-dependent rates | GryphonsHydras |
| Gryphon | Equipped-weight knockback, self-stun/counter window | GryphonsHydras |
| Stalker | Bleed special; Wiki damage explicitly uncertain and needs careful prototype choice | StalkersGargoyles |
| Nagua | Frost ground/prayer special; Earthen crush-special weakening/burn clearing; some encounter-specific restores | SlayerElementals |
| Killerwatt | Orb-to-limbs click transformation, exact mode/reach behaviour | SlayerElementals |
| Finishers | Rockslug1HP wander/autosalt/brine sabre; Zygomite pick-fungi/autospray; Gargoyle alternate hammers/autosmash perks | NechryaelsZygomites, StalkersGargoyles |
| Regeneration | Cave Crawler/Turoth/Kurask rapid source regeneration | CaveFamilies, GryphonsHydras, NechryaelsZygomites |
| Cave Horror | Scream/AoE, witchwood icon/protection and exact magic-melee rules | CaveFamilies |
| Venom/poison | OSRS cure conversion/consumables; Slime adjacency/zero-damage application; source-specific application rates | SlayerElementals, CaveFamilies |
| Loot accuracy | Independently chosen multi-herb/multi-seed identities; reviewed unique/preroll correlations; source distribution assumptions | Each release source_assumptions |
| Conditional loot/items | Task/quest/location tertiary and ordered collections, clues, inventory gameplay for collectible gear, notes/bank conversion | Enemy release notes |
| Wider combat | Full player ranged/magic/prayer, Slayer tasks/training/gates, elemental weaknesses and equipment bonuses | Existing combat systems |

Earlier documentation contains stale entries such as missing flat-armour support or poisonous Scorpion variants; later spectral/ordered releases supersede those implementation gaps. Preserve original historical notes rather than treating every old word "deferred" as current. Unrepresented family variants/bosses/superiors remain future expansion, not completed by regular-family acceptance.

## Agility / map acceptance outside current enemy milestone

- AGI-005 genuine distant one-click approach/immediate accepted-click roll still needs client/server design beyond stock near-range proxy.
- Interruption, logout/death/teleport/collision paths were not all individually verified by earlier traversal acceptance. New user success statements do not retroactively establish every edge case.
- Wall/terrain-dependent mechanics need measured placement and collision/visual QA; do not guess permanent geometry or commandeer the user's client.

## Delivery order

Follow repository AGENTS.md: one independently testable improvement per session when broad. After current summon acceptance, prioritise gear requirements, then Wall Beast placement and Ent harvesting; isolate shared temporary-stat changes from encounter-specific scripts. Builds and source tests never substitute for user gameplay acceptance. Preserve unrelated source/runtime/untracked work and existing player progress throughout.
