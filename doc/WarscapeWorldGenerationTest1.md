# Warscape World Generation Test 1

26 October 2026. **First milestone passed in the actual wowdecomp client.**
The full OSRS region is incomplete. This document distinguishes live checks from
generated files and future work. No NPC database migration was created or applied.

## Live result

- New non-instance map ID **901**, directory **WarscapeTest1**.
- GM entry: `.go xyz -266.666667 -266.666667 32 901`.
- Nine tiles, ADT X/Y 31..33, flat ground Z=30, existing Elwynn grass texture.
- Each tile is 533.333333 WoW units wide. The square spans world X/Y
  approximately -1066.666667 through +533.333333. It has no boundary wall;
  stay inside that range. This is a loading probe, not regional geography.
- Live `.gps`: map 901 (Warscape World Generation Test 1), X/Y -266.666656,
  Z=30.001240, GroundZ/FloorZ=30, Map/VMap/MMap all 1.
- Autorun and jump tested. After movement: X=-128.572754, Y=-266.666656,
  Z=30.001257: 138.093902 units travelled along X. This was a movement check,
  not a stopwatch calibration of that distance.
- Logout to character selection and re-enter world passed. `.gps` returned the
  same moved position, ground height and Map/VMap/MMap presence.
- Live `GetUnitSpeed("player")` during autorun returned **7 units/second**.
- Existing Azeroth login worked before teleport. No client/server binary,
  combat, XP, skill, addon, configuration or saved-variable source was modified.
  No NPC combat, creature respawn, object collision, water, tile-boundary travel,
  death recovery or server-restart persistence test has been performed here.

## Reproduce generation on Windows

Source: `contrib/warscape/worldgen/`. Python 3 with `mpyq==0.2.5` is required.
The existing local extractors are sufficient for this terrain-only milestone.
Run from `C:\WoWDev\TrinityCore`, choosing a **new** output folder:

```powershell
py -m pip install -r contrib/warscape/worldgen/requirements.txt
py contrib/warscape/worldgen/generate.py --output C:\WoWDev\Worldgen\Test1-next
py contrib/warscape/worldgen/build.py C:\WoWDev\Worldgen\Test1-next
```

`test1.json` controls map identity, tile coverage, texture, height and spawn.
`placements` is empty. The generator creates WDT v18, ADT v18 (256 MCNKs/tile),
an append-only 66-column Map.dbc and two MPQ v0 patches. MPQ contents are checked
by independent mpyq readback. The base texture is checked in the actual
wowdecomp common.MPQ. Original Map.dbc records are preserved byte-for-byte.

The generator checks the server's Map.dbc against the client's patch-enUS-3.MPQ
base, allowing this probe's appended record. It does not generally resolve
arbitrary future patch precedence. Reinspect bases after any client data update.
Use only the verified current enUS installation with this version of the tool.

The extractor runs against a separate staged Data tree. Immutable base MPQs are
hardlinked to save disk space: **never edit those linked base archives**. Reserved
generated patch-Z archives are excluded from hardlinking. No extractor writes to
the original client or server. Build output, asset copies, runtime manifests and
tool logs stay outside Git. Only authored configuration and tools belong in Git.

`build.py` invokes the existing `mapextractor.exe` and requires exactly the nine
configured output tiles. TrinityCore's navigation loader ignores the compact
`MAP_HEIGHT_NO_HEIGHT` representation, so the build expands this flat surface
into equivalent explicit V9/V8 float arrays before invoking `mmaps_generator.exe`.
It requires all nine navigation tiles, not just a `.mmap` header.

The collision tree represents zero placed WMO/M2 primitives, using the core's
`BIH::init_empty` layout and VMAP_4.8 tiled headers. It is correct only for this
terrain-only probe. Terrain collision comes from ADT heights/client and `.map`
heights/server. Building placement requires real collision extraction and cannot
reuse the empty tree as a substitute for model collision.

Probe-002 was extracted and generated nine navigation tiles successfully.
Probe-003 was regenerated from the same configuration after deployment; all three
runtime files were byte-identical. Probe-003 was not separately deployed.

## Deployment record and procedure

The client was initially stopped. `wowdecomp/WoW/Source/Client.cpp::SetPaths`
and the client README confirm the executable directory as the default game
directory; no `-datadir` was used. The launched process was verified as
`C:\WoWDev\wowdecomp\bin\Win\WowClient64.exe`.

With the client and game servers stopped, deployed these runtime files only:

