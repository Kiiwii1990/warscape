#!/usr/bin/env python3
"""Safely merge the validated standard-ore package into local client/server files."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CLIENT = Path(r"C:\WoWDev\wowdecomp\bin\Win")
SERVER = Path(r"C:\WoWDev\TrinityServer")
BACKUPS = Path(r"C:\WoWDev\Backups")
PACKAGE = Path(r"C:\WoWDev\Backups\WarscapeMiningExpansionAssets-20261031-StageB-m2-path-fix")
RELEASE_EXE = ROOT / "out/build/x64-Release/bin/Release/worldserver.exe"
sys.path.insert(0, str(ROOT / "contrib/warscape/mining"))
import copper_depletion_assets as copper  # noqa: E402
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
from deploy_sandbox import archive_entries  # noqa: E402
from generate import archive  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_dbc_append(old, new, expected_append=28):
    old_magic, old_count, old_fields, old_size, old_strings = struct.unpack_from("<4s4I", old)
    new_magic, new_count, new_fields, new_size, new_strings = struct.unpack_from("<4s4I", new)
    if ((old_magic, old_fields, old_size) != (b"WDBC", 19, 76) or
            (new_magic, new_fields, new_size) != (old_magic, old_fields, old_size) or
            new_count != old_count + expected_append):
        raise ValueError("Display DBC row layout/count changed unexpectedly")
    old_row_end, new_row_end = 20 + old_count * old_size, 20 + new_count * new_size
    if old[20:old_row_end] != new[20:old_row_end]:
        raise ValueError("Existing display DBC rows changed")
    if old[old_row_end:] != new[new_row_end:new_row_end + old_strings]:
        raise ValueError("Existing display DBC strings changed")
    if len(old) != old_row_end + old_strings or len(new) != new_row_end + new_strings:
        raise ValueError("Display DBC lengths do not match their headers")


def assert_item_dbc_append(old, new, expected_append=14):
    old_magic, old_count, old_fields, old_size, old_strings = struct.unpack_from("<4s4I", old)
    new_magic, new_count, new_fields, new_size, new_strings = struct.unpack_from("<4s4I", new)
    if ((old_magic, old_fields, old_size) != (b"WDBC", 8, 32) or
            (new_magic, new_fields, new_size) != (old_magic, old_fields, old_size) or
            new_count != old_count + expected_append):
        raise ValueError("Item.dbc row layout/count changed unexpectedly")
    old_row_end, new_row_end = 20 + old_count * old_size, 20 + new_count * new_size
    if old[20:old_row_end] != new[20:20 + old_count * old_size] or old[old_row_end:] != new[new_row_end:]:
        raise ValueError("Existing Item.dbc rows or string table changed")
    if len(old) != old_row_end + old_strings or len(new) != new_row_end + new_strings:
        raise ValueError("Item.dbc lengths do not match their headers")


def assert_server_dbc_preserved_with_path_fixes(old, new, manifest):
    old_magic, old_count, fields, row_size, old_strings = struct.unpack_from("<4s4I", old)
    new_magic, new_count, new_fields, new_size, new_strings = struct.unpack_from("<4s4I", new)
    if ((old_magic, fields, row_size) != (b"WDBC", 19, 76) or
            (new_magic, new_count, new_fields, new_size) != (old_magic, old_count, fields, row_size)):
        raise ValueError("Server display DBC count/layout changed unexpectedly")
    old_row_end, new_row_end = 20 + old_count * row_size, 20 + new_count * new_size
    if len(old) != old_row_end + old_strings or len(new) != new_row_end + new_strings:
        raise ValueError("Server display DBC lengths do not match their headers")
    old_rows, new_rows = {}, {}
    for data, count, size, rows in ((old, old_count, row_size, old_rows), (new, new_count, new_size, new_rows)):
        for index in range(count):
            row = data[20 + index * size:20 + (index + 1) * size]
            entry = struct.unpack_from("<I", row)[0]
            if entry in rows:
                raise ValueError(f"Duplicate server display DBC row {entry}")
            rows[entry] = row
    corrected_ids = {int(ore[key]) for ore in manifest["ores"] for key in ("active_display", "depleted_display")}
    if old_rows.keys() != new_rows.keys():
        raise ValueError("Server display DBC entries changed")
    expected_paths = {}
    for ore in manifest["ores"]:
        path = ore["source_model"].rsplit(".", 1)[0] + ".mdx"
        expected_paths[int(ore["active_display"])] = path
        expected_paths[int(ore["depleted_display"])] = path
    strings_start = new_row_end
    for entry, before in old_rows.items():
        after = new_rows[entry]
        if entry not in corrected_ids:
            if before != after:
                raise ValueError(f"Unrelated server display DBC row {entry} changed")
            continue
        if before[8:] != after[8:]:
            raise ValueError(f"Non-path fields changed in server display DBC row {entry}")
        path_offset = struct.unpack_from("<I", after, 4)[0]
        end = new.find(b"\0", strings_start + path_offset)
        path = new[strings_start + path_offset:end].decode("ascii")
        if path != expected_paths[entry]:
            raise ValueError(f"Incorrect server model path for display {entry}: {path}")
    if old[old_row_end:] != new[new_row_end:new_row_end + old_strings]:
        raise ValueError("Original server display DBC string table changed")


def main():
    runtime = PACKAGE / "patch-WarscapeMining.MPQ"
    locale_package = PACKAGE / "patch-enUS-WarscapeMining.MPQ"
    server_dbc_package = PACKAGE / "GameObjectDisplayInfo.dbc"
    vmap_package = PACKAGE / "GameObjectModels.dtree"
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    targets = [
        (CLIENT / "Data/patch-Z.MPQ", runtime),
        (CLIENT / "Data/enUS/patch-enUS-Z.MPQ", locale_package),
        (SERVER / "dbc/GameObjectDisplayInfo.dbc", server_dbc_package),
        (SERVER / "vmaps/GameObjectModels.dtree", vmap_package),
        (SERVER / "worldserver.exe", RELEASE_EXE),
    ]
    if os.name != "nt" or any(not p.is_file() for pair in targets for p in pair):
        raise ValueError("A required local Windows deployment file is missing")
    proc = subprocess.run(["powershell", "-NoProfile", "-Command",
        "@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, check=True)
    if proc.stdout.strip() != "0":
        raise ValueError("WoW and local servers must be stopped before deployment")

    client_patch, locale_patch = targets[0][0], targets[1][0]
    old_assets, additions = archive_entries(client_patch), archive_entries(runtime)
    obsolete_model_entries = {}
    for ore in manifest["ores"]:
        for model_key in ("active_model", "depleted_model"):
            base = ore[model_key].rsplit(".", 1)[0]
            obsolete_model_entries[base + ".md2"] = base + ".m2"
    merged_assets = dict(old_assets)
    for obsolete, correct in obsolete_model_entries.items():
        existing = next((key for key in merged_assets if key.lower() == obsolete.lower()), None)
        if existing is not None:
            correct_payload = additions.get(correct)
            if correct_payload is None or merged_assets[existing] != correct_payload:
                raise ValueError(f"Refusing to remove unexpected obsolete model entry: {existing}")
            del merged_assets[existing]
    seen = {}
    for name, payload in merged_assets.items():
        seen.setdefault(name.lower(), []).append((name, payload))
    for name, payload in additions.items():
        matches = seen.get(name.lower(), [])
        if len(matches) > 1 or (matches and matches[0][1] != payload):
            raise ValueError(f"Custom MPQ asset path collision: {name}")
        if not matches:
            merged_assets[name] = payload
            seen.setdefault(name.lower(), []).append((name, payload))
    expected_asset_files = set(additions)
    if len(expected_asset_files) != 124:
        raise ValueError("Ore package has an unexpected asset count")

    old_locale, new_locale = archive_entries(locale_patch), archive_entries(locale_package)
    allowed_new_entries = {r"DBFilesClient\Item.dbc".lower()}
    if not set(old_locale).issubset(new_locale) or any(k.lower() not in allowed_new_entries for k in set(new_locale) - set(old_locale)):
        raise ValueError("Locale package changes unrelated archive entries")
    dbc_key = next((key for key in old_locale if key.lower() == copper.DBC_NAME.lower()), None)
    if dbc_key is None:
        raise ValueError("Current locale patch lacks GameObjectDisplayInfo.dbc")
    item_dbc_key = next((key for key in new_locale if key.lower() == r"dbfilesclient\item.dbc"), None)
    if item_dbc_key is None:
        raise ValueError("Locale package lacks the custom item Item.dbc rows")
    if any(old_locale[k] != new_locale[k] for k in old_locale if k != dbc_key):
        raise ValueError("Locale package changes a non-DBC entry")
    if old_locale[dbc_key] != new_locale[dbc_key]:
        assert_dbc_append(old_locale[dbc_key], new_locale[dbc_key])
    item_source_path = SERVER / "dbc/Item.dbc"
    if not item_source_path.is_file():
        raise ValueError("Effective client Item.dbc source patch is missing")
    item_source = item_source_path.read_bytes()
    assert_item_dbc_append(item_source, new_locale[item_dbc_key])

    server_dbc = targets[2][0].read_bytes()
    new_server_dbc = server_dbc_package.read_bytes()
    assert_server_dbc_preserved_with_path_fixes(server_dbc, new_server_dbc, manifest)
    client_dbc = new_locale[dbc_key]
    for ore in manifest["ores"]:
        if copper.dbc_model_path(client_dbc, ore["active_display"]) != ore["active_model"]:
            raise ValueError(f"Client display path mismatch for {ore['ore']}")
        if copper.dbc_model_path(client_dbc, ore["depleted_display"]) != ore["depleted_model"]:
            raise ValueError(f"Client depleted display path mismatch for {ore['ore']}")
    old_vmap = targets[3][0].read_bytes()
    new_vmap = vmap_package.read_bytes()
    if new_vmap != old_vmap and not new_vmap.startswith(old_vmap):
        raise ValueError("Prepared collision index does not preserve existing records")
    vmap_records = copper.parse_gameobject_model_index(new_vmap)
    expected_display_ids = {entry[key] for entry in manifest["ores"]
                            for key in ("active_display", "depleted_display")}
    if not expected_display_ids.issubset(vmap_records):
        raise ValueError("One or more server collision aliases are missing")
    for record in manifest["ores"]:
        source = vmap_records[record["collision_display_source"]]
        for did in (record["active_display"], record["depleted_display"]):
            if vmap_records[did]["record"][4:] != source["record"][4:]:
                raise ValueError("A collision alias differs from its original model geometry")

    staged_dir = BACKUPS / ("WarscapeMiningExpansion-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    staged_dir.mkdir(parents=True, exist_ok=False)
    prepared = staged_dir / "prepared"
    prepared.mkdir()
    archive(prepared / "patch-Z.MPQ", merged_assets)
    shutil.copy2(locale_package, prepared / "patch-enUS-Z.MPQ")
    shutil.copy2(server_dbc_package, prepared / "GameObjectDisplayInfo.dbc")
    shutil.copy2(vmap_package, prepared / "GameObjectModels.dtree")
    shutil.copy2(RELEASE_EXE, prepared / "worldserver.exe")

    readback = archive_entries(prepared / "patch-Z.MPQ")
    if any(readback.get(k) != v for k, v in merged_assets.items()):
        raise ValueError("Prepared client MPQ failed readback")
    old_hashes, new_hashes, backups = {}, {}, {}
    for target, source in targets:
        backup = staged_dir / (target.name + ".before")
        shutil.copy2(target, backup)
        if digest(backup) != digest(target):
            raise ValueError(f"Backup checksum mismatch: {target.name}")
        staged = prepared / target.name
        if digest(staged) != digest(source) and source != runtime:
            raise ValueError(f"Prepared file differs from source: {target.name}")
        old_hashes[str(target)] = digest(target)
        new_hashes[str(target)] = digest(staged)
        backups[str(target)] = str(backup)
    (staged_dir / "deployment.json").write_text(json.dumps({"backup_dir": str(staged_dir),
        "old_sha256": old_hashes, "new_sha256": new_hashes, "backups": backups,
        "client_game_directory": str(CLIENT), "server_directory": str(SERVER),
        "database_changes": False}, indent=2) + "\n", encoding="utf-8")

    written = []
    try:
        for target, _source in targets:
            staged = prepared / target.name
            temporary = target.with_name(target.name + ".warscape-pending")
            if temporary.exists():
                raise ValueError(f"Stale staging file exists: {temporary.name}")
            shutil.copy2(staged, temporary)
            if digest(temporary) != new_hashes[str(target)]:
                raise ValueError(f"Staged checksum mismatch: {target.name}")
            os.replace(temporary, target)
            written.append(target)
            if digest(target) != new_hashes[str(target)]:
                raise ValueError(f"Deployment checksum mismatch: {target.name}")
    except BaseException:
        for target in reversed(written):
            shutil.copy2(backups[str(target)], target)
        raise

    print(json.dumps({"deployed": [str(p) for p in written], "backup_dir": str(staged_dir),
                      "client_game_directory": str(CLIENT), "release_exe_sha256": digest(SERVER / "worldserver.exe"),
                      "source_release_exe_sha256": digest(RELEASE_EXE),
                      "ore_count": len(manifest["ores"]), "database_changes": False}, indent=2))


if __name__ == "__main__":
    main()
