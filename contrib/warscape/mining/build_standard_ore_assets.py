#!/usr/bin/env python3
"""Build isolated Warscape active/depleted models for standard WotLK ores."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
CLIENT = Path(r"C:\WoWDev\wowdecomp\bin\Win")
SERVER = Path(r"C:\WoWDev\TrinityServer")
sys.path.insert(0, str(ROOT / "contrib/warscape/mining"))
import copper_depletion_assets as copper  # noqa: E402
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
from deploy_sandbox import archive_entries  # noqa: E402
from generate import archive  # noqa: E402

DBC = r"DBFilesClient\GameObjectDisplayInfo.dbc"
MPQ_ASSETS = CLIENT / "Data/patch-Z.MPQ"
LOCALE_MPQ = CLIENT / "Data/enUS/patch-enUS-Z.MPQ"
ITEM_DBC_SOURCE = SERVER / "dbc/Item.dbc"

ORES = [
    ("Tin", r"World\SkillActivated\TradeskillNodes\tin_Miningnode_01.m2", 315, 900118, 900104),
    ("Silver", r"World\SkillActivated\TradeskillNodes\TrueSilver_Miningnode_01.m2", 314, 900119, 900105),
    ("Iron", r"World\SkillActivated\TradeskillNodes\Iron_Miningnode_01.m2", 312, 900120, 900106),
    ("Gold", r"World\SkillActivated\TradeskillNodes\gold_Miningnode_01.m2", 311, 900121, 900107),
    ("Mithril", r"World\SkillActivated\TradeskillNodes\mithril_Miningnode_01.m2", 313, 900122, 900108),
    ("Truesilver", r"World\SkillActivated\TradeskillNodes\TrueSilver_Miningnode_01.m2", 314, 900123, 900109),
    ("DarkIron", r"World\Azeroth\BurningSteppes\ActiveDoodads\DarkIronNode\DarkIronNode.m2", 2571, 900124, 900110),
    ("Thorium", r"World\SkillActivated\TradeskillNodes\Thorium_Miningnode_01.m2", 3951, 900125, 900111),
    ("FelIron", r"World\SkillActivated\TradeskillNodes\FelIron_Miningnode_01.m2", 6799, 900126, 900112),
    ("Adamantite", r"World\SkillActivated\TradeskillNodes\Adamantium_Miningnode_01.m2", 6798, 900127, 900113),
    ("Khorium", r"World\SkillActivated\TradeskillNodes\Khorium_Miningnode_01.m2", 6800, 900128, 900114),
    ("Cobalt", r"World\SkillActivated\TradeskillNodes\Cobalt_Miningnode_01.m2", 7881, 900129, 900115),
    ("Saronite", r"World\SkillActivated\TradeskillNodes\Yoggthorite_Miningnode_01.m2", 7804, 900130, 900116),
    ("Titanium", r"World\SkillActivated\TradeskillNodes\Adamantium_Miningnode_01.m2", 6798, 900131, 900117),
]

ORE_ITEMS = [
    (900201, 2771), (900202, 2775), (900203, 2772), (900204, 2776),
    (900205, 3858), (900206, 7911), (900207, 11370), (900208, 10620),
    (900209, 23424), (900210, 23425), (900211, 23426), (900212, 36909),
    (900213, 36912), (900214, 36910),
]


def append_item_dbc_rows(dbc, source_item_dbc):
    """Add client item-ID rows copied from the matching stock ore records."""
    magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", dbc)
    source_magic, source_count, source_fields, source_size, source_strings = struct.unpack_from("<4s4I", source_item_dbc)
    if ((magic, fields, row_size) != (b"WDBC", 8, 32) or
            (source_magic, source_fields, source_size) != (magic, fields, row_size) or
            len(dbc) != 20 + count * row_size + strings_size or
            len(source_item_dbc) != 20 + source_count * source_size + source_strings):
        raise ValueError("Unexpected 3.3.5a Item.dbc layout")

    def rows(data, row_count, stride):
        result = {}
        for index in range(row_count):
            row = data[20 + index * stride:20 + (index + 1) * stride]
            entry = struct.unpack_from("<I", row)[0]
            if entry in result:
                raise ValueError(f"Duplicate Item.dbc entry {entry}")
            result[entry] = row
        return result

    existing = rows(dbc, count, row_size)
    sources = rows(source_item_dbc, source_count, source_size)
    additions = []
    for custom_id, vanilla_id in ORE_ITEMS:
        if custom_id in existing:
            raise ValueError(f"Custom item ID {custom_id} already exists in Item.dbc")
        source = sources.get(vanilla_id)
        if source is None:
            raise ValueError(f"Vanilla ore item {vanilla_id} is missing from Item.dbc")
        row = bytearray(source)
        struct.pack_into("<I", row, 0, custom_id)
        additions.append(bytes(row))
    return (struct.pack("<4s4I", magic, count + len(additions), fields, row_size, strings_size) +
            dbc[20:20 + count * row_size] + b"".join(additions) + dbc[20 + count * row_size:])


def add_display(dbc, source_id, target_id, model_path):
    magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", dbc)
    if (magic, fields, row_size) != (b"WDBC", 19, 76) or len(dbc) != 20 + count * row_size + strings_size:
        raise ValueError("Unexpected 3.3.5a GameObjectDisplayInfo DBC")
    rows_start, strings_start = 20, 20 + count * row_size
    source = None
    for index in range(count):
        row = dbc[rows_start + index * row_size:rows_start + (index + 1) * row_size]
        record_id = struct.unpack_from("<I", row)[0]
        if record_id == target_id:
            raise ValueError(f"Target display {target_id} already exists")
        if record_id == source_id:
            source = bytearray(row)
    if source is None:
        raise ValueError(f"Source display {source_id} missing")
    encoded = model_path.encode("ascii") + b"\0"
    struct.pack_into("<I", source, 0, target_id)
    struct.pack_into("<I", source, 4, strings_size)
    return (struct.pack("<4s4I", magic, count + 1, fields, row_size, strings_size + len(encoded)) +
            dbc[20:strings_start] + source + dbc[strings_start:] + encoded)


def model_textures(model):
    if model[:4] != b"MD20" or struct.unpack_from("<I", model, 4)[0] != 264:
        raise ValueError("Expected 3.3.5a M2 version 264")
    count, offset = struct.unpack_from("<II", model, 80)
    if count > 128 or offset + count * 16 > len(model):
        raise ValueError("M2 texture table outside file")
    paths = []
    for index in range(count):
        kind, _flags, length, name_offset = struct.unpack_from("<4I", model, offset + index * 16)
        if kind != 0 or not length or name_offset + length > len(model):
            raise ValueError("Unsupported/invalid non-filename M2 texture")
        paths.append(model[name_offset:name_offset + length].split(b"\0", 1)[0].decode("ascii"))
    return paths


def build(output):
    output = Path(output).resolve()
    if output.exists() or output.is_relative_to(ROOT) or output.is_relative_to(CLIENT) or output.is_relative_to(SERVER):
        raise ValueError("Output must be a new directory outside source and deployment trees")
    if not LOCALE_MPQ.is_file():
        raise ValueError("Existing client locale patch is required to preserve the copper display entry")
    if not ITEM_DBC_SOURCE.is_file():
        raise ValueError("Server's matching 3.3.5a Item.dbc source is missing")
    assets = copper.Assets(CLIENT)
    runtime, client_dbc, server_dbc = {}, archive_entries(LOCALE_MPQ), (SERVER / "dbc/GameObjectDisplayInfo.dbc").read_bytes()
    item_source_dbc = ITEM_DBC_SOURCE.read_bytes()
    dbc_key = next((key for key in client_dbc if key.lower() == DBC.lower()), None)
    if dbc_key is None:
        raise ValueError("Existing client locale patch has no GameObjectDisplayInfo override")
    client_dbc_payload = client_dbc[dbc_key]
    vmap_path = SERVER / "vmaps/GameObjectModels.dtree"
    vmap = copper.parse_gameobject_model_index(vmap_path.read_bytes())
    manifest = []
    try:
        for ore, source_path, source_display, active_display, depleted_display in ORES:
            stem = "Warscape" + ore + "Mining"
            source = assets.read(source_path)
            source_skin_path = source_path.rsplit(".", 1)[0] + "00.skin"
            skin = assets.read(source_skin_path)
            copper.validate_skin_profile(skin, source)
            paths = model_textures(source)
            replacements, texture_hashes = {}, []
            active_model = rf"World\Warscape\Mining\Standard\{stem}Active.mdx"
            depleted_model = rf"World\Warscape\Mining\Standard\{stem}Depleted.mdx"
            # The 3.3.5a client converts DBC .mdx paths to .m2 before MPQ lookup.
            # Replacing only the final character would incorrectly produce .md2.
            active_file = active_model.rsplit(".", 1)[0] + ".m2"
            depleted_file = depleted_model.rsplit(".", 1)[0] + ".m2"
            active_skin = active_model.rsplit(".", 1)[0] + "00.skin"
            depleted_skin = depleted_model.rsplit(".", 1)[0] + "00.skin"
            runtime[active_file], runtime[active_skin] = source, skin
            for index, original_texture in enumerate(dict.fromkeys(paths)):
                texture = assets.read(original_texture)
                lower = original_texture.lower()
                neutralize = any(term in lower for term in ("glow.blp", "glowstar.blp", "sparkle.blp"))
                target = rf"World\Warscape\Mining\Standard\Textures\{stem}Gray{index:02}.blp"
                grayscale, _mips = copper.grayscale_blp(texture, disable_glow=neutralize)
                copper.validate_grayscale_blp(grayscale, black=neutralize)
                runtime[target] = grayscale
                replacements[original_texture] = target
                texture_hashes.append({"source": original_texture, "target": target,
                                       "source_sha256": hashlib.sha256(texture).hexdigest(),
                                       "gray_sha256": hashlib.sha256(grayscale).hexdigest(),
                                       "glow_neutralized": neutralize})
            runtime[depleted_file] = copper.rewrite_model(source, replacements)
            runtime[depleted_skin] = skin
            copper.validate_skin_profile(runtime[depleted_skin], runtime[depleted_file])
            # The active copy is byte-identical; depleted geometry differs only in filename texture references.
            if runtime[active_file] != source:
                raise ValueError(f"{ore} active model is not byte-identical to its original")
            server_model_path = source_path.rsplit(".", 1)[0] + ".mdx"
            for did, client_path, server_path in ((active_display, active_model, server_model_path),
                                                   (depleted_display, depleted_model, server_model_path)):
                client_dbc_payload = add_display(client_dbc_payload, source_display, did, client_path)
                server_dbc = add_display(server_dbc, source_display, did, server_path)
                if source_display not in vmap:
                    raise ValueError(f"{ore}: collision model record {source_display} missing")
                collision_path = SERVER / "vmaps" / (vmap[source_display]["name"] + ".vmo")
                if not collision_path.is_file():
                    raise ValueError(f"{ore}: source collision asset is missing: {collision_path.name}")
                collision = vmap[source_display]["record"]
                for target_id in (did,):
                    vmap[target_id] = {"record": struct.pack("<I", target_id) + collision[4:],
                                       "name": vmap[source_display]["name"]}
            for target_id in (active_display, depleted_display):
                expected_client = active_model if target_id == active_display else depleted_model
                if copper.dbc_model_path(client_dbc_payload, target_id) != expected_client:
                    raise ValueError(f"{ore}: client display path failed readback")
            manifest.append({"ore": ore, "source_model": source_path, "source_sha256": hashlib.sha256(source).hexdigest(),
                             "active_model": active_model, "active_sha256": hashlib.sha256(runtime[active_file]).hexdigest(),
                             "depleted_model": depleted_model, "depleted_sha256": hashlib.sha256(runtime[depleted_file]).hexdigest(),
                             "skin_sha256": hashlib.sha256(skin).hexdigest(), "vertices": struct.unpack_from("<I", source, 60)[0],
                             "textures": texture_hashes, "active_display": active_display,
                             "depleted_display": depleted_display, "collision_display_source": source_display})
    finally:
        assets.close()
    item_dbc_key = r"DBFilesClient\Item.dbc"
    client_dbc[item_dbc_key] = append_item_dbc_rows(item_source_dbc, item_source_dbc)
    output.mkdir(parents=True)
    archive(output / "patch-WarscapeMining.MPQ", runtime)
    client_dbc[dbc_key] = client_dbc_payload
    archive(output / "patch-enUS-WarscapeMining.MPQ", client_dbc)
    vmap_payload = vmap_path.read_bytes()
    for item in manifest:
        for target_id in (item["active_display"], item["depleted_display"]):
            source_id = item["collision_display_source"]
            vmap_payload = copper.append_gameobject_model_alias(vmap_payload, source_id, target_id)
    (output / "GameObjectDisplayInfo.dbc").write_bytes(server_dbc)
    (output / "GameObjectModels.dtree").write_bytes(vmap_payload)
    (output / "manifest.json").write_text(json.dumps({"ores": manifest, "asset_count": len(runtime),
        "client_dbc_sha256": hashlib.sha256(client_dbc_payload).hexdigest(),
        "client_item_dbc_sha256": hashlib.sha256(client_dbc[item_dbc_key]).hexdigest(),
        "server_dbc_sha256": hashlib.sha256(server_dbc).hexdigest(),
        "vmap_sha256": hashlib.sha256(vmap_payload).hexdigest()}, indent=2) + "\n", encoding="utf-8")
    print(f"Validated asset package for {len(manifest)} ores; {len(runtime)} client files; package: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    build(parser.parse_args().output)
