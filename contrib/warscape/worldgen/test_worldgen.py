"""Structural and coordinate invariants; no deployment or database writes."""
import json
import mpyq
from pathlib import Path
import struct
import tempfile
import unittest

import generate
import lumbridge
import deploy


class WorldGenerationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(Path(__file__).with_name('lumbridge-a.json').read_text())

    def test_osrs_transform_roundtrip_and_directions(self):
        for point in [(3222,3218),(3246,3226),(3228,3298),(3189,3273)]:
            actual = lumbridge.osrs(self.cfg,*lumbridge.world(self.cfg,*point))
            for a,b in zip(actual,point): self.assertAlmostEqual(a,b)
        north=lumbridge.world(self.cfg,3222,3219); east=lumbridge.world(self.cfg,3223,3218)
        origin=lumbridge.world(self.cfg,3222,3218)
        self.assertGreater(north[0],origin[0]); self.assertLess(east[1],origin[1])

    def test_river_is_lowered_and_banks_are_dry(self):
        river=lumbridge.height(self.cfg,*lumbridge.world(self.cfg,3246,3226))
        land=lumbridge.height(self.cfg,*lumbridge.world(self.cfg,3222,3218))
        self.assertLess(river,self.cfg['river']['surface_z'])
        self.assertGreater(land,self.cfg['river']['surface_z'])

    def test_wdt_only_marks_configured_tiles(self):
        b=generate.wdt(self.cfg['tiles'],4)
        self.assertEqual(struct.unpack_from('<I',b,8)[0],18)
        self.assertEqual(struct.unpack_from('<I',b,20)[0],4)
        main=b[60:60+32768]
        found={(i%64,i//64) for i in range(4096) if struct.unpack_from('<I',main,i*8)[0]}
        self.assertEqual(found,{tuple(t) for t in self.cfg['tiles']})

    def test_existing_map_registration_is_preserved_byte_for_byte(self):
        original = bytearray(20 + 264 + 1)
        struct.pack_into('<4s4I', original, 0, b'WDBC', 1, 66, 264, 1)
        cfg = {'map_id':901,'directory':'WarscapeTest1','display_name':'Initial label'}
        registered = generate.map_dbc(bytes(original), cfg)
        cfg['display_name'] = 'Checkpoint B must not rewrite the deployed label'
        self.assertEqual(generate.runtime_map_dbc(bytes(original), registered, cfg), registered)

    def test_runtime_map_dbc_appends_new_map_without_rewriting_existing_custom_rows(self):
        original = bytearray(20 + 264 + 1)
        struct.pack_into('<4s4I', original, 0, b'WDBC', 1, 66, 264, 1)
        def cfg(map_id):
            return {'map_id': map_id, 'directory': f'Warscape{map_id}',
                    'display_name': f'Warscape {map_id}'}
        current = generate.runtime_map_dbc(bytes(original), bytes(original), cfg(901))
        before_901 = current[20 + 264:20 + 528]
        current = generate.runtime_map_dbc(bytes(original), current, cfg(902))
        before_902 = current[20 + 528:20 + 792]
        merged = generate.runtime_map_dbc(bytes(original), current, cfg(903))
        self.assertEqual(struct.unpack_from('<I', merged, 4)[0], 4)
        self.assertEqual(merged[20:20 + 264], original[20:20 + 264])
        self.assertEqual(merged[20 + 264:20 + 528], before_901)
        self.assertEqual(merged[20 + 528:20 + 792], before_902)
        self.assertEqual(struct.unpack_from('<I', merged, 20 + 792)[0], 903)
        for i, expected in ((1, 'Warscape901'), (2, 'Warscape902'), (3, 'Warscape903')):
            row = 20 + i * 264
            strings = 20 + 4 * 264
            offset = struct.unpack_from('<I', merged, row + 4)[0]
            end = merged.find(b'\0', strings + offset)
            self.assertEqual(merged[strings + offset:end].decode(), expected)

    def test_deployment_mpq_merge_preserves_existing_maps_and_unrelated_entries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = root / 'existing.MPQ'
            update = root / 'update.MPQ'
            merged = root / 'merged.MPQ'
            generate.archive(existing, {
                'World\\Maps\\WarscapeTest1\\WarscapeTest1.wdt': b'map901',
                'World\\Maps\\WarscapeTest2\\WarscapeTest2.wdt': b'map902',
                'Interface\\AddOns\\KeepMe\\KeepMe.toc': b'unrelated-addon',
                'World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha.wdt': b'old903',
            })
            generate.archive(update, {
                'World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha.wdt': b'new903',
                'World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha_32_32.adt': b'new-adt',
            })
            deploy.merged_archive(existing, update, merged)
            check = mpyq.MPQArchive(str(merged), listfile=True)
            try:
                self.assertEqual(check.read_file('World\\Maps\\WarscapeTest1\\WarscapeTest1.wdt'), b'map901')
                self.assertEqual(check.read_file('World\\Maps\\WarscapeTest2\\WarscapeTest2.wdt'), b'map902')
                self.assertEqual(check.read_file('Interface\\AddOns\\KeepMe\\KeepMe.toc'), b'unrelated-addon')
                self.assertEqual(check.read_file('World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha.wdt'), b'new903')
                self.assertEqual(check.read_file('World\\Maps\\WarscapeLumbridgeAlpha\\WarscapeLumbridgeAlpha_32_32.adt'), b'new-adt')
            finally:
                check.file.close()

    def test_alpha_map_903_uses_configurable_native_scale_and_non_neon_surfaces(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-alpha.json').read_text(encoding='utf-8-sig'))
        self.assertEqual((cfg['map_id'], cfg['directory']), (903, 'WarscapeLumbridgeAlpha'))
        self.assertEqual(cfg['scale']['units_per_tile'], 3.0)
        self.assertEqual(len(cfg['textures']), 4)
        self.assertFalse(any('ElwynnCrop' in texture for texture in cfg['textures']))
        castle = next(p for p in cfg['placements'] if p.get('landmark') == 'castle')
        self.assertTrue(castle['asset'].endswith('Castle02.wmo'))
        self.assertTrue(castle['align_to_ground'])
        self.assertEqual(castle['scale'], 1)
        for building in (p for p in cfg['placements'] if p['asset'].lower().endswith('.wmo')
                         and p.get('landmark') != 'bridge'):
            self.assertEqual(building['z'], 'terrain', building['name'])
            self.assertTrue(building['align_to_ground'], building['name'])
            self.assertEqual(building['scale'], 1, building['name'])
        self.assertGreaterEqual(len(cfg['placement_regions']), 4)
        self.assertTrue(all(region['seed'] and region['count'] for region in cfg['placement_regions']))

    def test_alpha_map_903_terrain_edges_are_repeatable_and_irregular(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-alpha.json').read_text(encoding='utf-8-sig'))
        settings = cfg['surface']['edge_noise']
        self.assertGreater(settings['amplitude_tiles'], 0)
        self.assertLessEqual(settings['amplitude_tiles'], 0.2)
        self.assertEqual(lumbridge.edge_noise(cfg, 3244.2, 3220.7),
                         lumbridge.edge_noise(cfg, 3244.2, 3220.7))
        samples = {round(lumbridge.edge_noise(cfg, 3244 + i / 8, 3220.7), 5)
                   for i in range(16)}
        self.assertGreater(len(samples), 3, 'edge field should vary smoothly along the river')
        # A mid-segment sample away from the town paving has an intermediate
        # dirt alpha, demonstrating a continuous blend instead of a hard edge.
        alpha = lumbridge.surface(cfg, 3207, 3240.5)[0]
        self.assertGreater(alpha, 0)
        self.assertLess(alpha, 255, 'path feather should blend with the grass')

    def test_alpha_map_903_liquid_metadata_is_standard_water_with_correct_vertex_heights(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-alpha.json').read_text(encoding='utf-8-sig'))
        data = lumbridge.adt(cfg, 32, 32, None, [])
        position = 0
        mcin = None
        while position + 8 <= len(data):
            tag = data[position:position + 4][::-1]
            size = struct.unpack_from('<I', data, position + 4)[0]
            if tag == b'MCIN':
                mcin = position + 8
                break
            position += size + 8
        self.assertIsNotNone(mcin)
        wet_chunks = 0
        for index in range(256):
            mcnk, _, _, _ = struct.unpack_from('<4I', data, mcin + index * 16)
            header = mcnk + 8
            flags = struct.unpack_from('<I', data, header)[0]
            if not flags & 4:
                continue
            wet_chunks += 1
            liquid_offset, liquid_size = struct.unpack_from('<2I', data, header + 96)
            liquid = mcnk + liquid_offset
            self.assertEqual(data[liquid:liquid + 4], b'QLCM')
            payload_size = struct.unpack_from('<I', data, liquid + 4)[0]
            self.assertEqual(liquid_size, payload_size + 8)
            payload = liquid + 8
            minimum, maximum = struct.unpack_from('<2f', data, payload)
            self.assertAlmostEqual(minimum, cfg['river']['surface_z'], delta=1e-5)
            self.assertAlmostEqual(maximum, cfg['river']['surface_z'], delta=1e-5)
            # wowdecomp uses the float at byte 4 of each 8-byte old liquid vertex.
            heights = [struct.unpack_from('<f', data, payload + 8 + vertex * 8 + 4)[0]
                       for vertex in range(81)]
            self.assertTrue(all(abs(value - cfg['river']['surface_z']) < 1e-5 for value in heights))
            topx = struct.unpack_from('<f', data, header + 108)[0]
            topy = struct.unpack_from('<f', data, header + 104)[0]
            step = generate.TILE / 128
            depths = []
            for row in range(9):
                for col in range(9):
                    vertex = row * 9 + col
                    vx, vy = topx - row * step, topy - col * step
                    expected_depth = max(0, min(255, round(
                        (cfg['river']['surface_z'] - lumbridge.height(cfg, vx, vy)) *
                        cfg['river']['depth_byte_per_world_unit'])))
                    depth = data[payload + 8 + vertex * 8]
                    self.assertEqual(depth, expected_depth)
                    depths.append(depth)
            self.assertGreater(max(depths), 0, 'river vertices need real depth samples for the client shader')
            tiles = data[payload + 8 + 81 * 8:payload + 8 + 81 * 8 + 64]
            self.assertTrue(any(value == 0 for value in tiles))
            self.assertTrue(any(value == 15 for value in tiles))
        self.assertGreater(wet_chunks, 0)

    def test_alpha_map_903_mcnk_alpha_size_matches_all_three_overlay_planes(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-alpha.json').read_text(encoding='utf-8-sig'))
        data = lumbridge.adt(cfg, 32, 32, None, [])
        position = 0
        mcin = None
        while position + 8 <= len(data):
            tag = data[position:position + 4][::-1]
            size = struct.unpack_from('<I', data, position + 4)[0]
            if tag == b'MCIN':
                mcin = position + 8
                break
            position += size + 8
        self.assertIsNotNone(mcin)
        for index in range(256):
            mcnk, _, _, _ = struct.unpack_from('<4I', data, mcin + index * 16)
            header = mcnk + 8
            layer_count = struct.unpack_from('<I', data, header + 12)[0]
            alpha_offset = struct.unpack_from('<I', data, header + 36)[0]
            alpha_size = struct.unpack_from('<I', data, header + 40)[0]
            expected_size = 8 + (layer_count - 1) * 64 * 64
            self.assertEqual(layer_count, 4)
            self.assertEqual(alpha_size, expected_size, f'MCNK {index} has a stale MCAL size')
            mcal = mcnk + alpha_offset
            self.assertEqual(data[mcal:mcal + 4], b'LACM')
            self.assertEqual(struct.unpack_from('<I', data, mcal + 4)[0] + 8, alpha_size)

    def test_original_flat_generator_keeps_mcin_offsets(self):
        b=generate.adt(32,32,30,self.cfg['texture'],flat=True)
        mcin=84
        for i in range(256):
            off,size,_,_=struct.unpack_from('<4I',b,mcin+8+i*16)
            self.assertEqual(b[off:off+4],b'KNCM')
            self.assertEqual(struct.unpack_from('<I',b,off+4)[0]+8,size)
            self.assertAlmostEqual(struct.unpack_from('<f',b,off+8+112)[0],30)

    def test_lumbridge_big_alpha_mcnks_use_client_supported_decoder(self):
        # The WDT advertises 8-bit alpha globally; wowdecomp's 3.3.5a client
        # requires MCNK flag 0x8000 before it accepts that alpha genFormat.
        b=lumbridge.adt(self.cfg,32,32,None,[])
        pos=0; mcin=None
        while pos+8<=len(b):
            tag=b[pos:pos+4][::-1]
            size=struct.unpack_from('<I',b,pos+4)[0]
            if tag==b'MCIN':
                mcin=pos+8
                break
            self.assertLessEqual(size,len(b)-pos-8)
            pos+=size+8
        self.assertIsNotNone(mcin)
        self.assertEqual(struct.unpack_from('<I',generate.wdt(self.cfg['tiles'],4),20)[0] & 4,4)
        for i in range(256):
            mcnk,size,_,_=struct.unpack_from('<4I',b,mcin+i*16)
            self.assertEqual(b[mcnk:mcnk+4],b'KNCM')
            header=mcnk+8
            flags=struct.unpack_from('<I',b,header)[0]
            nlayers=struct.unpack_from('<I',b,header+12)[0]
            self.assertTrue(flags & lumbridge.MCNK_FLAG_BIG_ALPHA, f'MCNK {i} lacks the 8-bit alpha decode flag')
            self.assertEqual(nlayers,3)
            ofs_layers=struct.unpack_from('<I',b,header+28)[0]
            ofs_alpha,size_alpha=struct.unpack_from('<2I',b,header+36)
            layers_chunk=mcnk+ofs_layers
            alpha_chunk=mcnk+ofs_alpha
            self.assertEqual(b[layers_chunk:layers_chunk+4],b'YLCM')
            self.assertEqual(b[alpha_chunk:alpha_chunk+4],b'LACM')
            self.assertEqual(struct.unpack_from('<I',b,layers_chunk+4)[0],3*16)
            self.assertEqual(struct.unpack_from('<I',b,alpha_chunk+4)[0]+8,size_alpha)
            self.assertEqual(size_alpha,2*64*64+8)
            for layer in range(1,nlayers):
                _,layer_flags,alpha_offset,_=struct.unpack_from('<4I',b,layers_chunk+8+layer*16)
                self.assertTrue(layer_flags & 0x100)
                self.assertGreaterEqual(alpha_offset,0)
                self.assertLessEqual(alpha_offset+64*64,size_alpha-8)

    def test_checkpoint_b_bridge_and_river_are_sized_to_native_player_bounds(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-b.json').read_text())
        bridge = next(p for p in cfg['placements'] if p.get('landmark') == 'bridge')
        # These checks use the configured native assets' measured bounds below;
        # no client model or placement is rescaled in the ADT.
        self.assertTrue(bridge['asset'].endswith('ElwynnFootbridge.wmo'))
        client = Path(r'C:\WoWDev\wowdecomp\bin\Win')
        if not (client / 'Data').is_dir():
            self.skipTest('Local wowdecomp assets are not installed')
        assets = lumbridge.Assets(client)
        self.addCleanup(lambda: [archive.file.close() for archive in assets.archives])
        b = assets.bounds(bridge['asset'])
        human = assets.bounds(r'Character\Human\Male\HumanMale.m2')
        length, width, height = (b[i + 3] - b[i] for i in range(3))
        player_height = human[5] - human[2]
        self.assertAlmostEqual(length, 26.31, delta=0.1)
        self.assertAlmostEqual(width, 8.25, delta=0.1)
        self.assertAlmostEqual(height, 4.28, delta=0.1)
        self.assertGreater(length / player_height, 5.5)
        self.assertLess(length / player_height, 7.0)
        self.assertGreater(width / player_height, 1.7)
        self.assertLess(width / player_height, 2.2)
        self.assertLessEqual(cfg['river']['width_tiles'] * cfg['scale']['units_per_tile'], length)
        self.assertLessEqual(cfg['roads'][0]['width_tiles'] * cfg['scale']['units_per_tile'], width)

    def test_checkpoint_b_bridge_walk_surface_clears_water_and_meets_banks(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-b.json').read_text())
        bridge = next(p for p in cfg['placements'] if p.get('landmark') == 'bridge')
        client = Path(r'C:\WoWDev\wowdecomp\bin\Win')
        if not (client / 'Data').is_dir():
            self.skipTest('Local wowdecomp assets are not installed')
        assets = lumbridge.Assets(client)
        self.addCleanup(lambda: [archive.file.close() for archive in assets.archives])
        group_name = bridge['asset'][:-4] + '_000.wmo'
        group = assets.read(group_name)
        def payload(tag):
            offset = group.index(tag[::-1].encode('ascii'))
            size = struct.unpack_from('<I', group, offset + 4)[0]
            return group[offset + 8:offset + 8 + size]
        vertices = list(struct.iter_unpack('<3f', payload('MOVT')))
        indices = struct.unpack('<' + 'H' * (len(payload('MOVI')) // 2), payload('MOVI'))
        deck_faces = []
        for i in range(0, len(indices), 3):
            a, b, c = (vertices[indices[i + j]] for j in range(3))
            u = tuple(b[k] - a[k] for k in range(3))
            v = tuple(c[k] - a[k] for k in range(3))
            normal = (u[1]*v[2] - u[2]*v[1], u[2]*v[0] - u[0]*v[2], u[0]*v[1] - u[1]*v[0])
            area2 = sum(n*n for n in normal) ** 0.5
            if area2 and normal[2] / area2 > .8 and area2 / 2 > 8:
                deck_faces.append((sum(point[0] for point in (a,b,c)) / 3,
                                   sum(point[2] for point in (a,b,c)) / 3))
        left = [z for x,z in deck_faces if x < -8]
        right = [z for x,z in deck_faces if x > 8]
        self.assertTrue(left and right, 'native bridge walk surface must span the river')
        scale = cfg['scale']['units_per_tile']
        self.assertGreater(bridge['z'] + min(left + right), cfg['river']['surface_z'] + .5)
        for local_x, deck_z in ((-12.0, sum(left)/len(left)), (11.0, sum(right)/len(right))):
            east = bridge['osrs'][0] + local_x / scale  # yaw=90 points local X east
            bank_z = lumbridge.height(cfg, *lumbridge.world(cfg, east, bridge['osrs'][1]))
            self.assertLess(abs((bridge['z'] + deck_z) - bank_z), .5)

    def test_checkpoint_b_uses_native_landmark_assets_and_configurable_fences(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-b.json').read_text())
        required = {'castle', 'church', 'general_store', 'axe_shop', 'fred_farm',
                    'chicken_farm', 'cow_farm', 'bridge'}
        placed = {p['landmark']: p for p in cfg['placements'] if 'landmark' in p}
        self.assertTrue(required <= placed.keys())
        self.assertGreaterEqual(len(cfg['placement_runs']), 3)
        assets = lumbridge.Assets(Path(r'C:\WoWDev\wowdecomp\bin\Win'))
        self.addCleanup(lambda: [archive.file.close() for archive in assets.archives])
        actual = lumbridge.placements(cfg, assets)
        self.assertGreaterEqual(len(actual), 100)
        self.assertEqual(len({p['uid'] for p in actual}), len(actual))
        for p in actual:
            self.assertEqual(len(p['local_bounds']), 6, p['asset'])
            self.assertEqual(len(p['bounds']), 6, p['asset'])

    def test_checkpoint_b_smooths_ground_and_texture_edges(self):
        cfg = json.loads(Path(__file__).with_name('lumbridge-b.json').read_text())
        # The river cross-section changes continuously through the bank taper.
        profile = json.loads(json.dumps(cfg))
        profile['river']['points'] = [[3245, 3100], [3245, 3225.5], [3245, 3350]]
        heights = [lumbridge.height(profile, *lumbridge.world(profile, 3245 + i / 10, 3225.5))
                   for i in range(-15, 16)]
        self.assertTrue(all(a >= b for a, b in zip(heights[:15], heights[1:16])))
        self.assertTrue(all(a <= b for a, b in zip(heights[15:], heights[16:])))
        self.assertLess(max(b - a for a, b in zip(heights, heights[1:])), 0.12)
        center = lumbridge.surface(cfg, 3240, 3226)[0]
        feather = lumbridge.surface(cfg, 3240, 3226.65)[0]
        far = lumbridge.surface(cfg, 3000, 3000)[0]
        self.assertEqual(center, 255)
        self.assertGreater(feather, 0)
        self.assertLess(feather, 255)
        self.assertEqual(far, 0)


if __name__=='__main__':
    unittest.main()
