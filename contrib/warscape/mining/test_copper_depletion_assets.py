import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "contrib" / "warscape" / "mining"))
sys.path.insert(0, str(ROOT / "contrib" / "warscape" / "worldgen"))

import copper_depletion_assets as copper
from briarbrook import Assets


class CopperDepletionAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = Assets(copper.CLIENT)

    @classmethod
    def tearDownClass(cls):
        cls.assets.close()

    def test_every_source_texture_mip_is_grayscale_and_alpha_preserved(self):
        for source_path, target_path, disable_glow in copper.TEXTURES:
            with self.subTest(source=source_path):
                source = self.assets.read(source_path)
                generated, images = copper.grayscale_blp(source, disable_glow)
                self.assertEqual(generated[:4], b"BLP2")
                self.assertEqual(generated[8], 3)
                original_mips, _ = copper.decode_blp_mips(source)
                count = len(images)
                offsets = struct.unpack_from("<16I", generated, 20)
                sizes = struct.unpack_from("<16I", generated, 84)
                for level in range(count):
                    pixels = memoryview(generated)[offsets[level]:offsets[level] + sizes[level]]
                    original_alpha = original_mips[level].getchannel("A").tobytes()
                    self.assertEqual(bytes(pixels[3::4]), original_alpha)
                    self.assertTrue(all(pixels[i] == pixels[i + 1] == pixels[i + 2]
                                        for i in range(0, len(pixels), 4)))
                    if disable_glow:
                        self.assertTrue(all(pixels[i] == pixels[i + 1] == pixels[i + 2] == 0
                                            for i in range(0, len(pixels), 4)))

    def test_custom_model_changes_only_texture_filename_references(self):
        original = self.assets.read(copper.SOURCE_MODEL)
        replacement_map = {source: target for source, target, _ in copper.TEXTURES}
        modified = copper.rewrite_model(original, replacement_map)
        texture_count, texture_offset = struct.unpack_from("<II", original, 80)
        texture_ranges = set()
        for index in range(texture_count):
            record = texture_offset + index * 16
            texture_type, _, old_length, old_offset = struct.unpack_from("<4I", original, record)
            old_name = original[old_offset:old_offset + old_length].split(b"\0")[0].decode("ascii")
            self.assertIn(old_name, replacement_map)
            texture_ranges.update(range(record + 8, record + 16))
            _, _, length, offset = struct.unpack_from("<4I", modified, record)
            self.assertGreater(length, 1)
            self.assertEqual(modified[offset:offset + length].rstrip(b"\0").decode("ascii"),
                             replacement_map[old_name])
            self.assertEqual(struct.unpack_from("<I", modified, record)[0], texture_type)
        for index, value in enumerate(original):
            if index not in texture_ranges:
                self.assertEqual(modified[index], value, f"unexpected M2 modification at {index}")
        self.assertTrue(modified.startswith(original[:texture_offset]))
        self.assertEqual(modified[:112], original[:112])
        material_count, material_offset = struct.unpack_from("<II", original, 112)
        self.assertGreater(material_count, 0)
        self.assertEqual(modified[material_offset:material_offset + material_count * 4],
                         original[material_offset:material_offset + material_count * 4])

    def test_both_custom_model_names_have_valid_matching_skin_profiles(self):
        original = self.assets.read(copper.SOURCE_MODEL)
        skin = self.assets.read(copper.SOURCE_SKIN)
        profile_count = struct.unpack_from("<I", original, 68)[0]
        self.assertEqual(profile_count, 1)
        self.assertEqual(copper.validate_skin_profile(skin, original)["sections"], 3)
        custom_model = copper.rewrite_model(
            original, {source: target for source, target, _ in copper.TEXTURES})
        self.assertEqual(copper.validate_skin_profile(skin, custom_model)["sections"], 3)
        self.assertEqual(copper.skin_profile_path(copper.PATH_TEST_MODEL, 0), copper.PATH_TEST_SKIN)
        self.assertEqual(copper.skin_profile_path(copper.CLIENT_MODEL, 0), copper.CLIENT_SKIN)
        self.assertEqual(copper.SOURCE_SKIN.rsplit("\\", 1)[-1], "copper_Miningnode_0100.skin")

    def test_collision_alias_reuses_display_310_record_without_modifying_it(self):
        name = b"World\\SkillActivated\\TradeskillNodes\\copper_Miningnode_01.m2.vmo"
        source = (b"VMAP_4.8" + struct.pack("<IBI", copper.SOURCE_DISPLAY_ID, 0, len(name)) +
                  name + struct.pack("<6f", -2, -2, -1, 2, 2, 3))
        updated = copper.append_gameobject_model_alias(source)
        records = copper.parse_gameobject_model_index(updated)
        self.assertEqual(records[copper.SOURCE_DISPLAY_ID]["record"],
                         copper.parse_gameobject_model_index(source)[copper.SOURCE_DISPLAY_ID]["record"])
        self.assertEqual(records[copper.DISPLAY_ID]["record"],
                         struct.pack("<I", copper.DISPLAY_ID) +
                         records[copper.SOURCE_DISPLAY_ID]["record"][4:])
        self.assertEqual(copper.append_gameobject_model_alias(updated), updated)

    def test_display_dbc_adds_custom_visual_but_keeps_server_collision_model(self):
        client_base = self.assets.read(copper.DBC_NAME)
        # The live server DBC includes the runtime display row after deployment;
        # exercise the append logic from the unchanged client base snapshot.
        server_base = client_base
        client_new = copper.append_display_record(client_base, copper.DISPLAY_ID, copper.CLIENT_MODEL)
        server_path = copper.SOURCE_MODEL[:-2] + "mdx"
        server_new = copper.append_display_record(server_base, copper.DISPLAY_ID, server_path)
        copper._assert_append(client_base, client_new)
        copper._assert_append(server_base, server_new)
        _, base_count, _, row_size, _ = struct.unpack_from("<4s4I", client_base)
        source_row = next(client_base[20 + i * row_size:20 + (i + 1) * row_size]
                          for i in range(base_count)
                          if struct.unpack_from("<I", client_base, 20 + i * row_size)[0] == copper.SOURCE_DISPLAY_ID)
        new_client_row = client_new[20 + base_count * row_size:20 + (base_count + 1) * row_size]
        new_server_row = server_new[20 + base_count * row_size:20 + (base_count + 1) * row_size]
        self.assertEqual(new_client_row[8:], source_row[8:])
        self.assertEqual(new_server_row[8:], source_row[8:])
        self.assertEqual(struct.unpack_from("<I", new_client_row)[0], copper.DISPLAY_ID)


if __name__ == "__main__":
    unittest.main()
