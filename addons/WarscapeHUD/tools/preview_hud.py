"""Render the Lua geometry and source artwork, not a client/gameplay preview.

The minimap is an empty circle because this tool does not run the native map
renderer. Use the custom client for the user's final visual acceptance.
"""
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
import runpy
from PIL import Image, ImageDraw, ImageChops
from client_assets import ClientAssets

ROOT = Path(__file__).resolve().parents[1]
parser = ArgumentParser()
parser.add_argument('--client', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
assets = ClientAssets(args.client)
lua = runpy.run_path(str(ROOT / 'tests/test_hud.py'))['lua']
lua.execute('''
UIParent:SetScale(1); UIParent:SetSize(1920,1080)
WarscapeHUDScales = {hud=1,skills=1}
for _, f in ipairs(widgets) do
    if f.events.PLAYER_LOGIN then f.scripts.OnEvent(f, "PLAYER_LOGIN") end
end
MinimapCompassTexture:Hide()
MinimapNorthTag:SetTexture("Interface\\\\Minimap\\\\CompassNorthTag")
MinimapNorthTag.layer = "OVERLAY"
for _, pair in ipairs({{MinimapZoomIn,"ZoomIn"},{MinimapZoomOut,"ZoomOut"}}) do
    local b = pair[1]; b:SetSize(32,32); b:SetFrameLevel(6)
    local t = b:CreateTexture(nil,"ARTWORK")
    t:SetTexture("Interface\\\\Minimap\\\\UI-Minimap-"..pair[2].."Button-Up")
    t:SetAllPoints(b)
end
for i,w in ipairs(widgets) do w.previewId = i end
''')
widgets = list(lua.globals().widgets.values())
assembly = lua.globals().WarscapeHUDAssembly
regions = {}
cache = {}
factors = {'TOPLEFT':(0,1),'TOP':(.5,1),'TOPRIGHT':(1,1),
           'LEFT':(0,.5),'CENTER':(.5,.5),'RIGHT':(1,.5),
           'BOTTOMLEFT':(0,0),'BOTTOM':(.5,0),'BOTTOMRIGHT':(1,0)}


def rect(w):
    key = w.previewId
    if key in cache:
        return cache[key]
    if key == assembly.previewId:
        result = (0, 0, w.width, w.height)
    elif w.allPoints:
        result = rect(w.allPoints)
    else:
        p = list(w.point.values()) if w.point else ['BOTTOMLEFT', w.parent, 'BOTTOMLEFT', 0, 0]
        rx, ry, rw, rh = rect(p[1])
        ax, ay = factors[p[0]]
        bx, by = factors[p[2]]
        width, height = w.width or 0, w.height or 0
        result = (rx + bx * rw + p[3] - ax * width,
                  ry + by * rh + p[4] - ay * height, width, height)
    cache[key] = result
    return result


def descendant(w):
    if w.previewId == assembly.previewId:
        return True
    return w.parent is not None and descendant(w.parent)


def shown(w):
    return w.shown is not False and (w.previewId == assembly.previewId or shown(w.parent))


def asset(path):
    prefix = 'Interface\\AddOns\\'
    if path.startswith(prefix):
        local = ROOT.parent / path[len(prefix):].replace('\\', '/')
        if not local.suffix:
            local = local.with_suffix('.tga')
        return Image.open(local).convert('RGBA')
    data, _ = assets.get(path + ('' if path.lower().endswith('.blp') else '.blp'))
    return Image.open(BytesIO(data)).convert('RGBA')


scale, margin, caption = 2, 16, 38
canvas = Image.new('RGBA', (round(assembly.width * scale) + 2 * margin,
                            round(assembly.height * scale) + margin + caption), (38, 45, 38, 255))
draw = ImageDraw.Draw(canvas)
draw.text((margin, 10), 'OFFLINE LUA GEOMETRY / ORIGINAL ASSET PROOF — minimap contents are not rendered', fill=(240,220,160))


def pixel_rect(w):
    x, y, width, height = rect(w)
    return (round(margin + x * scale), round(caption + (assembly.height - y - height) * scale),
            max(1, round(width * scale)), max(1, round(height * scale)))


for w in widgets:
    if descendant(w) and shown(w):
        if w.texture and w.kind == 'Texture':
            level = w.parent.level or 1
            layer = {'BACKGROUND':0,'BORDER':1,'ARTWORK':2,'OVERLAY':3}.get(w.layer, 1)
            regions.setdefault((level, layer), []).append(w)
        elif w.name == 'Minimap':
            regions.setdefault((w.level, 0), []).append(w)

for key in sorted(regions):
    for w in regions[key]:
        x, y, width, height = pixel_rect(w)
        if w.name == 'Minimap':
            draw.ellipse((x,y,x+width-1,y+height-1), fill=(16,21,16))
            continue
        im = asset(w.texture)
        if w.texcoord:
            u1,u2,v1,v2 = list(w.texcoord.values())
            im = im.crop((round(min(u1,u2)*im.width), round(min(v1,v2)*im.height),
                          round(max(u1,u2)*im.width), round(max(v1,v2)*im.height)))
            if u1 > u2:
                im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if w.color:
            color = list(w.color.values())
            tint = tuple(round(v*255) for v in color[:3]) + (255,)
            im = ImageChops.multiply(im, Image.new('RGBA', im.size, tint))
        canvas.alpha_composite(im.resize((width,height), Image.Resampling.LANCZOS), (x,y))
args.output.parent.mkdir(parents=True, exist_ok=True)
canvas.convert('RGB').save(args.output)
print(args.output.resolve())
