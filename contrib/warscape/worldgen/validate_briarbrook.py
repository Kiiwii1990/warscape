"""Artifact-level map-905 validation, including road navmesh connectivity."""
import argparse
import hashlib
from collections import Counter, deque
import json
from pathlib import Path
import struct

import mpyq
import numpy as np

from briarbrook import HALF, spline, rotation
from native_preview import chunks


class Navigation:
    def __init__(self,path):
        data=Path(path).read_bytes()
        h=struct.unpack_from('<15I10f',data,20)
        if h[0]!=0x444e4156:raise ValueError('Unexpected Detour tile magic')
        count,nv=h[6:8]
        verts=np.frombuffer(data,'<f4',count=nv*3,offset=120).reshape(-1,3)
        self.polys=[];self.neighbors=[]
        for i in range(count):
            record=struct.unpack_from('<I6H6HHBB',data,120+nv*12+i*32)
            self.polys.append(verts[list(record[1:1+record[-2]])])
            self.neighbors.append([n-1 for n in record[7:7+record[-2]] if n and not n&0x8000])
        self.components=[-1]*count;component=0
        for i in range(count):
            if self.components[i]>=0:continue
            queue=[i];self.components[i]=component
            while queue:
                for neighbor in self.neighbors[queue.pop()]:
                    if self.components[neighbor]<0:self.components[neighbor]=component;queue.append(neighbor)
            component+=1
        self.largest=Counter(self.components).most_common(1)[0][0]
        self.lo=np.array([p[:,[0,2]].min(axis=0) for p in self.polys])
        self.hi=np.array([p[:,[0,2]].max(axis=0) for p in self.polys])
        self.planes=[np.linalg.lstsq(np.column_stack([p[:,0],p[:,2],np.ones(len(p))]),p[:,1],rcond=None)[0]
                     for p in self.polys]
        # Trinity uses DT_POLYREF64, so dtLink occupies 16 bytes. Follow the
        # DetourNavMeshBuilder buffer layout and use the actual detail surface;
        # a plane through the coarse polygon loses curved terrain elevations.
        detail_offset=120+nv*12+count*32+h[8]*16
        detail_verts_offset=detail_offset+h[9]*12
        detail_tris_offset=detail_verts_offset+h[10]*12
        detail_verts=np.frombuffer(data,'<f4',count=h[10]*3,offset=detail_verts_offset).reshape(-1,3)
        detail_tris=np.frombuffer(data,'u1',count=h[11]*4,offset=detail_tris_offset).reshape(-1,4)
        self.detail=[]
        for i,poly in enumerate(self.polys):
            if i>=h[9]:self.detail.append([]);continue
            vertex_base,tri_base,vertex_count,tri_count=struct.unpack_from('<2IBB',data,detail_offset+i*12)
            vertices=np.concatenate([poly,detail_verts[vertex_base:vertex_base+vertex_count]])
            self.detail.append(vertices[detail_tris[tri_base:tri_base+tri_count,:3]])

    def surface_height(self,index,point):
        for a,b,c in self.detail[index]:
            denominator=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
            if abs(denominator)<1e-8:continue
            u=((b[2]-c[2])*(point[0]-c[0])+(c[0]-b[0])*(point[1]-c[2]))/denominator
            v=((c[2]-a[2])*(point[0]-c[0])+(a[0]-c[0])*(point[1]-c[2]))/denominator
            if min(u,v,1-u-v)>=-.001:return float(u*a[1]+v*b[1]+(1-u-v)*c[1])
        return float(self.planes[index]@np.array([*point,1]))

    def query(self,e,n,z,max_distance=1.8):
        # Trinity TerrainBuilder stores Detour (worldY, worldZ, worldX).
        point=np.array([-HALF-e,n-HALF])
        best=None
        candidates=np.where(np.all(point>=self.lo-max_distance,axis=1)&np.all(point<=self.hi+max_distance,axis=1))[0]
        for i in candidates:
            poly=self.polys[i]
            p=poly[:,[0,2]];following=np.roll(p,-1,axis=0);edge=following-p
            cross=edge[:,0]*(point[1]-p[:,1])-edge[:,1]*(point[0]-p[:,0])
            if np.all(cross>=-.001) or np.all(cross<=.001):distance=0;closest=point
            else:
                t=np.clip(((point-p)*edge).sum(axis=1)/(edge*edge).sum(axis=1),0,1)
                candidates_on_edge=p+t[:,None]*edge
                distances=np.linalg.norm(point-candidates_on_edge,axis=1);near=int(distances.argmin())
                distance=float(distances[near]);closest=candidates_on_edge[near]
            dz=abs(self.surface_height(i,closest)-z)
            if distance>max_distance or dz>2:continue
            score=distance+dz*.2
            if best is None or score<best[0]:best=(score,i,distance,dz)
        return best