| Generated input under probe-002 | Destination |
| --- | --- |
| runtime/patch-Z.MPQ | wowdecomp/bin/Win/Data/patch-Z.MPQ |
| runtime/patch-enUS-Z.MPQ | wowdecomp/bin/Win/Data/enUS/patch-enUS-Z.MPQ |
| runtime/Map.dbc | TrinityServer/dbc/Map.dbc |
| extracted/maps/901*.map (9) | TrinityServer/maps/ |
| extracted/vmaps/901.vmtree and 901_*.vmtile (10) | TrinityServer/vmaps/ |
| extracted/mmaps/901.mmap and 901*.mmtile (10) | TrinityServer/mmaps/ |

Actual staging directory: `C:\WoWDev\Worldgen\Test1-probe-002`.
Original server DBC backup:
`C:\WoWDev\Backups\Worldgen-Test1-20261026-probe002\Map.dbc`.
Reserved client patch targets and map-901 terrain targets were absent before
deployment. Existing original archives and original map files were not replaced.

Before repeating deployment, re-identify the client process, executable and any
`-datadir`. Stop the client and game servers; inspect all destination files and
back up every previous probe runtime file outside Git. Copy only the table above,
checking hashes afterward. Do not copy the extractor's custom-only Map.dbc into
the server: only `runtime/Map.dbc` contains all existing maps.

World/auth/characters database status was inspected: no pending migrations or
hash conflicts. World permissions were inspected using `contrib/warscape/db.py`.
Then the existing local worldserver/authserver were started with their existing
configurations and `C:\WoWDev\TrinityServer` as working directory; DataDir is `.`.
World initialization completed and ports 8085/3724 listened. Updater policy was
not changed. Recheck status before every future start; pending migrations must
not be auto-applied. Starting a server is not approval for a new migration.

To remove the experiment later: first move every character off map 901 through
normal game commands and verify the saved location. With client and servers
stopped, restore the backed-up original Map.dbc and move only the exact deployed
probe patches/map901 files into an external archive. Do not remove map files
while characters are still saved there. No database restore is needed for this
milestone. Database recovery or deletion is never implied by these instructions.

## Scale work and remaining regional pipeline

The live speed measurement is recorded in `calibration.json`. OSRS movement is
one tile per tick when walking and two when running; the nominal tick is 0.6s
([energy](https://oldschool.runescape.wiki/w/Run),
[game tick](https://oldschool.runescape.wiki/w/Game_tick)). Therefore initial
cardinal-only conversions at measured WoW speed 7 are 4.2 units/tile for OSRS
walking and 2.1 for continuous OSRS running. These are derived candidates,
**not measured three-city travel-time matches**. No regional scale is selected.

OSRS diagonal steps and WoW continuous Euclidean movement differ; straight-line
city distances cannot determine a travel-time-correct scale. Trace the actual
free-to-play roads and accessible bridge crossings, measure all three intercity
routes under a documented walk/run policy, and record tile polylines and observed
durations in `calibration.json`. `calibrate.py` fits the common scale and reports
per-route errors. It deliberately refuses a regional fit until all three route
measurements exist. Normal travel must not depend on changing existing movement
speeds or introducing run-energy gameplay as an incidental world-generation fix.

Remaining work, in dependency order:

1. Obtain and trace an accurate OSRS ground-level region reference; record
   provenance and distinguish surveyed coordinates from adaptations. Include
   Lumbridge, Varrock, Falador, Draynor, Barbarian Village, farms, River Lum,
   bridges, woods and relevant connecting roads/landmarks. Do not use RuneScape 3
   or a 2004 map as if it were the requested current OSRS geography.
2. Complete the measured route fit, then extend the terrain authoring code for
   variable height, road texture layers/alpha, water and bridge crossings. The
   present generator is deliberately flat; it cannot generate those features yet.
3. Add a separate AreaTable registration and lighting/environment data. Area 0
   currently has no zone name, and the old zone label can linger until relog.
   No minimap or world-map art is generated.
4. Survey actual WoW WMO/M2 assets, record paths, positions, orientation, scale,
   footprint and function in editable configuration. Add actual placements;
   regenerate VMAPs through vmap4extractor/vmap4assembler and navigation afterward.
   No map editor, WMO conversion or asset placement capability was installed here.
5. Prepare dedicated starter creature templates and spawns restricted to map 901.
   Use existing Warscape profile/override and attack-speed tables, preserving
   the current x10 health/damage display scale. Verify OSRS versions and stats
   for Men/Women, level-2 Lumbridge goblins, chickens and cows before seeding.
   No unverified stats were written to the database.
6. Review the exact SQL and pre/postconditions and obtain explicit migration
   approval. Stop game servers/updaters, then use db.py's fresh-backup apply path.
   Only after application test targeting, retaliation, kills, XP, respawns,
   building/bridge collision, route times and relogging in the completed region.

The custom-map loading pipeline is **not blocked**. The unimplemented regional
authoring and unmeasured geography/route data above are the remaining work;
neither the flat map nor its tool validation constitutes an OSRS-region result.
