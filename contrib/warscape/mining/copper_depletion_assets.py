#!/usr/bin/env python3
"""Build and safely deploy a grayscale-only copper-rock depletion asset."""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
CLIENT = Path(r"C:\WoWDev\wowdecomp\bin\Win")
SERVER = Path(r"C:\WoWDev\TrinityServer")
BACKUPS = Path(r"C:\WoWDev\Backups")
DISPLAY_ID = 900102
SOURCE_DISPLAY_ID = 310
SOURCE_MODEL = r"World\SkillActivated\TradeskillNodes\copper_Miningnode_01.m2"
SOURCE_SKIN = r"World\SkillActivated\TradeskillNodes\copper_Miningnode_0100.skin"
CLIENT_MODEL = r"World\Warscape\Mining\CopperRockDepleted.mdx"
CLIENT_MODEL_M2 = r"World\Warscape\Mining\CopperRockDepleted.m2"
CLIENT_SKIN = r"World\Warscape\Mining\CopperRockDepleted00.skin"
PATH_TEST_MODEL = r"World\Warscape\Mining\CopperRockPathTest.mdx"
PATH_TEST_MODEL_M2 = r"World\Warscape\Mining\CopperRockPathTest.m2"
PATH_TEST_SKIN = r"World\Warscape\Mining\CopperRockPathTest00.skin"
DBC_NAME = r"DBFilesClient\GameObjectDisplayInfo.dbc"
GAMEOBJECT_MODELS_NAME = "GameObjectModels.dtree"
TEXTURES = (
    (r"World\Generic\NightElf\Passive Doodads\MagicalImplements\glow.blp",
     r"World\Warscape\Mining\CopperRockDepletedGlow.blp", True),
    (r"World\SkillActivated\TradeskillNodes\copper.blp",
     r"World\Warscape\Mining\CopperRockDepletedCopper.blp", False),
    (r"World\SkillActivated\TradeskillNodes\BindstoneReflect.blp",
     r"World\Warscape\Mining\CopperRockDepletedReflect.blp", False),
    (r"World\SkillActivated\TradeskillNodes\baseore02.blp",
     r"World\Warscape\Mining\CopperRockDepletedBaseOre.blp", False),
)

WORLDGEN = ROOT / "contrib" / "warscape" / "worldgen"
sys.path.insert(0, str(WORLDGEN))
from briarbrook import Assets  # noqa: E402
from deploy_sandbox import archive_entries  # noqa: E402
from generate import archive  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def skin_profile_path(model_path, profile):
    return model_path.rsplit(".", 1)[0] + f"{profile:02d}.skin"


def validate_skin_profile(payload, model):
    """Validate the external skin arrays the 3.3.5 client reads for an M2."""
    if len(payload) < 48 or payload[:4] != b"SKIN":
        raise ValueError("Expected a 3.3.5 M2 SKIN profile")
    if model[:4] != b"MD20" or struct.unpack_from("<I", model, 4)[0] != 264:
        raise ValueError("SKIN profile must accompany the expected 3.3.5 copper M2")
    model_vertices = struct.unpack_from("<I", model, 60)[0]
    array_specs = ((4, 2), (12, 2), (20, 4), (28, 48), (36, 24))
    counts = []
    for header_offset, element_size in array_specs:
        count, offset = struct.unpack_from("<II", payload, header_offset)
        if count and (offset < 48 or offset + count * element_size > len(payload)):
            raise ValueError("SKIN profile contains an out-of-range array")
        counts.append(count)
    vertex_count, index_count, bone_count, section_count, batch_count = counts
    vertex_offset = struct.unpack_from("<I", payload, 8)[0]
    index_offset = struct.unpack_from("<I", payload, 16)[0]
    if vertex_count > model_vertices:
        raise ValueError("SKIN vertex lookup exceeds the M2 vertex array")
    if any(index >= vertex_count for (index,) in struct.iter_unpack("<H", payload[index_offset:index_offset + index_count * 2])):
        raise ValueError("SKIN triangle index exceeds its vertex lookup")
    # The client checks each M2Array range before initializing the profile.
    # These extra checks ensure the shared sections address valid skin indices.
    section_offset = struct.unpack_from("<I", payload, 32)[0]
    for index in range(section_count):
        section = section_offset + index * 48
        index_start, index_count_section = struct.unpack_from("<HH", payload, section + 8)
        vertex_start, vertex_count_section = struct.unpack_from("<HH", payload, section + 4)
        if index_start + index_count_section > index_count or vertex_start + vertex_count_section > vertex_count:
            raise ValueError("SKIN section references data outside its profile arrays")
    return {"vertices": vertex_count, "indices": index_count, "bones": bone_count,
            "sections": section_count, "batches": batch_count}


