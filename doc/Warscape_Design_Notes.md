# Warscape — Design Conversation Notes
Updated: 26 October 2026
Status: Discussion notes; proposals are not approved implementations unless marked decided.

## Core direction — decided
- Rebuild a game that feels approximately 95% Old School RuneScape using WoW 3.3.5a engine, models, monsters, animations and movement.
- Retain OSRS-style formulas, XP pacing and skills, while fixing progression issues that do not make sense (for example, 99 Smithing to make equipment requiring only 40 Defence).
- Use Azeroth initially; explore a custom world much later.
  Historical planning decision: the separate World Generation Test 1 below was
  subsequently authorized on 26 October 2026; it does not replace existing gameplay.
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

## World Generation Test 1 — authorized, 26 October 2026
- The user authorized an isolated playable OSRS free-to-play region experiment
  containing Lumbridge, Varrock and Falador, using WoW 3.3.5a assets where practical.
  This explicitly revises the earlier plan to defer all custom-world exploration;
  existing Azeroth/Warscape gameplay remains in place.
- Work locally on Windows with wowdecomp and the existing server. Preserve combat,
  XP, skills and addons. Measure travel scale; do not claim playability without
  loading and testing in the actual client.
- First milestone passed: map 901 loaded in wowdecomp with a working GM entry,
  ground collision, movement/jump and logout/login persistence. This is flat
  terrain only; the OSRS geography, roads, buildings, water and NPCs are incomplete.
- No NPC migration was created or applied. Future database changes retain the
  exact-migration approval and fresh-backup requirements.
- [Reproduction, deployment, live evidence and remaining work](WarscapeWorldGenerationTest1.md).

## World Generation Test 2 Checkpoint B visual direction — approved, 26 October 2026
- The user approved an isolated Lumbridge-inspired starting-settlement redesign as
  a near-deployable visual alpha. It should read as a genuine vanilla WoW human
  settlement first, with Lumbridge identity carried by the keep, chapel/graveyard,
  village, farm, river and bridge relationships. Exact OSRS dimensions are not a
  target; native WoW model dimensions, character proportions and movement speed
  remain unchanged.
- Keep the alpha isolated from maps 901/902 and original Azeroth data. Use
  deterministic configuration for terrain, textures, roads, buildings and scenery;
  use native WoW assets and reject visual acceptance based only on technical tests.
- The first separate design iteration uses map 903, WoW-native Castle02, four
  blended Elwynn surfaces and seeded scenery regions. Its offline extraction,
  collision and navigation passed. Client deployment, visual approval, in-world
  collision and NPC pathfinding remain outstanding. Do not begin Checkpoint C
  before the user approves the completed Checkpoint B environment.

## Warscape local testing handoff — user-approved, 26 October 2026

- The user has changed the permanent Warscape testing workflow: the user performs
  in-game visual inspection and manual gameplay testing; Codex performs development,
  automated validation, builds, deployment and technical troubleshooting.
- Do not launch or operate WoW for manual QA unless the user explicitly requests it
  or approves direct investigation of a specific technical issue. Never report
  manual visual or gameplay checks as passed before the user confirms them.
- After successful automated checks and safe local deployment, provide the exact
  teleport coordinates/commands and a concise inspection checklist, then stop for
  the user's feedback. Keep further checkpoint work outside scope until approved.
- This is an explicit workflow revision; it does not change the existing combat,
  progression, UI, database or world-generation design decisions.

## Original one-tile settlement challenge — authorized, 26 October 2026

- The user authorized a separate, original RuneScape-inspired settlement using
  native classic WoW visual language on exactly one ADT tile. This is a new
  challenge; it neither continues the Lumbridge geography nor starts Checkpoint C.
- Deliberate composition, player-scale architecture, rich domestic/work details,
  soft ground transitions and natural wooded/elevated framing take priority over
  technical file counts. Codex has creative freedom over the settlement.
- Preserve maps 901–903, the permanent flat sandbox (904), Azeroth, gameplay,
  addons and unrelated work. Use an unused map ID and safe external backups.
  Do not commit or push the new environment before the user's review/approval.
- Continue the established Windows development → automated validation → safe
  deployment → user in-game review workflow. No manual client operation by Codex.
- The resulting first candidate is Briarbrook, map 905. Its package and sampled
  entrance/road navigation checks passed and it is deployed for user inspection.
  **The design/visual result is not yet accepted by the user.** Confirmed scope
  and implementation status must remain distinct from visual acceptance.
- [Composition, findings, reproduction, validation and handoff](WarscapeBriarbrook.md).

## Briarbrook accepted foundation and refinement — approved, 26 October 2026

- The user inspected map 905 in-game and confirmed that its village layout,
  architecture, proportions, winding roads, market stalls, well, benches and
  atmosphere are a substantial success. Briarbrook is now the permanent starting
  point for world-building and gameplay testing. This explicitly supersedes the
  earlier pending-acceptance statement for those aspects; that statement remains
  historical. The fluorescent terrain remains a confirmed defect.
- Refine the existing map 905 without redesigning its village. Correct the actual
  texture-loading failure first, soften the enclosing woodland slopes, and add
  controlled native ground vegetation while keeping routes and entrances clear.
- Add a small goblin-raided abandoned farm in the surrounding woodland, with an
  approach/retreat route and maneuver space for future beginner combat testing.
  Enemy spawning, combat mechanics, loot and quests are explicitly excluded now.
- Preserve the existing buildings and scales, market, common, roads, interiors,
  working collision/navigation, other maps and permanent flat map 904. Maintain
  reusable clutter placement and use the existing backup/build/deployment workflow.
- The implementation candidate names the farm Cinderfield. Its updated appearance
  requires the user's next in-game review. No commit/push is authorized before
  that visual approval. The user continues to perform all manual WoW testing.

## Briarbrook environment acceptance and final lighting correction — approved, 26 October 2026

- The user has visually approved Briarbrook (map 905) as Warscape's primary
  development and gameplay testing environment. This explicitly supersedes the
  preceding refinement candidate's pending environment acceptance; the earlier
  record remains historical.
- Freeze the existing village, terrain, buildings, foliage, paths and world
  layout. The only authorized remaining visual work is correcting the excessive
  white nighttime ground glare in the custom wowdecomp renderer. Do not generate
  another map iteration or rebuild terrain for this correction.
