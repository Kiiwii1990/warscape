# Warscape Development Sandbox

Map 904 is the permanent minimal gameplay testing map. It contains one WoW 3.3.5a ADT tile, at MCNK base elevation Z=30 with flat relative-height samples, one native Elwynn grass terrain texture, and no additional terrain layers, liquids, decoration, objects or NPCs. The one-tile WDT bounds the generated terrain area; the development spawn is near the tile center at X/Y=-266.666667, Z=32.

The generator preserves the core's validated map-generation and packaging path. Configuration is in `contrib/warscape/worldgen/warscape-dev-sandbox.json`; terrain ADT/WDT/Map.dbc generation uses `generate.py`; extraction, terrain collision and one-tile navigation use `build.py`; deployment uses the map-904-only, backup-first `deploy_sandbox.py`. The client and server registration use Map.dbc only; there are no SQL changes, database migrations, combat changes or gameplay-data edits.

## Reproduce on local Windows

From `C:\WoWDev\TrinityCore`:

```powershell
py -m unittest discover -s contrib/warscape/worldgen -p test_sandbox.py -v
py contrib/warscape/worldgen/generate.py --config contrib/warscape/worldgen/warscape-dev-sandbox.json --output C:\WoWDev\Worldgen\WarscapeDevSandbox-next
py contrib/warscape/worldgen/build.py C:\WoWDev\Worldgen\WarscapeDevSandbox-next
py contrib/warscape/worldgen/deploy_sandbox.py C:\WoWDev\Worldgen\WarscapeDevSandbox-next
```

Choose a new external output directory for each generation. The deployer is hard-limited to map ID 904 and directory `WarscapeDevSandbox`; it refuses to run while the custom client or either local game server is active. It merges the generated client MPQ entries, verifies matching client/server Map.dbc registration, backs up every target externally, copies only map-904 server artifacts and verifies deployed bytes. Map 901, 902 and 903 data is not selected or replaced.

## In-game handoff

After logging in with the custom wowdecomp client and entering a character, use:

```text
.go xyz -266.666667 -266.666667 32.0 904
```

Automated checks verify the single WDT tile, all 256 MCNKs at the configured base Z with zero height deltas, one MCLY layer, the grass MTEX, empty object/liquid references, map 904 registration and MPQ merge preservation. The terrain extractor, VMap generation and MMap generator must each emit the single configured tile. The custom client visual load and manual in-game movement acceptance are confirmed only by the user.

## Deployment record (2026-10-26)

Map 904 was deployed from `C:\WoWDev\Worldgen\WarscapeDevSandbox-001`. The deployment script backed up the two client patch MPQs and server `dbc/Map.dbc` under `C:\WoWDev\Backups\Warscape-DevSandbox-20261026-203814-324050`, then copied and hash-verified eight runtime files. The package contains one extracted terrain tile, one VMap tree/tile and one MMap mesh/tile. The map-specific server artifacts had no prior map-904 files to back up. Authserver and worldserver were restarted using the local Test 2 configs with database updates and autosetup disabled. Client visual loading and in-game movement remain for the user to verify.
