"""Offline geometry/texture inspection of installed native assets, never game QA.

Requires numpy, moderngl and Pillow, in addition to worldgen's mpyq.
WMO batches and M2 first-LOD skin indices are read from the installed MPQs.
This deliberately omits animation, lights, embedded doodads and game shaders.
"""
import io
import math
import struct
from pathlib import Path

import numpy as np
import moderngl
from PIL import Image, ImageDraw


def chunks(data, start=0):
    while start + 8 <= len(data):
        tag = data[start:start + 4][::-1].decode('ascii')
        size = struct.unpack_from('<I', data, start + 4)[0]
        if start + 8 + size > len(data):
            raise ValueError('Truncated native chunk ' + tag)
        yield tag, data[start + 8:start + 8 + size]
        start += size + 8


def cstring(data, offset):
    return data[offset:data.index(b'\0', offset)].decode('ascii')


def geometry(assets, name):
    """Return textured triangle batches in native right-handed model coordinates."""
    data = assets.read(name)
    if name.lower().endswith('.wmo'):
        root = dict(chunks(data))
        materials = root['MOMT']
        count = struct.unpack_from('<I', root['MOHD'], 4)[0]
        for group in range(count):
            gd = dict(chunks(assets.read(name[:-4] + f'_{group:03}.wmo')))
            parts = dict(chunks(gd['MOGP'], 68))
            v = np.frombuffer(parts['MOVT'], '<f4').reshape(-1, 3)
            uv = np.frombuffer(parts['MOTV'], '<f4').reshape(-1, 2)[:len(v)]
            idx = np.frombuffer(parts['MOVI'], '<u2').reshape(-1, 3)
            mats = np.frombuffer(parts['MOPY'], 'u1').reshape(-1, 2)[:, 1]
            for material in np.unique(mats):
                material = int(material)
                if material == 255 or material * 64 + 16 > len(materials):
                    continue
                texture = cstring(root['MOTX'], struct.unpack_from('<I', materials, int(material) * 64 + 12)[0])
                blend = struct.unpack_from('<I', materials, material * 64 + 8)[0]
                yield v, uv, idx[mats == material].ravel(), (texture, blend != 0)
    else:
        count, offset = struct.unpack_from('<2I', data, 60)
        verts = np.frombuffer(data, '<f4', count=count * 12, offset=offset).reshape(-1, 12)
        v, uv = verts[:, :3], verts[:, 8:10]
        skin = assets.read(name[:-3] + '00.skin')
        nc, no, tc, to = struct.unpack_from('<4I', skin, 4)
        indices = np.frombuffer(skin, '<u2', count=nc, offset=no)
        triangles = indices[np.frombuffer(skin, '<u2', count=tc, offset=to)]
        nt, ot = struct.unpack_from('<2I', data, 80)
        texture_names = []
        for i in range(nt):
            typ, flags, length, pos = struct.unpack_from('<4I', data, ot + i * 16)
            texture_names.append(cstring(data, pos) if typ == 0 and length else None)
        nl, ol = struct.unpack_from('<2I', data, 128)
        lookup = struct.unpack_from('<' + 'H' * nl, data, ol)
        ns, osub, nu, ou = struct.unpack_from('<4I', skin, 28)
        assigned = set()
        for unit in range(nu):
            u = struct.unpack_from('<12H', skin, ou + unit * 24)
            sub, tex = u[2], u[8]
            if sub in assigned or sub >= ns:
                continue
            assigned.add(sub)
            start, size = struct.unpack_from('<2H', skin, osub + sub * 48 + 8)
            texid = lookup[tex] if tex < len(lookup) else 0
            texture = texture_names[texid] if texid < len(texture_names) else None
            nr, oflags = struct.unpack_from('<2I', data, 112)
            blend = struct.unpack_from('<H', data, oflags + u[5] * 4 + 2)[0] if u[5] < nr else 0
            yield v, uv, triangles[start:start + size], (texture, blend != 0)