- Preserve the moon, sky, night atmosphere, warm windows, lanterns, daytime
  lighting, other maps and normal materials. The user will perform all in-game
  visual testing; Codex handles diagnosis, automated checks, builds and safe
  deployment without launching the game.
- A terrain-only nighttime specular bound is now deployed for map 905. Its
  automated checks pass; visual acceptance of the lighting remains pending.
  See the final lighting record in [WarscapeBriarbrook.md](WarscapeBriarbrook.md).
- Once the user confirms the glare is corrected, Briarbrook is complete for the
  current development needs and work may move on to other Warscape systems.
  This statement does not authorize implementing any particular future system.

## HUD Skills icon direction — user clarification, 27 October 2026

- The user supplied the OSRS Skills icon as a visual reference: several coloured
  bars of different heights. The Warscape button should represent graphs or
  data; a literal match is optional. This supersedes the proposed book and
  checklist direction for this button.
- The user requested comparisons before deciding and has not approved an icon
  selection. The original Blizzard data-display and prismatic punch-card
  candidates remain proposals. See [HUD rescue diagnosis](WarscapeHUDRescue.md).
- Subsequent user selection: use the multicoloured data card,
  `Interface\Icons\INV_Misc_PunchCards_Prismatic`, for the Skills menu. This
  explicitly resolves the preceding pending decision and supersedes the proposed
  data-display, checklist and book choices. Visual acceptance of the completed
  HUD remains pending the user's in-game inspection.

## Inventory Phase 1 and shared menus — approved, 27 October 2026

- The user explicitly authorized building Inventory Phase 1 in this checkout
  after inspection found no existing implementation to extend.
- Preserve the current HUD artwork, dimensions and positions. Assign its slot
  immediately left of the minimap to Inventory with Blizzard's original backpack
  icon and B. Skills stays immediately right with N and its approved data card.
- One shared manager owns exclusive main-panel visibility, HUD highlighting
  and independent panel scales. All future Warscape main panels must register.
  Loot, confirmation dialogs, tooltips and other essential temporary interfaces
  remain outside that restriction. Switching panels retains their preferences.
- Inventory matches the Skills exterior and shows 28 positions in four columns
  and seven rows: 24 real usable storage slots initially, with four grey locked
  padlocks in the bottom row. A future tutorial reward unlocks those four;
  unlock state must persist per character. The tutorial quest itself is future
  work, not authorized for this implementation.
- Retain native WoW item, loot, equipment and persistence behavior. No fake extra
  usable slots. HUD, Skills and Inventory scale independently at 50-150% through
  the existing Ctrl-wheel/magnifier interaction and saved preferences.
- Build, test and safely deploy locally; no game launch or commit/push. Final
  visual, loot and relog acceptance remains with the user. Implementation and
  checks are documented in [Inventory Phase 1](WarscapeInventoryPhase1.md).

## Universal HUD framework Phase 1 — approved revision, 27 October 2026

- The user approved a revised framework: one main panel per side, with up to
  one left and one right panel open simultaneously. Same-side panels replace
  each other; opposite-side panels remain open. This supersedes the prior
  single-panel exclusivity decision above. Temporary loot, tooltip and
  confirmation interfaces remain outside this manager.
- All custom Warscape panels use one shared 350 x 514 base exterior, about 30%
  narrower than the earlier design. Inventory, Skills, Attack Styles, Prayer
  and Spellbook share one persisted 50–150% panel scale; HUD scaling remains
  independent. The prior independent panel scaling and 500 x 514 descriptions
  are superseded for this framework phase.
- The HUD has named functions and shortcuts across its ten existing positions:
  ESC Settings, O Friends, reserved empty position, L Quest Journal, B
  Inventory; then N Skills, C Equipment, K empty Attack Styles, I empty Prayer,
  P empty Spellbook/Magic. Quest Journal uses the user-selected
  `INV_Misc_Note_05` icon and Spellbook uses `INV_Misc_Book_01`.
- Three empty, resizable Warscape panels are established without implementing
  gameplay mechanics. Inventory retains native server-backed storage with 28
  visible positions, 24 usable slots and four locked slots. The inventory grid
  is compact and square. Key labels and invisible future resource-bar anchors
  provide the requested HUD layout without implementing health or prayer bars.
- Implementation and automated validation are documented in
  [Universal UI Framework Phase 1](WarscapeUIFrameworkPhase1.md). Deployment
  and the user's in-game visual/gameplay review are recorded separately.

## HUD refinement — approved layout; Prayer icon pending, 27 October 2026

- The user reports that panel groups, button assignments, keybinds and compact
  Inventory layout work in-game. Preserve those decisions and the Inventory
  grid. Refine the HUD by removing the bottom gap, lowering buttons/labels,
  moving gryphons outward without distortion, hiding minimap tracking/world-map
  controls, and bringing the zoom controls closer to the ring.
- Prayer key I must reliably open/close the existing right-side panel and keep
  the left panel unaffected. The prior Prayer icon is rejected as too much like
  a healing spell. The user selected original Blizzard icon
  `INV_Jewelry_Talisman_08`, the golden sun symbol, from the visual comparison.
- Health and Prayer bars remain future layout space only. No mechanics or
  resource bars are authorized in this refinement.

## Final HUD button sizing — approved, 28 October 2026

- The user approved the HUD layout and requested all ten button frames and
  their icon artwork at 95% of the prior size. Preserve each button's existing
  center, horizontal spacing, order, labels and minimap position. Apply equally
  to the empty reserved slot; change no other HUD element.
- The 95% adjustment is implemented in the existing HUD addon. Targeted HUD
  geometry/scale tests pass and the updated Lua file is deployed locally. Final
  visual acceptance remains with the user.

## Final HUD material and button padding — approved, 28 October 2026

- Reuse the exact tiled `WarscapeSkills\art\Stone.tga` backdrop used by the
  Prayer panel under the HUD rail. Preserve the original bronze rail top edge
  as a transparent overlay. Do not change the Prayer panel itself.
- Raise the existing 95%-size buttons and labels within a taller rail backing.
  Keep button centers horizontally, minimap position, gryphons, icons and
  functionality unchanged. User visual acceptance remains pending.

## Final HUD button alignment — approved, 28 October 2026