def parse_gameobject_model_index(data):
    """Read GameObjectModels.dtree records without changing their bytes."""
    magic = b"VMAP_4.8"
    if not data.startswith(magic):
        raise ValueError("Unexpected GameObjectModels.dtree header")
    records = {}
    cursor = len(magic)
    while cursor < len(data):
        start = cursor
        if cursor + 9 > len(data):
            raise ValueError("Truncated GameObjectModels.dtree record")
        display_id, _, name_length = struct.unpack_from("<IBI", data, cursor)
        cursor += 9
        end = cursor + name_length + 24
        if name_length >= 500 or end > len(data) or display_id in records:
            raise ValueError("Invalid or duplicate GameObjectModels.dtree record")
        name = data[cursor:cursor + name_length].decode("ascii")
        records[display_id] = {"record": data[start:end], "name": name}
        cursor = end
    return records


def append_gameobject_model_alias(data, source_id=SOURCE_DISPLAY_ID, target_id=DISPLAY_ID):
    """Add a display-ID alias to the same server VMap collision model record."""
    records = parse_gameobject_model_index(data)
    if source_id not in records:
        raise ValueError(f"Source collision display {source_id} is missing")
    source_record = records[source_id]["record"]
    alias_record = struct.pack("<I", target_id) + source_record[4:]
    if target_id in records:
        if records[target_id]["record"] != alias_record:
            raise ValueError(f"Collision display {target_id} exists with different geometry")
        return data
    return data + alias_record


def _dds_header(width, height, fourcc, mip_count=1):
    block_size = 8 if fourcc == b"DXT1" else 16
    linear_size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_size
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000
    if mip_count > 1:
        flags |= 0x20000
    header = bytearray(128)
    header[:4] = b"DDS "
    struct.pack_into("<7I", header, 4, 124, flags, height, width, linear_size, 0, mip_count)
    struct.pack_into("<8I", header, 76, 32, 4, int.from_bytes(fourcc, "little"), 0, 0, 0, 0, 0)
    struct.pack_into("<5I", header, 108, 0x1000 | (0x8 | 0x400000 if mip_count > 1 else 0), 0, 0, 0, 0)
    return header


