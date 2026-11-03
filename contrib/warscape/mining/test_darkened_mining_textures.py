import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
import copper_depletion_assets as copper
from deploy_sandbox import archive_entries

PACKAGE = Path(os.environ.get("WARSCAPE_DARKENED_TEXTURE_PACKAGE",
    r"C:\WoWDev\Backups\WarscapeMiningDarkenedTextures-20261031-validated-v2"))
SOURCE_MPQ = Path(os.environ.get("WARSCAPE_DARKENED_SOURCE_MPQ",
    r"C:\WoWDev\wowdecomp\bin\Win\Data\patch-Z.MPQ"))


class DarkenedMiningTexturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
        cls.before = archive_entries(SOURCE_MPQ)
        cls.after = archive_entries(PACKAGE / "patch-WarscapeMiningDarkened.MPQ")

    def test_all_fifteen_ores_and_seventy_two_textures_are_in_scope(self):
        self.assertEqual(len(self.manifest["ore_groups"]), 15)
        self.assertIn("Copper", self.manifest["ore_groups"])
        self.assertEqual(self.manifest["texture_count"], 72)
        self.assertEqual(len(self.manifest["textures"]), 72)
        changed = {item["path"] for item in self.manifest["textures"] if item["changed"]}
        self.assertEqual(self.manifest["changed_texture_count"], len(changed))
        self.assertEqual(set(self.after), changed)
        for ore, paths in self.manifest["ore_groups"].items():
            self.assertTrue(paths, f"{ore} has no depleted textures")
            self.assertTrue(all(next(item for item in self.manifest["textures"]
                                     if item["path"] == path)["ore"] == ore for path in paths))

    def test_each_mip_is_grayscale_darker_by_sixty_percent_and_alpha_is_unchanged(self):
        self.assertEqual(self.manifest["brightness_multiplier"], 0.4)
        for item in self.manifest["textures"]:
            path = item["path"]
            before = self.before[path]
            after = self.after.get(path, before)
            self.assertEqual(hashlib.sha256(before).hexdigest(), item["source_sha256"], path)
            self.assertEqual(hashlib.sha256(after).hexdigest(), item["darkened_sha256"], path)
            self.assertEqual(item["changed"], before != after, path)
            self.assertEqual(before[:1172], after[:1172], path)
            copper.validate_grayscale_blp(before)
            copper.validate_grayscale_blp(after)
            width, height = struct.unpack_from("<II", before, 12)
            levels = max(width, height).bit_length() if before[11] & 1 else 1
            offsets = struct.unpack_from("<16I", before, 20)
            sizes = struct.unpack_from("<16I", before, 84)
            for level in range(levels):
                offset, size = offsets[level], sizes[level]
                after_offset = struct.unpack_from("<I", after, 20 + level * 4)[0]
                after_size = struct.unpack_from("<I", after, 84 + level * 4)[0]
                self.assertEqual((offset, size), (after_offset, after_size), path)
                old_pixels = before[offset:offset + size]
                new_pixels = after[offset:offset + size]
                self.assertEqual(old_pixels[3::4], new_pixels[3::4], f"alpha changed: {path} mip {level}")
                for index in range(0, size, 4):
                    old = old_pixels[index]
                    expected = min(255, int(old * 0.4 + 0.5))
                    self.assertEqual(new_pixels[index:index + 3], bytes((expected,) * 3),
                                     f"RGB brightness/grayscale mismatch: {path} mip {level}")
                    self.assertEqual(old_pixels[index], old_pixels[index + 1])
                    self.assertEqual(old_pixels[index], old_pixels[index + 2])

    def test_packaged_updates_contain_only_depleted_blp_textures(self):
        self.assertTrue(all(path.lower().endswith(".blp") for path in self.after))
        self.assertTrue(all(path in self.before for path in self.after))
        self.assertTrue(all(self.before[path] != self.after[path] for path in self.after))


if __name__ == "__main__":
    unittest.main()