- The Inventory button is the immutable vertical reference. Its anchor is
  `CENTER` relative to the HUD assembly's `BOTTOM`, at y=48 UI units; keep its
  x position unchanged. Every other button, including the reserved slot, uses
  that exact vertical anchor. Every key label uses the Inventory label's same
  `TOP` to button `BOTTOM` anchor and offset. Preserve horizontal coordinates.

## Finished HUD top trim and row adjustment — approved, 28 October 2026

- The user approved a finished bronze-gold top bevel across the full width of
  the black HUD background, matching existing Blizzard/Warscape trim. Reuse
  the original rail artwork over the existing Stone fill.
- This revision supersedes the prior y=48 Inventory anchor position: lower the
  full ten-button row and its labels by four UI units, placing Inventory at
  y=44. Inventory remains the vertical reference; preserve each x coordinate
  and the label-to-button spacing. Do not change other HUD components.

## Visible HUD top border — approved, 28 October 2026

- The user confirmed that the previous dark rail bevel was not visible enough.
  Add a thin bronze/gold line across the two button sections, using the existing
  panel border art. Preserve the textured black background and approved layout.
- Anchor the line to the HUD backing so resolution and saved HUD scaling carry
  it. Let the minimap and gryphons meet/overlap the line naturally; do not cover
  the buttons or alter any other HUD element.

## HUD gryphon metallic palette — approved, 28 October 2026

- Recolour both existing HUD gryphons to match the high-contrast dark-metal,
  silver and bronze palette of the approved custom menu ornaments. Preserve
  the original Blizzard gryphon's exact alpha silhouette and all HUD geometry.
- Add only a subtle warm light in the existing eye socket, using the custom
  menu ornament's gold eye as reference. Keep panel artwork unchanged.

## Gryphon palette correction — approved, 28 October 2026

- The first gryphon recolour did not sufficiently match the panel decoration.
  Use the actual shared `Dragon.tga` texture from Inventory and Attack Styles
  to sample the deep-shadow, bronze and silver palette and the eye glow.
- Transfer source luminance ranks monotonically to the panel ornament's visible
  tone distribution, preserving detail order while matching its shadow/highlight
  range; retain the exact alpha silhouette.
  Apply the recolour to the separate Warscape gryphon texture only; keep all
  HUD geometry and panel artwork unchanged.

## OSRS Mining foundation — approved, 28 October 2026

- Add Mining as an independent Warscape skill at level 1, using the existing
  OSRS level curve and the Skills panel's established server snapshot protocol.
  Keep Blizzard Mining intact but inaccessible.
- Preserve integer XP storage. Copper's 17.5 XP award is represented by a
  character-persisted half-point accumulator, producing 17, 18, 17, 18 XP.
- Copper requires level 1 and grants one Copper Ore only after a successful
  extraction. Item 2901 is the temporary bronze-equivalent pickaxe at 8 ticks
  (4.8 seconds) per attempt. Attempt success must use OSRS's rock-specific
  parameters; do not invent copper values.
- Open-world GM-spawned copper nodes remain at their location. A successful
  extraction depletes that node for three seconds with a pale-grey appearance;
  nodes have independent timers and GM placements persist across restarts.
- Expand the existing Skills panel with Mining and scrolling only when content
  exceeds its current viewport. Preserve its dimensions and approved styling.
- Character and world database migrations require exact user approval and a
  fresh verified backup immediately before application. No migration is
  applied as part of this design authorization.

## HUD gryphon replacement — Design 5 approved, 28 October 2026

- The user approved replacing both HUD gryphons with the supplied Design 5
  armoured gryphon. This supersedes the earlier decision to retain the Blizzard
  gryphon silhouette and its later palette-only corrections. Preserve the
  supplied artwork's colours, shading, details and eye glow; remove only its
  charcoal backdrop and fit it proportionally inside the existing texture crop.
- Keep the two 160 x 95 HUD texture frames, anchors, positions and mirrored
  right-side orientation unchanged. The fitted art occupies 126 x 76 pixels in
  the existing 128 x 76 visible slice, with one-pixel transparent side padding.

## Copper rock depletion and scale — approved, 28 October 2026

- The user confirmed that active copper entry 900101 and grayscale entry
  900103 render correctly, approving the grayscale asset for depletion.
- Keep the saved active spawn as the sole persistent rock. Each active rock
  manages one hidden, non-selectable grayscale counterpart at the same map,
  position, orientation and 50% runtime scale. The two objects share the active
  phase while the grayscale object is shown. The counterpart is a temporary map
  object, so map unloads and server restarts cannot leave an orphan persistent
  grayscale spawn.
- On a successful extraction, show the grayscale object and hide the active
  rock through phase visibility; after three seconds, reverse visibility.
  Keep timers independent per active spawn and preserve all Mining reward,
  animation, success and XP mechanics.
- Apply the same 50% scale to all loaded or newly spawned 900101 rocks and
  their runtime collision. Do not update the shared Blizzard model or unrelated
  veins, and do not change database templates or saved character/world data.

## Copper mining adjustments — approved, 28 October 2026

- Increase the per-rock depleted appearance from three to nine seconds while
  retaining independent timers and the existing active/grayscale switching.
- Copper Ore item 2770 uses `item_template.stackable = 1`, so each newly
  collected ore occupies its own slot. Preserve `maxcount`, all other item
  template fields, and existing character inventory data. The reviewed world
  migration is prepared but awaits explicit approval before application.
- Custom skill content uses separate, category-specific ID namespaces and
  reviewed 200-ID blocks for Mining and Woodcutting. See
  [Warscape Skill ID Allocations](WarscapeSkillIdAllocations.md) for exact
  ranges, current usage and unassigned proposals.

## Skills panel grid refinement — approved, 29 October 2026

- Keep the approved ornate Warscape/WotLK frame, dark stone, gold trim, title,
  close button and native skill icons. Replace the internal two-column layout
  with a compact three-column grid: Attack, Hitpoints, Strength; Ranged,
  Defence, Magic; Prayer, Mining, then future skills or an empty placeholder.
- Each skill tile shows its icon, gold name, current level and a thin independent
  green XP bar. Calculate progress from the existing server snapshot's XP,
  current-level floor and next-level threshold; fill the bar at level 99. Keep
  total XP, next threshold, remaining XP and base level (when it differs) in the
  hover tooltip. Do not change progression, saved skill data or server systems.
