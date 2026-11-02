# Briarbrook — one-tile world-building challenge

26 October 2026. This is an original settlement on map **905**, directory
`WarscapeBriarbrook`. It does not continue Lumbridge or start Checkpoint C.
The user has inspected and accepted the first village's layout, architecture,
proportions, roads, market, well, benches and atmosphere, and made Briarbrook the
permanent starting point for world-building and gameplay testing. The original
build/deployment record below is retained as history. The subsequent visual
refinement and Cinderfield farm require a fresh user inspection; no manual
collision or gameplay result is inferred from the earlier visual approval.

## Composition and method

Briarbrook is a wooded market hamlet, with an approach that reveals a common,
well and old oak between the Blue Bough inn and Copperkettle smithy. The high
street bends toward a provisioner and an orchard cottage. Two smaller homes,
kitchen gardens, a harvest barn and a returning woodland path make a connected
place with working and domestic spaces. The core is approximately 185 by 165
world units, contained in one 533⅓-unit ADT tile at 32,32. Wooded hills frame the
playable routes well inside the tile boundary.

The native Goldshire inn/smithy, HumanTwoStory, three human farm houses and barn
are complete, unscaled WMOs. They are arranged in a new layout. Native awnings
already include their counters; goods sit on the measured counter surfaces.
Beer-garden furniture, sacks, cart, woodpile, anvil, crops, varied trees,
property fences, flowers and lamps support specific uses of each property.
There are no new NPC records, SQL changes, quests or scripted interactions.

The selected method combines explicit door-oriented building placement,
authored curved routes and property details with deterministic terrain and
ecological framing. Native model geometry and textures were rendered offline
to select assets and inspect composition. Noggit is installed locally and the
output remains standard editable Wrath ADT/WDT; this pass uses source-controlled
authoring to keep collision, navigation, ground levels and packaging reproducible.
Blender conversion or new client rendering features were unnecessary.

The offline renderer is an authoring aid. It omits animation, native lighting,
WMO embedded furniture/effects and several game shaders. Its images are **not
screenshots of wowdecomp and do not establish visual acceptance**.

## Causes found and corrections

- Previous experiments spread landmarks over nine tiles with weak near-town
  height variation and loosely related building origins. The new composition
  concentrates the settlement and deliberately joins its entrances and routes.
- Render bounds include buried foundations and cellars. For example, the farm
  model's first walk surface is around local Z=3.611, while its bounding minimum
  is near zero. Aligning that minimum to terrain exposes several yards of stone.
  Farm landing ground is now local Z=3.111, the two-story landing is -1.687 and
  the smithy's landing is zero. Interiors subsequently connect to outdoor nav.
- The inn uses entrance ground, not its cellar minimum, as its placement datum.
  Terrain beneath its native cellar/stairs is excavated; one classic hole quad
  is accepted only after native floor triangles cover its sampled footprint.
- The custom client consumes big-alpha overlays as final blend weights. The
  new materials form a nonnegative simplex with overlay sums at most 255.
  Paths have full-resolution, irregular, soft edges; automatic rectangular
  building-bound texture patches are avoided.
- Several native Elwynn trees refer to glue textures in locale MPQs. Asset
  lookup includes those archives and checks resolved model/texture dependencies.
- The four native surfaces are Elwynn grass shadow, dirt base 2, cobblestone and
  tree dirt. A small worn cobble center and leafier woodland floor vary the
  ground. There are no liquid records in this build. An appended Light.dbc
  default reuses native Azeroth day/night curves without changing existing rows.

## Source and reproduction

Authoring: `contrib/warscape/worldgen/briarbrook.json` and `briarbrook.py`.
`native_preview.py` reads native WMO/M2 mesh batches and BLP textures for offline
inspection. The existing `lumbridge.adt` binary encoder gained optional height
and surface samplers; its original defaults and earlier layouts remain intact.
The sandbox generator and deployer were not changed.

```powershell
py -m pip install -r contrib/warscape/worldgen/requirements-briarbrook.txt
py -m unittest discover -s contrib/warscape/worldgen -p test_briarbrook.py -v
py contrib/warscape/worldgen/briarbrook.py C:/WoWDev/Worldgen/Briarbrook-next
py contrib/warscape/worldgen/build_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-next
py contrib/warscape/worldgen/validate_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-next
```

