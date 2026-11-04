# Warscape — The Cogfall Coast (map 913)

This folder contains the latest saved Noggit terrain package from 3 November
2026: one WDT and all 25 ADTs for tiles X=30–34, Y=30–34. The 34_34 tile is
unchanged from the preceding saved update. The map includes its saved terrain,
liquid data, and placed-object references.

## Test it

Use this package with a WoW 3.3.5a client and the Warscape TrinityCore server.
Install the map files under `World/Maps/WarscapeCogfallCoast` in a client MPQ
that has priority over the base game archives. Add map ID 913, directory
`WarscapeCogfallCoast`, display name `Warscape - The Cogfall Coast` to your own
client and server `Map.dbc` files, preserving every existing row. Do not replace
your DBCs with a copy from another installation.

The repository's `contrib/warscape/worldgen/generate.py` provides
`map_dbc(original, cfg)` for this additive registration. Use your own original
3.3.5a `Map.dbc` bytes and this configuration:

```python
cfg = {
    "map_id": 913,
    "directory": "WarscapeCogfallCoast",
    "display_name": "Warscape - The Cogfall Coast",
}
```

It refuses to overwrite an existing map ID. Use the generated DBC as the
client's locale patch input and the server's `dbc/Map.dbc` input.

Run the normal 3.3.5a server data pipeline against your own game assets to
extract the map, build VMaps, and generate MMaps. Start the server and client,
then teleport with:

```text
.go xyz -166.720 -362.360 80.902 913
```

Check the edited terrain, water, placed rocks, collision, and walkability.
The arrival area is Larkhaven; the map covers the full 5x5 tile square.

## Package contents

- `World/Maps/WarscapeCogfallCoast/WarscapeCogfallCoast.wdt`
- 25 `WarscapeCogfallCoast_X_Y.adt` files for X/Y 30–34

This package does not include WoW client assets, DBC files, MPQ archives, or
extracted server data. Use your own licensed 3.3.5a client assets for
registration and server-data extraction. No manual in-game review has been
performed by the author of this package; appearance and traversal need your
in-game check.
