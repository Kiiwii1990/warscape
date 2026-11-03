"""Binary reuse and deployment isolation regressions; no runtime mutations."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np

import briarbrook
from build_briarbrook import namespace_models
import lumbridge
from native_preview import chunks
from deploy_briarbrook import assert_dbc_append


class BriarbrookTests(unittest.TestCase):
    def test_native_model_axes_match_adt_and_vmap_conventions(self):
        np.testing.assert_allclose(briarbrook.rotation(0)@np.array([1.,0.]),[0,-1],atol=1e-7)
        np.testing.assert_allclose(briarbrook.rotation(90)@np.array([1.,0.]),[1,0],atol=1e-7)
        np.testing.assert_allclose(briarbrook.rotation(0)@np.array([0.,1.]),[1,0],atol=1e-7)

    def test_sampler_extension_encodes_nonliquid_variable_terrain(self):
        cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text())
        data=lumbridge.adt(cfg,32,32,None,[],height_sampler=lambda x,y:30+x*.01,
                          surface_sampler=lambda e,n:(64,48,32))
        chunks_seen=0
        for tag,body in chunks(data):
            if tag!='MCNK':continue
            chunks_seen+=1
            flags=struct.unpack_from('<I',body)[0]
            self.assertTrue(flags&0x8000)
            self.assertFalse(flags&0x1c)
            offset,size=struct.unpack_from('<2I',body,36)
            self.assertEqual(size,12296)
            self.assertEqual(body[offset-8:offset-4],b'LACM')
            self.assertEqual(set(body[offset:offset+4096]),{64})
            self.assertEqual(set(body[offset+4096:offset+8192]),{48})
            self.assertEqual(set(body[offset+8192:offset+12288]),{32})
        self.assertEqual(chunks_seen,256)

    def test_lighting_append_preserves_original_rows_and_strings(self):
        row=struct.pack('<2I5f8I',1,0,0,0,0,0,0,12,13,10,13,4,0,0,0)
        data=struct.pack('<4s4I',b'WDBC',1,15,60,1)+row+b'\0'
        class FakeAssets:
            def read(self,name):return data
        result=briarbrook.light_dbc(FakeAssets(),905)
        self.assertEqual(result[20:80],row)
        self.assertEqual(result[-1:],b'\0')
        new=result[80:140]
        self.assertEqual(struct.unpack_from('<2I',new),(2,905))
        self.assertEqual(new[8:],row[8:])

    def test_lighting_refuses_existing_map_id(self):
        row=struct.pack('<2I5f8I',1,905,0,0,0,0,0,*([0]*8))
        class FakeAssets:
            def read(self,name):return struct.pack('<4s4I',b'WDBC',1,15,60,1)+row+b'\0'
        with self.assertRaisesRegex(ValueError,'already exists'):
            briarbrook.light_dbc(FakeAssets(),905)

    def test_deployer_accepts_only_an_append_with_preserved_strings(self):
        old=struct.pack('<4s4I',b'WDBC',1,2,8,4)+struct.pack('<2I',12,1)+b'\0old'
        new=struct.pack('<4s4I',b'WDBC',2,2,8,8)+old[20:28]+struct.pack('<2I',13,4)+b'\0oldnew\0'
        assert_dbc_append(old,new,2,8)
        damaged=bytearray(new);damaged[20]=99
        with self.assertRaisesRegex(ValueError,'altered'):assert_dbc_append(old,damaged,2,8)
        damaged=bytearray(new);damaged[-7]=ord('x')
        with self.assertRaisesRegex(ValueError,'altered'):assert_dbc_append(old,damaged,2,8)

    @staticmethod
    def spawn(name,flags=1,map_id=905):
        result=struct.pack('<3IIHI7f',map_id,32,32,flags,0,42,1,2,3,0,90,0,1)
        if flags&4:result+=struct.pack('<6f',-2,-2,-2,2,2,2)
        return result+struct.pack('<I',len(name))+name.encode()

    def test_namespacing_preserves_transforms_bounds_and_both_record_layouts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'raw';source.mkdir()
            (source/'Barrel.m2').write_bytes(b'raw-model-data')
            (source/'Farm.wmo').write_bytes(b'raw-building-data')
            records=[self.spawn('Barrel.m2'),self.spawn('Farm.wmo',4)]
            (source/'dir_bin').write_bytes(b''.join(records))
            self.assertEqual(namespace_models(source,root/'out',905),(2,2))
            # Prefix is eleven ASCII bytes; keep expectations independent of parser offsets.
            expected=b''.join(r[:-len(name)-4]+struct.pack('<I',len('warscape905_'+name))+('warscape905_'+name).encode()
                              for r,name in zip(records,['Barrel.m2','Farm.wmo']))
            self.assertEqual((root/'out/dir_bin').read_bytes(),expected)
            self.assertEqual((root/'out/warscape905_Farm.wmo').read_bytes(),b'raw-building-data')

    def test_namespacing_refuses_another_map(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'raw';source.mkdir()
            (source/'dir_bin').write_bytes(self.spawn('Farm.wmo',4,904))
            with self.assertRaisesRegex(ValueError,'escaped'):
                namespace_models(source,root/'out',905)

    def test_namespacing_refuses_path_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'raw';source.mkdir()
            (source/'dir_bin').write_bytes(self.spawn('../Farm.wmo',4))
            with self.assertRaisesRegex(ValueError,'path'):
                namespace_models(source,root/'out',905)


if __name__=='__main__':unittest.main()