- Keep the existing panel dimensions, scroll only the grid as the list grows,
  and pin the title and Total Level footer. Total Level remains the sum of actual
  base levels. This UI refinement supersedes the 26 October two-column layout
  direction while preserving the rest of its presentation and functionality.
- [Implementation and acceptance checklist](WarscapeStage2A.md).

## Skills panel icon, level and scaling refinement — approved, 29 October 2026

- Keep the three-column grid and ornate frame, remove visible skill-name text
  from tiles, enlarge each icon to dominate its tile, and retain the attained
  XP bar at the bottom. Display `current/attained` in each tile. Tooltips retain
  the name and show current level, attained level, total XP, the next-level XP
  threshold and XP remaining. Total Level sums attained levels only.
- Ctrl + mouse wheel over the Skills grid uses the existing `WarscapePanels`
  scale manager and saved panel preference. With Ctrl released, wheel input
  scrolls the grid by one row. HUD scale remains separate.
- The existing skills snapshot has an optional effective-level field, but the
  server currently emits `-` and stores only attained level and XP. Until an
  actual server effective level is available, show attained/attained for
  unmodified skills. Do not synthesize buffs or drains; future modifier support
  requires an authoritative effective-level source and snapshot updates.

## Client mirror-buffer corruption — confirmed root cause and safeguards, 29 October 2026

- WinDbg identified the write in `CopyMirrorFields` (`WoW/Source/ObjectMgrClient/ObjectMgrClient.cpp`) during `SMSG_UPDATE_OBJECT` object creation. Gameobject display field index 2 had no entry in the mirror-field mapping `{3, 8, 11, 12}`. The lookup silently fell back to slot 12, although only four gameobject mirror slots were allocated. The computed write therefore exceeded the active object's mirror allocation and landed on the adjacent depleted copper object's `m_heapIndex`, changing it to display ID 310. Later, `CObjectHeapList::Delete` used 310 as the heap handle and crashed.
- The permanent correction in `wowdecomp/WoW/Source/Object/GameObject.cpp` appended display field index 2 as slot 4 and expanded the saved mirror allocation by one field while keeping the original four slots stable. The focused regression is `wowdecomp/Tools/Tests/GameObjectMirrorLayout.cpp`.
- Follow-up safeguards add an explicit invalid mapping result, range checks before mirror copying and callback reads, and focused build-time/CTest validation. Unknown mappings are refused and reported through bounded debugger output; no allocator or object-destruction workaround is used.
- This failure demonstrates that successful compilation does not validate mirror bounds. Any future client object-layout or lifetime change must be checked against its allocated storage and deferred-destruction behaviour. See `wowdecomp/AGENTS.md` for mandatory review rules.
- Release PDB generation remains enabled. Lifecycle tracing remains opt-in and bounded; PageHeap is not permanently enabled.

## Natural walkable ground — user-confirmed default, 31 October 2026

- New landscapes receive biome-appropriate, irregular local relief on walkable ground by default during initial generation. Flat terrain requires an explicit request or a deliberately protected surface.
- The user approved denser, less predictable small-scale variation over Ashen Crown's successful broader ground undulations, with comfortable traversal, protected critical surfaces and no accumulated displacement/elevation drift.
- Implement this standard in the reusable tooling for future initial generation, with seed/scale/density/strength controls and volcanic, woodland, snow and settlement character. Explicit flat practice maps and deliberately level floors remain level.
- This decision authorizes updating Ashen Crown 911 now. It does not authorize automatically changing other existing maps or saved Noggit projects. Preserve the latest woodland and other newer work.
- Shared implementation: `contrib/warscape/worldgen/terrain_detail.py`. Entry points, masks, flat exceptions, stage ordering, historical-author boundaries and validation are documented in `doc/WarscapeTerrainGeneration.md` and the applicable worldgen AGENTS.md files. The user continues to perform in-game visual/gameplay testing.


## Docked landscape menu controls — approved, 31 October 2026

- The user's approved UI image is a layout reference, not replacement artwork.
  Reuse the original dragons, gryphons, stone, borders and icons; resize only
  suitable frame segments. Widen the bottom-button spacing and default menus.
- All main menus default to locked landscape shells directly attached to the
  bottom HUD, inside the eagle/gryphon noses and clear of minimap/zoom controls.
  This supersedes the earlier free-floating portrait default without changing
  menu assignments, shortcuts, one-menu-per-side or two-main-menu limits.
- Each menu independently persists lock state, landscape/portrait orientation
  and detached position. The header padlock unlocks dragging without a jump;
  relocking snaps home while preserving orientation and scale. The circular
  arrow works in both lock states; detached layout changes preserve bottom centre.
- Preserve the universal panel scale, independent HUD scale, sensible limits,
  native controls and all real inventory slot identities/capacity/locked rules.
  Landscape Inventory is 7 x 4; portrait retains 4 x 7. Apply both orientations
  throughout the main menus, with shared state/layout helpers and reachable
  controls across resolution/UI-scale changes.
- Implementation and verification details are appended to
  `doc/WarscapeUIFrameworkPhase1.md`. Codex handles backed-up addon deployment;
  the user performs in-client visual/gameplay review. This authorizes no new
  gameplay system, map alteration, database change, native build, commit or push.


## UI symmetry and fidelity refinement — approved, 31 October 2026

- The user confirmed existing UI functionality works and authorized a focused
  visual pass: mirror locked menu placement about the minimap, use matching
  exterior profiles for a chosen orientation, harmonise HUD/Inventory/Skills
  visual sizes, and improve the same approved bronze gryphon's source fidelity.
- Preserve independent orientation/lock/detached choices, established shared
  panel scale and independent HUD scale, shortcuts, highlights, native actions,
  slot identities and XP calculations. Deliberately detached windows may remain
  asymmetric. No Mining, combat, XP-system or database changes are authorized.
- A higher-resolution 494 x 299 source of the same approved gryphon exists.
  Compile from it instead of enlarging the 128 x 76 runtime reduction. Preserve
  source RGB/silhouette/transparency and existing dragon textures; no new design
  or aggressive sharpening is authorized or needed.
- This supersedes the prior unequal left/right dock gutters and mixed native/
  custom portrait exterior profiles. Measurements, asset provenance, diagnostics,
  tests and deployment are recorded in `doc/WarscapeUIFrameworkPhase1.md`.
  The user performs in-game review. Do not launch WoW, commit or push this pass.


