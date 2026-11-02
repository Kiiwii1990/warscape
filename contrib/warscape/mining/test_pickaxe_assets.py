"""Focused offline integration checks against the staged, real-client assets."""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import unittest

import build_pickaxe_assets as pick

PACKAGE = Path(os.environ.get('WARSCAPE_PICKAXE_ASSETS',
    r'C:\WoWDev\Artifacts\WarscapePickaxes-20261101-001\assets-002'))


class PickaxeAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = pick.ClientAssets(pick.CLIENT)
        cls.root = pick.archive_entries(PACKAGE / 'patch-WarscapePickaxes.MPQ')
        cls.locale = pick.archive_entries(PACKAGE / 'patch-enUS-WarscapePickaxes.MPQ')
        cls.source = (pick.ROOT / 'src/server/scripts/Custom/warscape_copper_mining.cpp').read_text()

    @classmethod
    def tearDownClass(cls):
        for _, opened in cls.assets.archives:
            opened.file.close()

    def test_unique_displays_icons_and_replaceable_hand_textures(self):
        items, _ = pick.dbc(self.locale[r'DBFilesClient\Item.dbc'], 8)
        self.assertTrue(set(range(900201, 900215)).issubset(items))
        displays, strings = pick.dbc(self.locale[r'DBFilesClient\ItemDisplayInfo.dbc'], 25)
        for entry, tier in pick.TIERS:
            self.assertEqual(items[entry][5], entry)
            display = displays[entry]
            self.assertEqual(pick.string(strings, display[1]), 'Axe_1H_Pick_A_01.mdx')
            texture = pick.WEAPON + pick.string(strings, display[3]) + '.blp'
            icon = 'Interface\\Icons\\' + pick.string(strings, display[5]) + '.blp'
            self.assertIn(texture, self.root)
            self.assertIn(icon, self.root)
            self.assertEqual(items[entry][1:5], items[2901][1:5])
            self.assertEqual(items[entry][6:], items[2901][6:])
            self.assertEqual(display[7:], displays[6568][7:])
        model = self.assets.get(pick.MODEL)[0]
        self.assertGreater(pick.validate_skin_profile(self.assets.get(pick.SKIN)[0], model)['sections'], 0)
        count, offset = struct.unpack_from('<II', model, 80)
        self.assertIn(2, [struct.unpack_from('<I', model, offset + i*16)[0] for i in range(count)])
        manifest = json.loads((PACKAGE / 'manifest.json').read_text())
        for path in manifest['dependencies']:
            self.assertTrue(self.assets.get(path)[0])

    def test_all_mips_preserve_alpha_and_unmasked_wood_and_outline(self):
        for original, is_icon in ((pick.ICON, True), (pick.DIFFUSE, False)):
            source, _ = pick.decode(self.assets.get(original)[0])
            seen = set()
            for _, tier in pick.TIERS:
                name = (f'Interface\\Icons\\INV_Warscape_Pickaxe_{tier}.blp' if is_icon else
                        pick.WEAPON + f'WarscapePickaxe{tier}.blp')
                payload = self.root[name]
                self.assertNotIn(pick.sha(payload), seen)
                seen.add(pick.sha(payload))
                result, _ = pick.decode(payload)
                self.assertEqual(len(result), len(source))
                for a, b in zip(result, source):
                    self.assertEqual(a.size, b.size)
                    self.assertEqual(a.getchannel('A').tobytes(), b.getchannel('A').tobytes())
                mask = pick.metal_mask(source[0], is_icon)
                for xy in ((x,y) for y in range(mask.height) for x in range(mask.width)):
                    if not mask.getpixel(xy):
                        self.assertEqual(result[0].getpixel(xy), source[0].getpixel(xy))

    def test_every_tier_recolors_the_head_socket_in_icon_and_model_texture(self):
        for original, is_icon, socket_bounds in (
                (pick.ICON, True, (32, 25, 41, 35)),
                (pick.DIFFUSE, False, (50, 34, 62, 53))):
            source = pick.decode(self.assets.get(original)[0])[0][0]
            left, top, right, bottom = socket_bounds
            for _, tier in pick.TIERS:
                name = (f'Interface\\Icons\\INV_Warscape_Pickaxe_{tier}.blp' if is_icon else
                        pick.WEAPON + f'WarscapePickaxe{tier}.blp')
                result = pick.decode(self.root[name])[0][0]
                changed = sum(source.getpixel((x, y)) != result.getpixel((x, y))
                              for y in range(top, bottom) for x in range(left, right))
                self.assertGreater(changed, 0, f'{tier} socket was not recolored in {name}')

    def test_all_existing_dbc_rows_and_strings_unchanged(self):
        for name, fields in (('Item',8), ('ItemDisplayInfo',25)):
            for prefix in ('', 'server-'):
                old = (self.assets.get(f'DBFilesClient\\{name}.dbc')[0] if not prefix else
                       (pick.SERVER / 'dbc' / f'{name}.dbc').read_bytes())
                previous, oldstrings = pick.dbc(old, fields)
                current, strings = pick.dbc((PACKAGE / f'{prefix}{name}.dbc').read_bytes(), fields)
                self.assertEqual(len(current), len(previous) + 3)
                self.assertTrue(strings.startswith(oldstrings))
                self.assertEqual({key:current[key] for key in previous}, previous)
        self.assertNotIn(pick.ICON, self.root)
        self.assertNotIn(pick.DIFFUSE, self.root)
        self.assertNotIn(pick.MODEL, self.root)

    def test_merged_archives_preserve_unrelated_assets(self):
        for original, staged, update in ((pick.CLIENT / 'Data/patch-Z.MPQ', PACKAGE / 'patch-Z.MPQ', self.root),
            (pick.CLIENT / 'Data/enUS/patch-enUS-Z.MPQ', PACKAGE / 'patch-enUS-Z.MPQ', self.locale)):
            before, after = pick.archive_entries(original), pick.archive_entries(staged)
            changed = {name.lower() for name in update}
            for name, payload in before.items():
                if name.lower() not in changed:
                    self.assertEqual(hashlib.sha256(after[name]).digest(), hashlib.sha256(payload).digest())

    def test_shared_15_ore_engine_has_inventory_selection_and_native_visual_restore(self):
        expected = [('Copper',35,100,350),('Tin',35,100,350),('Silver',80,25,200),
                    ('Iron',70,96,350),('Gold',130,7,75),('Mithril',160,4,50),
                    ('Truesilver',80,18,180),('Dark Iron',180,24,200),('Thorium',200,20,190),
                    ('Fel Iron',180,28,220),('Adamantite',190,3,25),('Khorium',240,30,230),
                    ('Cobalt',160,32,220),('Saronite',200,24,200),('Titanium',250,15,170)]
        found = re.findall(r'"go_warscape_[^"]+", "([^"]+)", (\d+), (\d+), (\d+), (?:true|false)', self.source)
        self.assertEqual([(name,int(xp),int(low),int(high)) for name,xp,low,high in found], expected)
        self.assertIn('Warscape::SelectMiningPickaxe(player->GetRSSkillLevel(Player::RS_Skill::Mining)', self.source)
        self.assertIn('return player->GetItemByEntry(entry) != nullptr;', self.source)
        self.assertIn('GetItemByEntry(_selectedPickaxe->ItemEntry)', self.source)
        self.assertIn('SetVisibleItemSlot(MainHandEquipmentSlot, pick)', self.source)
        self.assertIn('player->GetItemByPos(INVENTORY_SLOT_BAG_0, MainHandEquipmentSlot)', self.source)
        self.assertNotIn('EquipItem(', self.source)
        self.assertIn('DepletionDurationMs = 9000', self.source)
        self.assertIn('MiningRockScale = 0.5f', self.source)
        self.assertEqual(self.source.count('StoreNewItem(destination, _config.itemEntry, true)'), 1)
        self.assertIn('player->GetRSSkillLevel(Player::RS_Skill::Mining),\n                _config.low, _config.high', self.source)

    def test_asset_rejects_reused_ids_and_bad_binary_ranges(self):
        data = (PACKAGE / 'Item.dbc').read_bytes()
        with self.assertRaises(ValueError):
            pick.append_dbc(data, 8, 2901)
        with self.assertRaises(ValueError):
            pick.dbc(data[:-1], 8)
        damaged = bytearray(next(iter(self.root.values())))
        struct.pack_into('<I', damaged, 20, len(damaged) + 4)
        with self.assertRaises(ValueError):
            pick.decode(damaged)


if __name__ == '__main__':
    unittest.main()
