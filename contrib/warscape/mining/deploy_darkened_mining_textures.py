#!/usr/bin/env python3
"""Safely merge only validated darkened depleted-ore BLPs into patch-Z.MPQ."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
CLIENT_DATA = Path(r"C:\WoWDev\wowdecomp\bin\Win\Data")
BACKUPS = Path(r"C:\WoWDev\Backups")
PACKAGE = Path(r"C:\WoWDev\Backups\WarscapeMiningDarkenedTextures-20261031-validated-v2")
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
from deploy_sandbox import archive_entries  # noqa: E402
from generate import archive  # noqa: E402


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    package_mpq = PACKAGE / "patch-WarscapeMiningDarkened.MPQ"
    manifest_path = PACKAGE / "manifest.json"
    target = CLIENT_DATA / "patch-Z.MPQ"
    if not package_mpq.is_file() or not manifest_path.is_file() or not target.is_file():
        raise ValueError("A required Mining texture package or client archive is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    updates = archive_entries(package_mpq)
    changed_paths = {item["path"].lower() for item in manifest["textures"] if item.get("changed")}
    if (manifest.get("texture_count") != 72 or manifest.get("changed_texture_count") != len(updates) or
            {p.lower() for p in updates} != changed_paths or manifest.get("brightness_multiplier") != 0.4):
        raise ValueError("Darkened texture package does not match the reviewed 72-texture scope")
    if len(changed_paths) >= 72:
        raise ValueError("Expected already-black neutral glow textures to remain unchanged")
    processes = subprocess.run(["powershell", "-NoProfile", "-Command",
        "@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, check=True)
    if processes.stdout.strip() != "0":
        raise ValueError("Client and servers must be stopped before asset deployment")

    old_entries = archive_entries(target)
    merged = dict(old_entries)
    seen_keys = {}
    for key in old_entries:
        seen_keys.setdefault(key.lower(), key)
    for item in manifest["textures"]:
        key = item["path"]
        current_key = seen_keys.get(key.lower())
        if current_key is None:
            raise ValueError(f"Refusing to add an unreferenced depleted texture: {key}")
        if digest(old_entries[current_key]) != item["source_sha256"]:
            raise ValueError(f"Depleted texture changed since package validation: {key}")
        if item.get("changed"):
            merged[current_key] = updates[key]
        elif item["darkened_sha256"] != item["source_sha256"]:
            raise ValueError(f"Unchanged texture is not byte-identical: {key}")
    if set(merged) != set(old_entries):
        raise ValueError("Deployment attempted to add or remove unrelated MPQ entries")

    backup_dir = BACKUPS / ("WarscapeDarkenedMiningTextures-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / target.name
    shutil.copy2(target, backup)
    old_hash = digest(target.read_bytes())
    if digest(backup.read_bytes()) != old_hash:
        raise ValueError("Fresh client MPQ backup checksum verification failed")
    prepared = backup_dir / "prepared-patch-Z.MPQ"
    archive(prepared, merged)
    readback = archive_entries(prepared)
    if readback != merged:
        raise ValueError("Prepared MPQ readback differs from the merged archive")
    for key, old_payload in old_entries.items():
        if key not in updates and readback[key] != old_payload:
            raise ValueError(f"Unrelated client asset changed: {key}")
    staged = target.with_name(target.name + ".warscape-pending")
    if staged.exists():
        raise ValueError(f"Stale staging archive exists: {staged.name}")
    shutil.copy2(prepared, staged)
    staged_hash = digest(staged.read_bytes())
    os.replace(staged, target)
    deployed_hash = digest(target.read_bytes())
    if deployed_hash != staged_hash:
        shutil.copy2(backup, target)
        raise ValueError("Deployed MPQ checksum mismatch; original restored")
    (backup_dir / "deployment.json").write_text(json.dumps({
        "target": str(target), "backup": str(backup), "old_sha256": old_hash,
        "new_sha256": deployed_hash, "texture_count": manifest["texture_count"],
        "changed_texture_count": len(updates),
        "brightness_multiplier": 0.4, "unrelated_entries_preserved": True,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"target": str(target), "backup_dir": str(backup_dir),
        "old_sha256": old_hash, "new_sha256": deployed_hash,
        "texture_count": manifest["texture_count"], "changed_texture_count": len(updates),
        "unrelated_entries_preserved": True}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError) as exc:
        print(f"Darkened Mining texture deployment failed: {exc}", file=sys.stderr)
        sys.exit(1)