def decode_blp_mips(payload):
    if len(payload) < 1172 or payload[:4] != b"BLP2" or struct.unpack_from("<I", payload, 4)[0] != 1:
        raise ValueError("Expected a BLP2 version 1 texture")
    encoding, alpha_size, preferred = payload[8], payload[9], payload[10]
    if encoding != 2 or preferred not in (0, 7) or alpha_size not in (0, 8):
        raise ValueError("Copper texture is not the expected DXT1/DXT5 BLP2 format")
    width, height = struct.unpack_from("<II", payload, 12)
    if not width or not height:
        raise ValueError("BLP texture has invalid dimensions")
    offsets = struct.unpack_from("<16I", payload, 20)
    sizes = struct.unpack_from("<16I", payload, 84)
    fourcc = b"DXT1" if alpha_size == 0 else b"DXT5"
    expected_count = (max(width, height).bit_length()) if payload[11] & 1 else 1
    mips = []
    for level in range(expected_count):
        offset, size = offsets[level], sizes[level]
        mip_width, mip_height = max(1, width >> level), max(1, height >> level)
        expected_size = max(1, (mip_width + 3) // 4) * max(1, (mip_height + 3) // 4) * (8 if fourcc == b"DXT1" else 16)
        if offset < 1172 or size != expected_size or offset + size > len(payload):
            raise ValueError(f"BLP mip {level} has an invalid offset or size")
        dds = _dds_header(mip_width, mip_height, fourcc) + payload[offset:offset + size]
        image = Image.open(io.BytesIO(dds)).convert("RGBA")
        if image.size != (mip_width, mip_height):
            raise ValueError(f"BLP mip {level} decoded at an unexpected size")
        mips.append(image)
    if any(offsets[i] or sizes[i] for i in range(expected_count, 16)):
        raise ValueError("BLP has unexpected mip data after the complete mip chain")
    return mips, alpha_size


def grayscale_image(image, disable_glow=False):
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    gray = Image.new("L", rgba.size, 0) if disable_glow else ImageOps.grayscale(rgba.convert("RGB"))
    return Image.merge("RGBA", (gray, gray, gray, alpha))


def encode_raw_blp(mips, alpha_size):
    if not mips:
        raise ValueError("Cannot encode an empty BLP mip chain")
    header_size = 1172
    header = bytearray(header_size)
    header[:4] = b"BLP2"
    struct.pack_into("<I", header, 4, 1)
    header[8:12] = bytes((3, alpha_size, 2, int(len(mips) > 1)))  # raw BGRA8888
    struct.pack_into("<II", header, 12, *mips[0].size)
    payload = bytearray()
    cursor = header_size
    for level, image in enumerate(mips):
        if image.size != (max(1, mips[0].width >> level), max(1, mips[0].height >> level)):
            raise ValueError("Output BLP mips are not a complete halving chain")
        raw = image.tobytes("raw", "BGRA")
        struct.pack_into("<I", header, 20 + level * 4, cursor)
        struct.pack_into("<I", header, 84 + level * 4, len(raw))
        payload.extend(raw)
        cursor += len(raw)
    return bytes(header + payload)


def grayscale_blp(payload, disable_glow=False):
    decoded, alpha_size = decode_blp_mips(payload)
    result = [grayscale_image(image, disable_glow) for image in decoded]
    encoded = encode_raw_blp(result, alpha_size)
    validate_grayscale_blp(encoded, disable_glow)
    return encoded, result


def validate_grayscale_blp(payload, black=False):
    if payload[:4] != b"BLP2" or payload[8] != 3:
        raise ValueError("Generated BLP must use raw BGRA data")
    width, height = struct.unpack_from("<II", payload, 12)
    levels = max(width, height).bit_length() if payload[11] & 1 else 1
    offsets = struct.unpack_from("<16I", payload, 20)
    sizes = struct.unpack_from("<16I", payload, 84)
    for level in range(levels):
        w, h = max(1, width >> level), max(1, height >> level)
        offset, size = offsets[level], sizes[level]
        if offset < 1172 or size != w * h * 4 or offset + size > len(payload):
            raise ValueError("Generated BLP mip table is invalid")
        pixels = memoryview(payload)[offset:offset + size]
        for index in range(0, size, 4):
            b, g, r = pixels[index:index + 3]
            if b != g or g != r or (black and r != 0):
                raise ValueError("Generated texture contains non-grayscale color")


def darken_grayscale_blp(payload, brightness=0.4):
    """Darken an existing raw grayscale BLP mip chain without changing alpha or layout."""
    if not 0.0 <= brightness <= 1.0:
        raise ValueError("Brightness multiplier must be between 0 and 1")
    validate_grayscale_blp(payload)
    width, height = struct.unpack_from("<II", payload, 12)
    levels = max(width, height).bit_length() if payload[11] & 1 else 1
    offsets = struct.unpack_from("<16I", payload, 20)
    sizes = struct.unpack_from("<16I", payload, 84)
    result = bytearray(payload)
    for level in range(levels):
        w, h = max(1, width >> level), max(1, height >> level)
        offset, size = offsets[level], sizes[level]
        if size != w * h * 4 or offset < 1172 or offset + size > len(payload):
            raise ValueError(f"Raw grayscale BLP mip {level} has invalid bounds")
        for index in range(offset, offset + size, 4):
            blue, green, red, alpha = payload[index:index + 4]
            if blue != green or green != red:
                raise ValueError("Cannot darken a colored texture as a grayscale texture")
            value = min(255, int(red * brightness + 0.5))
            result[index:index + 3] = bytes((value, value, value))
            result[index + 3] = alpha
    darkened = bytes(result)
    validate_grayscale_blp(darkened)
    return darkened


def append_display_record(dbc, display_id, model_path):
    if len(dbc) < 20:
        raise ValueError("Truncated GameObjectDisplayInfo.dbc")
    magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", dbc)
    if (magic, fields, row_size) != (b"WDBC", 19, 76) or len(dbc) != 20 + count * row_size + strings_size:
        raise ValueError("Unexpected 3.3.5a GameObjectDisplayInfo.dbc layout")
    strings_start = 20 + count * row_size
    source = None
    for index in range(count):
        offset = 20 + index * row_size
        entry = struct.unpack_from("<I", dbc, offset)[0]
        if entry == display_id:
            raise ValueError(f"Display ID {display_id} already exists")
        if entry == SOURCE_DISPLAY_ID:
            source = bytearray(dbc[offset:offset + row_size])
    if source is None:
        raise ValueError(f"Original copper display ID {SOURCE_DISPLAY_ID} is missing")
    encoded_path = model_path.encode("ascii") + b"\0"
    struct.pack_into("<I", source, 0, display_id)
    struct.pack_into("<I", source, 4, strings_size)
    return (struct.pack("<4s4I", magic, count + 1, fields, row_size, strings_size + len(encoded_path)) +
            dbc[20:strings_start] + bytes(source) + dbc[strings_start:] + encoded_path)


def rewrite_model(original, replacements):
    if original[:4] != b"MD20" or struct.unpack_from("<I", original, 4)[0] != 264:
        raise ValueError("Expected the client copper M2 model version 264")
    data = bytearray(original)
    texture_count, texture_offset = struct.unpack_from("<II", original, 80)
    if texture_count != len(replacements) or texture_offset + texture_count * 16 > len(data):
        raise ValueError("Unexpected copper M2 texture table")
    names = []
    for index in range(texture_count):
        record = texture_offset + index * 16
        texture_type, flags, length, offset = struct.unpack_from("<4I", original, record)
        if texture_type != 0 or not length:
            raise ValueError(f"Copper M2 texture {index} is not a filename texture")
        old_name = original[offset:offset + length].split(b"\0")[0].decode("ascii")
        new_name = replacements.get(old_name)
        if not new_name:
            raise ValueError("No grayscale replacement for M2 texture: " + old_name)
        name = new_name.encode("ascii") + b"\0"
        names.append((record, name))
    for record, name in names:
        new_offset = len(data)
        data.extend(name)
        struct.pack_into("<I", data, record + 8, len(name))
        struct.pack_into("<I", data, record + 12, new_offset)
    # Preserve the working model's render flags, transparency, geometry,
    # collision and all other metadata. Only its filename texture references
    # differ in the Warscape variant.
    return bytes(data)


def build(output):
    output = Path(output).resolve()
    if output.exists() or any(output.is_relative_to(path.resolve()) for path in (ROOT, CLIENT, SERVER)):
        raise ValueError("Build output must be a new directory outside the repository, client and server")
    assets = Assets(CLIENT)
    try:
        client_dbc = assets.read(DBC_NAME)
        server_dbc = (SERVER / "dbc" / "GameObjectDisplayInfo.dbc").read_bytes()
        server_vmap = (SERVER / "vmaps" / GAMEOBJECT_MODELS_NAME).read_bytes()
        vmap_entries = parse_gameobject_model_index(server_vmap)
        if SOURCE_DISPLAY_ID not in vmap_entries:
            raise ValueError("Original copper collision record is missing from GameObjectModels.dtree")
        collision_asset = SERVER / "vmaps" / (vmap_entries[SOURCE_DISPLAY_ID]["name"] + ".vmo")
        if not collision_asset.is_file():
            raise ValueError("Original copper VMap collision asset is missing")
        original_model = assets.read(SOURCE_MODEL)
        original_skin = assets.read(SOURCE_SKIN)
        skin_stats = validate_skin_profile(original_skin, original_model)
        replacement_map = {}
        runtime_files = {}
        preview_dir = output / "preview"
        preview_dir.mkdir(parents=True)
        texture_records = []
        for source_path, target_path, disable_glow in TEXTURES:
            source = assets.read(source_path)
            output_blp, preview_mips = grayscale_blp(source, disable_glow)
            runtime_files[target_path] = output_blp
            replacement_map[source_path] = target_path
            preview_mips[0].save(preview_dir / (Path(target_path).stem + ".png"))
            texture_records.append({"source": source_path, "target": target_path,
                                    "source_sha256": hashlib.sha256(source).hexdigest(),
                                    "sha256": hashlib.sha256(output_blp).hexdigest(),
                                    "dimensions": list(preview_mips[0].size),
                                    "mip_count": len(preview_mips), "glow_disabled": disable_glow})
        runtime_files[CLIENT_MODEL_M2] = rewrite_model(original_model, replacement_map)
        runtime_files[CLIENT_SKIN] = original_skin
        runtime_files[PATH_TEST_MODEL_M2] = original_model
        runtime_files[PATH_TEST_SKIN] = original_skin
        if runtime_files[PATH_TEST_MODEL_M2] != original_model:
            raise ValueError("Path-test M2 is not an unmodified copy of the working copper model")
        validate_skin_profile(runtime_files[CLIENT_SKIN], runtime_files[CLIENT_MODEL_M2])
        validate_skin_profile(runtime_files[PATH_TEST_SKIN], runtime_files[PATH_TEST_MODEL_M2])
        client_display = append_display_record(client_dbc, DISPLAY_ID, CLIENT_MODEL)
        server_model = SOURCE_MODEL[:-2] + "mdx"
        expected_server_display = append_display_record(client_dbc, DISPLAY_ID, server_model)
        if server_dbc == client_dbc:
            # Fresh-install package: include the server-side collision DBC row.
            server_display = expected_server_display
        elif server_dbc == expected_server_display:
            # Existing Warscape install: retain its already-installed collision
            # row and rebuild only the client visual assets.
            server_display = server_dbc
        else:
            raise ValueError("Server GameObjectDisplayInfo.dbc differs from the known base and installed Warscape row")
        if client_display[:20] != struct.pack("<4s4I", b"WDBC", struct.unpack_from("<I", client_dbc, 4)[0] + 1,
                                               19, 76, struct.unpack_from("<I", client_dbc, 16)[0] + len(CLIENT_MODEL) + 1):
            raise ValueError("Client display DBC append verification failed")
        runtime_dir = output / "runtime"
        runtime_dir.mkdir(parents=True)
        archive(runtime_dir / "patch-Z.MPQ", runtime_files)
        archive(runtime_dir / "patch-enUS-Z.MPQ", {DBC_NAME: client_display})
        (runtime_dir / "GameObjectDisplayInfo.dbc").write_bytes(server_display)
        collision_vmap = append_gameobject_model_alias(server_vmap)
        (runtime_dir / GAMEOBJECT_MODELS_NAME).write_bytes(collision_vmap)
        manifest = {
            "display_id": DISPLAY_ID,
            "source_display_id": SOURCE_DISPLAY_ID,
            "client_model": CLIENT_MODEL,
            "server_collision_model": server_model,
            "original_mesh_sha256": hashlib.sha256(original_model).hexdigest(),
            "client_dbc_source_sha256": hashlib.sha256(client_dbc).hexdigest(),
            "server_dbc_source_sha256": hashlib.sha256(server_dbc).hexdigest(),
            "server_dbc_sha256": hashlib.sha256(server_display).hexdigest(),
            "server_vmap_source_sha256": hashlib.sha256(server_vmap).hexdigest(),
            "server_vmap_sha256": hashlib.sha256(collision_vmap).hexdigest(),
            "client_dbc_sha256": hashlib.sha256(client_display).hexdigest(),
            "skin_profile": {"source": SOURCE_SKIN, "sha256": hashlib.sha256(original_skin).hexdigest(),
                              "model_count": struct.unpack_from("<I", original_model, 68)[0], **skin_stats},
            "textures": texture_records,
            "validation": "Both SKIN profiles and M2 arrays validated; path-test M2 is byte-identical to source; server collision alias uses display 310 geometry; DBC append validated; texture mips are grayscale",
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    finally:
        assets.close()
    print(f"Built custom display {DISPLAY_ID} with grayscale assets, both matching SKIN profiles, and a display-ID collision alias.")
    print(f"Package: {output}")


def _assert_append(old, new):
    old_magic, old_count, fields, row_size, old_strings = struct.unpack_from("<4s4I", old)
    new_magic, new_count, new_fields, new_size, new_strings = struct.unpack_from("<4s4I", new)
    old_start, new_start = 20 + old_count * row_size, 20 + new_count * row_size
    if ((old_magic, fields, row_size) != (b"WDBC", 19, 76) or
            (new_magic, new_fields, new_size) != (old_magic, fields, row_size) or
            new_count != old_count + 1 or new_strings <= old_strings or
            old[20:old_start] != new[20:old_start] or not new[new_start:].startswith(old[old_start:])):
        raise ValueError("DBC append modified existing GameObjectDisplayInfo records")
    if len(old) != 20 + old_count * row_size + old_strings or len(new) != 20 + new_count * row_size + new_strings:
        raise ValueError("DBC append has inconsistent lengths")
    row = new[20 + old_count * row_size:new_start]
    if struct.unpack_from("<I", row)[0] != DISPLAY_ID:
        raise ValueError("New display record ID is wrong")


def dbc_model_path(dbc, display_id):
    magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", dbc)
    if (magic, fields, row_size) != (b"WDBC", 19, 76) or len(dbc) != 20 + count * row_size + strings_size:
        raise ValueError("Unexpected 3.3.5a GameObjectDisplayInfo.dbc layout")
    rows_start = 20
    strings_start = rows_start + count * row_size
    for index in range(count):
        row = rows_start + index * row_size
        if struct.unpack_from("<I", dbc, row)[0] == display_id:
            string_offset = struct.unpack_from("<I", dbc, row + 4)[0]
            end = dbc.find(b"\0", strings_start + string_offset)
            if string_offset >= strings_size or end < 0:
                raise ValueError("Display DBC model-name offset is invalid")
            return dbc[strings_start + string_offset:end].decode("ascii")
    raise ValueError(f"Display DBC record {display_id} is missing")


def set_dbc_model_path(dbc, display_id, model_path):
    """Change only the selected display's model-name offset, retaining its DBC."""
    magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", dbc)
    if (magic, fields, row_size) != (b"WDBC", 19, 76) or len(dbc) != 20 + count * row_size + strings_size:
        raise ValueError("Unexpected 3.3.5a GameObjectDisplayInfo.dbc layout")
    row_start = next((20 + index * row_size for index in range(count)
                      if struct.unpack_from("<I", dbc, 20 + index * row_size)[0] == display_id), None)
    if row_start is None:
        raise ValueError(f"Display DBC record {display_id} is missing")
    strings_start = 20 + count * row_size
    strings = dbc[strings_start:]
    encoded = model_path.encode("ascii") + b"\0"
    offset = 0
    found = -1
    while True:
        found = strings.find(encoded, found + 1)
        if found < 0:
            break
        if found == 0 or strings[found - 1] == 0:
            offset = found
            break
    data = bytearray(dbc)
    if found < 0:
        offset = strings_size
        struct.pack_into("<I", data, 16, strings_size + len(encoded))
        data.extend(encoded)
    struct.pack_into("<I", data, row_start + 4, offset)
    return bytes(data)


def _assert_same_dbc_rows_except_model_path(old, expected, display_id):
    old_magic, old_count, old_fields, old_size, old_strings = struct.unpack_from("<4s4I", old)
    new_magic, new_count, new_fields, new_size, new_strings = struct.unpack_from("<4s4I", expected)
    if (old_magic, old_count, old_fields, old_size) != (new_magic, new_count, new_fields, new_size):
        raise ValueError("Current client DBC record layout differs from the package")
    for index in range(old_count):
        start = 20 + index * old_size
        old_row, new_row = old[start:start + old_size], expected[start:start + old_size]
        if struct.unpack_from("<I", old_row)[0] == display_id:
            if old_row[:4] != new_row[:4] or old_row[8:] != new_row[8:]:
                raise ValueError("Current custom display DBC metadata differs from the reviewed record")
        elif old_row != new_row:
            raise ValueError("An unrelated client display DBC record changed")
    old_start, new_start = 20 + old_count * old_size, 20 + new_count * new_size
    if (len(old) != old_start + old_strings or len(expected) != new_start + new_strings or
            old[old_start:old_start + min(old_strings, new_strings)] != expected[new_start:new_start + min(old_strings, new_strings)]):
        raise ValueError("Client DBC string table does not retain the reviewed base strings")


def deploy(output):
    output = Path(output).resolve()
    runtime = output / "runtime"
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("display_id") != DISPLAY_ID:
        raise ValueError("Package display ID does not match this deployer")
    running = subprocess.run(["powershell", "-NoProfile", "-Command",
        "@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, check=True)
    if running.stdout.strip() != "0":
        raise ValueError("The custom client and local servers must be stopped before deploying")
    if not (CLIENT / "WowClient64.exe").is_file():
        raise ValueError("Verified wowdecomp client executable is missing")

    client_data = CLIENT / "Data"
    client_patch = client_data / "patch-Z.MPQ"
    locale_patch = client_data / "enUS" / "patch-enUS-Z.MPQ"
    server_dbc = SERVER / "dbc" / "GameObjectDisplayInfo.dbc"
    server_vmap = SERVER / "vmaps" / GAMEOBJECT_MODELS_NAME
    old_assets = archive_entries(client_patch)
    old_locale = archive_entries(locale_patch)
    additions = archive_entries(runtime / "patch-Z.MPQ")
    locale_additions = archive_entries(runtime / "patch-enUS-Z.MPQ")
    expected_assets = ({texture[1] for texture in TEXTURES} |
                       {CLIENT_MODEL_M2, CLIENT_SKIN, PATH_TEST_MODEL_M2, PATH_TEST_SKIN})
    if set(additions) != expected_assets:
        raise ValueError("Client asset patch contains unexpected or missing files")
    if set(locale_additions) != {DBC_NAME}:
        raise ValueError("Locale patch contains unexpected files")
    old_dbc_keys = [entry for entry in old_locale if entry.lower() == DBC_NAME.lower()]
    if len(old_dbc_keys) != 1:
        raise ValueError("Expected exactly one existing client display DBC override")
    if dbc_model_path(old_locale[old_dbc_keys[0]], DISPLAY_ID) not in (CLIENT_MODEL, PATH_TEST_MODEL, SOURCE_MODEL[:-2] + "mdx"):
        raise ValueError("Current client display path is not a known Warscape copper test state")
    merged_assets = dict(old_assets)
    for name, payload in additions.items():
        matches = [entry for entry in merged_assets if entry.lower() == name.lower()]
        if len(matches) > 1:
            raise ValueError("Client MPQ has duplicate case-insensitive custom asset paths")
        merged_assets[matches[0] if matches else name] = payload
    client_base_assets = Assets(CLIENT)
    try:
        client_base_dbc = client_base_assets.read(DBC_NAME)
    finally:
        client_base_assets.close()
    if hashlib.sha256(client_base_dbc).hexdigest() != manifest["client_dbc_source_sha256"]:
        raise ValueError("Client base GameObjectDisplayInfo.dbc changed after package generation")
    _assert_append(client_base_dbc, locale_additions[DBC_NAME])
    _assert_same_dbc_rows_except_model_path(old_locale[old_dbc_keys[0]], locale_additions[DBC_NAME], DISPLAY_ID)
    merged_dbc = set_dbc_model_path(old_locale[old_dbc_keys[0]], DISPLAY_ID, CLIENT_MODEL)
    if dbc_model_path(merged_dbc, DISPLAY_ID) != CLIENT_MODEL:
        raise ValueError("Merged client display DBC does not resolve to the grayscale model")

    current_server_dbc = server_dbc.read_bytes()
    new_server_dbc = (runtime / "GameObjectDisplayInfo.dbc").read_bytes()
    if (hashlib.sha256(current_server_dbc).hexdigest() != manifest["server_dbc_source_sha256"] or
            current_server_dbc != new_server_dbc):
        raise ValueError("Server display DBC differs from the already-installed collision record")
    server_model = SOURCE_MODEL[:-2] + "mdx"
    if dbc_model_path(current_server_dbc, DISPLAY_ID) != server_model:
        raise ValueError("Server collision DBC does not retain the original copper model")
    new_client_dbc = locale_additions[DBC_NAME]
    def find_display_row(dbc, display_id):
        count = struct.unpack_from("<I", dbc, 4)[0]
        return next(dbc[20 + index * 76:20 + (index + 1) * 76]
                    for index in range(count)
                    if struct.unpack_from("<I", dbc, 20 + index * 76)[0] == display_id)
    client_row = find_display_row(new_client_dbc, DISPLAY_ID)
    server_row = find_display_row(current_server_dbc, DISPLAY_ID)
    if client_row[:4] != server_row[:4] or client_row[8:76] != server_row[8:76]:
        raise ValueError("Client/server display rows differ beyond their expected model path")
    client_string_offset = struct.unpack_from("<I", client_row, 4)[0]
    client_strings_start = 20 + (struct.unpack_from("<I", new_client_dbc, 4)[0]) * 76
    client_string_len = struct.unpack_from("<I", new_client_dbc, 16)[0]
    client_strings = new_client_dbc[client_strings_start:client_strings_start + client_string_len]
    if client_string_offset >= len(client_strings):
        raise ValueError("Client model string offset is invalid")
    client_model_name = client_strings[client_string_offset:].split(b"\0", 1)[0].decode("ascii")
    if client_model_name != CLIENT_MODEL:
        raise ValueError("Client display DBC does not reference its custom visual model")

    current_vmap = server_vmap.read_bytes()
    new_vmap = (runtime / GAMEOBJECT_MODELS_NAME).read_bytes()
    if hashlib.sha256(current_vmap).hexdigest() != manifest["server_vmap_source_sha256"]:
        raise ValueError("Server VMap index changed after package generation")
    if append_gameobject_model_alias(current_vmap) != new_vmap:
        raise ValueError("Prepared server collision index is not a display-310 alias")
    model_entry = parse_gameobject_model_index(current_vmap)[SOURCE_DISPLAY_ID]
    if not (SERVER / "vmaps" / (model_entry["name"] + ".vmo")).is_file():
        raise ValueError("Original copper VMap collision asset is missing")

    output.mkdir(exist_ok=True)
    prepared = output / ("deploy-prepared-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    prepared.mkdir(exist_ok=False)
    merged_locale = dict(old_locale)
    merged_locale[old_dbc_keys[0]] = merged_dbc
    archive(prepared / "patch-Z.MPQ", merged_assets)
    archive(prepared / "patch-enUS-Z.MPQ", merged_locale)
    (prepared / GAMEOBJECT_MODELS_NAME).write_bytes(new_vmap)
    verify_assets = archive_entries(prepared / "patch-Z.MPQ")
    verify_locale = archive_entries(prepared / "patch-enUS-Z.MPQ")
    verify_vmap = (prepared / GAMEOBJECT_MODELS_NAME).read_bytes()
    if verify_assets != merged_assets:
        raise ValueError("Prepared client patch did not preserve existing assets")
    if verify_locale != merged_locale:
        raise ValueError("Prepared locale patch did not preserve existing entries")
    if verify_locale[old_dbc_keys[0]] != merged_dbc or verify_vmap != new_vmap:
        raise ValueError("Prepared locale patch failed display DBC readback")
    if any(verify_assets.get(name) != payload for name, payload in additions.items()):
        raise ValueError("Prepared client patch failed custom asset readback")

    pairs = [(prepared / "patch-Z.MPQ", client_patch),
             (prepared / "patch-enUS-Z.MPQ", locale_patch),
             (prepared / GAMEOBJECT_MODELS_NAME, server_vmap)]
    for source, _ in pairs:
        if not source.is_file():
            raise ValueError("A prepared deployment source file is missing")
    before = {str(path): digest(path) for path in (CLIENT / "WowClient64.exe",)}
    backup = BACKUPS / ("Warscape-CopperGrayscale-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True, exist_ok=False)
    records = []
    for index, (source, target) in enumerate(pairs):
        saved = backup / f"{index:04}-{target.name}"
        shutil.copy2(target, saved)
        if digest(saved) != digest(target):
            raise ValueError("Deployment backup checksum mismatch")
        records.append({"source": str(source), "target": str(target), "backup": str(saved),
                        "previous_sha256": digest(target), "new_sha256": digest(source)})
    (backup / "deployment.json").write_text(json.dumps({"files": records, "preserved": before}, indent=2) + "\n", encoding="utf-8")
    written = []
    try:
        for index, record in enumerate(records):
            source, target = Path(record["source"]), Path(record["target"])
            staged = target.with_name(target.name + ".copper-pending")
            if staged.exists():
                raise ValueError("Stale pending deployment file exists")
            shutil.copy2(source, staged)
            if digest(staged) != record["new_sha256"]:
                raise ValueError("Staged deployment checksum mismatch")
            os.replace(staged, target)
            written.append(record)
            if digest(target) != record["new_sha256"]:
                raise ValueError("Deployed file checksum mismatch")
        if any(digest(path) != expected for path, expected in before.items()):
            raise ValueError("An unrelated client binary changed")
    except BaseException:
        for record in reversed(written):
            shutil.copy2(record["backup"], record["target"])
        raise
    result = {"files_deployed": len(records), "backup": str(backup),
              "client_executable": str(CLIENT / "WowClient64.exe"), "game_directory": str(CLIENT),
              "server_collision_index": str(server_vmap), "database_changes": False,
              "manual_visual_test": False, "display_id": DISPLAY_ID}
    (output / "deployment-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--output", type=Path, required=True)
    deploy_parser = commands.add_parser("deploy")
    deploy_parser.add_argument("package", type=Path)
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("Local Windows execution only")
    if args.command == "build":
        build(args.output)
    else:
        deploy(args.package)


if __name__ == "__main__":
    main()
