# Warscape Bronze, Iron and Steel Pickaxes

Implemented and staged, 1 November 2026. Database application and deployment
await explicit approval. No WoW session was launched; in-game rendering and
gameplay remain for the user to confirm after installation.

| Tool | Item / display ID | Attained Mining | Future Attack to wield | Mining interval | GM command after installation |
|---|---:|---:|---:|---|---|
| Warscape Bronze Pickaxe | 900220 | 1 | 1 | 8 ticks / 4.8 seconds | `.additem 900220 1` |
| Warscape Iron Pickaxe | 900221 | 1 | 1 | 7 ticks / 4.2 seconds | `.additem 900221 1` |
| Warscape Steel Pickaxe | 900222 | 6 | 5 | 6 ticks / 3.6 seconds | `.additem 900222 1` |
| Original Mining Pick | 2901 / 6568 | 1 | 1 | 8 ticks / 4.8 seconds | `.additem 2901 1` |

The shared engine uses `WarscapeMiningTools.h`. `GetRSSkillLevel(Mining)` supplies
the permanently attained level. The fastest eligible tool in carried bags,
backpack or equipment wins; bank items do not qualify. Equipping is unnecessary
and Attack never gates inventory mining. Custom Bronze wins an equal-speed tie
with 2901. Losing/gaining a better tool during mining restarts a full interval.
Steel alone below Mining 6 cannot mine; a carried lower-tier tool is the fallback.

All 15 ores retain their existing success parameters, half-point XP, one-item
reward and non-stackable ore templates. No pickaxe multiplies success probability.
Nine-second depletion, grayscale models, scaling/collision, independent sessions,
animation/interruption, skill persistence and ore requirements are unchanged.

## OSRS combat audit: documentation only

