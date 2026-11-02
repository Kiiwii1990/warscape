"""Default, biome-aware walking relief in continuous east/north world metres.

Pure scalar Python works without NumPy; array callers get the same field with
NumPy when available. A sampler always retains its undetailed base, so wrapping
again replaces settings instead of accumulating displacement. Never pass saved
terrain through this implicitly: refinements must identify their base/component.
"""
from dataclasses import dataclass
import math

try:
    import numpy as np
except ImportError:
    np = None

VERTEX_SPACING = (1600 / 3) / 128


def _array(v):
    return np is not None and np.ndim(v) > 0


def _clip(v, low, high):
    return np.clip(v, low, high) if _array(v) else max(low, min(high, v))


def smooth(v):
    v = _clip(v, 0., 1.)
    return v * v * (3 - 2 * v)


def _hash(i, j, seed):
    if _array(i) or _array(j):
        i, j = np.asarray(i, dtype=np.int64), np.asarray(j, dtype=np.int64)
    else:
        i, j = int(i), int(j)
    h = (i * 374761393 + j * 668265263 + (int(seed) & 0xffffffff) * 1442695041) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return (h ^ (h >> 16)) / 4294967295.


def coherent(e, n, scale, seed):
    x, y = e / scale, n / scale
    floor = np.floor if _array(x) or _array(y) else math.floor
    i, j = floor(x), floor(y)
    x, y = x - i, y - j
    fade = lambda t: t * t * t * (t * (t * 6 - 15) + 10)
    x, y = fade(x), fade(y)
    return 2 * ((_hash(i, j, seed) * (1-x) + _hash(i+1, j, seed) * x) * (1-y) +
                (_hash(i, j+1, seed) * (1-x) + _hash(i+1, j+1, seed) * x) * y) - 1


@dataclass(frozen=True)
class Settings:
    seed: int = 17031
    biome: str = 'woodland'
    scale: float = 25.
    density: float = 1.15
    strength: float = 1.
    vertex_spacing: float = VERTEX_SPACING
    enabled: bool = True
    flat: bool = False

    def __post_init__(self):
        if self.biome not in ('woodland', 'volcanic', 'snow', 'settlement'):
            raise ValueError('Unknown walking-relief biome')
        if not all(math.isfinite(x) for x in (self.scale, self.density, self.strength, self.vertex_spacing)):
            raise ValueError('Walking-relief controls must be finite')
        if self.scale <= 0 or not 0 <= self.density <= 4 or not 0 <= self.strength <= 3 or self.vertex_spacing <= 0:
            raise ValueError('Invalid walking-relief controls')

    @classmethod
    def from_config(cls, cfg):
        options = cfg.get('ground_detail', {})
        if options is False:
            options = {'enabled': False}
        options = dict(options)
        options.pop('protected', None)
        options.setdefault('seed', cfg.get('seed', cfg.get('map_id', 0) * 7919 + 17))
        options.setdefault('biome', cfg.get('biome', 'woodland'))
        options.setdefault('flat', bool(cfg.get('flat_terrain', False)))
        return cls(**options)


