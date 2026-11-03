"""Natural-ground default, native seam and protected-surface regressions."""
import struct
import unittest
from dataclasses import replace

import numpy as np

import generate
from native_preview import chunks
import terrain_detail as detail


def native_grid(data):
    h=np.zeros((129,129));normals={}
    for tag,b in chunks(data):
        if tag!='MCNK':continue
        cx,cy=struct.unpack_from('<2I',b,4);o=struct.unpack_from('<I',b,20)[0];on=struct.unpack_from('<I',b,24)[0]
        v=np.frombuffer(b,'<f4',145,o)+struct.unpack_from('<f',b,112)[0];nm=np.frombuffer(b,'i1',435,on).reshape(145,3);index=0
        for row in range(17):
            for col in range(8 if row%2 else 9):
                if row%2==0:
                    y,x=cy*8+row//2,cx*8+col;h[y,x]=v[index];normals[(y,x)]=nm[index]
                index+=1
    return h,normals


class GroundDetailTests(unittest.TestCase):
    def test_coordinate_sampling_is_independent_of_batch_and_tile_partition(self):
        s=detail.Settings(seed=9137,biome='volcanic')
        x=np.linspace(-600,600,257);e,n=np.meshgrid(x,x[::-1]);whole=detail.field(e,n,s)
        np.testing.assert_array_equal(whole[:,:128],detail.field(e[:,:128],n[:,:128],s))
        for row,col in [(0,0),(127,128),(256,256)]:
            self.assertAlmostEqual(float(whole[row,col]),detail.field(float(e[row,col]),float(n[row,col]),s),places=10)

    def test_reconfiguration_replaces_detail_instead_of_stacking(self):
        base=lambda x,y:30+.01*x
        a=detail.prepare(base,settings=detail.Settings(seed=97))
        b=detail.prepare(a,settings=detail.Settings(seed=98))
        c=detail.prepare(base,settings=detail.Settings(seed=98))
        self.assertEqual(b(45.,-17.),c(45.,-17.))
        self.assertEqual(detail.prepare(a,settings=detail.Settings(flat=True))(45.,-17.),base(45.,-17.))

    def test_structure_and_liquid_masks_hold_surfaces_and_roads_are_gentler(self):
        mask=detail.Protection().box(-10,-8,10,8,10).road([(40,-50),(40,50)],8,12,minimum=0.)
        sample=detail.prepare(lambda x,y:30.,settings=detail.Settings(seed=42),protection=mask)
        self.assertEqual(sample(0.,0.),30.)
        self.assertEqual(sample(20.,-40.),30.)
        road=detail.Protection().road([(0,-100),(0,100)],8,10)
        self.assertEqual(road(0.,0.),.4)
        self.assertEqual(road(30.,0.),1.)

    def test_more_density_increases_frequency_without_multiplying_height(self):
        x=np.arange(-1500,1500,detail.VERTEX_SPACING/2);y=x*.27+37
        sparse=detail.field(x,y,detail.Settings(seed=123,density=.5))
        dense=detail.field(x,y,detail.Settings(seed=123,density=1.65))
        turns=lambda v:int(np.count_nonzero(np.diff(np.sign(np.diff(v)))))
        self.assertGreater(turns(dense),turns(sparse)*1.3)
        self.assertLess(np.quantile(abs(dense),.95),np.quantile(abs(sparse),.95)*1.8)
        self.assertLess(float(np.max(abs(np.diff(dense))))/(detail.VERTEX_SPACING/2),.45)

    def test_liquid_protection_uses_actual_world_scale(self):
        cfg={'scale':{'units_per_tile':4.2},'river':{'points':[(0,-50),(0,50)],'width_tiles':4,'bank_width_tiles':3}}
        mask=detail.config_protection(cfg,world=lambda e,n:(n*4.2,-e*4.2))
        self.assertEqual(mask(20.,0.),0.)
        self.assertEqual(mask(40.,0.),1.)

    def test_briarbrook_initial_height_stage_and_prepared_sampler_encoder(self):
        import briarbrook
        import lumbridge
        village=briarbrook.Village.__new__(briarbrook.Village)
        village.cfg={'map_id':1999};village.buildings=[];village.roads=[]
        axis=np.linspace(-100,100,49);e,n=np.meshgrid(axis,axis)
        first=village.height_field(e,n);second=village.height_field(e,n)
        np.testing.assert_array_equal(first,second)
        self.assertGreater(float(np.std(first-village.base_height_field(e,n))),.1)
        cfg={'map_id':1999,'height':30,'scale':{'units_per_tile':1,'osrs_origin':[0,0],'world_origin':[0,0]},'textures':['grass.blp'],'roads':[]}
        sampler=detail.prepare(lambda x,y:30.,settings=detail.Settings(seed=8))
        data=lumbridge.adt(cfg,32,32,None,[],height_sampler=sampler,surface_sampler=lambda e,n:())
        grid,_=native_grid(data)
        self.assertAlmostEqual(float(grid[0,0]),sampler(0.,0.),places=5)

    def test_biomes_are_distinct_and_flat_is_exact(self):
        x=np.arange(-100,100,4.1666667);y=x*.3
        fields=[detail.field(x,y,detail.Settings(seed=51,biome=b)) for b in ['volcanic','woodland','snow','settlement']]
        self.assertTrue(all(not np.array_equal(fields[0],f) for f in fields[1:]))
        np.testing.assert_array_equal(detail.field(x,y,detail.Settings(flat=True)),np.zeros(len(x)))

    def test_real_adjacent_adts_use_detail_by_default_and_share_edges_and_normals(self):
        s=detail.Settings(seed=411)
        left,ln=native_grid(generate.adt(31,32,30,'grass.blp',ground_detail=s))
        right,rn=native_grid(generate.adt(32,32,30,'grass.blp',ground_detail=s))
        self.assertGreater(float(np.ptp(left)),.8)
        np.testing.assert_array_equal(left[:,-1],right[:,0])
        for row in range(129):np.testing.assert_array_equal(ln[(row,128)],rn[(row,0)])
        flat,nm=native_grid(generate.adt(32,32,30,'grass.blp',flat=True))
        np.testing.assert_array_equal(flat,np.full((129,129),30.))

    def test_direct_encoder_respects_explicit_disable_and_declared_protection(self):
        flat,_=native_grid(generate.adt(32,32,30,'grass.blp',ground_detail=False))
        np.testing.assert_array_equal(flat,np.full((129,129),30.))
        options={'protected':[{'kind':'circle','center':[0,0],'radius':8}]}
        protected,_=native_grid(generate.adt(32,32,30,'grass.blp',ground_detail=options))
        self.assertEqual(float(protected[0,0]),30.)
        sampler=detail.prepare(lambda x,y:30.,{'ground_detail':options})
        self.assertEqual(sampler(0.,0.),30.)


if __name__=='__main__':unittest.main()
