"""Regression checks for the permanent one-tile Warscape dev sandbox."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

import mpyq

import build
import deploy_sandbox
import generate


CONFIG_PATH = Path(__file__).with_name('warscape-dev-sandbox.json')


def chunks(data):
    position = 0
    while position + 8 <= len(data):
        tag = data[position:position + 4][::-1].decode('ascii')
        size = struct.unpack_from('<I', data, position + 4)[0]
        if size > len(data) - position - 8:
            raise ValueError(f'{tag} chunk exceeds file bounds')
        yield tag, position, size
        position += size + 8
    if position != len(data):
        raise ValueError('Trailing bytes after final ADT/WDT chunk')


def make_base_map_dbc():
    row = bytearray(264)
    return struct.pack('<4s4I', b'WDBC', 1, 66, 264, 1) + row + b'\0'


class DevelopmentSandboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(CONFIG_PATH.read_text(encoding='utf-8-sig'))

    def test_config_is_one_empty_flat_grass_tile(self):
        cfg = self.cfg
        self.assertEqual((cfg['map_id'], cfg['directory']), (904, 'WarscapeDevSandbox'))
        self.assertEqual(cfg['tiles'], [[32, 32]])
        self.assertEqual(cfg['height'], 30.0)
        self.assertEqual(cfg['texture'], r'Tileset\Elwynn\ElwynnGrassBase.blp')
        self.assertEqual(cfg['placements'], [])
        for field in ('river', 'roads', 'terrain_mode', 'terrain_profile', 'placement_regions', 'placement_runs'):
            self.assertNotIn(field, cfg)

    def test_generated_wdt_advertises_exactly_the_single_tile(self):
        data = generate.wdt(self.cfg['tiles'])
        found = {tag: (offset, size) for tag, offset, size in chunks(data)}
        self.assertEqual(set(found), {'MVER', 'MPHD', 'MAIN', 'MWMO'})
        mphd = found['MPHD'][0] + 8
        self.assertEqual(struct.unpack_from('<I', data, mphd)[0], 0)
        main = found['MAIN'][0] + 8
        tiles = {(i % 64, i // 64) for i in range(4096)
                 if struct.unpack_from('<I', data, main + i * 8)[0]}
        self.assertEqual(tiles, {(32, 32)})
        self.assertEqual(found['MWMO'][1], 0)

    def test_adt_has_only_level_ground_grass_and_no_liquid_or_objects(self):
        texture = self.cfg['texture']
        data = generate.adt(32, 32, self.cfg['height'], texture)
        top = {tag: (offset, size) for tag, offset, size in chunks(data)}
        self.assertEqual(data[top['MTEX'][0] + 8:top['MTEX'][0] + 8 + top['MTEX'][1]],
                         texture.encode() + b'\0')
        for tag in ('MMDX', 'MWMO', 'MDDF', 'MODF'):
            self.assertEqual(top[tag][1], 0, tag)

        mcin = top['MCIN'][0] + 8
        self.assertEqual(top['MCIN'][1], 256 * 16)
        self.assertFalse(any(tag == 'MCLQ' for tag, _, _ in chunks(data)))
        for index in range(256):
            offset, size, _, _ = struct.unpack_from('<4I', data, mcin + index * 16)
            self.assertEqual(data[offset:offset + 4], b'KNCM')
            self.assertEqual(struct.unpack_from('<I', data, offset + 4)[0] + 8, size)
            header = offset + 8
            flags, layer_count, base_z = (struct.unpack_from('<I', data, header)[0],
                                          struct.unpack_from('<I', data, header + 12)[0],
                                          struct.unpack_from('<f', data, header + 112)[0])
            self.assertEqual(flags, 0)
            self.assertEqual(layer_count, 1)
            self.assertAlmostEqual(base_z, self.cfg['height'])

            height_offset = struct.unpack_from('<I', data, header + 20)[0]
            height_chunk = offset + height_offset
            self.assertEqual(data[height_chunk:height_chunk + 4], b'TVCM')
            self.assertEqual(struct.unpack_from('<I', data, height_chunk + 4)[0], 145 * 4)
            self.assertEqual(data[height_chunk + 8:height_chunk + 8 + 145 * 4], bytes(145 * 4))

            normal_offset = struct.unpack_from('<I', data, header + 24)[0]
            normal_chunk = offset + normal_offset
            normals = data[normal_chunk + 8:normal_chunk + 8 + 145 * 3]
            self.assertEqual(normals, bytes([0, 0, 127]) * 145)

            layer_offset = struct.unpack_from('<I', data, header + 28)[0]
            layer_chunk = offset + layer_offset
            self.assertEqual(data[layer_chunk:layer_chunk + 4], b'YLCM')
            self.assertEqual(struct.unpack_from('<I', data, layer_chunk + 4)[0], 16)
            self.assertEqual(struct.unpack_from('<4I', data, layer_chunk + 8), (0, 0, 0, 0))
            alpha_offset, alpha_size = struct.unpack_from('<2I', data, header + 36)
            alpha_chunk = offset + alpha_offset
            self.assertEqual((data[alpha_chunk:alpha_chunk + 4], alpha_size), (b'LACM', 8))
            self.assertEqual(struct.unpack_from('<I', data, alpha_chunk + 4)[0], 0)
            self.assertEqual(struct.unpack_from('<2I', data, header + 96), (0, 0))

    def test_map_dbc_registers_sandbox_without_rewriting_existing_rows(self):
        original = make_base_map_dbc()
        server_string = b'\0Warscape903\0Existing map\0'
        existing = bytearray(264)
        struct.pack_into('<I', existing, 0, 903)
        struct.pack_into('<I', existing, 4, 1)
        struct.pack_into('<I', existing, 20, 1 + len(b'Warscape903\0'))
        server = (struct.pack('<4s4I', b'WDBC', 2, 66, 264, len(server_string)) +
                  original[20:20 + 264] + existing + server_string)

        registered = generate.runtime_map_dbc(original, server, self.cfg)
        _, count, fields, row_size, string_size = struct.unpack_from('<4s4I', registered)
        self.assertEqual((count, fields, row_size), (3, 66, 264))
        self.assertEqual(registered[20:20 + 264], original[20:20 + 264])
        self.assertEqual(registered[20 + 264:20 + 528], server[20 + 264:20 + 528])
        row_offset = 20 + 2 * row_size
        self.assertEqual(struct.unpack_from('<I', registered, row_offset)[0], 904)
        strings_offset = 20 + count * row_size
        strings = registered[strings_offset:strings_offset + string_size]
        directory_offset = struct.unpack_from('<I', registered, row_offset + 4)[0]
        display_offset = struct.unpack_from('<I', registered, row_offset + 20)[0]
        self.assertEqual(strings[directory_offset:strings.index(b'\0', directory_offset)].decode(),
                         self.cfg['directory'])
        self.assertEqual(strings[display_offset:strings.index(b'\0', display_offset)].decode(),
                         self.cfg['display_name'])

    def test_mpq_merge_preserves_prior_custom_maps_and_overlays_new_map(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing, update, result = (root / 'existing.MPQ', root / 'update.MPQ', root / 'merged.MPQ')
            generate.archive(existing, {
                'World\\Maps\\WarscapeTest1\\WarscapeTest1.wdt': b'map901',
                'World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha.wdt': b'map903',
            })
            generate.archive(update, {
                'World\\Maps\\WarscapeDevSandbox\\WarscapeDevSandbox.wdt': b'map904',
            })
            deploy_sandbox.merge_archive(existing, update, result)
            archive = mpyq.MPQArchive(str(result), listfile=True)
            try:
                self.assertEqual(archive.read_file('World\\Maps\\WarscapeTest1\\WarscapeTest1.wdt'), b'map901')
                self.assertEqual(archive.read_file('World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha.wdt'), b'map903')
                self.assertEqual(archive.read_file('World\\Maps\\WarscapeDevSandbox\\WarscapeDevSandbox.wdt'), b'map904')
            finally:
                archive.file.close()

    def test_navigation_validator_requires_walkable_full_tile_coverage(self):
        tile_size = 1600 / 3
        fields = [0] * 15
        fields[6], fields[7] = 625, 676
        floats = [1.6, 0.5333, 1.6, -tile_size, 30.0, -tile_size,
                  0.0, 30.0, 0.0, 3.75]
        detour = struct.pack('<15I10f', *fields, *floats)
        blob = struct.pack('<4I4s', 0x4D4D4150, 7, 15, len(detour), b'\1\0\0\0') + detour
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / '9043232.mmtile'
            path.write_bytes(blob)
            self.assertEqual(build.validate_navigation_tile(path, require_full_flat_tile=True), (625, 676))
            fields[6] = 0
            path.write_bytes(struct.pack('<4I4s', 0x4D4D4150, 7, 15, len(detour), b'\1\0\0\0') +
                             struct.pack('<15I10f', *fields, *floats))
            with self.assertRaisesRegex(ValueError, 'no walkable polygons'):
                build.validate_navigation_tile(path)


if __name__ == '__main__':
    unittest.main()