def field(e, n, settings=None):
    """Local component only; scale/density affect frequency, not peak height."""
    s = settings or Settings()
    if _array(e) or _array(n):
        e, n = np.broadcast_arrays(np.asarray(e, float), np.asarray(n, float))
    if not s.enabled or s.flat or s.density == 0 or s.strength == 0:
        return (e + n) * 0.
    step = max(s.scale / math.sqrt(s.density), 3 * s.vertex_spacing)
    warp = step * .20
    u = e + warp * coherent(e, n, step*4.1, s.seed+1)
    v = n + warp * coherent(e, n, step*3.7, s.seed+2)
    floor = np.floor if _array(u) or _array(v) else math.floor
    ci, cj = floor(u/step), floor(v/step)
    regional = .56 + .44 * (.5 + .5*coherent(e, n, step*5.3, s.seed+3))
    value = (e+n)*0.
    amplitude = {'woodland': 1., 'volcanic': 1.1, 'snow': .9, 'settlement': .48}[s.biome]
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            i, j = ci+di, cj+dj
            x = (i+.5+.28*(_hash(i,j,s.seed+4)-.5))*step
            y = (j+.5+.28*(_hash(i,j,s.seed+5)-.5))*step
            angle = _hash(i,j,s.seed+6)*math.tau
            sin, cos = (np.sin, np.cos) if _array(angle) else (math.sin, math.cos)
            dx, dy = u-x, v-y
            xx, yy = dx*cos(angle)+dy*sin(angle), -dx*sin(angle)+dy*cos(angle)
            maximum = np.maximum if _array(i) or _array(j) else max
            rx = maximum(3*s.vertex_spacing, step*(.72+.21*_hash(i,j,s.seed+7)))
            ry = maximum(3*s.vertex_spacing, step*(.57+.28*_hash(i,j,s.seed+8)))
            if s.biome == 'snow':
                ry = maximum(3*s.vertex_spacing, ry*.77)
            q = (xx/rx)**2+(yy/ry)**2
            bump = _clip(1-q, 0., 1.)**3
            sign = 2*_hash(i,j,s.seed+9)-1
            if s.biome == 'volcanic':
                sign -= .13  # shallow subsidence between irregular ash banks
            active = _hash(i,j,s.seed+10) < .83
            value += bump * sign * (1.15+.65*_hash(i,j,s.seed+11)) * active
    value += .22*coherent(u,v,step*1.8,s.seed+12)+.12*coherent(u,v,step*.85,s.seed+13)
    return value * regional * amplitude * s.strength


def path_distance(e, n, points):
    result = (e+n)*0.+float('inf')
    for (x,y),(xx,yy) in zip(points, points[1:]):
        dx,dy=xx-x,yy-y;length=dx*dx+dy*dy
        if not length:
            continue
        t=_clip(((e-x)*dx+(n-y)*dy)/length,0.,1.)
        hypot=np.hypot if _array(t) else math.hypot
        d=hypot(e-x-t*dx,n-y-t*dy)
        result=np.minimum(result,d) if _array(d) else min(result,d)
    return result


class Protection:
    """World-metre masks. Zero is protected; roads retain gentler variation."""
    def __init__(self):
        self.shapes=[]

    def circle(self, e, n, radius, falloff=8):
        self.shapes.append(('circle',(e,n,radius),max(.1,falloff),0.))
        return self

    def box(self, e0, n0, e1, n1, falloff=10):
        self.shapes.append(('box',(min(e0,e1),min(n0,n1),max(e0,e1),max(n0,n1)),max(.1,falloff),0.))
        return self

    def road(self, points, width, falloff=10, minimum=.4):
        self.shapes.append(('road',(tuple(map(tuple,points)),width),max(.1,falloff),minimum))
        return self

    def __call__(self,e,n):
        if _array(e) or _array(n):
            e,n=np.broadcast_arrays(np.asarray(e,float),np.asarray(n,float))
        result=(e+n)*0.+1.
        for kind,data,fade,minimum in self.shapes:
            if kind=='circle':
                x,y,r=data;hypot=np.hypot if _array(e) or _array(n) else math.hypot;d=hypot(e-x,n-y)-r
            elif kind=='box':
                x0,y0,x1,y1=data
                d=np.maximum.reduce([x0-e,e-x1,y0-n,n-y1]) if _array(e) or _array(n) else max(x0-e,e-x1,y0-n,n-y1)
            else:
                points,width=data;d=path_distance(e,n,points)-width/2
            gain=minimum+(1-minimum)*smooth(d/fade)
            result=np.minimum(result,gain) if _array(gain) else min(result,gain)
        return result