Sources checked 1 November 2026:
[Pickaxe comparison](https://oldschool.runescape.wiki/w/Pickaxe),
[Iron pickaxe](https://oldschool.runescape.wiki/w/Iron_pickaxe), and
[Steel equipment](https://oldschool.runescape.wiki/w/Steel_equipment).
These original bonuses are recorded for a future approved equipment mapping.
They are not converted into WoW damage, ratings, requirements or Warscape bonuses.

| Pickaxe | Attack stab / slash / crush / magic / ranged | Defence stab / slash / crush / magic / ranged | Melee strength |
|---|---|---|---:|
| Bronze | +4 / -2 / +2 / 0 / 0 | 0 / +1 / 0 / 0 / 0 | +5 |
| Iron | +5 / -2 / +3 / 0 / 0 | 0 / +1 / 0 / 0 / 0 | +7 |
| Steel | +8 / -2 / +6 / 0 / 0 | 0 / +1 / 0 / 0 / 0 | +9 |

Ranged strength, magic damage and prayer bonuses are zero. Original weight is
2.267 kg. Attack requirements 1/1/5 are metadata for future wielding integration;
the current custom items inherit 2901's existing WoW weapon properties equally.
Mining intervals are separate from combat swing speed.

## Assets and native weapon visuals

`contrib/warscape/mining/build_pickaxe_assets.py` creates six private-path BLP2
textures and appends three rows each to Item.dbc and ItemDisplayInfo.dbc. Existing
rows and string bytes remain intact. The letter-patch precedence is handled
locally so installed custom ore Item.dbc rows survive the merge.

- Icons: `Interface\Icons\INV_Warscape_Pickaxe_{Bronze,Iron,Steel}.blp`.
- Hand textures: `Item\ObjectComponents\Weapon\WarscapePickaxe{Bronze,Iron,Steel}.blp`.
- Shared original silhouette: `Item\ObjectComponents\Weapon\Axe_1H_Pick_A_01.m2`,
  its original `00.skin`, and `ARMORREFLECT3.BLP`, all resolved in the actual client.
- Display rows clone 6568, replacing only ID, model texture basename and icon.
  The native client uses model replaceable texture type 2 for the tier metal.
- Only metal pixels are recolored; original shading, alpha, outline and wood are
  retained. Every mip is read back and checked. No original texture/model changes.

Mining uses native `SetVisibleItemSlot` with the selected carried Item, without
equipping, allocating or retaining Item pointers. Stop restores the current
equipped mainhand and enchantments, including changed equipment or an empty slot.
An appearance already replaced by a real equipment operation is preserved.

Memory review: only existing mainhand entry/enchantment update fields are used;
compile-time checks bound them to PLAYER_END. No client C++ code, structures,
mapping tables, object allocation/destruction or deferred-lifetime paths changed.
The existing Release `MirrorLayoutSafetyCheck` passed. This does not substitute
for user testing of a rendered hand model or an equipment change in-game.

## Validation and release candidate

- Release worldserver and tests built successfully. CMake was reconfigured to
  refresh its cached source list so the preexisting Mining script is linked.
- All 33 `[warscape]` Release cases passed: 70,642 assertions.
- The runtime fixture compiles the actual selection/show/stop method bodies;
  3,461 checks passed, including all inventory combinations over levels 0–99,
  all 15 ores/four tools, inventory-only visuals, equipped weapon/enchant restore,
  equipment changes, unarmed restore, tool removal and offline cleanup.
- Six asset integration tests passed: unique mappings, original DBC preservation,
  model/SKIN/static texture dependencies, exact alpha at every mip, preserved
  nonmetal pixels, additive MPQ readback, all 15 ore rates/XP and malformed inputs.
- Eight database-tool guard tests passed. Read-only migration preconditions pass;
  postconditions correctly report false before application.
- Original and generated icon/texture proofs were visually inspected as images.
  No actual WoW icon/model loading or gameplay test has been performed.

Release candidate:
`C:\WoWDev\Artifacts\WarscapePickaxes-20261101-001\assets-002`.
The earlier `assets` directory is superseded and must not be installed.
Server executable is staged under the same artifact root's `server` directory.
Source backups: `C:\WoWDev\Backups\WarscapePickaxes-before-20261101-005142`.

Repeat focused checks from the TrinityCore checkout:

```powershell
py -B -m unittest discover -s contrib/warscape/mining -p test_pickaxe_assets.py -v
py -B contrib/warscape/mining/run_pickaxe_runtime_tests.py --output C:\WoWDev\Artifacts\PickaxeCallbacks-check
```

## Exact pending migration and installation gate

Review `contrib/warscape/migrations/pending/2026_11_01_00_world.sql`, SHA-1
`37214478DF0AFA8A5FDA90344B889F30DA719FFF`, with matching verification JSON under
`contrib/warscape/verifications`. It inserts exactly three item_template rows by
cloning 2901. Overrides are entry, name, displayid, description, stackable=1,
maxcount=0 and zero WoW RequiredSkill/Rank/Level. No schema or existing-row writes.
Full base-row identity, schema, engine, key, unused IDs and clone-field equality
are checked before/after application. The explicit Mining gate remains server logic.

This review file deliberately stays outside updater paths. Once the user approves
this exact hash, copy unchanged bytes into `sql/custom/world/2026_11_01_00_world.sql`
so db.py can discover it; do not promote it before approval. Use db.py status,
permissions and apply with stopped servers/updaters; apply creates a fresh verified
backup. Never bypass its history, hash, backup, precondition or failure-lock guards.

After approval, recheck source hashes and regenerate additive merges if another
session changed either MPQ or server DBC. Back up every replaced installed file
outside Git; install the paired server executable, additive server DBCs and client
patches together. Preserve all unrelated archive entries. No deployment has occurred.
Restart the server and fully close/restart the client after installation; `/reload`
does not reload MPQs/DBC. Do not launch WoW automatically, commit or push.

User checklist after installation: obtain each tool, compare icons and hand colors,
mine with each from bags, test Steel at levels 5/6 and mixed inventories, move to
interrupt, check weapon/enchant restoration and a nine-second depletion/recovery.

## Collar recolour correction — 1 November 2026

The metal socket/collar at the head-to-handle joint is included in every tier's metal recolour mask for both the inventory icon and model diffuse. The adjacent wrapped handle bindings and wood remain unchanged. Future pickaxe recolours must include this socket while preserving the same boundary.

Corrected art review: `C:\WoWDev\Artifacts\WarscapePickaxes-20261101-001\assets-003\Bronze-collar-review.png`. This revision is prepared only; it has not been deployed.


## Approved art and deployment preparation — 1 November 2026

The user approved all three tiers including the socket recolours. `assets-003` supersedes `assets-002`. The prepared, checksummed deployment bundle is `C:\WoWDev\Artifacts\WarscapePickaxes-20261101-002\prepared`; it contains the two additive client MPQs, server Item.dbc and ItemDisplayInfo.dbc, and the reviewed Release worldserver.exe. Seven asset integration checks and 3,461 mining runtime checks pass against the approved revision. The bundle is not installed. Applying the reviewed world migration is still gated on explicit approval of its exact file and SHA-1, per `AGENTS.md` and `doc/WarscapeDatabaseWorkflow.md`.


## Approved deployment — 1 November 2026

The exact world migration was approved and applied through `contrib/warscape/db.py`; postconditions pass and status shows no pending world migrations. A fresh verified database backup was created by the apply command. The five-file client/server deployment completed with checksum verification: client `Data\patch-Z.MPQ` and `Data\enUS\patch-enUS-Z.MPQ`; server `dbc\Item.dbc`, `dbc\ItemDisplayInfo.dbc` and `worldserver.exe`. All replaced files were backed up outside Git under `C:\WoWDev\Backups\WarscapePickaxes-deploy-20261101T2134058874Z`. The corrected `assets-003` package is installed; original item 2901 rows/assets and all preexisting DBC rows were verified unchanged. Restart the server and fully restart the client before testing. The game was not launched.

\n