Generation requires map 905 to be unused, and deployment refuses to replace
existing map-905 artifacts. These commands document first-install reproduction;
after this installation, an iteration must deliberately handle the existing
registration and preserve its deployment backup. Do not remove it or allocate
another ID merely to make a rerun pass. Use a new external build directory.

`build_briarbrook.py` uses the existing Windows map extractor, native VMap
extractor/assembler and MMap generator. Extractor inputs are isolated, with
immutable base MPQs hardlinked and separate generated patch files. Collision
model names are prefixed `warscape905_` so no shared collision model is replaced.

`deploy_briarbrook.py` permits only this one-tile map, verifies completed artifact
checks, appends Map/Light DBC rows, preserves existing archive entries and prior
DBC rows/strings, verifies external backups and hashes all copied runtime files.
It refuses deployment while wowdecomp or either local server is running and
attempts rollback if a copy or preservation check fails. It never invokes a
database updater or database-management tool.

## Validated deployment

Final package: `C:\WoWDev\Worldgen\Briarbrook-905-005`.
External backup: `C:\WoWDev\Backups\Warscape-Briarbrook-20261026-215223-309645`.

- All 30 regression tests passed: 16 legacy worldgen, 6 sandbox and 8 Briarbrook.
- All 256 MCNKs have valid offsets, supported alpha flags, correct layer sizes,
  in-range object references and continuous shared height edges.
- All 1,048,576 sampled overlay combinations have sums at most 255.
- Terrain extraction produced exactly one map tile; height range is about
  Z=24.067 to 103.418, including the inn excavation and outer wooded hills.
  Building landing levels range from Z=30.6 to 36.5.
- Native collision assembly produced one tree/tile and 72 isolated model files,
  with 735 extracted collision instances, including WMO embedded doodads.
- One navigation tile contains 3,546 polygons and 5,607 vertices. All 467 road
  samples, seven sampled interior entrances and four inn cellar/stair probes
  reach the main connected component. Roofs and other separate surfaces produce
  additional components; this is not evidence of live NPC pathfinding.
- 80 runtime files were deployed and hash-verified. All 24 previous client patch
  entries and 112 prior map-specific server artifacts were preserved. Map 904
  remains the permanent flat sandbox; maps 901–903 are retained.
- The custom client was stopped. `Client::SetPaths` was checked: its launch
  executable is `C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe`, and its default
  game directory is that executable's directory. No datadir override was active.
- Authserver/worldserver were stopped through their graceful Windows signal
  handlers and restarted hidden with their existing configs. Database updates
  and autosetup remained disabled. World initialization/readiness and both
  listening ports were confirmed. No client launch or manual WoW input occurred.

No combat, XP, skill, addon, client executable, client settings, saved-variable,
database migration or original Azeroth file was changed. Nothing was staged,
committed or pushed. This build still requires the user's visual/playability
review before it can be called an accepted near-alpha environment.

## User inspection

Enter the custom wowdecomp client normally, then use the approach spawn:

```text
.go xyz -322.666667 -257.666667 33.5 905
```

Optional common/well inspection point:

```text
.go xyz -260.666667 -264.666667 33 905
```

Inspect the approach and common at player height; walk into the inn, smithy,
provisioner and cottages, including the inn cellar; follow the garden track
and woodland loop. Check entrance contact, unwanted terrain inside buildings,
solid walls, texture blending, foliage/camera obstruction and performance.
Return screenshots and observations. Stop for that feedback; no further
checkpoint work or commits are authorized by this handoff.

## Visual refinement and Cinderfield — 26 October 2026

The user accepted the original village as a permanent foundation and authorized
refining the existing map. This revision preserves that layout rather than
rerolling it. The updated package is deployed; its new visual result remains
pending the user's next in-game inspection.

### Verified fluorescent-terrain diagnosis

