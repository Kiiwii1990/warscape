"""Briarbrook: an authored one-tile village, independent of the Lumbridge layout.

All execution is local Windows. Output, previews, manifests and extracted client
assets stay outside Git. No SQL, server configuration or saved variables.
"""
import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess

import mpyq
import numpy as np
from PIL import Image, ImageDraw

import generate
import lumbridge
from native_preview import chunks, geometry, cstring, Renderer

CLIENT = Path(r'C:\WoWDev\wowdecomp\bin\Win')
SERVER = Path(r'C:\WoWDev\TrinityServer')
HALF = generate.TILE / 2
ELWYNN = 'World\\Azeroth\\Elwynn\\PassiveDoodads\\'
HUMAN = 'World\\Generic\\Human\\Passive Doodads\\'
GENERIC = 'World\\Generic\\PassiveDoodads\\'


class Assets(lumbridge.Assets):
    def __init__(self, client=CLIENT):
        super().__init__(client)
        # Some native world M2s reference glue textures in locale archives.
        for name in ['patch-enUS-3.MPQ', 'patch-enUS-2.MPQ', 'patch-enUS.MPQ',
                     'lichking-locale-enUS.MPQ', 'expansion-locale-enUS.MPQ', 'locale-enUS.MPQ']:
            path = Path(client) / 'Data/enUS' / name
            if path.exists():
                self.archives.append(mpyq.MPQArchive(str(path), listfile=False))

    def close(self):
        for a in self.archives:
            a.file.close()


def rotation(yaw):
    a = math.radians(yaw - 90)
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def spline(points):
    p = np.array([points[0], *points, points[-1]], dtype=float)
    result = []
    for i in range(1, len(p) - 2):
        for t in np.linspace(0, 1, max(3, int(np.linalg.norm(p[i+1]-p[i])/2)), endpoint=False):
            result.append(.5*((2*p[i])+(-p[i-1]+p[i+1])*t+
                         (2*p[i-1]-5*p[i]+4*p[i+1]-p[i+2])*t*t+
                         (-p[i-1]+3*p[i]-3*p[i+1]+p[i+2])*t*t*t))
    return np.array([*result, points[-1]])


def path_distance(e, n, points):
    d = np.full(np.broadcast(e, n).shape, np.inf)
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = bx-ax, by-ay
        t = np.clip(((e-ax)*dx+(n-ay)*dy)/(dx*dx+dy*dy), 0, 1)
        d = np.minimum(d, np.hypot(e-ax-t*dx, n-ay-t*dy))
    return d