## Persistent HUD-side menu windows — approved correction, 31 October 2026

- Window position, lock state, orientation, scale and layout persistence belong
  to LEFT and RIGHT HUD-side containers, not individual menus. Switching menus
  replaces content without a default-anchor flash or layout reset. Keep actual
  menu-to-side assignments and the one-main-window-per-side limit.
- This explicitly supersedes the earlier per-menu layout settings and universal
  menu scale. The two sides are independently movable, lockable, rotatable and
  scalable; the HUD keeps its independent scale. Relocking returns a side to
  its existing dock without resetting orientation or scale.
- Reuse the existing registry/frame infrastructure. Preserve native item/menu
  interactions, keybinds, highlighting, Escape, scrolling and artwork. Shared
  preferred bottom-centre positions survive content-size changes, with viewport
  fitting only where needed to keep controls reachable.
- Migrate legacy preferences where possible, preserve the originals, and use
  normal per-character SavedVariables for the new side records. The user forbids
  launching WoW, database changes, commits and pushes for this revision.
- Implementation and validation: `doc/WarscapeUIFrameworkPhase1.md`, persistent
  left/right window ownership entry. The user performs actual client review.

## Bronze, Iron and Steel Mining tools — approved design, 1 November 2026

- Separate tools use item/display IDs 900220–900222. Attained Mining levels are
  1/1/6; Mining roll intervals are 8/7/6 ticks (4.8/4.2/3.6 seconds). Choose the
  fastest eligible carried tool, without requiring equipment. Original 2901
  remains a bronze-speed fallback. Ore success probability and XP stay unchanged.
- OSRS Attack-to-wield levels 1/1/5 and original combat bonuses are documented
  for future equipment integration; they do not gate inventory Mining or imply
  an approved conversion to WoW combat ratings.
- Reuse the original Mining Pick silhouette with separate bronze, iron and steel
  icon/hand textures; preserve shared Blizzard assets and all 15 ore lifecycles.
- Implementation and validation: `doc/WarscapePickaxeProgression.md`. Database
  migration requires separate exact approval; no WoW launch, commit or push.


## Cogfall Coast terrain map — approved layout, 1 November 2026

- Create a separate 5x5 Noggit 3.3580/WoW 3.3.5a landscape from the user-supplied
  Cogfall Coast illustration, interpreted as geographic layout rather than literal
  buildings, text or ferry connections. Map 913, Warscape - The Cogfall Coast,
  occupies ADTs X=30..34, Y=30..34. Existing maps 901..912 stay unchanged.
- Preserve the connected northwest Rimecap/Splitstone range, western coastal
  Cogfall/waterfall, downstream Drowned Reach and inland southeastern Siltfall
  Abbey; central Stillwater/islands/Larkhaven; elevated Widowmoor and northeastern
  Graveshore headland; eastern Sunglade with a ragged blighted northern edge;
  compact Amberhoof farmland east of the southern river; eastern-shore Wayfarers
  Rest and southern coastal Shellbank. Reserve buildable surfaces, no buildings.
- Use an inspected broad-shape pass followed by one biome-aware natural-detail
  stage at native mesh resolution. Sea level 0, lake 64; use real client materials
  and descending native liquid data. No objects, NPCs, quests or live deployment.
- Graveshore reserves a mostly intact circular upper platform, a small seaward
  collapse, solid under-city volume and a lower cave/lift ledge. No roofed ADT
  cave, overhang, WMO, lift or other placements are authorized by this pass.
- Generated project, validation and clearly labelled offline terrain previews:
  C:\WoWDev\Worldgen\WarscapeCogfallCoast-913\README.txt. Manual Noggit/game
  appearance and traversal remain for user review. The editable project is the
  NoggitProject folder, not one of its preserved generated drafts.


## Cogfall Coast exploration deployment - authorized 1 November 2026

- The user explicitly authorized deploying map 913 after receiving the editing
  project and teleport command. This supersedes the initial no-live-deployment
  instruction for installation only; terrain, saved source and zero-object scope
  remain unchanged. No NPCs, quests, database migration or new systems.
- Freshly merged client patches and Map.dbc registration, terrain data, empty
  object collision and terrain navigation are installed with checked backups.
  Source Noggit files, existing maps and unrelated patch payloads are preserved.
- Start the existing server/client normally and use
  `.go xyz -166.720 -362.360 80.902 913`. Server terrain at arrival is about 77.902.
  Codex did not launch/operate WoW or start/stop servers. User in-game review
  remains pending; details: C:\WoWDev\Worldgen\WarscapeCogfallCoast-913\Deployment-001\DEPLOYMENT.txt.

## Smithing framework � approved and implemented, 1 November 2026

- User authorized an independent Warscape Smithing skill through the existing
  shared framework, levels 1�99 with the OSRS curve, starting at level 1 / 0 XP.
- Persist XP and an independent half-point carry; synchronize through the
  existing Skills menu and reuse custom GM permissions and self targeting.
- Framework only: recipes, bars, equipment, furnaces/anvils, interactions,
  crafting UI, timers, animations and materials remain deferred.
- [Smithing implementation plan and validation](Warscape%20Smithing%20Plan.txt).

## First Bronze smelting loop - approved, 1 November 2026

- The user's new request supersedes the earlier Smithing framework-only scope
  for this one recipe: Copper Ore 2770 + custom Tin Ore 900201 yield one new,
  non-stackable Bronze Bar 900500, guaranteed at Warscape Smithing level 1.
- Award exactly 6.2 XP using persisted tenths; migrate the former Smithing half
  carry by multiplying by five. Mining's half carry stays unchanged.
- Use native Forge spell focus 3 and each object template's distance, distinct
  from Anvil focus 1. No furnace/anvil template or Blizzard profession changes.
- One-bar action with configurable temporary 3000ms duration. Validate at start
  and completion, cancel on movement/combat/death/logout/proximity loss, and
  save ingredients, output and XP through the existing character transaction.
- Small Bronze recipe card within Skills, opened from the Smithing tile.
  Equipment recipes, other bars, batch smelting and anvil crafting are deferred.
- [Implementation, deployment and test details](Warscape%20Smithing%20Plan.txt).

## Forge Smelting interface - approved design, Stage A prepared, 1 November 2026