The original ADT had no `MTXF` texture flags. In wowdecomp,
`CMapArea::LoadTerrainTexture` (`WoW/Source/WorldClient/MapArea.cpp:156`) requests
`name_s.blp` when specular terrain is enabled unless MTXF bit 0 selects the named
base asset. `TextureCreate` (`Engine/Source/Services/Texture.cpp:2476`) falls back
to solid `0xFF00FF00` when the requested texture cannot load. The user's existing
screenshots show this solid green where the grass/forest layers dominate, while
the dirt paths continue to render.

All four base BLPs exist. `ElwynnGrassShadow_s.blp` and
`ElwynnTreeDirtBase_s.blp` do not exist in the active native archives;
`ElwynnDirtBase2_s.blp` and `ElwynnCobbleStoneBase_s.blp` do. The fix is the native
per-texture MTXF array **[1, 0, 0, 1]**, reached through MHDR offset 0x2C. The
grass and woodland floor now resolve to their existing base resources; the dirt
and cobblestone retain their native specular resources. Automated checks resolve
every effective BLP with specular terrain both enabled and disabled.

No texture image was darkened, recolored or replaced. MTEX references, existing
village road/cobble masks, Light.dbc, client settings and the client executable
remain unchanged. Live confirmation of the corrected appearance is still the
user's test; source/resource verification does not substitute for it.

### Terrain and foliage

The enclosing 64-unit outer rise was replaced with a much lower, broader rolling
profile. Building pads, the original village ground and the inn excavation are
protected. The package's extracted range is now approximately Z=24.067–53.704
instead of 24.067–103.418. On the sampled woodland outside radius 140, the 95th
percentile gradient falls from 0.751 to 0.149 (about 80%); the 99th percentile
falls from 0.858 to 0.180. These are automated terrain measurements, not a visual
acceptance claim.

Existing objects retain their UIDs, native assets, XY positions, rotations and
scales. All seven original WMO placement records remain byte-identical. The
validator confirms unchanged elevations for 299 original village placements;
woodland objects and the outer orchard fence follow the changed terrain while
retaining their prior model-to-ground offsets. Only 23 natural scenery instances
inside the newly authorized farm clearing were removed.

813 additional plants and small details occupy 21 explicitly named patches:
pathside grasses, wildflowers, low shrubs, small ferns, mushrooms and pebbles.
Fallen logs and branches complement the farm/woodland margins. Exclusions keep
roads, WMO footprints, entrances, furniture, the common and encounter maneuver
space clear.

`ground_clutter.py` provides the reusable patch sampler. Asset profiles, weights,
scale ranges, patch centers/radii, spacing, counts and independent seeds live in
`briarbrook-refinement.json`. The world supplies its geometry-exclusion callback.
Each patch's seed is independent of ordering, so adding another patch does not
reshuffle existing beds. Unachievable density fails explicitly rather than
relaxing the path/building exclusions.

### Cinderfield

A short branch from the eastern woodland ramble reaches a small raided holding.
It contains a native burnt farmhouse, damaged wooden fence sections, overgrown
crop rows, a broken supply cart, abandoned harvest equipment, grain sacks,
barrels, scattered crates, shovels, discarded timber and woodland boundaries.
The disturbance is composed around the property and its approach rather than
forming an arena boundary.

The clear maneuver space is approximately 40 by 30 units, with room to approach,
retreat and move between future enemies. Five future-only authoring anchors are
recorded and checked against navigation. **No enemies were spawned; no combat,
loot, quest or database work was performed.**

### Reproduction and replacement safeguards

```powershell
py contrib/warscape/worldgen/refine_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-refinement-next --baseline C:/WoWDev/Worldgen/Briarbrook-905-005
py contrib/warscape/worldgen/build_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-refinement-next
py contrib/warscape/worldgen/validate_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-refinement-next
py contrib/warscape/worldgen/deploy_briarbrook.py C:/WoWDev/Worldgen/Briarbrook-refinement-next --replace-existing --prepare-only
```

These commands describe this revision's approved input. Once this revision is
installed, its original-baseline check intentionally refuses to overwrite it with
another first-refinement run. A subsequent user-approved iteration must select
and preserve the then-current approved package, not bypass its hashes or assign
a different map ID. The original first-install commands earlier in this document
remain historical reproduction instructions.