class Village:
    def __init__(self, cfg, assets):
        self.cfg, self.assets = cfg, assets
        self.buildings = []
        for source in cfg['buildings']:
            b = dict(source)
            b['r'] = rotation(b['yaw'])
            b['origin'] = np.array(b['foot']) - b['r'] @ np.array(b['entry_local'][:2])
            b['bounds'] = assets.bounds(b['asset'])
            self.buildings.append(b)
        self.roads = [(r, spline(r['points'])) for r in cfg['roads']]
        axis = np.linspace(-HALF, HALF, 1025)
        self.e, self.n = np.meshgrid(axis, axis[::-1])
        self.heights = self.height_field(self.e, self.n)
        self.holes = self.excavate_cellar()
        self.alphas = self.surface_field(self.e[:-1,:-1]+generate.TILE/2048,
                                         self.n[:-1,:-1]-generate.TILE/2048)
        self.sources = []
        self.author_objects()

    def excavate_cellar(self):
        """Clear terrain from the inn's real cellar and stair mesh.

        Hole quads are accepted only where native upward floor triangles cover
        every sampled point. Remaining interior vertices are lowered under the
        lowest native floor. Exterior terrain is retained at the foundation.
        """
        b=self.buildings[0];rootz=b['ground']-b['entry_local'][2];triangles=[]
        for verts,uv,indices,texture in geometry(self.assets,b['asset']):
            t=verts[np.asarray(indices).reshape(-1,3)]
            normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
            lengths=np.linalg.norm(normals,axis=1)
            mask=(lengths>.001)&(normals[:,2]>lengths*.7)&(t[:,:,2].max(axis=1)<1.2)
            for tri in t[mask]:
                out=tri.astype(float).copy();out[:,:2]=out[:,:2]@b['r'].T+b['origin'];out[:,2]+=rootz
                triangles.append(out)
        def floor(e,n):
            shape=np.broadcast(e,n).shape;result=np.full(shape,np.inf)
            for tri in triangles:
                a,bb,c=tri;den=(bb[1]-c[1])*(a[0]-c[0])+(c[0]-bb[0])*(a[1]-c[1])
                if abs(den)<1e-8:continue
                u=((bb[1]-c[1])*(e-c[0])+(c[0]-bb[0])*(n-c[1]))/den
                v=((c[1]-a[1])*(e-c[0])+(a[0]-c[0])*(n-c[1]))/den
                inside=(u>=-1e-4)&(v>=-1e-4)&(u+v<=1.0001)
                z=u*a[2]+v*bb[2]+(1-u-v)*c[2]
                result=np.minimum(result,np.where(inside,z,np.inf))
            return result
        corners=np.concatenate(triangles)[:,:2];lo,hi=corners.min(axis=0),corners.max(axis=0)
        region=(self.e>=lo[0])&(self.e<=hi[0])&(self.n>=lo[1])&(self.n<=hi[1])
        low=floor(self.e[region],self.n[region]);old=self.heights[region]
        self.heights[region]=np.where(np.isfinite(low)&(low<old-.25),np.minimum(old,low-.4),old)
        holes=[];size=generate.TILE/64
        for gy in range(64):
            n0=HALF-(gy+1)*size
            if n0+size<lo[1] or n0>hi[1]:continue
            for gx in range(64):
                e0=-HALF+gx*size
                if e0+size<lo[0] or e0>hi[0]:continue
                ee,nn=np.meshgrid(np.linspace(e0+.02,e0+size-.02,5),np.linspace(n0+.02,n0+size-.02,5))
                z=floor(ee,nn)
                if np.isfinite(z).all() and z.min()<b['ground']-.5:
                    holes.append((gx,gy))
        return holes

    def pad_distance(self, b, e, n):
        dx, dy = e-b['origin'][0], n-b['origin'][1]
        # Inverse of the native model->east/north rotation.
        x = b['r'][0,0]*dx + b['r'][1,0]*dy
        y = b['r'][0,1]*dx + b['r'][1,1]*dy
        lo, hi = b['bounds'][:2], b['bounds'][3:5]
        return np.hypot(np.maximum(np.maximum(lo[0]-x,x-hi[0]),0),
                        np.maximum(np.maximum(lo[1]-y,y-hi[1]),0))

    def base_height_field(self, e, n):
        radius = np.sqrt(((e-4)/1.04)**2+((n-8)/1.12)**2)
        h = 30.6 + .023*n + .008*e
        h += .65*np.sin(e/33+.4)*np.cos(n/40) + .32*np.sin(e/14+n/25)
        h += 64*smooth((radius-116)/117)
        for x,y,rx,ry,z in [(-133,35,48,70,22),(121,103,50,40,18),(-65,153,65,47,24),
                              (135,-86,52,50,27),(-110,-126,55,48,18)]:
            h += z*np.exp(-2*(((e-x)/rx)**2+((n-y)/ry)**2))
        # Smooth, oriented native footprints: doors have measured ground levels,
        # hills resume gradually behind each property instead of clipping walls.
        for b in self.buildings:
            weight = 1-smooth(self.pad_distance(b,e,n)/11)
            h = h*(1-weight)+b['ground']*weight
        return h

    def height_field(self, e, n):
        # Apply once after authored grading and before cellar cutting/object
        # grounding. Encoder is told this sampler already contains the detail.
        import terrain_detail
        h = self.base_height_field(e,n)
        s = terrain_detail.Settings.from_config(self.cfg)
        if not s.enabled or s.flat:
            return h
        mask = terrain_detail.Protection()
        for b in self.buildings:
            bb=b['bounds'];corners=np.array([[x,y] for x in [bb[0],bb[3]] for y in [bb[1],bb[4]]])@b['r'].T+b['origin']
            lo,hi=corners.min(axis=0),corners.max(axis=0)
            mask.box(lo[0]+HALF,lo[1]-HALF,hi[0]+HALF,hi[1]-HALF,12)
        for road,points in self.roads:
            mask.road([(x+HALF,y-HALF) for x,y in points],road.get('width',5),10)
        d=terrain_detail.VERTEX_SPACING
        dx=(self.base_height_field(e+d,n)-self.base_height_field(e-d,n))/(2*d)
        dy=(self.base_height_field(e,n+d)-self.base_height_field(e,n-d))/(2*d)
        gain=(1-terrain_detail.smooth((np.hypot(dx,dy)-.25)/.3))*mask(e+HALF,n-HALF)
        return h+terrain_detail.field(e+HALF,n-HALF,s)*gain

    def height(self, e, n):
        x = np.clip((e+HALF)/generate.TILE*1024,0,1024)
        y = np.clip((HALF-n)/generate.TILE*1024,0,1024)
        ix, iy = int(x), int(y); jx, jy = min(ix+1,1024), min(iy+1,1024)
        fx, fy = x-ix,y-iy
        return float((self.heights[iy,ix]*(1-fx)+self.heights[iy,jx]*fx)*(1-fy)+
                     (self.heights[jy,ix]*(1-fx)+self.heights[jy,jx]*fx)*fy)

    def surface_field(self, e, n):
        noise = .36*np.sin(e*.37+np.sin(n*.21))+.28*np.cos(n*.45-e*.13)
        dirt = np.zeros(np.broadcast(e,n).shape)
        for r, points in self.roads:
            d = path_distance(e,n,points)-r['width']/2 + noise
            dirt = np.maximum(dirt,1-smooth((d+.8)/2.6))
        for c in self.cfg['clearings']:
            d = np.sqrt(((e-c['center'][0])/c['radii'][0])**2+((n-c['center'][1])/c['radii'][1])**2)
            dirt = np.maximum(dirt,c['strength']*(1-smooth((d-.7)/.5)))
        for b in self.buildings:
            d=np.hypot((e-b['foot'][0])/7,(n-b['foot'][1])/6)+noise*.05
            dirt = np.maximum(dirt,.82*(1-smooth((d-.6)/.6)))
        for g in self.cfg['gardens']:
            d = np.sqrt(((e-g['center'][0])/g['radii'][0])**2+((n-g['center'][1])/g['radii'][1])**2)
            dirt = np.maximum(dirt,.94*(1-smooth((d-.80)/.26)))
        # An irregular, softly worn cobble core; never rectangular paving.
        d = np.sqrt(((e+4)/13)**2+((n-6)/10)**2)+noise*.04
        cobble = .74*(1-smooth((d-.58)/.5))
        forest = .56*smooth((np.hypot(e,n)-91)/52)
        forest *= .65+.35*np.sin(e/19+np.cos(n/23))**2
        forest *= 1-dirt
        # Big-alpha is a set of independent final blend weights in wowdecomp.
        # Sequential coverage is converted to a normalized, nonnegative simplex.
        dirt = dirt*(1-cobble)
        base = (1-dirt-cobble)*(1-forest)
        leaf = np.maximum(0,1-base-dirt-cobble)
        return np.stack([np.floor(dirt*255),np.floor(cobble*255),np.floor(leaf*255)],axis=-1).astype('u1')

    def alpha(self,e,n):
        x = max(0,min(1023,int((e+HALF)/generate.TILE*1024)))
        y = max(0,min(1023,int((HALF-n)/generate.TILE*1024)))
        return tuple(int(v) for v in self.alphas[y,x])

    def road_clearance(self, e, n):
        return min(float(path_distance(e,n,p))-r['width']/2 for r,p in self.roads)

    def add(self, name, asset, e, n, yaw=0, scale=1, offset=0, **kwargs):
        self.sources.append(dict(name=name,asset=asset,osrs=[float(e),float(n)],
                                 z=self.height(e,n)+offset,yaw=float(yaw),scale=scale,**kwargs))

    def author_objects(self):
        for b in self.buildings:
            self.add(b['name'],b['asset'],*b['origin'],yaw=b['yaw'],
                     offset=b['ground']-self.height(*b['origin'])-b['entry_local'][2],
                     doodad_set=b['doodad_set'],landmark='building')
        prop = {
            'well':GENERIC+'Well\\Well.m2','crate':GENERIC+'Crate01\\Crate01.m2',
            'barrel':GENERIC+'Barrel\\Barrel01.m2','sack':GENERIC+'Furniture\\Containers\\Sack02.m2',
            'table':HUMAN+'Tables\\InnTable.m2','bench':HUMAN+'Benches\\InnBench.m2',
            'lamp':ELWYNN+'LampPost\\LampPost.m2','flowers':ELWYNN+'Detail\\ElwynnFlower01.m2',
            'flowers2':ELWYNN+'Detail\\ElwynnFlower02.m2',
            'tree':ELWYNN+'Trees\\ElwynnTreeMid01.m2','oak':ELWYNN+'Trees\\ElwynnTreeCanopy01.m2',
            'fir':ELWYNN+'Trees\\ElwynnFirTree01.m2','pine':ELWYNN+'Trees\\ElwynnTree01\\ElwynnPine01.m2',
            'bush':ELWYNN+'Bush\\ElwynnBush01.m2','bush2':ELWYNN+'Bush\\ElwynnBush03.m2',
            'rock':ELWYNN+'Detail\\ElwynnRock1\\ElwynnRock1.m2',
            'grass':ELWYNN+'Detail\\ElwynnDetailGrass\\ElwynnDetailGrass01.m2',
            'stump':ELWYNN+'Trees\\Stumps\\ElwynnTreeStump01.m2',
            'fence':ELWYNN+'ElwynnFences\\ElwynnWoodFence01.m2',
            'wall':ELWYNN+'ElwynnFences\\ElwynnStoneFence.m2',
            'wagon':'World\\Azeroth\\Westfall\\PassiveDoodads\\HayWagon\\WestfallHayWagon.m2',
            'cabbage':'World\\Azeroth\\Westfall\\PassiveDoodads\\Detail\\WestFallCabbage.m2',
            'pumpkin':'World\\Azeroth\\Duskwood\\PassiveDoodads\\Bush\\Pumpkin01.m2',
            'wheat':ELWYNN+'Detail\\ElwynnWheat\\ElwynnWheat01.m2',
            'anvil':ELWYNN+'Anvil\\Anvil.m2',
            'sign':HUMAN+'SignPosts\\WoodSignPostNice01.m2',
            'pointer':HUMAN+'SignPosts\\WoodSignPointerNice01.m2',
            'bread':HUMAN+'Food\\BreadLoaf01.m2','cheese':HUMAN+'Food\\CheeseWheel01.m2',
            'wood':'World\\Generic\\DarkIronDwarf\\Passive Doodads\\WoodPiles\\DarkIronWoodPile01.m2'
        }
        prop['awning']=HUMAN+'VendorAwnings\\StormwindVendorAwning01.m2'
        self.props = prop
        def put(kind, e, n, yaw=0, scale=1, offset=0, name=None):
            self.add(name or kind,prop[kind],e,n,yaw,scale,offset,landmark=kind)
        # Common: a little green island and a well leave two clear passing lanes.
        put('well',-5,8,35);put('oak',-6,20,12,.61)
        for e,n,y in [(-10,14,35),(-12,3,120),(1,12,225)]: put('bench',e,n,y)
        for e,n,y in [(-19,12,12),(11,23,205),(20,-20,80),(-24,-20,340),(-6,40,20),(23,73,60)]:
            put('lamp',e,n,y)
        for e,n in [(-13,-67),(15,26)]:
            put('sign',e,n,35);put('pointer',e,n,35,offset=3.2)
        # Three individual traders' tables, each with a specific set of goods.
        for e,n,y,goods in [(-3,27,10,'bread'),(-7,34,-12,'cheese'),(-12,-3,62,'cabbage')]:
            put('awning',e,n,y,name='market '+goods)
            for lx in [-1.2,-.2,.7]:
                de,dn=rotation(y)@np.array([lx,1.46])
                put(goods,e+de,n+dn,y,offset=1.04)
            put('crate',e+3.1,n-1.0,y+15);put('sack',e+3.8,n+.4,y-25)
        # Inn beer garden, with goods on the furniture, not floating above it.
        for e,n,y in [(-28,-5,90),(-39,-7,80),(-27,21,90)]:
            put('table',e,n,y)
            put('bench',e-2.3,n,y);put('bench',e+2.3,n,y+180)
            put('bread',e,n-.5,30,offset=1.04)
            put('cheese',e+.4,n+.8,55,offset=1.04)
        for e,n,y in [(-26,13,23),(-27,14,76),(-28,12,15)]:put('barrel',e,n,y)
        # Goods collect at the wall beside each entrance; doorstep centers stay open.
        for e,n,y,kinds in [(28,23,30,['anvil','crate','barrel']),
                             (34,22,10,['wood','crate','sack']),
                             (-6,47,15,['crate','crate','sack','barrel']),
                             (20,-34,42,['barrel','sack','crate']),
                             (-34,-27,33,['crate','sack']),
                             (13,85,10,['barrel','crate']),
                             (62,-13,14,['crate','sack','barrel','sack'])]:
            for i,kind in enumerate(kinds):put(kind,e+(i%2)*1.35,n+(i//2)*1.6,y+i*21)
        put('wagon',58,-18,18);put('wood',51,29,10);put('stump',53,26,0)
        # Kitchen garden: small native crops with gaps, not a giant flat green texture.
        put('wheat',53,-57,8,.47,offset=.1)
        for row in range(4):
            for col in range(6):
                put('cabbage',-56+col*3.1,-56+row*3.0,17+row*31+col*17,.78)
        for e,n in [(65,-53),(67,-56),(65,-59),(68,-61)]:put('pumpkin',e,n,43,.72)
        # Property boundaries have generous entrance gaps and measured segment lengths.
        def run(kind, points):
            bounds=self.assets.bounds(prop[kind]);axis=0 if bounds[3]-bounds[0]>bounds[4]-bounds[1] else 1
            length=bounds[axis+3]-bounds[axis]; mid=(bounds[axis+3]+bounds[axis])/2
            for (ax,ay),(bx,by) in zip(points,points[1:]):
                distance=math.hypot(bx-ax,by-ay);count=max(1,round(distance/(length*.97)))
                angle=math.degrees(math.atan2(by-ay,bx-ax));yaw=angle+(90 if axis==0 else 0)
                for i in range(count):
                    t=(i+.5)/count; e=ax+(bx-ax)*t;n=ay+(by-ay)*t
                    shift=rotation(yaw)@np.eye(2)[axis]*mid
                    put(kind,e-shift[0],n-shift[1],yaw)
        run('fence',[(38,-69),(72,-69),(76,-40)])
        run('fence',[(38,-69),(38,-48)])
        run('fence',[(-62,-65),(-34,-65),(-32,-47)])
        run('fence',[(-62,-65),(-64,-39),(-46,-37)])
        run('fence',[(48,88),(49,107),(70,111)])
        run('wall',[(-21,24),(-21,34),(-40,35)])
        # Deliberately positioned village trees frame reveals and property corners.
        for kind,e,n,s in [('oak',-69,-12,.75),('oak',-54,43,.68),('oak',50,-36,.64),
                            ('oak',77,65,.78),('oak',-25,-64,.69),('oak',-22,101,.76),
                            ('tree',34,-23,1),('tree',-41,-16,1.15),('tree',4,60,1.2),
                            ('tree',38,73,1.1),('tree',48,87,1.25),('tree',57,91,1.15),
                            ('tree',47,101,1.3),('tree',61,103,1.2),('tree',72,96,1.12)]:
            put(kind,e,n,31+e*7,s)
        # Flowers are authored around garden walls, door edges and common benches.
        rng=random.Random(90517)
        for cx,cy,rx,ry in [(-14,19,3,3),(-10,14,2,2),(-1,13,2,2),(-38,-31,3,3),
                              (-62,-45,2,7),(31,-42,3,2),(37,29,3,2),(-14,54,3,3),
                              (23,91,3,3),(40,-67,8,1.5),(-34,-61,1,5)]:
            for j in range(7):
                put('flowers' if j%3 else 'flowers2',cx+rng.uniform(-rx,rx),cy+rng.uniform(-ry,ry),rng.uniform(0,360),rng.uniform(.8,1.3))
        # Woodland is ecological framing. It does not supply the village's authored detail.
        rng=random.Random(self.cfg['woodland']['seed']);accepted=[]
        for key,kind,inner,outer,spacing,clearance,smin,smax in [
                ('canopy_count','oak',112,233,15,12,.72,1.06),
                ('understory_count','tree',92,237,8,7,.95,1.6),
                ('shrub_count','bush',88,233,6,4,.52,.86),
                ('floor_detail_count','grass',85,236,3,2,.8,1.4)]:
            group=[];attempts=0
            while len(group)<self.cfg['woodland'][key]:
                attempts+=1
                if attempts>50000:raise ValueError('Ecology cannot satisfy requested clearances: '+kind)
                e,n=rng.uniform(-outer,outer),rng.uniform(-outer,outer)
                radial=math.hypot(e,n)
                edge=inner+11*math.sin(e/35+n/39)
                if not edge<radial<outer:continue
                if self.road_clearance(e,n)<clearance:continue
                if min(float(self.pad_distance(b,e,n)) for b in self.buildings)<clearance:continue
                if any(math.hypot(e-x,n-y)<spacing for x,y in group):continue
                group.append((e,n));accepted.append((e,n))
                chosen=kind
                if kind=='oak' and len(group)%5==0:chosen='fir'
                if kind=='tree' and len(group)%3==0:chosen='pine'
                if kind=='bush' and len(group)%2==0:chosen='bush2'
                if kind=='grass' and len(group)%7==0:chosen='rock'
                put(chosen,e,n,rng.uniform(0,360),rng.uniform(smin,smax))
        # A few soft shrub groups define the village edge without blocking doors.
        for cx,cy,yaw in [(-64,16,15),(-42,39,85),(-43,-33,15),(42,-65,90),(68,86,20),
                            (30,89,10),(5,90,70),(-10,62,20),(-77,-3,90),(96,-26,15)]:
            put('bush',cx,cy,yaw,.64)
        pconfig=dict(self.cfg,placements=self.sources)
        self.placed=lumbridge.placements(pconfig,self.assets)


def light_dbc(assets, map_id):
    original=assets.read('DBFilesClient\\Light.dbc')
    magic,count,fields,size,ss=struct.unpack_from('<4s4I',original)
    if (magic,fields,size)!=(b'WDBC',15,60):raise ValueError('Unexpected Light.dbc')
    rows=[original[20+i*size:20+(i+1)*size] for i in range(count)]
    if any(struct.unpack_from('<I',r,4)[0]==map_id for r in rows):raise ValueError('Map lighting already exists')
    row=bytearray(next(r for r in rows if struct.unpack_from('<I',r)[0]==1))
    uid=max(struct.unpack_from('<I',r)[0] for r in rows)+1
    struct.pack_into('<2I',row,0,uid,map_id)
    # Native Azeroth default palette and day/night curves. A zero-position record
    # is the map default, as selected by wowdecomp DayNight::GetDefaultLight.
    return struct.pack('<4s4I',magic,count+1,fields,size,ss)+b''.join(rows)+row+original[20+count*size:]


def audit(village, output):
    assets=village.assets; records=[]
    for name in sorted({p['asset'] for p in village.placed}):
        dependencies=set()
        for v,uv,idx,texture in geometry(assets,name):
            if texture[0]:dependencies.add(texture[0])
        if name.lower().endswith('.wmo'):
            root=dict(chunks(assets.read(name)))
            for raw in root.get('MODN',b'').split(b'\0'):
                if raw:
                    child=raw.decode('ascii');child=child[:-4]+'.m2' if child.lower().endswith(('.mdx','.mdl')) else child
                    assets.read(child)
        for dependency in dependencies:assets.read(dependency)
        records.append(dict(asset=name,sha256=hashlib.sha256(assets.read(name)).hexdigest(),
                            bounds=assets.bounds(name),textures=sorted(dependencies)))
    (output/'asset-audit.json').write_text(json.dumps(records,indent=2)+'\n')


def generate_package(output):
    if output.exists():raise ValueError('Choose a NEW external build directory')
    repo=Path(__file__).resolve().parents[3]
    if any(output.is_relative_to(p) for p in (repo,CLIENT,SERVER)):raise ValueError('Output must be external')
    cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text())
    a=Assets();v=Village(cfg,a)
    original=a.read('DBFilesClient\\Map.dbc');server=(SERVER/'dbc/Map.dbc').read_bytes()
    ids={struct.unpack_from('<I',server,20+i*264)[0] for i in range(struct.unpack_from('<I',server,4)[0])}
    if cfg['map_id'] in ids:raise ValueError('New map ID conflicts with existing registrations')
    for kind in ('maps','vmaps','mmaps'):
        if any((SERVER/kind).glob(str(cfg['map_id'])+'*')):raise ValueError('Unregistered map artifacts conflict')
    runtime=generate.runtime_map_dbc(original,server,cfg)
    output.mkdir(parents=True)
    audit(v,output)
    prefix='World\\Maps\\'+cfg['directory']+'\\'+cfg['directory']
    terrain=lumbridge.adt(cfg,32,32,a,v.placed,
                         height_sampler=lambda x,y:v.height(-y-HALF,x+HALF),
                         surface_sampler=v.alpha,detail_applied=True)
    terrain=bytearray(terrain)
    # Reuse validated MCIN offsets; the classic hole mask is 4x4 per MCNK.
    mcin=next(body for tag,body in chunks(terrain) if tag=='MCIN')
    for gx,gy in v.holes:
        offset=struct.unpack_from('<I',mcin,((gy//4)*16+gx//4)*16)[0]
        old=struct.unpack_from('<H',terrain,offset+8+60)[0]
        struct.pack_into('<H',terrain,offset+8+60,old|(1<<((gy%4)*4+gx%4)))
    terrain=bytes(terrain)
    files={prefix+'.wdt':generate.wdt(cfg['tiles'],4),prefix+'_32_32.adt':terrain}
    locale={'DBFilesClient\\Map.dbc':runtime,'DBFilesClient\\Light.dbc':light_dbc(a,cfg['map_id'])}
    generate.archive(output/'runtime/patch-Z.MPQ',files)
    generate.archive(output/'runtime/patch-enUS-Z.MPQ',locale)
    (output/'runtime/Map.dbc').write_bytes(runtime)
    staged=output/'extract-input/Data'
    for source in (CLIENT/'Data').rglob('*.MPQ'):
        if source.name.lower() in ('patch-z.mpq','patch-enus-z.mpq'):continue
        target=staged/source.relative_to(CLIENT/'Data');target.parent.mkdir(parents=True,exist_ok=True)
        os.link(source,target)
    generate.archive(staged/'patch-Z.MPQ',files)
    extraction={'DBFilesClient\\Map.dbc':generate.map_dbc(original,cfg,only_custom=True),
                # Do not extract unrelated GameObjectDisplayInfo models.
                'DBFilesClient\\GameObjectDisplayInfo.dbc':struct.pack('<4s4I',b'WDBC',0,19,76,1)+b'\0'}
    generate.archive(staged/'enUS/patch-enUS-Z.MPQ',extraction)
    manifest=dict(configuration=cfg,placements=v.placed,cellar_holes=v.holes,base_server_map_sha256=hashlib.sha256(server).hexdigest(),
                  height_range=[float(v.heights.min()),float(v.heights.max())],
                  validation='Generated and asset-audited; no live visual acceptance')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    np.savez_compressed(output/'authoring.npz',height=v.heights,alpha=v.alphas)
    print('Generated',output,'placements',len(v.placed),'height range',manifest['height_range'])
    preview(v,output)
    a.close()


def preview(v, output):
    renderer=Renderer(v.assets,(1600,1000));items=[]
    # Native-texture material composition, with the same final alpha simplex.
    resolution=2048
    axis=np.linspace(-HALF,HALF,resolution,endpoint=False)+generate.TILE/(resolution*2)
    e,n=np.meshgrid(axis,axis[::-1]);alpha=v.alphas.repeat(2,axis=0).repeat(2,axis=1)/255
    weights=[1-alpha.sum(axis=-1),*[alpha[:,:,i] for i in range(3)]]
    baked=np.zeros((resolution,resolution,3))
    # The native tile UV cadence is eight repeats per MCNK (4.1667 yards).
    for texture,weight in zip(v.cfg['textures'],weights):
        im=np.array(Image.open(io.BytesIO(v.assets.read(texture))).convert('RGB'))
        u=((e/(generate.TILE/128))%1*im.shape[1]).astype(int)
        vv=((-n/(generate.TILE/128))%1*im.shape[0]).astype(int)
        baked+=im[vv,u]*weight[:,:,None]
    ground=Image.fromarray(np.clip(baked,0,255).astype('u1'));ground.save(output/'surface-plan.jpg')
    tex=renderer.ctx.texture(ground.size,3,ground.tobytes());tex.build_mipmaps()
    renderer.textures['authored-ground']=tex
    coords=np.linspace(-HALF,HALF,257);ee,nn=np.meshgrid(coords,coords[::-1])
    zz=v.heights[::4,::4]
    vertices=np.stack([ee.ravel(),nn.ravel(),zz.ravel()],axis=-1)
    uv=np.stack([(ee.ravel()+HALF)/generate.TILE,(HALF-nn.ravel())/generate.TILE],axis=-1)
    ind=[]
    for row in range(256):
        for col in range(256):
            if (col//4,row//4) in v.holes:continue
            i=row*257+col;ind.extend([i,i+257,i+1,i+1,i+257,i+258])
    items.append(([(vertices,uv,np.array(ind),'authored-ground')],np.eye(4)))
    for p in v.placed:
        r=rotation(p['yaw']);mat=np.eye(4);mat[:2,:2]=r*p['scale'];mat[2,2]=p['scale']
        mat[:3,3]=[*p['osrs'],p['z']]
        items.append((renderer.batches(p['asset']),mat))
    renderer.render(items,[-205,-255,240],[0,18,33],260,output/'village-overview.jpg')
    renderer.render(items,[135,-135,150],[-3,12,33],200,output/'market-and-inn.jpg')
    renderer.render(items,[-2,-50,42],[-5,14,35],70,output/'street-approach.jpg',perspective=True)
    if v.cfg.get('combat_farm'):
        renderer.render(items,[116,54,v.height(116,54)+6],[160,85,v.height(160,85)+3],80,
                        output/'cinderfield-approach.jpg',perspective=True)
        renderer.render(items,[231,12,145],[150,79,37],95,output/'cinderfield-overview.jpg')
    plan=ground.copy();draw=ImageDraw.Draw(plan)
    def pixel(e,n):return ((e+HALF)/generate.TILE*resolution,(HALF-n)/generate.TILE*resolution)
    for b in v.buildings:
        lo,hi=b['bounds'][:2],b['bounds'][3:5]
        corners=[b['origin']+b['r']@np.array(c) for c in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
        draw.polygon([pixel(*c) for c in corners],outline='white',width=3)
        x,y=pixel(*b['foot']);draw.ellipse((x-5,y-5,x+5,y+5),fill='orange')
        draw.text((x+6,y),b['name'],fill='white')
    plan.save(output/'annotated-plan.jpg')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--preview',action='store_true',help='Refresh offline previews only')
    args=parser.parse_args()
    if os.name!='nt':raise SystemExit('Local Windows execution only')
    if args.preview:
        cfg=json.loads(Path(__file__).with_name('briarbrook.json').read_text())
        a=Assets();preview(Village(cfg,a),args.output.resolve());a.close()
    else:
        generate_package(args.output.resolve())


if __name__=='__main__':main()
