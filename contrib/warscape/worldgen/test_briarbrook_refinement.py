"""Regression guards for native material selection and reusable vegetation beds."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

from briarbrook import Assets
from ground_clutter import patch_points
from lumbridge import adt
from native_preview import chunks
from refine_briarbrook import selected_texture, check_materials
from validate_briarbrook import Navigation
from briarbrook import HALF


class RefinementTests(unittest.TestCase):
    def test_client_specular_path_selects_the_required_native_resource(self):
        self.assertEqual(selected_texture('grass.blp',0,True),'grass_s.blp')
        self.assertEqual(selected_texture('grass.blp',1,True),'grass.blp')
        self.assertEqual(selected_texture('grass.blp',0,False),'grass.blp')

    def test_missing_flags_expose_the_exact_two_missing_specular_resources(self):
        assets=Assets()
        try:
            cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text())
            for index in [0,3]:
                with self.assertRaisesRegex(ValueError,'Native asset not found'):
                    assets.read(selected_texture(cfg['textures'][index],0,True))
            self.assertEqual(len(check_materials(assets,cfg)),4)
        finally:assets.close()

    def test_mtxf_has_a_valid_mhdr_pointer_and_one_word_per_texture(self):
        cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text())
        data=adt(cfg,32,32,None,[],height_sampler=lambda x,y:30,surface_sampler=lambda e,n:(0,0,0))
        top=dict((t,b) for t,b in chunks(data) if t!='MCNK')
        offset=struct.unpack_from('<I',top['MHDR'],44)[0]
        self.assertEqual(data[20+offset:24+offset],b'FXTM')
        self.assertEqual(struct.unpack('<4I',top['MTXF']),(1,0,0,1))

    def test_mtxf_rejects_incomplete_texture_metadata(self):
        cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text());cfg['texture_flags']=[1]
        with self.assertRaisesRegex(ValueError,'one supported flag'):
            adt(cfg,32,32,None,[],height_sampler=lambda x,y:30,surface_sampler=lambda e,n:(0,0,0))

    @staticmethod
    def patch(name):
        return dict(name=name,seed=12,center=[0,0],radii=[10,10],profile='plants',count=16,spacing=.6)

    def test_patch_seed_is_stable_when_patch_order_changes(self):
        profiles={'plants':[dict(asset='native.m2',radius=.2)]}
        a,b=self.patch('A'),self.patch('B');allow=lambda *args:True
        first=list(patch_points([a,b],profiles,allow));second=list(patch_points([b,a],profiles,allow))
        for name in ['A','B']:
            self.assertEqual([p[2:] for p in first if p[0]['name']==name],[p[2:] for p in second if p[0]['name']==name])

    def test_patch_sampling_honors_the_worlds_exclusions(self):
        profile={'plants':[dict(asset='native.m2',radius=.2)]}
        result=list(patch_points([self.patch('A')],profile,lambda e,n,r,p:e>2 and n>0))
        self.assertEqual(len(result),16)
        self.assertTrue(all(p[2]>2 and p[3]>0 for p in result))

    def test_impossible_patch_density_fails_instead_of_silently_cluttering_paths(self):
        with self.assertRaisesRegex(ValueError,'adjust its footprint'):
            list(patch_points([self.patch('blocked')],{'plants':[dict(asset='native.m2')]},lambda *args:False))

    def test_navmesh_queries_use_detail_height_above_a_nonplanar_polygon(self):
        header=[0]*15;header[0]=0x444e4156;header[6]=1;header[7]=4
        header[9],header[10],header[11]=1,1,4
        mesh=struct.pack('<15I10f',*header,*([0]*10))
        vertices=[(-1,0,-1),(1,0,-1),(1,0,1),(-1,0,1)]
        mesh+=b''.join(struct.pack('<3f',*v) for v in vertices)
        mesh+=struct.pack('<I6H6HHBB',0,0,1,2,3,0,0,*([0]*6),1,4,1)
        mesh+=struct.pack('<2IBB2x',0,0,1,4)+struct.pack('<3f',0,3,0)
        mesh+=bytes([0,1,4,0,1,2,4,0,2,3,4,0,3,0,4,0])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'curved.mmtile';path.write_bytes(bytes(20)+mesh)
            nav=Navigation(path)
            found=nav.query(-HALF,HALF,3,max_distance=.1)
            self.assertIsNotNone(found)
            self.assertAlmostEqual(found[3],0,places=5)


if __name__=='__main__':unittest.main()
