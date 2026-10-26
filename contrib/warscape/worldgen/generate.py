"""Windows-only, offline loading probe. Never deploys or writes to a database.

Requires mpyq==0.2.5. Outputs must be outside the source checkout.
Binary layouts: this checkout's map_extractor and wowdecomp WorldClient headers.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct

import mpyq

U32 = 0xFFFFFFFF
TILE = 1600 / 3


def chunk(tag, payload):
    return tag.encode("ascii")[::-1] + struct.pack("<I", len(payload)) + payload


def adt(tx, ty, height, texture):
    data = bytearray(chunk("MVER", struct.pack("<I", 18)) + chunk("MHDR", bytes(64)))
    offsets = {}
    for tag, body in [("MCIN", bytes(4096)), ("MTEX", texture.encode() + b"\0"),
                      ("MMDX", b""), ("MMID", b""), ("MWMO", b""),
                      ("MWID", b""), ("MDDF", b""), ("MODF", b"")]:
        offsets[tag] = len(data)
        data += chunk(tag, body)
    for index, tag in enumerate(["MCIN", "MTEX", "MMDX", "MMID", "MWMO", "MWID", "MDDF", "MODF"], 1):
        struct.pack_into("<I", data, 20 + index * 4, offsets[tag] - 20)
    for cy in range(16):
        for cx in range(16):
            header = bytearray(128)
            struct.pack_into("<4I", header, 0, 0, cx, cy, 1)
            struct.pack_into("<3f", header, 104,
                             (32 - tx) * TILE - cx * TILE / 16,
                             (32 - ty) * TILE - cy * TILE / 16, height)
            body = bytearray(header)
            # MCNK offsets include its eight-byte chunk header.
            for tag, field, payload in [
                ("MCVT", 20, bytes(145 * 4)),
                ("MCNR", 24, bytes([0, 0, 127]) * 145 + bytes(13)),
                ("MCLY", 28, struct.pack("<4I", 0, 0, 0, 0)),
                ("MCRF", 32, b""), ("MCAL", 36, b""), ("MCSE", 88, b"")
            ]:
                struct.pack_into("<I", body, field, len(body) + 8)
                body += chunk(tag, payload)
            struct.pack_into("<I", body, 40, 8)
            encoded = chunk("MCNK", body)
            struct.pack_into("<4I", data, offsets["MCIN"] + 8 + (cy * 16 + cx) * 16,
                             len(data), len(encoded), 0, 0)
            data += encoded
    return bytes(data)


def wdt(tiles, flags=0):
    main = bytearray(64 * 64 * 8)
    for x, y in tiles:
        struct.pack_into("<I", main, (y * 64 + x) * 8, 1)
    return chunk("MVER", struct.pack("<I", 18)) + chunk("MPHD", struct.pack('<8I', flags, 0, 0, 0, 0, 0, 0, 0)) + chunk("MAIN", main) + chunk("MWMO", b"")


def map_dbc(original, cfg, only_custom=False):
    magic, count, fields, size, strings_size = struct.unpack_from("<4s4I", original)
    if (magic, fields, size) != (b"WDBC", 66, 264) or len(original) != 20 + count * size + strings_size:
        raise ValueError("Expected intact 3.3.5a 66-column Map.dbc")
    rows = [original[20 + i * size:20 + (i + 1) * size] for i in range(count)]
    if any(struct.unpack_from("<I", row)[0] == cfg["map_id"] for row in rows):
        raise ValueError("Map ID already exists; refusing to replace it")
    row = bytearray(next(row for row in rows if struct.unpack_from("<I", row)[0] == 0))
    strings = bytearray(original[20 + count * size:])
    def string(value):
        offset = len(strings)
        strings.extend(value.encode() + b"\0")
        return offset
    struct.pack_into("<5I", row, 0, cfg["map_id"], string(cfg["directory"]), 0, 0, 0)
    row[20:84] = bytes(64)  # clear all localized names
    struct.pack_into("<I", row, 20, string(cfg["display_name"]))
    struct.pack_into("<I", row, 88, 0)  # no inherited Elwynn zone
    row[92:228] = bytes(136)  # no inherited descriptions
    struct.pack_into("<i", row, 236, -1)  # no corpse destination in Azeroth
    struct.pack_into("<2f", row, 240, 0, 0)
    struct.pack_into("<3I", row, 252, 0, 0, 0)
    output_rows = [bytes(row)] if only_custom else rows + [bytes(row)]
    return struct.pack("<4s4I", b"WDBC", len(output_rows), 66, 264, len(strings)) + b"".join(output_rows) + strings


def runtime_map_dbc(original, server_map, cfg):
    """Append a new test-map row while preserving every existing server row."""
    magic, count, fields, row_size, strings_size = struct.unpack_from('<4s4I', original)
    if (magic, fields, row_size) != (b'WDBC', 66, 264) or len(original) != 20 + count * row_size + strings_size:
        raise ValueError('Expected intact client 3.3.5a Map.dbc')

    def registered(data, record_count):
        for i in range(record_count):
            row = 20 + i * row_size
            if struct.unpack_from('<I', data, row)[0] == cfg['map_id']:
                string_offset = struct.unpack_from('<I', data, row + 4)[0]
                string_start = 20 + record_count * row_size
                if string_offset >= len(data) - string_start:
                    raise ValueError('Existing Map.dbc directory string is out of bounds')
                end = data.find(b'\0', string_start + string_offset)
                if end < 0:
                    raise ValueError('Existing Map.dbc directory string is unterminated')
                directory = data[string_start + string_offset:end].decode('ascii')
                if directory != cfg['directory']:
                    raise ValueError('Existing map ID is registered to a different directory')
                return True
        return False

    magic2, count2, fields2, row_size2, strings_size2 = struct.unpack_from('<4s4I', server_map)
    if (magic2, fields2, row_size2) != (b'WDBC', 66, 264) or len(server_map) != 20 + count2 * row_size2 + strings_size2:
        raise ValueError('Expected intact server 3.3.5a Map.dbc')
    if server_map == original:
        if registered(original, count):
            return original
        return map_dbc(original, cfg)
    if count2 < count or server_map[20:20 + count * row_size] != original[20:20 + count * row_size]:
        raise ValueError('Server Map.dbc base records differ from the client; refusing to overwrite registrations')
    if registered(server_map, count2):
        return server_map

    # The server already contains custom test registrations (901/902). Keep
    # every row and existing string byte intact, then append just the new row.
    generated = map_dbc(original, cfg, only_custom=True)
    _, _, _, _, generated_strings_size = struct.unpack_from('<4s4I', generated)
    generated_string_start = 20 + row_size
    generated_strings = generated[generated_string_start:generated_string_start + generated_strings_size]
    original_strings = original[20 + count * row_size:]
    server_strings = server_map[20 + count2 * row_size:]
    if not generated_strings.startswith(original_strings):
        raise ValueError('Generated map strings do not preserve the client base string table')
    row = bytearray(generated[20:20 + row_size])
    delta = len(server_strings) - len(original_strings)
    for field_offset in (4, 20):
        old_offset = struct.unpack_from('<I', row, field_offset)[0]
        # Offset zero may refer to the original empty string and must remain zero.
        if old_offset >= len(original_strings):
            struct.pack_into('<I', row, field_offset, old_offset + delta)
    strings = server_strings + generated_strings[len(original_strings):]
    rows = server_map[20:20 + count2 * row_size] + row
    return struct.pack('<4s4I', b'WDBC', count2 + 1, fields2, row_size, len(strings)) + rows + strings


def archive(path, files):
    """Uncompressed MPQ v0, encrypted hash/block tables, independently read back."""
    helper = mpyq.MPQArchive.__new__(mpyq.MPQArchive)
    def encrypt(data, key):
        seed = 0xEEEEEEEE
        result = bytearray()
        for (value,) in struct.iter_unpack("<I", data):
            seed = (seed + helper.encryption_table[0x400 + (key & 255)]) & U32
            result += struct.pack("<I", (value ^ (key + seed)) & U32)
            key = (((~key << 21) + 0x11111111) | (key >> 11)) & U32
            seed = (value + seed + (seed << 5) + 3) & U32
        return result
    files = dict(files)
    files["(listfile)"] = ("\r\n".join(files) + "\r\n(listfile)\r\n").encode()
    slots = 1
    while slots < len(files) * 2:
        slots *= 2
    hashes = [bytes([255]) * 16 for _ in range(slots)]
    blocks, content = bytearray(), bytearray()
    for index, (name, payload) in enumerate(files.items()):
        slot = helper._hash(name, "TABLE_OFFSET") % slots
        while hashes[slot] != bytes([255]) * 16:
            slot = (slot + 1) % slots
        hashes[slot] = struct.pack("<IIHHI", helper._hash(name, "HASH_A"), helper._hash(name, "HASH_B"), 0, 0, index)
        blocks += struct.pack("<4I", 32 + len(content), len(payload), len(payload), 0x81000000)
        content += payload
    hash_offset = 32 + len(content)
    block_offset = hash_offset + slots * 16
    header = struct.pack("<4sIIHH4I", b"MPQ\x1a", 32, block_offset + len(blocks), 0, 3,
                         hash_offset, block_offset, slots, len(files))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + content + encrypt(b"".join(hashes), helper._hash("(hash table)", "TABLE")) + encrypt(blocks, helper._hash("(block table)", "TABLE")))
    check = mpyq.MPQArchive(str(path))
    try:
        for name, payload in files.items():
            if check.read_file(name) != payload:
                raise ValueError("MPQ readback mismatch: " + name)
    finally:
        check.file.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("test1.json"))
    parser.add_argument("--client", type=Path, default=Path(r"C:\WoWDev\wowdecomp\bin\Win"))
    parser.add_argument("--server", type=Path, default=Path(r"C:\WoWDev\TrinityServer"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("Local Windows execution only")
    root = Path(__file__).resolve().parents[3]
    output = args.output.resolve()
    if any(output.is_relative_to(p.resolve()) for p in [root, args.client, args.server]) or output.exists():
        raise SystemExit("Output must be a NEW directory outside Git")
    cfg = json.loads(args.config.read_text())
    if not 800 <= cfg["map_id"] <= 999 or not cfg["directory"].isalnum():
        raise ValueError("Expected reserved test map ID and alphanumeric directory")
    for x, y in cfg["tiles"]:
        if not (0 <= x < 64 and 0 <= y < 64):
            raise ValueError("Invalid tile")
    client_map = mpyq.MPQArchive(str(args.client / "Data/enUS/patch-enUS-3.MPQ"), listfile=False).read_file("DBFilesClient\\Map.dbc")
    original = client_map
    server_map = (args.server / "dbc/Map.dbc").read_bytes()
    texture = mpyq.MPQArchive(str(args.client / "Data/common.MPQ"), listfile=False).read_file(cfg["texture"])
    if not texture or texture[:4] != b"BLP2":
        raise ValueError("Configured texture is not present in the actual client")
    full_dbc = runtime_map_dbc(original, server_map, cfg)
    prefix = "World\\Maps\\" + cfg["directory"] + "\\" + cfg["directory"]
    files = {prefix + ".wdt": wdt(cfg["tiles"])}
    for x, y in cfg["tiles"]:
        files[f"{prefix}_{x}_{y}.adt"] = adt(x, y, cfg["height"], cfg["texture"])
    output.mkdir(parents=True)
    archive(output / "runtime/patch-Z.MPQ", files)
    archive(output / "runtime/patch-enUS-Z.MPQ", {"DBFilesClient\\Map.dbc": full_dbc})
    (output / "runtime/Map.dbc").write_bytes(full_dbc)
    # Isolated extractor input: hardlink immutable base assets; never edits them.
    staged = output / "extract-input/Data"
    for source in (args.client / "Data").rglob("*.MPQ"):
        if source.name.lower() in ("patch-z.mpq", "patch-enus-z.mpq"):
            continue  # NEVER hardlink an output archive that this build rewrites.
        target = staged / source.relative_to(args.client / "Data")
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(source, target)
    archive(staged / "patch-Z.MPQ", files)
    extraction_dbc = {"DBFilesClient\\Map.dbc": map_dbc(original, cfg, only_custom=True)}
    archive(staged / "enUS/patch-enUS-Z.MPQ", extraction_dbc)
    manifest = {"configuration": cfg, "base_map_dbc_sha256": hashlib.sha256(original).hexdigest(),
                "texture_sha256": hashlib.sha256(texture).hexdigest(), "placements": [],
                "validation": "MPQ roundtrip passed; not yet loaded in game"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "extracted").mkdir()
    # Terrain-only map: no WMO/M2 collision primitives. Serialize BIH::init_empty
    # (BoundingIntervalHierarchy.h) with real tiled VMAP_4.8 headers, without
    # disabling collision globally or inventing collision for absent buildings.
    vmaps = output / "extracted/vmaps"
    vmaps.mkdir()
    empty_bih = struct.pack("<6f5I", *([float("inf")] * 3),
                            *([float("-inf")] * 3), 3, 3 << 30, 0, 0, 0)
    (vmaps / f'{cfg["map_id"]:03}.vmtree').write_bytes(b"VMAP_4.8\x01NODE" + empty_bih + b"GOBJ")
    for x, y in cfg["tiles"]:
        (vmaps / f'{cfg["map_id"]:03}_{y:02}_{x:02}.vmtile').write_bytes(b"VMAP_4.8" + struct.pack("<I", 0))
    print("Generated loading probe and isolated extractor input:", output)
    print("Spawn command:", f'.go xyz {cfg["spawn"]["x"]} {cfg["spawn"]["y"]} {cfg["spawn"]["z"]} {cfg["map_id"]}')


if __name__ == "__main__":
    main()