- User approved the attached Smelting design: hammer corners, heated stone,
  eight bars in two rows of four, quantities 1/5/10/All and automatic opening
  from a forge interaction, initially entry 173063. Keep interaction panels
  independent of both saved HUD-side containers.
- Bronze retains its existing approved recipe/XP/timing; seven other bar slots
  remain disabled without invented recipes or substituted vanilla items.
- This supersedes the single-card interaction and one-bar-only scope for the
  later interface milestone; those behaviours are still the deployed version.
- Stage A audits the native client click limitation and prepares the shared
  recipe registry. Later stages remain outstanding. New database migrations
  require explicit approval under the user's latest Stage D instruction.
- [Audit, registry, implementation checkpoints and status](Warscape%20Smithing%20Plan.txt).

## Smelting Stage B - authorized and implemented, 1 November 2026

- User explicitly authorized finishing forge interaction and the functional
  Bronze UI/batching vertical slice after Stage A. Only entry 173063 gains the
  targeted native interaction permission; its spell-focus function is preserved.
- Inventory's shared frame/typography/controls and independent interaction
  scaling host the approved hammer/heated-stone Smelting design, eight slots,
  disabled future bars, dynamic availability and quantities 1/5/10/All.
- Bronze reuses its current recipe, safe inventory path and persisted tenths.
  Server binds each batch to the clicked forge and validates each bar. No new
  database migration or other bar recipes were needed. In-game QA remains pending.
- [Builds, tests, assets, deployment and exact test sequence](Warscape%20Smithing%20Plan.txt).

### Smelting interaction adjustment - 2 November 2026

Confirmed implementation detail: Warscape forge entry 173063 uses a 2.5-yard
center-distance interaction limit, matching the native spell-focus client
metric. The server config may tighten this limit up to the client's fixed 2.5
maximum. The bound UI closes on server-confirmed acceptance; accepted batches
continue with the panel hidden and retain the existing cancellation safeguards.
A 3.3.5a data audit found the furnace (1.08) and Warscape anvil template 173065
(1.85) are their verified source sizes, with no per-spawn scale or display
mapping override. Those stock dimensions were preserved; reducing them would
change collision and depart from verified data.

### Forge range correction - Stage D, 2 November 2026

This explicitly supersedes Stage C's temporary 2.5-yard center-origin cap.
The client uses a 5-yard margin from forge display bounds, and server use/session
checks use the same rotated, template-scaled display-box boundary. Server spell
focus discovery retains its native 10-yard template distance. Display 305's
asymmetric local bounds extend toward the bellows, so the existing model-aware
interaction box covers the firebox, middle, and bellows without moving the model
or adding a guessed center offset. The shared range must be balanced in client
and server together; a server-only runtime override would permit inconsistent
client/server decisions.

### Smelting forge interaction refinement - Stage E, 2 November 2026

The user requested a centre between the firebox and bellows and a shorter,
consistent boundary. Stage D had no centre offset: it expanded display 305's
entire asymmetric bounds by five yards. Stage E instead derives a ground-plane
centre from the DBC footprint midpoint, applies template scale 1.08, and rotates
that point with entry 173063. The paired client/server radius is 4 yards for
opening/validating interaction, menu refresh and batch cancellation; the native
spell-focus candidate search remains 10 yards. The chosen radius is an initial
geometry-based value. Screenshot-distance acceptance remains pending manual
in-game testing; no gameplay result is claimed.

## OSRS enemy catalogue - approved direction, 7 November 2026

The user approved OSRS Wiki bestiary data as the source for enemy variants,
combat stats and drop chances, with suitable WoW models/animations/sounds.
The first implemented milestone is an additive ordinary level-2 Goblin entry,
using existing monster profiles/combat XP and an exact integer-weighted F2P
main loot pool. Drops are currently collectible item identities; equipment,
consumable/currency functionality, conditional tertiary drops and other Goblin
variants remain future work. See `WarscapeOSRSEnemies.md` for the verified scope,
deployment record and manual acceptance steps. Do not treat the rest of the
bestiary as implemented or approved balancing data without per-variant sourcing.

## Kieran enemy-family notes - approved direction, 7 November 2026

The user supplied Kieran's family/model list and confirmed that the first Goblin
works and drops Bones. Families have shared Slayer identity, with separately
defined level/role subcategories and loot. The model directions are preserved
in `contrib/warscape/enemies/family-roadmap.json`; planned entries are not active
content. The next implemented release adds Cows, ordinary/Stronghold Rats and
three Giant Rat tiers, plus shared family metadata and `.rs enemy` diagnostics.
See `WarscapeEnemyFamilies.md` for sources, contributor workflow, validation and
known limitations, including the stock Bess model's missing attack animation.
Slayer task assignment/rewards and global world spawning remain future work.

## Larger enemy batches - user direction, 7 November 2026

The user confirmed the Cow/Rat batch working with correct drops and authorized
larger implementation batches chosen independently from Kieran's list. The next
implemented batch contains 21 variants across Bats, Bears, Wolves, Spiders and
non-poisonous Scorpions. It adds opt-in published maximum-hit caps and per-style
melee defences for these new variants, retaining the seven accepted entries'
prior combat policy. Wolves use members-world Wolf bones for all Warscape players;
there is no membership gate. Conditional/tertiary loot and the poisonous Scorpion
remain separate work. See `WarscapeWildlifeBatch.md` for source snapshots,
validation, deployment and manual test steps. Source-backed model directions remain
a roadmap for unimplemented families, not a claim of complete bestiary support.

### Enemy catalogue: larger coastal/wildlife checkpoint (7 November 2026)

Confirmed: the user accepted the previous Bats/Bears/Wolves/Spiders/Scorpions batch
with correct drops and authorized an even larger batch, choosing families from
the updated supplied list. The next implementation adds 28 distinct variants in
Birds, Crabs, Crocodiles, Dogs, Monkeys, Snakes and Terrorbirds. Main-table loot
uses exact rational chances, native quantity ranges and paired outcomes; quest,
tertiary and special AI mechanics remain separately scoped. See
[coastal wildlife checkpoint](WarscapeCoastalWildlifeBatch.md) for explicit policy
choices and manual acceptance steps. New entries are pending user acceptance.

### Enemy catalogue: dungeon/humanoid checkpoint (7 November 2026)