def validate(output):
    manifest=json.loads((output/'manifest.json').read_text());cfg=manifest['configuration']
    npz=np.load(output/'authoring.npz');height=npz['height'];alpha=npz['alpha']
    assert cfg['tiles']==[[32,32]] and cfg['map_id']==905
    assert height.max()-height.min()>(10 if cfg.get('refinement') else 50) and np.isfinite(height).all()
    assert np.max(alpha.astype(int).sum(axis=-1))<=255,'Overlapping big-alpha weights'
    arc=mpyq.MPQArchive(str(output/'runtime/patch-Z.MPQ'),listfile=True)
    prefix='World\\Maps\\'+cfg['directory']+'\\'+cfg['directory']
    data=arc.read_file(prefix+'_32_32.adt');wdt=dict(chunks(arc.read_file(prefix+'.wdt')))
    main=wdt['MAIN'];tiles=[i for i in range(4096) if struct.unpack_from('<I',main,i*8)[0]]
    assert tiles==[32*64+32]
    top=dict((tag,body) for tag,body in chunks(data) if tag!='MCNK')
    nm,nw=len(top['MDDF'])//36,len(top['MODF'])//64
    ids=[struct.unpack_from('<I',top['MDDF'],i*36+4)[0] for i in range(nm)]
    ids += [struct.unpack_from('<I',top['MODF'],i*64+4)[0] for i in range(nw)]
    assert len(ids)==len(set(ids))==len(manifest['placements'])
    assert nw==len(cfg['buildings'])==(8 if cfg.get('refinement') else 7)
    boundaries=[]
    for index in range(256):
        offset,size,_,_=struct.unpack_from('<4I',top['MCIN'],index*16)
        assert data[offset:offset+4]==b'KNCM' and struct.unpack_from('<I',data,offset+4)[0]+8==size
        body=data[offset+8:offset+size];flags,x,y,layers,nmr=struct.unpack_from('<5I',body)
        assert flags&0x8000 and not flags&0x1c and layers==4
        alpha_offset,alpha_size=struct.unpack_from('<2I',body,36)
        assert alpha_size==8+3*4096
        assert data[offset+alpha_offset:offset+alpha_offset+4]==b'LACM'
        planes=np.frombuffer(data,'u1',count=3*4096,offset=offset+alpha_offset+8).reshape(3,4096)
        assert planes.astype(int).sum(axis=0).max()<=255
        nwr=struct.unpack_from('<I',body,56)[0];ref=struct.unpack_from('<I',body,32)[0]
        refs=struct.unpack_from('<'+'I'*(nmr+nwr),data,offset+ref+8)
        assert all(i<nm for i in refs[:nmr]) and all(i<nw for i in refs[nmr:])
        # Check adjacent MCNK edge heights (145 values have alternating 9/8 rows).
        ho=struct.unpack_from('<I',body,20)[0]
        values=np.frombuffer(data,'<f4',count=145,offset=offset+ho+8)
        outer=np.array([values[r*17:r*17+9] for r in range(9)])
        boundaries.append(outer)
    for y in range(16):
        for x in range(16):
            q=boundaries[y*16+x]
            if x<15:assert np.allclose(q[:,-1],boundaries[y*16+x+1][:,0],atol=.001)
            if y<15:assert np.allclose(q[-1,:],boundaries[(y+1)*16+x][0,:],atol=.001)
    def terrain(e,n):
        x=int(np.clip((e+HALF)/533.333333*1024,0,1024))
        y=int(np.clip((HALF-n)/533.333333*1024,0,1024))
        return float(height[y,x])
    nav=Navigation(output/'extracted/mmaps/9053232.mmtile')
    issues=[];samples=0
    for road in cfg['roads']:
        for e,n in spline(road['points']):
            samples+=1;found=nav.query(e,n,terrain(e,n))
            if found is None or nav.components[found[1]]!=nav.largest:
                issues.append(dict(road=road['name'],east=round(float(e),2),north=round(float(n),2),
                                   reason='missing surface' if found is None else 'disconnected navigation'))
    interiors=[]
    probes=[(18,-2.6,.423),(9,0,1.756),(11.7,-6.3,-.503),
            (-1.54,-5.2,4.109),(-1.54,-5.2,4.109),(-1.54,-5.2,4.109),(0,-15,.14)]
    for building,local in zip(manifest['placements'][:7],probes):
        e,n=np.array(building['osrs'])+rotation(building['yaw'])@np.array(local[:2])
        found=nav.query(e,n,building['z']+local[2])
        connected=found is not None and nav.components[found[1]]==nav.largest
        interiors.append(dict(building=building['name'],entrance_connected=bool(connected)))
        if not connected:issues.append(dict(building=building['name'],reason='interior entrance is disconnected'))
    cellar=[];inn=manifest['placements'][0]
    for local in [(-20,7,-6.73),(-30,7,-6.73),(-34,0,-6.73),(-26,-7,-1.5)]:
        e,n=np.array(inn['osrs'])+rotation(inn['yaw'])@np.array(local[:2])
        found=nav.query(e,n,inn['z']+local[2])
        connected=found is not None and nav.components[found[1]]==nav.largest
        cellar.append(bool(connected))
        if not connected:issues.append(dict(building=inn['name'],reason='cellar/stair navigation is disconnected'))
    refinement_checks=None
    if cfg.get('refinement'):
        from refine_briarbrook import check_materials, field_sample
        from briarbrook import Assets
        report=manifest['refinement'];baseline=Path(report['baseline'])
        assert hashlib.sha256((baseline/'manifest.json').read_bytes()).hexdigest()==report['baseline_source_hash']
        original=json.loads((baseline/'manifest.json').read_text());prior={p['uid']:p for p in original['placements']}
        old_height=np.load(baseline/'authoring.npz')['height']
        current={p['uid']:p for p in manifest['placements']};removed=set(report['removed_ecology_uids'])
        assert set(prior)-removed<=set(current)
        fixed=0
        for uid,p in prior.items():
            if uid in removed:continue
            after=current[uid]
            assert all(p[k]==after[k] for k in ['asset','osrs','x','y','yaw','scale'])
            e,n=p['osrs']
            if p['asset'].lower().endswith('.wmo') or (-96<e<96 and -86<n<95):
                assert p['z']==after['z'],'Village furniture or building elevation moved'
                fixed+=1
            else:
                before_offset=p['z']-float(field_sample(old_height,e,n))
                after_offset=after['z']-float(field_sample(height,e,n))
                assert abs(before_offset-after_offset)<.0001,'Ground contact changed after terrain refinement'
        assert cfg['roads'][:len(original['configuration']['roads'])]==original['configuration']['roads']
        old_arc=mpyq.MPQArchive(str(baseline/'runtime/patch-Z.MPQ'),listfile=False)
        old_top=dict((t,b) for t,b in chunks(old_arc.read_file(prefix+'_32_32.adt')) if t!='MCNK')
        assert top['MODF'][:7*64]==old_top['MODF'],'Existing building records changed'
        assert top['MTEX']==old_top['MTEX'],'Native material references must remain unchanged'
        assert arc.read_file(prefix+'.wdt')==old_arc.read_file(prefix+'.wdt')
        flags=struct.unpack('<4I',top['MTXF']);assert list(flags)==cfg['texture_flags']==[1,0,0,1]
        flags_offset=struct.unpack_from('<I',top['MHDR'],44)[0]
        assert data[20+flags_offset:24+flags_offset]==b'FXTM'
        old_alpha=np.load(baseline/'authoring.npz')['alpha']
        east=np.linspace(-HALF,HALF,1025)[:-1]+533.333333/2048
        assert np.array_equal(alpha[:,east<100],old_alpha[:,east<100]),'Village dirt/cobble blend changed'
        for p in manifest['placements']:
            if p.get('landmark')=='ground_clutter':
                assert abs(p['z']-float(field_sample(height,*p['osrs'])))<.0001,'Floating ground clutter'
        assert report['new_terrain']['outer_slope_p95']<report['old_terrain']['outer_slope_p95']*.5
        assets=Assets()
        try:materials=check_materials(assets,cfg)
        finally:assets.close()
        farm=report['farm'];free=farm['combat_space'];combat_samples=0
        for de in [-12,-6,0,6,12]:
            for dn in [-9,-3,3,9]:
                e,n=free['center'][0]+de,free['center'][1]+dn
                found=nav.query(e,n,float(field_sample(height,e,n)),max_distance=.8);combat_samples+=1
                if found is None or nav.components[found[1]]!=nav.largest:
                    issues.append(dict(area='Cinderfield maneuver space',east=e,north=n,reason='not connected'))
        for e,n in farm['future_spawn_points']:
            found=nav.query(e,n,float(field_sample(height,e,n)),max_distance=.8)
            if found is None or nav.components[found[1]]!=nav.largest:
                issues.append(dict(area='Future-only spawn anchor',east=e,north=n,reason='not connected'))
        ruin=next(p for p in manifest['placements'] if p.get('landmark')=='ruined_farm')
        e,n=np.array(ruin['osrs'])+rotation(ruin['yaw'])@np.array([-1.54,-5.2])
        found=nav.query(e,n,ruin['z']+4.109)
        if found is None or nav.components[found[1]]!=nav.largest:issues.append(dict(area='Ruined farmhouse entry',reason='not connected'))
        refinement_checks=dict(material_settings_checked=2,all_material_resources_resolved=True,
                               fixed_village_props_and_buildings=fixed,existing_building_records_unchanged=True,
                               village_road_and_cobble_masks_unchanged=True,combat_maneuver_samples=combat_samples,
                               future_only_spawn_anchors=len(farm['future_spawn_points']),spawned_enemies=0)
    result=dict(adt_chunks=256,normalized_alpha_samples=1024*1024,placements=len(ids),buildings=nw,
                continuous_chunk_edges=True,road_samples=samples,road_navigation_issues=issues,
                interior_entrances=interiors,cellar_and_stair_probes=cellar,
                navigation_components=len(set(nav.components)),largest_component_polygons=Counter(nav.components)[nav.largest])
    if refinement_checks:result['refinement']=refinement_checks
    (output/'artifact-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    if issues:raise SystemExit('Road navigation needs refinement before deployment')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    validate(parser.parse_args().output)
