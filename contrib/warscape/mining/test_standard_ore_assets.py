import json
import os
from pathlib import Path
import re
import struct
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "contrib/warscape/worldgen"))
import copper_depletion_assets as copper
from deploy_sandbox import archive_entries

PACKAGE = Path(os.environ.get("WARSCAPE_MINING_ASSET_PACKAGE",
    r"C:\WoWDev\Backups\WarscapeMiningExpansionAssets-20261031-StageB-m2-path-fix"))
SOURCE = ROOT / "src/server/scripts/Custom/warscape_copper_mining.cpp"


def m2_without_texture_references(model, original_length):
    data = bytearray(model)
    count, offset = struct.unpack_from("<II", model, 80)
    for index in range(count):
        start = offset + index * 16
        data[start + 8:start + 16] = b"\0" * 8
    return bytes(data[:original_length])


class StandardOreAssetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
        cls.assets = archive_entries(PACKAGE / "patch-WarscapeMining.MPQ")
        cls.locale = archive_entries(PACKAGE / "patch-enUS-WarscapeMining.MPQ")
        cls.client_dbc = cls.locale[next(k for k in cls.locale if k.lower() == copper.DBC_NAME.lower())]
        cls.item_dbc = cls.locale[next(k for k in cls.locale if k.lower() == r"dbfilesclient\item.dbc")]
        cls.server_dbc = (PACKAGE / "GameObjectDisplayInfo.dbc").read_bytes()
        cls.source_assets = copper.Assets(copper.CLIENT)

    @classmethod
    def tearDownClass(cls):
        cls.source_assets.close()

    def test_all_fourteen_models_skins_and_collision_aliases_exist(self):
        self.assertEqual(len(self.manifest["ores"]), 14)
        self.assertFalse(any("warscapemining" in key.lower() and key.lower().endswith(".md2")
                             for key in self.assets))
        cache_source = Path(r"C:\WoWDev\wowdecomp\Engine\Source\Model2\M2Cache.cpp").read_text(encoding="utf-8")
        self.assertIn('strcpy(ext, ".m2")', cache_source)
        for ore in self.manifest["ores"]:
            active = ore["active_model"].rsplit(".", 1)[0] + ".m2"
            depleted = ore["depleted_model"].rsplit(".", 1)[0] + ".m2"
            active_skin = ore["active_model"].rsplit(".", 1)[0] + "00.skin"
            depleted_skin = ore["depleted_model"].rsplit(".", 1)[0] + "00.skin"
            self.assertIn(active, self.assets)
            self.assertIn(depleted, self.assets)
            self.assertIn(active_skin, self.assets)
            self.assertIn(depleted_skin, self.assets)
            self.assertEqual(self.assets[active_skin], self.assets[depleted_skin])
            source = self.source_assets.read(ore["source_model"])
            self.assertEqual(self.assets[active], source)
            copper.validate_skin_profile(self.assets[active_skin], self.assets[active])
            copper.validate_skin_profile(self.assets[depleted_skin], self.assets[depleted])
            self.assertEqual(m2_without_texture_references(self.assets[active], len(self.assets[active])),
                             m2_without_texture_references(self.assets[depleted], len(self.assets[active])))
            self.assertEqual(struct.unpack_from("<I", self.assets[active], 60)[0], ore["vertices"])
            self.assertEqual(struct.unpack_from("<I", self.assets[depleted], 60)[0], ore["vertices"])
            source_id = ore["collision_display_source"]
            alias = copper.parse_gameobject_model_index((PACKAGE / "GameObjectModels.dtree").read_bytes())
            self.assertIn(ore["active_display"], alias)
            self.assertIn(ore["depleted_display"], alias)
            self.assertEqual(alias[ore["active_display"]]["name"], alias[source_id]["name"])
            self.assertEqual(alias[ore["depleted_display"]]["name"], alias[source_id]["name"])
            self.assertTrue((copper.SERVER / "vmaps" / (alias[source_id]["name"] + ".vmo")).is_file())

    def test_display_paths_and_texture_dependencies_resolve(self):
        for ore in self.manifest["ores"]:
            self.assertEqual(copper.dbc_model_path(self.client_dbc, ore["active_display"]), ore["active_model"])
            self.assertEqual(copper.dbc_model_path(self.client_dbc, ore["depleted_display"]), ore["depleted_model"])
            server_path = ore["source_model"].rsplit(".", 1)[0] + ".mdx"
            self.assertEqual(copper.dbc_model_path(self.server_dbc, ore["active_display"]), server_path)
            self.assertEqual(copper.dbc_model_path(self.server_dbc, ore["depleted_display"]), server_path)
            for texture in ore["textures"]:
                self.assertIn(texture["target"], self.assets)
                copper.validate_grayscale_blp(self.assets[texture["target"]], black=texture["glow_neutralized"])

    def test_custom_item_dbc_rows_resolve_to_matching_vanilla_ore_icons(self):
        magic, count, fields, row_size, strings_size = struct.unpack_from("<4s4I", self.item_dbc)
        self.assertEqual((magic, fields, row_size), (b"WDBC", 8, 32))
        self.assertEqual(len(self.item_dbc), 20 + count * row_size + strings_size)
        rows = {}
        for index in range(count):
            row = self.item_dbc[20 + index * row_size:20 + (index + 1) * row_size]
            entry = struct.unpack_from("<I", row)[0]
            self.assertNotIn(entry, rows)
            rows[entry] = row
        source_items = {
            900201: 2771, 900202: 2775, 900203: 2772, 900204: 2776,
            900205: 3858, 900206: 7911, 900207: 11370, 900208: 10620,
            900209: 23424, 900210: 23425, 900211: 23426, 900212: 36909,
            900213: 36912, 900214: 36910,
        }
        for custom_id, vanilla_id in source_items.items():
            self.assertIn(custom_id, rows)
            self.assertIn(vanilla_id, rows)
            self.assertEqual(rows[custom_id][4:], rows[vanilla_id][4:])

    def test_deployed_client_and_server_references_resolve_for_all_ores(self):
        client_root = copper.CLIENT / "Data"
        deployed_models = archive_entries(client_root / "patch-Z.MPQ")
        deployed_locale = archive_entries(client_root / "enUS/patch-enUS-Z.MPQ")
        deployed_client_dbc = deployed_locale[next(k for k in deployed_locale if k.lower() == copper.DBC_NAME.lower())]
        deployed_item_dbc = deployed_locale[next(k for k in deployed_locale if k.lower() == r"dbfilesclient\item.dbc")]
        deployed_server_dbc = (copper.SERVER / "dbc/GameObjectDisplayInfo.dbc").read_bytes()
        collision = copper.parse_gameobject_model_index((copper.SERVER / "vmaps/GameObjectModels.dtree").read_bytes())
        for ore in self.manifest["ores"]:
            active = ore["active_model"].rsplit(".", 1)[0] + ".m2"
            depleted = ore["depleted_model"].rsplit(".", 1)[0] + ".m2"
            for path in (active, depleted,
                         ore["active_model"].rsplit(".", 1)[0] + "00.skin",
                         ore["depleted_model"].rsplit(".", 1)[0] + "00.skin"):
                self.assertIn(path.lower(), {key.lower() for key in deployed_models})
            self.assertEqual(copper.dbc_model_path(deployed_client_dbc, ore["active_display"]), ore["active_model"])
            self.assertEqual(copper.dbc_model_path(deployed_client_dbc, ore["depleted_display"]), ore["depleted_model"])
            server_model = ore["source_model"].rsplit(".", 1)[0] + ".mdx"
            self.assertEqual(copper.dbc_model_path(deployed_server_dbc, ore["active_display"]), server_model)
            self.assertEqual(copper.dbc_model_path(deployed_server_dbc, ore["depleted_display"]), server_model)
            self.assertIn(ore["active_display"], collision)
            self.assertIn(ore["depleted_display"], collision)
        self.assertTrue(any(k.lower() == r"dbfilesclient\item.dbc" for k in deployed_locale))
        self.assertEqual(struct.unpack_from("<I", deployed_item_dbc, 4)[0],
                         struct.unpack_from("<I", (copper.SERVER / "dbc/Item.dbc").read_bytes(), 4)[0] + 14)

    def test_ore_configuration_ids_and_level_one_chance(self):
        source = SOURCE.read_text(encoding="utf-8")
        rows = re.findall(r'^\s*\{(900\d+),\s*(900\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*"([^"]+)",\s*"([^"]+)",\s*(\d+),\s*(\d+),\s*(\d+),\s*(true|false)\}', source, re.M)
        self.assertEqual(len(rows), 15)
        ids = set()
        config_by_name = {}
        for active, depleted, _active_display, depleted_display, item, script_name, name, xp_half, low, high, provisional in rows:
            self.assertGreater(int(low), 0)
            self.assertGreaterEqual(int(high), 0)
            self.assertGreater(int(xp_half), 0)
            self.assertNotEqual(active, depleted)
            self.assertNotIn(active, ids)
            self.assertNotIn(depleted, ids)
            ids.update((active, depleted))
            self.assertTrue(script_name.startswith("go_warscape_"))
            self.assertIn(f'"{name}"', source)
            config_by_name[name] = (int(active), int(depleted), int(_active_display),
                                    int(depleted_display), int(item), int(xp_half), int(low), int(high))
        self.assertIn("requiredLevel = 1", source)
        self.assertIn("MiningSuccessOutOf256", source)
        self.assertIn("StoreNewItem(destination, _config.itemEntry, true)", source)
        self.assertEqual(source.count("StoreNewItem(destination, _config.itemEntry, true)"), 1)
        self.assertIn("AddRSSkillHalfXP(Player::RS_Skill::Mining, _config.xpHalfPoints)", source)
        self.assertIn("DepletionDurationMs = 9000", source)
        self.assertIn("uint32 _depletionTimer", source)
        self.assertIn("ShowDepletedAppearance()", source)
        self.assertIn("RestoreActiveAppearance()", source)
        self.assertIn("EnsureDepletedCounterpart()", source)
        plan = (ROOT / "doc/WarscapeMiningExpansionPlan.md").read_text(encoding="utf-8")
        plan_rows = re.findall(r'^\| ([A-Za-z ]+) \| (900\d+) \| (900\d+) \| (900\d+) \| (900\d+) \| (900\d+) — Warscape .*? \|$', plan, re.M)
        self.assertEqual(len(plan_rows), 14)
        migration = (ROOT / "contrib/warscape/migrations/pending/2026_10_31_00_world.sql").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "sql/updates/world/3.3.5/2026_10_31_00_world.sql").exists())
        source_items = {"Tin": 2771, "Silver": 2775, "Iron": 2772, "Gold": 2776,
                        "Mithril": 3858, "Truesilver": 7911, "Dark Iron": 11370,
                        "Thorium": 10620, "Fel Iron": 23424, "Adamantite": 23425,
                        "Khorium": 23426, "Cobalt": 36909, "Saronite": 36912, "Titanium": 36910}
        for name, active, depleted, active_display, depleted_display, item in plan_rows:
            config = config_by_name[name]
            self.assertEqual(config[:5], tuple(map(int, (active, depleted, active_display, depleted_display, item))))
            self.assertIn(f"VALUES ({active}, 3, {active_display}, 'Warscape {name} Rock'", migration)
            self.assertIn(f"VALUES ({depleted}, 5, {depleted_display}, 'Warscape Depleted {name} Rock'", migration)
            self.assertRegex(migration, rf"INSERT INTO `item_template` .*? SELECT {item}, .*? 'Warscape {name} Ore'.*? FROM `item_template` WHERE `entry` = {source_items[name]};")


if __name__ == "__main__":
    unittest.main()