The refiner loads the approved manifest, ADT and height/alpha arrays directly;
it never calls the original object authoring/scatter routine. Replacement staging
requires matching deployed baseline hashes, successful material/geometry/nav
checks, unchanged DBC bytes and the exact map-905 runtime allowlist. The existing
backup-first transaction verifies all copies and retains rollback data externally.

Navigation queries now read Detour's detail triangles, following this checkout's
64-bit-reference buffer layout. A plane fitted to a coarse polygon can differ
from the actual curved walking surface; the new regression fixture ensures
queries use the detailed elevation rather than falsely rejecting a valid path.

### Updated deployment record

Package: `C:\WoWDev\Worldgen\Briarbrook-905-Refinement-002`.
Backup: `C:\WoWDev\Backups\Warscape-Briarbrook-20261026-224244-168977`.

- All **40 regression tests** passed, including the existing worldgen/sandbox
  suites, MTXF/resource-selection tests, deterministic patch/exclusion tests,
  detailed-navigation-height test and isolated replacement-staging tests.
- Terrain, native VMap collision and MMap navigation were rebuilt for the single
  existing tile. There are 78 isolated collision models and 753 collision
  instances; the navigation tile contains 3,450 polygons and 5,421 vertices.
- All 505 road samples, seven original interior entrance probes, four inn
  cellar/stair probes and the ruined farmhouse entrance connect to the main
  navigation component. Twenty maneuver-space samples and all five future-only
  spawn anchors also pass. No live NPC pathfinding result is claimed.
- All 256 MCNKs, alpha sums, shared height edges, object references and texture
  flags pass artifact validation. The original village WMO records and existing
  village road/cobble blend data are preserved.
- 84 runtime files were backed up/replaced and hash-verified. All 24 unrelated
  client patch entries, 112 prior map-specific server artifacts and the two
  protected registration files remain unchanged. No Map.dbc or Light.dbc row
  was added or replaced; maps 901–904 and the flat testing area are preserved.
- The running custom client executable and its command line were verified; it
  used `C:\WoWDev\wowdecomp\bin\Win` with no datadir override. It was closed
  gracefully for patch replacement. Servers were stopped through their graceful
  signal handlers and restarted hidden with existing configs and both database
  updater/autosetup settings disabled. The client was not launched for QA.
- Nothing was staged, committed or pushed. Sources, package diagnostics and
  recovery data remain available for the next user review.

Village approach (unchanged):

```text
.go xyz -322.666667 -257.666667 33.5 905
```

Cinderfield maneuver space:

```text
.go xyz -203.666667 -411.666667 37.158264 905
```

First confirm that grass and forest-floor textures are natural instead of solid
green, while dirt/cobble retain their blends. Then inspect the softened woodland
slopes, vegetation near paths/doors, existing building interiors/cellar and the
farm approach, ruin and retreat space. Check for floating props or foliage/FPS
issues and return screenshots. Further changes wait for that feedback.

## Final nighttime lighting correction — 26 October 2026

The user has now visually approved the environment as the primary development
and gameplay testing map. This supersedes the preceding pending refinement review;
the historical records above are retained. All world layout and terrain authoring
are frozen. Only the white nighttime ground glare is being corrected.

### Diagnosis

Offline inspection of wowdecomp's lighting code, the deployed material metadata,
native BLP headers and disassembled native terrain shaders established the cause:

- `DayNight::SetDirection` supplies the directional light used for terrain's
  diffuse response and its Blinn-Phong reflection. Specular intensity is separate:
  `World.cpp` assigns `m_sunCloudColors[0]` to the shared light's `m_specColor`.
  `MapRenderChunk::InitializeVertexShaderConstants` copied that sky colour into
  terrain vertex constant c27, with exponent 20, without a nighttime energy bound.
- Briarbrook inherits native fallback Light 1 / LightParams 12. Its midnight
  sky/specular colour is `0xE8F1FF`, while directional diffuse is `0x6182A2` and
  ambient is `0x1D3C54`. The almost-white reflection therefore remains much
  stronger than the actual directional lighting of the ground at night.
- The already-correct MTXF selection loads the opaque grass and forest-floor
  base textures, which have no alpha channel. Their sampled alpha is 1. The
  global terrain specular shader treats that as a full reflection mask. Dirt and
  cobble continue to use their native `_s.blp` resources. No texture RGB content,
  texture resource selection or map data is changed for this correction.