class DetailedHeight:
    def __init__(self,base,settings,protection=None,slope_limit=True):
        self.base=base.base if isinstance(base,DetailedHeight) else base
        self.settings=settings;self.protection=protection;self.slope_limit=slope_limit

    def __call__(self,x,y):
        h=sample(self.base,x,y);gain=1.
        if self.slope_limit:
            d=self.settings.vertex_spacing
            dx=(sample(self.base,x+d,y)-sample(self.base,x-d,y))/(2*d);dy=(sample(self.base,x,y+d)-sample(self.base,x,y-d))/(2*d)
            hypot=np.hypot if _array(dx) or _array(dy) else math.hypot
            gain*=1-smooth((hypot(dx,dy)-.25)/.3)
        if self.protection is not None:
            gain*=self.protection(-y,x)
        return h+field(-y,x,self.settings)*gain


def sample(callback,x,y):
    """Batch vector-aware samplers, with a scalar fallback for legacy authors."""
    if not (_array(x) or _array(y)):
        return callback(x,y)
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
    try:
        result=callback(x,y)
        return np.broadcast_to(np.asarray(result,float),x.shape)
    except (TypeError,ValueError):
        return np.fromiter((callback(float(a),float(b)) for a,b in zip(x.flat,y.flat)),float,count=x.size).reshape(x.shape)


def prepare(base, cfg=None, *, settings=None, protection=None, slope_limit=True):
    """Wrap a fresh base; rewrapping replaces detail rather than stacking it."""
    s=settings or Settings.from_config(cfg or {})
    original=base.base if isinstance(base,DetailedHeight) else base
    if not s.enabled or s.flat:
        return original
    if protection is None and cfg is not None:
        protection=config_protection(cfg)
    return DetailedHeight(original,s,protection,slope_limit)


def config_protection(cfg, placed=(), world=None):
    """Infer safe masks for native serializers; custom sites can add exact masks.

    Native placement bounds are ADT coordinates. Legacy OSRS config geometry is
    converted with the generator's existing world transform supplied by caller.
    """
    mask=Protection();center=(1600/3)*32
    for p in placed:
        b=p.get('bounds')
        if not b:
            continue
        asset=p.get('asset','').lower()
        if asset.endswith('.wmo') or any(k in asset for k in ('stable','blacksmith','windmill','house','barn','bridge')):
            mask.box(b[0]-center,center-b[5],b[3]-center,center-b[2],12)
        else:
            # Keep the already grounded native base stable, without flattening
            # the entire canopy/branch bounding box of every tree.
            e,n=-p.get('y',center-(b[0]+b[3])/2),p.get('x',center-(b[2]+b[5])/2)
            radius=max(.8,min(4.,min(b[3]-b[0],b[5]-b[2])*.28))
            mask.circle(e,n,radius,7)
    if world is not None:
        def en(point):
            x,y=world(*point);return (-y,x)
        scale=cfg.get('scale',{}).get('units_per_tile',cfg.get('osrs_scale') or 1.)
        for road in cfg.get('roads',[]):
            mask.road([en(p) for p in road['points']],road.get('width_tiles',road.get('width',4))*scale)
        for p in cfg.get('paved',[]):
            rect=p.get('rect')
            if rect:
                a,b=en(rect[:2]),en(rect[2:]);mask.box(*a,*b,7)
        river=cfg.get('river')
        if river:
            points=river.get('points',river.get('centerline',[]))
            if len(points)>1:
                width=(river.get('width_tiles',3)+2*river.get('bank_width_tiles',2.5))*scale
                mask.road([en(p) for p in points],width,8,minimum=0.)
    for p in cfg.get('ground_detail',{}).get('protected',[]) if isinstance(cfg.get('ground_detail',{}),dict) else []:
        if p['kind']=='circle':mask.circle(*p['center'],p['radius'],p.get('falloff',8))
        elif p['kind']=='box':mask.box(*p['bounds'],p.get('falloff',10))
        else:raise ValueError('Unknown protected-surface shape')
    return mask