Confirmed: the user accepted the entire coastal wildlife checkpoint with correct
drops and authorized the next large batch. This checkpoint adds 39 variants in
Dwarves, Pirates, Skeletons, Zombies, Ghosts, Ghouls, Hellhounds and Minotaurs.
Native equipment templates supply visible weapons; source stats and exact
main-table loot use the existing architecture. Source gaps and prototype policies
are explicit in [dungeon/humanoid batch](WarscapeDungeonHumanoidBatch.md).
These new entries await user gameplay acceptance.

### Enemy catalogue: martial-family checkpoint (7 November 2026)

Confirmed: the user accepted the dungeon/humanoid batch with drops and asked
for the next batch. This checkpoint adds 53 melee variants across Warriors,
Knights, Hobgoblins, Flesh Crawlers, Ogres, Bandits and Rogues. Shared authoring
now supports the reviewed low-level general seed tier and uncommon seeds, with
listed probabilities retained and the uncommon table's unlisted two slots
explicitly modeled empty. See [martial-family batch](WarscapeMartialFamiliesBatch.md)
for model approximations, source assumptions and acceptance steps. The new
53 variants await user gameplay acceptance.

### Enemy catalogue: giants/demons checkpoint (7 November 2026)

Confirmed: the user accepted the martial-family batch with drops and authorized
the next batch, including more entries where appropriate. This checkpoint adds
57 variants across Giants, Demons, Werewolves, Trolls, Mammoths and Possessed
Tools. Native loot references support fixed quantities above 255 without
changing existing item stacks; monster-only zero Ranged/Magic stats preserve
the published Mountain troll stats. See [giants/demons checkpoint](WarscapeGiantsDemonsBatch.md)
for scope, assumptions, model approximations and pending acceptance.


### Enemy catalogue: Slayer and melee prototypes checkpoint (7 November 2026)

Confirmed: the user accepted the 57-variant giants/demons batch with drops and
asked for an even larger next batch from the updated Kieran list and OSRS Wiki.
The preceding 205 catalogue entries now have reported gameplay acceptance.
This checkpoint adds 70 variants, bringing the prototype catalogue to 275 across
50 families. See [Slayer/melee checkpoint](WarscapeSlayerPrototypesBatch.md) for
all spawn IDs, verified deployment and pending manual acceptance.

Implementation decisions under the user's delegated judgment: select non-poison
melee forms and baby dragons, implement magical melee using Magic equipment
resistance and the separately truncated 70% Magic / 30% Defence level blend,
and retain source Slayer requirements as explicit reference metadata. Warscape
has no Slayer skill; gating, task assignment and Slayer XP remain future work.
These are combat/loot prototypes with native WoW models and AI, rather than a
claim that original special mechanics or the entire enemy family are complete.
The new 70 entries await the user's gameplay/visual/drop acceptance.


### Enemy catalogue: smaller checkpoints (7 November 2026)

Confirmed user direction: reduce future enemy batches to a few at a time as the
remaining families require more specialised behaviour. The user delegated which
families to implement next. This supersedes the earlier request for increasingly
large batches; it does not establish gameplay acceptance for unreported tests.

This checkpoint selects Otherworldly being 64 and Catacombs Shade 140, adding
successful-player-melee flat armour support with source values -2/-3. Misses stay
at zero; adjusted OSRS damage feeds display scaling and health-capped combat XP.
Every earlier catalogue variant defaults to zero armour, preserving prior policy.
See [spectral checkpoint](WarscapeSpectralEnemies.md) for sources, deployment and
manual tests. Other Shade variants, spectral Prayer rewards, elemental weaknesses,
Slayer tasks, and ranged flat armour remain separate work. These two new entries
await the user's in-game acceptance.


### Enemy catalogue: follow the supplied list order (7 November 2026)

Confirmed: the user accepted both spectral entries working with drops and now
requires the remaining enemy families in the supplied list order. The explicit
next batch is Lizard, Scarab, Druid and Dwarf. Preserve this ordering for future
choices, skipping already covered families unless the user requests additions.
This refines the earlier permission to choose freely; batches remain focused.

The implementation adds three desert-lizard tiers with an ice-cooler finishing
item, one Scarab Swarm with source-speed melee and a scoped poison aura, one
Taverley Druid with mixed melee/magic, and the missing level-20 Dwarf. The prior
13 Dwarves remain unchanged. Data, documented assumptions, deployment and pending
manual tests are in [ordered checkpoint](WarscapeOrderedEnemyBatch.md).
Only source Slayer requirement metadata is retained; no Slayer skill was added.


### Enemy catalogue: Elf, Aviansie, Hobgoblin and Suqah (7 November 2026)

Confirmed: the user accepted the preceding ordered batch working with drops and
requested these next four families, continuing the supplied order and delegating
routine decisions. Six new entries represent Elf Warriors, low/high Aviansie and
Suqah melee/hybrid forms. All seven existing Hobgoblins match the current complete
Wiki page hash, stats, IDs and attack speeds; they are retained without duplication.

The batch introduces NPC ranged attacks, ordinary-player-melee protection for
Aviansie, melee-range-only hybrid casts and precise fractional Slayer XP reference
metadata. No Slayer skill/training is added. Existing player ranged/magic paths
remain in use. Native models, selected spell probabilities, a three-second freeze
and deferred source exceptions are documented prototype choices. See the
[checkpoint](WarscapeElvesAviansieSuqah.md) for exact scope and pending user tests.


## OSRS Coin stacking � user-approved revision, 7 November 2026

The user requested OSRS-style Gold stacking. Warscape's existing Coins item
902006 now uses the OSRS maximum of 2,147,483,647 per stack instead of 200. This
supersedes the earlier collectible-only 200-stack policy for Coins specifically;
existing balances and other items remain intact. Native WoW money stays separate.
Currency conversion, vendor spending and a complete OSRS economy are not implied.
See [Coin stack implementation and acceptance](WarscapeCoinStacks.md). Manual
client acceptance remains pending until the user confirms it.


### Enemy catalogue: Lizardman, TzHaar, Drake, Wyrm and Wyvern (7 November 2026)

The user confirmed the preceding Elf/Aviansie/Hobgoblin/Suqah batch working with
drops and requested these next five families in list order. Seven representative
variants add Lizardman53/62, TzHaar-Ket149/Xil133, Drake192, Wyrm97 and Skeletal
Wyvern140. Source stats/loot, large-quantity drops, poison, style switching and
breath prototypes build on the shared catalogue. Other family variants remain
future work. See [checkpoint](WarscapeDraconicTzHaarBatch.md) for source ambiguities,
chosen policies, deployment checks and pending user acceptance. Only the user's
observed earlier drop acceptance is recorded; this batch is not yet accepted.


