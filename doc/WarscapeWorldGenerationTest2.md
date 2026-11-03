# Warscape World Generation Test 2 — Lumbridge

Updated 26 October 2026. Checkpoint A passed its initial user in-game check: map 901 loaded with rendered terrain and a bridge. The prior client crash (`CMapChunk::UnpackAlphaShadowBits(): Bad genformat`) was fixed in the generator and guarded by a regression test. Checkpoint B passed offline regression, extractor, collision and navigation validation and was deployed locally. Live Checkpoint B acceptance remains pending. Checkpoint C is not started.

This experiment uses the existing, registered map 901 (`WarscapeTest1`). It does not alter Azeroth, combat, XP, skills, UI, movement speed, or database records. No migration is included.

## Coordinates, geography and scale

The transform remains 4.2 WoW world units per OSRS tile. OSRS east/north `(3222,3218)` maps to world `(X=-266.666667,Y=-266.666667)`. North increases world X; east decreases world Y. `lumbridge.py` provides the inverse. Travel-time scale is kept independent of local building, bridge and water dimensions; no global movement-speed setting is changed.

Placement anchors and extents use the OSRS coordinate survey in [`RESEARCH.md`](https://github.com/iangogentic/osrs-lumbridge/blob/main/RESEARCH.md), which says its coordinates were extracted from 2004scape map data and cross-checked against the OSRS Wiki. The OSRS Wiki confirms the settlement relationships: the castle courtyard is central, the church graveyard is south of the church, and the cow pasture is north of Fred's farm. The survey's specific landmarks include:

| Landmark | OSRS east,north coordinate or extent | Generator placement |
| --- | --- | --- |
| Castle | x 3204–3230, n 3207–3230 | Castle WMO origin at 3217,3218.5; courtyard remains centered on spawn 3222,3218 |
| River Lum | approximately x 3242–3252, north–south | Smooth lowered channel through the existing river control points |
| Bridge deck | x 3242–3248, n 3225–3226 | Native footbridge at 3245,3225.5 |
| Church | 3244,3206 | Chapel WMO substitution at the surveyed church anchor |
| Graveyard | x 3238–3241, n 3192–3198 | Stone fence and six tombstones immediately south of church |
| General store | keepers at 3209 and 3212, n 3247 | Building centered at 3210.5,3247 |
| Bob's Brilliant Axes | 3232,3203 | Small human-farm WMO substitution at the shop anchor |
| Windmill | 3166,3306–3307 | Westfall windmill M2 at 3166,3306 |
| Fred's farm | farmer at 3189,3273; sheep field x 3190–3210, n 3255–3280 | Farmhouse and barn beside the farm anchor |
| North chicken farm | x 3225–3232, n 3297–3300 | Coop building and accessible fenced enclosure |
| Cow field | x 3243–3261, n 3258–3295 | Barn, accessible fenced perimeter and field entrance |

The 2004scape-derived source remains a community coordinate reference, not an official current OSRS map dump. Road centerlines, house footprints, the exact castle model origin and scenery positions not specified by that source are authored approximations; those are marked as adjustable configuration. See the [OSRS Lumbridge page](https://oldschool.runescape.wiki/w/Lumbridge) for current settlement context and landmark relationships.

## Checkpoint A terrain refinements

Configuration: `contrib/warscape/worldgen/lumbridge-b.json`. The original `lumbridge-a.json` baseline is retained unchanged. New terrain settings reduce the channel from 8.0 to 2.6 projected OSRS tiles (10.92 world units) and feather it into the 30.0-unit banks over 2.8 tiles (11.76 world units). The bed is Z=28.0 and the water plane is Z=28.5. These local dimensions fit the reduced bridge while leaving the 4.2-unit intercity projection unchanged.

The main approach road is 1.8 tiles (7.56 units) wide, narrower than the bridge's 8.25-unit clear model width. Farm and church lanes are narrower. Roads, paved areas and crop fields use full-resolution 64×64 MCAL sampling with smooth alpha falloff; the earlier 16×16 repeated sampling is removed. Terrain uses continuous world-space height sampling, a smooth bank curve and terrain-following scenery placement.

### Measured bridge scale

Dimensions come from the actual installed WMO/M2 bounds in `C:\WoWDev\wowdecomp\bin\Win\Data`, not a screenshot estimate. The old KeepBridge01 WMO is 46.29 × 17.85 × 17.80 units. The selected ElwynnFootbridge WMO is 26.31 × 8.25 × 4.28 units. The installed Human Male M2 render bounds are 3.94 × 2.92 × 4.25 units. Against that character height, the bridge span/width/height change from about 10.89/4.20/4.19 player-heights to 6.19/1.94/1.01. This reduces length 43%, width 54% and bounding height 76%, while the 8.25-unit deck width exceeds the 7.56-unit main road width.

The footbridge is placed at Z=27.4. Parsing its installed WMO group geometry finds the broad, upward-facing walk surface between local Z≈1.95 at the approaches and Z≈2.68 at the arch. This puts the deck around Z=29.35 at the ends and Z=30.08 at the arch, about 0.85–1.58 units above the Z=28.5 water plane. Its low structural geometry begins at Z≈0.42, or world Z≈27.82, below the Z=28 riverbed. Generated bank heights at the model's deck ends are about Z=28.9–29.2, within 0.5 units of the deck. A regression test extracts these deck faces and checks clearance and bank alignment. Live client inspection is still needed to confirm the rendered water/deck appearance and walkability. WMO placements use native scale because this pipeline/game format does not support reliable WMO scaling.

## Checkpoint B native landmark layout

The B config contains 220 native placements: 11 WMO building/bridge instances and 209 M2 scenery instances, including repeated fence segments. Model references are resolved against the custom client's installed MPQs during generation; names are never guessed or synthesized.

| OSRS landmark | Installed Warcraft asset | Documented substitution or layout note |
| --- | --- | --- |
| Castle | `World\\wmo\\Azeroth\\Buildings\\Castle\\castle01.wmo` | Native human castle equivalent; OSRS does not have a matching WoW asset |
| Church | `World\\wmo\\Azeroth\\Buildings\\Chapel\\Chapel.wmo` | Native chapel equivalent |
| General store, Bob's shop, nearby homes, Fred/chicken buildings | `human_farm\\farm.wmo`, `HumanTwoStory.wmo`, and `Human_Barn_Silo\\barn.wmo` | Native human-house, barn and farm equivalents; ground-floor entry/interior accessibility remains a client QA item |
| Mill Lane Mill | `World\\Azeroth\\Westfall\\Buildings\\Windmill\\WestfallWindmill.m2` | Native Westfall farm windmill equivalent |
| Graveyard | Westfall `Tombstone01`–`Tombstone04.m2` and Elwynn stone-fence M2 | Native grave marker equivalents; fence is configurable polyline placement |
| Trees, shrubs, flowers, rocks and lamps | Installed Elwynn native M2 assets | Positions and orientations are editable in `lumbridge-b.json` |
| Farm and graveyard perimeters | Elwynn wood/stone-fence M2 assets | Deterministic line runs; OSRS field gates are represented by open fence gaps |

The castle and chapel are complete native WMO roots with extracted collision models, but the exact open-door orientation and usable interior have not yet been confirmed in the client. The Test 2 scope has no NPC spawns, quest systems or interaction logic.

## Deterministic pipeline and verification

`generate.py` reads `lumbridge-b.json`; building anchors, yaw, local scale, roads, bank width/height, texture feathering, field extents, scenery coordinates and fence polylines are editable config. M2 placements may follow sampled terrain. WMO scale is rejected unless native scale is used. The prior MCNK big-alpha bit fix remains in place and is tested against wowdecomp's 3.3.5a decoder.

Offline regression command:

```powershell
py -m unittest discover -s contrib/warscape/worldgen -p test_worldgen.py -v
```

The suite checks coordinate transforms, local bridge/player ratios using installed client bounds, native model resolution and placement references, smooth bank and texture edges, MCNK big-alpha flags/MCAL layout, WDT tiles and baseline Test 1 structures. `build.py` runs the local map extractor, verifies exactly nine terrain tiles, extracts and namespaces native VMAP collision, generates all nine navigation tiles, and fails on missing terrain/navigation output. No worldserver database updater or migration is run.

Final external build directory: `C:\WoWDev\Worldgen\Test2-B-deploy-001`. Deployment backup: `C:\WoWDev\Backups\Worldgen-20261026-151404-258046`. The deployer verified and copied 54 runtime files after the custom client and both local servers had stopped. The existing Map.dbc registration remained byte-identical; no database migration, updater, or gameplay-data change was run. The server was restarted with `Updates.EnableDatabases=0` and `Updates.AutoSetup=0`.

The custom wowdecomp executable was launched from `C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe`. It returned to a character in Sentinel Hill on map 0 without a startup crash, but the map 901 teleport and B screenshots were not completed. Computer Use reported that the user stopped it with the physical Escape key, so no further client input was issued. Terrain appearance, castle entrance/interior, bridge traversal, solid-terrain collision, and in-game collision remain unverified for this B build. The requested views (both bridge banks, overhead bridge, castle, village/church and farms) still need capture and visual review.

Inspection teleport commands for the restored admin character:

```text
.go xyz -266.666667 -266.666667 32 901
.go xyz -235.166667 -363.266667 30.1 901
```

The first is the existing castle courtyard spawn; the second is near the bridge center/arched deck. Checkpoint C remains blocked on the user's visual approval of Checkpoint B.

## Checkpoint C and unrelated combat issue

Checkpoint C NPC spawning has not started. No NPC templates/spawns or SQL migration were created or applied. The user previously confirmed new characters should begin at combat level 3 while individual combat skills start at level 1 (Hitpoints at 10); that separate issue remains outside Test 2 and no combat-level calculation is changed here.

## Checkpoint B production-quality alpha iteration — in progress

The earlier map-901 procedural layout and its screenshots remain preserved as historical work. A new isolated alpha is being authored as map 903 (`WarscapeLumbridgeAlpha`), keeping maps 901 and 902 and the existing custom patch entries intact. It is a compact WoW-first composition on a 3×3 tile footprint; WoW-native asset dimensions, player scale and movement speed remain unchanged. The editable source is `contrib/warscape/worldgen/lumbridge-alpha.json` and the generator is `contrib/warscape/worldgen/lumbridge.py`.

The alpha configuration uses the native Castle02 WMO instead of the oversized Castle01, a chapel, native human farm/house/barn buildings, a narrow Elwynn footbridge, configurable dirt routes, riverbanks, farm/graveyard fences and seeded scenery regions. Castle02 bounds are approximately 48.05 × 40.90 × 18.50 units; that is about 4.35 installed Human Male model heights. The chapel remains a visual risk at about 45.57 units tall and requires player-height screenshot review. Four native Elwynn grass, dirt and river-mud textures are layered; the fluorescent ElwynnCrop texture is excluded. Current generation resolves 313 native placements (11 WMO and 302 M2); all referenced assets resolve from the local wowdecomp archives.

The generator supports appending 903 to the existing custom Map.dbc tail while retaining prior rows and string data. The initial 002 build was superseded after the client crash exposed incorrect MCNK alpha metadata; the corrected 004 package is documented below. The latest full regression run passed all 13 tests. `build.py` completed map extraction, collision assembly and nine navigation tiles. Prior client patch entries and map 901/902 row records were byte-checked.

Deployment and live loading are confirmed for corrected package 004, with the 17:49 crash fixed. The live screenshot and remaining acceptance gaps are described below. No map 901/902 terrain files, original Azeroth assets, gameplay systems, database records or migrations were changed by this alpha iteration. Entrance/interior use, complete bridge traversal, solid-building collision and live NPC pathfinding still require validation. The zone must not be called alpha-ready until those visual and live checks pass. Checkpoint C remains out of scope.

### Corrected deployment retry and live checkpoint findings (2026-10-26)

The first deployed map-903 attempt crashed the custom client. Inspection traced this to the generator writing four MCLY texture layers and three 4096-byte alpha planes but declaring MCNK `sizeAlpha=8200` and only three layers. The client then advanced into the middle of MCAL while parsing chunks. `lumbridge.py` now writes the configured layer count and `8 + 4096 × overlay_count`; a regression test checks all 256 MCNKs. The corrected 004 package passed the full 13-test worldgen suite and `build.py` (nine extracted terrain tiles, collision output and nine navigation tiles). The corrected package was deployed with backups under `C:\WoWDev\Backups\Warscape-CheckpointB-903-fix-20261026-175639`; map 901/902 rows and terrain artifacts were preserved.

Live retry: the custom wowdecomp client loaded and entered map 903 without a new crash. `.gps` reported `Map: 903 (Warscape Lumbridge Alpha)` at the configured spawn; the last crash folder entry remains the earlier 17:49:23 crash. The player was teleported onto the bridge. `.gps` then reported bridge `FloorZ≈30.0957` above terrain `GroundZ≈27.8`, consistent with the WMO deck collision being present. This confirms rendered bridge geometry and a deck collision surface, but the automated movement attempt did not establish a complete end-to-end crossing; building collision and NPC pathfinding were not verified in-game.

The live screenshots at `C:\WoWDev\Worldgen\CheckpointB-Alpha-903-004\Screenshots\bridge-live-inspection.jpg` and `C:\WoWDev\Worldgen\CheckpointB-Alpha-903-004\Screenshots\bridge-floor-collision-gps.jpg` show the bridge and terrain. The recorded bridge position was X≈-244.1387, Y≈-335.6667, Z≈30.0957; the floor-height reading was recorded in the in-game `.gps` output. It also exposes a blocking visual defect: the river renders fluorescent green, while the scene has hard-edged grass/dirt transitions and the bridge dominates the view. These appearance issues must be fixed and re-inspected before this is a successful Checkpoint B visual result. The current package is a technical load/build pass only, not visual acceptance. No NPC was spawned; no database changes or migration were made. Do not proceed to Checkpoint C.



## Checkpoint B visual corrections and user testing workflow (26 October 2026)

The user assigned in-game visual inspection and manual gameplay testing to themselves as a permanent Warscape workflow. Codex is responsible for code, map generation, automated tests, validation, builds, safe local deployment, and technical troubleshooting. Codex must not launch or drive WoW for manual QA unless specifically requested or approved for a focused technical diagnosis, and must not mark manual tests as passed without user confirmation.

The current map 903 refinement adds deterministic low-frequency signed-distance variation to river banks and dirt paths, slightly broadens the path texture feather, and stores per-vertex liquid depth from the terrain-to-water-surface distance. Inspection of wowdecomp shows MCLQ depth byte 0 drives the liquid depth-texture coordinate; the previous generator wrote zero for every vertex, forcing the shallowest lookup everywhere. The generator now derives that byte using the client table scale (9 entries per world unit) while retaining standard water type 1 and the correct height float at byte offset 4. Offline regression checks verify these values and all MCLQ sizes. This is the evidence-backed correction for the flat fluorescent appearance; the resulting water color and shoreline still require your visual confirmation after deployment.

After technical validation and deployment, provide the exact map 903 teleport commands and inspection points, then stop for user screenshots and gameplay feedback. Checkpoint C remains out of scope.

### Map 903 visual-correction candidate 006 (2026-10-26)

The generator now uses a seeded smooth signed-distance field (`surface.edge_noise`) to add bounded irregularity to river-bank and path edges. The dirt path texture feather was widened from 0.7 to 0.9 OSRS tiles. River water remains MCLQ standard water (MCNK type bit 0x4/type 1). The confirmed client-side encoding defect was the MCLQ depth byte: wowdecomp reads byte 0 per 8-byte vertex into its depth-coordinate lookup, but the prior generator emitted zero at every vertex. The generator now computes byte depth from the sampled terrain-to-water-surface difference at each of 81 vertices, using the client lookup scale of nine steps per world unit. Liquid heights, water type, native bridge and building scales, global transform, movement speed, and gameplay systems are unchanged.

Automated verification: 16 world-generation tests pass. Package `C:\WoWDev\Worldgen\CheckpointB-Alpha-903-006` generated 313 native placements, contains the expected 9 ADTs plus WDT, and passed the local map extractor, VMap collision extraction/assembly and all 9 MMap tiles. 903 runtime files were deployed after a verified backup at `C:\WoWDev\Backups\Worldgen-20261026-192110-493020`. Client MPQ merge verification confirms all 12 pre-existing client archive entries were preserved, with only matching map-903 package entries overlaid; map 901 source assets and the rest of the archive were retained. Only map-903 server terrain/collision/navigation files were selected. Server-side Map.dbc and database contents were not deployed or changed. Automatic database updates/setup were disabled during server startup.

Authserver and worldserver are running for the user's review. The client was not launched. In-game water color, texture blending, bridge crossing, collision and the visual change remain pending user inspection; technical validation is not visual acceptance.

Suggested GM inspection commands:

```text
.go xyz -266.6667 -266.6667 32.0 903
.go xyz -244.1667 -335.6667 30.1 903
.go xyz -244.1667 -320.6667 30.5 903
.go xyz -244.1667 -350.6667 30.5 903
.go xyz -265.1667 -251.6667 32.0 903
.go xyz -302.6667 -332.6667 32.0 903
.go xyz -179.6667 -232.1667 32.0 903
.go xyz -26.6667 -284.6667 32.0 903
.go xyz -92.6667 -359.6667 32.0 903
```

Checkpoint C remains out of scope. Stop here for the user's screenshots and approval.