- In the native VS 2.0 / VS 3.0 terrain permutations, ambient, diffuse and point
  lights form the albedo-modulated ground colour. A separate view-dependent
  `pow(max(N dot H, 0), 20) * c27.rgb` supplies specular. The four-layer pixel
  shader blends texture alpha, then adds alpha times specular after diffuse
  lighting, before fog. Full alpha plus almost-white c27 can clip all channels,
  producing the screenshot's spotlight-like patches. Point lights contribute
  diffuse illumination, not this separate directional reflection.

### Small correction and scope

The only existing client source file changed is
`C:\WoWDev\wowdecomp\WoW\Source\WorldClient\MapRenderChunk.cpp`, with six added
lines. The small pure helper is in `BriarbrookTerrainLighting.h` alongside it.
For map 905, each terrain specular channel is bounded by the corresponding
directional diffuse channel at full night. An already weaker reflection is
preserved. The existing cyclic `DayNight::DNInfo::m_curve0` blends between the
original and bounded values: full night overnight, transitions 06:00–07:00 and
20:30–21:30, zero correction during the intervening daytime.

Only the terrain shader's local c27 RGB values change. Exponent, light direction,
ambient/diffuse ground illumination, texture masks, shadows, point lights, fog,
global/model lighting, sky and moon rendering are untouched. Daytime and other
maps return the exact original constants. The bound retains subdued reflections
rather than disabling terrain lighting or specular rendering globally.

### Automated validation, package and deployment

- `Tools/Tests/BriarbrookTerrainLighting.cpp` is a standalone Windows C++
  regression executable. CTest passed (1/1). It checks all 256×256 input colour
  pairs, unchanged daytime and already-weak reflections, twilight interpolation,
  and 1,000 other map IDs across 101 blend values. A native midnight lighting
  fixture reproduces three-channel clipping with an opaque grass sample before
  the correction and stays below clipping after it, across 256 mask values and
  101 reflection angles. This is a numerical shader check, not in-game QA.
- MSVC Release x64 `WorldClient` compiled and `WowClient64.exe` linked
  successfully, staged outside the game directory. Existing enum-conversion
  warnings in `WorldClient/Types.h` and `Event/Types.h` remain; no build error.
- Package and offline shader evidence:
  `C:\WoWDev\Lighting\BriarbrookGlare-001`.
- Verified external backup:
  `C:\WoWDev\Backups\Warscape-Briarbrook-Lighting-20261026-231422`.
  It retains the original executable, with a second original copy from the
  atomic swap. The first swap attempt rejected an empty optional backup path;
  it left the original in place, and the retry with an explicit path succeeded.
- The previously running client was PID 99564 at
  `C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe`, without `-datadir`. It had
  stopped before deployment. `Client.cpp::SetPaths` confirms that no override
  means the executable's directory; the client CMake target confirms the launch
  output path. The client was not launched or operated for testing.
- Only `C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe` was deployed. Its valid
  PE32+ AMD64 binary exactly matches the staged package by SHA-256:
  `E0F607B389E1E407CFC5705234DCDD2C65AD83FEC136D51F5DC7049432F99F17`.
  Original SHA-256:
  `055F669C18E768019A63C387C28EEBB59EF3DB456C449DC0FB775B3CCBDB6D2E`.
- Before/after SHA-256 checks cover 112 protected files, including both custom
  client patch MPQs, server map/collision/navigation/registration data and all
  world-generator Python/JSON sources. All are unchanged. No assets were rebuilt,
  no database work occurred, and no servers, settings, saved variables or addons
  were changed. Nothing was staged, committed or pushed.

### User visual approval pending

Start the normal custom client and return to the village:

```text
.go xyz -322.666667 -257.666667 33.5 905
```

At night, compare the ground from the screenshot's camera angle and while moving
the camera. Confirm the white pools are gone while moon/sky, natural ground
visibility, warm windows and lanterns remain. Briefly check daytime ground and
another map. The exact perceived brightness and full live rendering result
remain unverified until the user reports back. No further environment work is
authorized before that feedback.