class Renderer:
    def __init__(self, assets, size=(1024, 768)):
        self.assets, self.size = assets, size
        self.ctx = moderngl.create_standalone_context()
        self.program = self.ctx.program(vertex_shader='''#version 330
        uniform mat4 mvp; in vec3 pos; in vec2 uv; out vec2 texcoord;
        out vec3 p; void main(){p=pos; texcoord=uv; gl_Position=mvp*vec4(pos,1);}''',
        fragment_shader='''#version 330
        uniform sampler2D tex; in vec2 texcoord; in vec3 p; out vec4 color;
        void main(){vec4 c=texture(tex,texcoord); if(c.a<0.45)discard;
        vec3 n=normalize(cross(dFdx(p),dFdy(p))); float l=0.64+0.36*abs(dot(n,normalize(vec3(-0.5,-0.7,1.0))));
        color=vec4(c.rgb*l,1);}''')
        self.textures = {}
        self.models = {}

    def batches(self, name):
        if name not in self.models:
            self.models[name] = list(geometry(self.assets, name))
        return self.models[name]

    def texture(self, name):
        if name not in self.textures:
            filename, transparent = name if isinstance(name, tuple) else (name, False)
            im = Image.open(io.BytesIO(self.assets.read(filename))).convert('RGBA') if filename else Image.new('RGBA',(2,2),(155,136,104,255))
            if not transparent: im.putalpha(255)
            t = self.ctx.texture(im.size, 4, im.tobytes())
            t.build_mipmaps()
            self.textures[name] = t
        return self.textures[name]

    def render(self, items, eye, target, span, path=None, perspective=False):
        fbo = self.ctx.simple_framebuffer(self.size)
        fbo.use(); fbo.clear(.15,.19,.20,1)
        self.ctx.enable(moderngl.DEPTH_TEST)
        eye, target = np.array(eye, dtype=float), np.array(target, dtype=float)
        forward = target-eye; forward /= np.linalg.norm(forward)
        side = np.cross(forward,[0,0,1]); side /= np.linalg.norm(side)
        up = np.cross(side,forward)
        view = np.eye(4); view[:3,:3] = [side,up,-forward]; view[:3,3] = -view[:3,:3] @ eye
        ar = self.size[0]/self.size[1]
        proj = np.diag([2/(span*ar),2/span,-2/2000,1]); proj[2,3] = -1
        if perspective:
            f=1/math.tan(math.radians(60)/2); near,far=.2,1200
            proj=np.array([[f/ar,0,0,0],[0,f,0,0],[0,0,-(far+near)/(far-near),-2*far*near/(far-near)],[0,0,-1,0]])
        self.program['mvp'].write(np.asarray(proj@view,dtype='f4').T.tobytes())
        for batches, transform in items:
            for v, uv, idx, texture in batches:
                points = (np.column_stack([v,np.ones(len(v))]) @ transform.T)[:,:3]
                buffer = self.ctx.buffer(np.column_stack([points,uv]).astype('f4').tobytes())
                ib = self.ctx.buffer(np.asarray(idx,dtype='u4').tobytes())
                vao = self.ctx.vertex_array(self.program,[(buffer,'3f 2f','pos','uv')],ib)
                self.texture(texture).use(); vao.render()
                vao.release(); buffer.release(); ib.release()
        im = Image.frombytes('RGB',self.size,fbo.read(components=3)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        fbo.release()
        if path: im.save(path)
        return im

    def asset_sheet(self, names, path):
        tiles=[]
        for name in names:
            batches=self.batches(name)
            v=np.concatenate([b[0] for b in batches]); lo,hi=v.min(axis=0),v.max(axis=0)
            center=(lo+hi)/2; span=max(hi-lo)*1.15
            im=self.render([(batches,np.eye(4))],center+np.array([1.4,-1.8,1.15])*span,center,span)
            im.thumbnail((512,384)); tiles.append((name,im))
        sheet=Image.new('RGB',(1024,420*math.ceil(len(tiles)/2)),(30,36,38)); draw=ImageDraw.Draw(sheet)
        for i,(name,im) in enumerate(tiles):
            x,y=(i%2)*512,(i//2)*420;sheet.paste(im,(x,y));draw.text((x+8,y+386),name.split('\\')[-1],fill='white')
        sheet.save(path)