### Enemy catalogue: Waterfiend, Banshee and Revenant (7 November 2026)

The user confirmed Lizardman retaliation with GM mode off, then requested these
next three families. Five representative entries cover Waterfiend115, Banshee23,
Twisted Banshee89, Revenant imp7 and knight126. They extend the shared system with
magical-Ranged defence, equipable ear protection, finite Revenant healing and
independent stepped loot pools. Source ambiguities, chosen prototype mechanics
and unimplemented stat drains/charged-bracelet effects are explicit in the
[checkpoint](WarscapeWaterBansheeRevenants.md). Manual acceptance is pending.


### Enemy catalogue: Killerwatt through Basilisk (8 November 2026)

The user confirmed Waterfiend/Banshee/Revenant working and requested Killerwatt,
Nagua, Aberrant Spectre, Aquanite, Araxyte and Basilisk in that order. Ten variants
cover all lesser Nagua, regular/Deviant Spectres, both ordinary Araxyte tiers and
representatives of the other families. Shared additions cover gear damage caps,
double hits, venom and per-encounter lure/reinforcement defences. Stat drains,
Basilisk gaze/mirror enforcement and several quest/prayer specials are explicitly
unimplemented; see [checkpoint](WarscapeSlayerElementals.md). User acceptance of
this new batch remains pending.

8 November 2026 enemy checkpoint: user confirmed prior six families working with drops. Added Catablepon, Cave Crawler, Cave Horror, Cave Slime and Cockatrice; seven representative entries, source-backed stats/loot, existing poison prototype. Temporary drains, gaze and Cave Horror scream remain future work. See WarscapeCaveFamilies.md; new in-game acceptance pending.

8 November 2026: user confirmed cave batch working. Stalker/Dark beast/Dust devil/Ent/Gargoyle checkpoint adds nine entries and reusable Gargoyle finishing hammer. Ent harvesting, Stalker bleed and Dust devil facemask/stat effects remain pending. See WarscapeStalkersGargoyles.md.

8 November 2026: user confirmed preceding five-family checkpoint working. Gryphon/Harpie/Hydra/Infernal Mage/Kurask checkpoint adds five regular profiles; Hydra three-attack style cycle supported. Weight/lantern/leaf-weapon requirements, Hydra poison pools and ordered ring pieces remain pending. See WarscapeGryphonsHydras.md.

8 November 2026: prior five-family checkpoint confirmed working. Nechryael/Rockslug/Smoke Devil/Sourhog/Turoth/Wall Beast/Zygomite checkpoint adds eleven regular variants. Salt finisher and single-dose fungicide prototype implemented; refills, summons, environmental interactions and equipment restrictions remain pending. See WarscapeNechryaelsZygomites.md.

8 November2026: user confirmed refillable spray and requested review of unfinished conversation work. Central backlog: WarscapePendingWork.md. First reviewed milestone adds owned Nechryael Death spawns with cap/timer/cleanup; native WoW retaliation/logout exceptions remain explicit. See WarscapeDeathSpawns.md; gameplay acceptance pending.

8 November2026 backlog milestone: Harpie902301 equipped Lit bug lantern902586 requirement uses generic off-hand rule and current player/owner equipment at damage time. Stats/loot unchanged. Lighting/Firemaking remains future work; manual gameplay acceptance pending. See WarscapeHarpieLantern.md.

8 November2026: Harpie lantern checkpoint confirmed working. Smoke Devil902402 Facemask902587 head-slot requirement implemented via generalized equipment registry; existing source stats/loot unchanged. Smoke hazards/stat drains/Dust Devil mitigation remain pending. See WarscapeSmokeFacemask.md; manual acceptance pending.

8 November2026: Smoke Devil facemask checkpoint confirmed working. Sourhog saliva equipment milestone uses Reinforced goggles902588 on head; unprotected20-30 source damage, protected existing roll/max6. Temporary skill drains remain pending. See WarscapeSourhogGoggles.md; manual acceptance pending.

8 November2026 pending equipment milestone: Dust Devil902204/902205 Facemask902587 head protection now restores source max8/10 with ranged-defence accuracy and melee reach; unprotected fixed16. No XP/stat drains, environmental smoke or prayer system invented. See WarscapeDustProtection.md; manual acceptance pending.

8 November2026 backlog milestone: Cave Crawler902103 and Kurask902304 replace native regeneration with one source HP each3seconds, including combat. Native percentage regen disabled for only those entries. Turoth source rate not verified, unchanged. See WarscapeNaturalRegeneration.md; runtime timing acceptance pending.

8 November2026 finisher backlog milestone: Rockslug902401 at1 source HP stops retaliation/chase and uses native local random movement while remaining saltable. Loot ownership retained, native regen paused for finish window and restored on reset; owner abandonment triggers normal evade. Autosalt/brine sabre remain pending. See WarscapeRockslugWander.md; manual acceptance pending.

8 November2026 weapon/finisher backlog milestone: new Brine sabre902589 uses existing source item bonus/speed profile and permanent40 Attack equip guard; main-hand usable player melee auto hits bypass Rockslug salt floor. Other finishers unchanged. Liquify/acquisition remain pending. See WarscapeBrineSabre.md; manual acceptance pending.

8 November2026 leafy-weapon checkpoint: new usable Leaf-bladed sword902590 uses existing bonus/speed profile and50 Attack equip helper. Four Turoths/Kurask now reject unsupported player-owned damage, permit eligible main-hand auto melee. Old collectible stacks/loot preserved. Broad ammo/Magic Dart/other leaf weapons/conversion remain pending. See WarscapeLeafWeaponGate.md; manual acceptance pending.


### 8 November 2026 - Leaf-bladed spear checkpoint

User confirmed the preceding sword checkpoint working. Added usable two-handed spear 902591 through existing item profiles/equip guard and Turoth/Kurask damage gate: 50 Attack, 5 ticks, Wiki bonuses. Existing XP/items preserved. Built/deployed; spear gameplay acceptance pending. Slayer 55, acquisition, full source Controlled style selection, battleaxe and broad/Magic Dart remain future. See WarscapeLeafSpear.md.
