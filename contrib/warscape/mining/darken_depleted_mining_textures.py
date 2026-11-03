#!/usr/bin/env python3
"""Prepare a 40%-brightness update for all deployed depleted Mining textures."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
CLIENT_DATA = Path(r"C:\WoWDev\wowdecomp\bin\Win\Data")
STANDARD_MANIFEST = Path(r"C:\WoWDev\Backups\WarscapeMiningExpansionAssets-20261031-StageB-m2-path-fix\manifest.json")
COPPER_MODULE = ROOT / "contrib/warscape/mining/copper_depletion_assets.py"
sys.path.insert(0, str(ROOT / "contrib/warscape/mining"))
import copper_depletion_assets as copper  # noqa: E402
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
from deploy_sandbox import archive_entries  # noqa: E402
from generate import archive  # noqa: E402

BRIGHTNESS = 0.4


def texture_groups():
    standard = json.loads(STANDARD_MANIFEST.read_text(encoding="utf-8"))
    return {"Copper": sorted({target for _source, target, _neutralized in copper.TEXTURES}),
            **{ore["ore"]: sorted({texture["target"] for texture in ore["textures"]})
               for ore in standard["ores"]}}


def build(output):
    output = Path(output).resolve()
    if output.exists() or output.is_relative_to(ROOT) or output.is_relative_to(CLIENT_DATA):
        raise ValueError("Output must be a new directory outside source and client trees")
    source_patch = CLIENT_DATA / "patch-Z.MPQ"
    source_assets = archive_entries(source_patch)
    changed = {}
    details = []
    groups = texture_groups()
    if len(groups) != 15:
        raise ValueError("Expected Copper and fourteen standard Mining ore texture groups")
    for ore, paths in groups.items():
        for path in paths:
            key = next((name for name in source_assets if name.lower() == path.lower()), None)
            if key is None:
                raise ValueError(f"Depleted Mining texture is missing from the client archive: {path}")
            before = source_assets[key]
            copper.validate_grayscale_blp(before)
            after = copper.darken_grayscale_blp(before, BRIGHTNESS)
            if before[:1172] != after[:1172]:
                raise ValueError(f"Darkening unexpectedly changed the BLP header: {path}")
            is_changed = before != after
            if is_changed:
                changed[key] = after
            details.append({"ore": ore, "path": key, "source_sha256": hashlib.sha256(before).hexdigest(),
                            "darkened_sha256": hashlib.sha256(after).hexdigest(), "changed": is_changed})
    if len(details) != 72:
        raise ValueError(f"Expected 72 Copper and standard ore depleted textures, found {len(details)}")
    output.mkdir(parents=True, exist_ok=False)
    archive(output / "patch-WarscapeMiningDarkened.MPQ", changed)
    if archive_entries(output / "patch-WarscapeMiningDarkened.MPQ") != changed:
        raise ValueError("Prepared darkened-texture MPQ failed readback")
    manifest = {"brightness_multiplier": BRIGHTNESS, "brightness_reduction_percent": 60,
                "ore_groups": groups,
                "texture_count": len(details), "changed_texture_count": len(changed), "textures": details}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"package": str(output), "textures": len(changed),
                      "brightness_multiplier": BRIGHTNESS}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    build(parser.parse_args().output)
