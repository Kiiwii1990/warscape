"""Extract and validate an already-generated probe in its external staging folder."""
import argparse
import json
from pathlib import Path
import struct
import subprocess


def validate_navigation_tile(path, require_full_flat_tile=False):
    data = Path(path).read_bytes()
    if len(data) < 20 + 100:
        raise ValueError(f'Navigation tile is truncated: {path}')
    magic, detour_version, mmap_version, payload_size = struct.unpack_from('<4I', data)
    if magic != 0x4D4D4150 or detour_version <= 0 or mmap_version != 15:
        raise ValueError(f'Navigation tile has an invalid MMap header: {path}')
    if payload_size != len(data) - 20:
        raise ValueError(f'Navigation tile size field does not match file length: {path}')

    # Detour dtMeshHeader is 15 32-bit fields followed by 10 floats.
    mesh = struct.unpack_from('<15I10f', data, 20)
    polygon_count, vertex_count = mesh[6], mesh[7]
    if polygon_count == 0 or vertex_count < 3:
        raise ValueError(f'Navigation tile contains no walkable polygons: {path}')
    if require_full_flat_tile:
        bounds_min, bounds_max = mesh[18:21], mesh[21:24]
        expected_tile_size = 1600 / 3
        if (abs((bounds_max[0] - bounds_min[0]) - expected_tile_size) > 1.0 or
                abs((bounds_max[2] - bounds_min[2]) - expected_tile_size) > 1.0 or
                abs(bounds_max[1] - bounds_min[1]) > 0.01):
            raise ValueError(f'Flat sandbox navmesh does not cover one level terrain tile: {path}')
    return polygon_count, vertex_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tools", type=Path, default=Path(r"C:\WoWDev\TrinityServer"))
    args = parser.parse_args()
    output = args.output.resolve()
    cfg = json.loads((output / "manifest.json").read_text())["configuration"]
    extracted = output / "extracted"
    with (output / "extractor.log").open("wb") as log:
        subprocess.run([str(args.tools / "mapextractor.exe"), "-i", str(output / "extract-input"),
                        "-o", str(extracted), "-e", "1", "-f", "0"], stdout=log, stderr=log, check=True)
    expected = {f'{cfg["map_id"]:03}{y:02}{x:02}.map' for x, y in cfg["tiles"]}
    if {p.name for p in (extracted / "maps").glob("*.map")} != expected:
        raise ValueError("Extractor did not produce exactly the configured tiles")
    for name in expected:
        path = extracted / "maps" / name
        data = bytearray(path.read_bytes())
        header = list(struct.unpack_from("<4s10I", data))
        offset = header[5]
        magic, flags, low, high = struct.unpack_from("<4sIff", data, offset)
        if header[:2] != [b"MAPS", 10] or magic != b"MHGT" or (low, high) != (cfg["height"], cfg["height"]):
            raise ValueError("Unexpected extracted terrain")
        # Trinity TerrainBuilder ignores MAP_HEIGHT_NO_HEIGHT entirely. Keep the
        # identical flat surface but store explicit float vertices for navmesh.
        if flags == 1:
            if offset + 16 != len(data) or header[7] or header[9]:
                raise ValueError("Flat expansion only supports this terrain-only probe")
            struct.pack_into("<I", data, offset + 4, 0)
            data += struct.pack("<f", low) * (129 * 129 + 128 * 128)
            header[6] = len(data) - offset
            struct.pack_into("<4s10I", data, 0, *header)
            path.write_bytes(data)
        elif flags not in (0, 1):
            raise ValueError("Unexpected height encoding")
    dbc = extracted / "dbc"
    dbc.mkdir(exist_ok=True)
    (dbc / "LiquidType.dbc").write_bytes((args.tools / "dbc/LiquidType.dbc").read_bytes())
    with (output / "mmaps.log").open("wb") as log:
        subprocess.run([str(args.tools / "mmaps_generator.exe"), str(cfg["map_id"]), "--threads", "2", "--silent"],
                       cwd=extracted, stdout=log, stderr=log, check=True)
    nav = list((extracted / "mmaps").glob("*.mmtile"))
    if len(nav) != len(expected) or any(p.stat().st_size <= 20 for p in nav):
        raise ValueError("Navigation generator did not produce all configured tiles")
    for tile in nav:
        validate_navigation_tile(tile, require_full_flat_tile=True)
    print(f"Validated {len(expected)} extracted terrain tiles and {len(nav)} navigation tiles; live loading remains untested")


if __name__ == "__main__":
    main()
