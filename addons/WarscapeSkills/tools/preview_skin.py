"""Render the real Lua layout locally with sample data (not an in-game capture).

Requires Pillow, mpyq and lupa. Client textures/fonts are read locally for preview
only; they are never copied into the addon. Output stays in the ignored build dir.
"""
from pathlib import Path
from io import BytesIO
import argparse
import re
import runpy
from PIL import Image, ImageDraw, ImageFont
import mpyq

parser = argparse.ArgumentParser()
parser.add_argument('--client', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / 'tests/test_addon.py'))['lua']
lua.execute('''
local events
for _, w in ipairs(widgets) do if w.scripts.OnEvent then events=w end end
clock = 20
events.scripts.OnEvent(events, "PLAYER_LOGIN")
local token=string.match(messages[#messages][2], "HELLO|1|(.+)")
local function recv(m)
    events.scripts.OnEvent(events,"CHAT_MSG_ADDON","WCSkills",m,"WHISPER","Tester")
end
recv("B|1|"..token.."|1|7")
local skills={
    {"attack",50,105000,101333,111945}, {"strength",99,13034431,13034431,"-"},
    {"defence",50,105000,101333,111945}, {"hitpoints",12,1700,1584,1833},
    {"ranged",1,0,0,83}, {"magic",1,0,0,83}, {"prayer",1,0,0,83}
}
for _, s in ipairs(skills) do
    recv("S|1|"..token.."|1|"..s[1].."|"..s[2].."|-|"..s[3].."|"..s[4].."|"..s[5])
end
recv("E|1|"..token.."|1")
WarscapeSkillsFrame:Show()
''')
widgets = list(lua.globals().widgets.values())
archives = [mpyq.MPQArchive(str(p), listfile=False) for p in
            list((args.client/'Data/enUS').glob('*.MPQ')) + list((args.client/'Data').glob('*.MPQ'))]


def native(path):
    for archive in archives:
        data = archive.read_file(path)
        if data:
            return data
    raise FileNotFoundError(path)


font_data = native(r'Fonts\FRIZQT__.TTF')
scale = 2
canvas = Image.new('RGBA', (1100, 1100), (35, 47, 34, 255))
draw = ImageDraw.Draw(canvas)
for y in range(0, 1100, 32):
    for x in range(0, 1100, 32):
        if (x//32+y//32) % 2:
            draw.rectangle((x, y, x+31, y+31), fill=(47, 58, 43, 255))

factors = {'TOPLEFT':(0,0),'TOP':(.5,0),'TOPRIGHT':(1,0),'LEFT':(0,.5),
           'CENTER':(.5,.5),'RIGHT':(1,.5),'BOTTOMLEFT':(0,1),'BOTTOM':(.5,1),'BOTTOMRIGHT':(1,1)}


def children(w):
    # Lua table identity must be compared in Lua (Python wrappers are not stable).
    equal = lua.eval('function(a,b) return a==b end')
    return [c for c in widgets if c.parent is not None and equal(c.parent, w)]


def text_size(w):
    text = re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', str(w.text or ''))
    font = ImageFont.truetype(BytesIO(font_data), round((w.fontSize or 10)*scale))
    bbox = font.getbbox(text)
    return font, text, font.getlength(text)/scale, (bbox[3]-bbox[1])/scale


def rect(w, parent_rect):
    width, height = w.width or 0, w.height or 0
    if w.kind == 'FontString':
        _, _, width, height = text_size(w)
    p = list(w.point.values()) if w.point else ['TOPLEFT', 0, 0]
    point = p[0]
    if len(p) >= 5:
        relative, dx, dy = p[2], p[3], p[4]
    else:
        relative = point
        dx, dy = (p[1:3] if len(p) >= 3 else (0, 0))
    ax, ay = factors[point]
    rx, ry = factors[relative]
    px, py, pw, ph = parent_rect
    return (px+pw*rx+dx-width*ax, py+ph*ry-dy-height*ay, width, height)


def image_asset(path):
    path = str(path)
    if path.startswith('Interface\\AddOns\\WarscapeSkills\\'):
        return Image.open(root / (path.split('WarscapeSkills\\', 1)[1].replace('\\', '/')+'.tga')).convert('RGBA')
    return Image.open(BytesIO(native(path+'.blp'))).convert('RGBA')


def composite(image, r):
    x, y, width, height = [round(v*scale) for v in r]
    if width > 0 and height > 0:
        canvas.alpha_composite(image.resize((width, height), Image.Resampling.LANCZOS), (x, y))


def render(w, r):
    if w.shown is False:
        return
    if w.backdrop:
        b = w.backdrop
        left, right, top, bottom = [b.insets[k] for k in ('left', 'right', 'top', 'bottom')]
        image = image_asset(b.bgFile)
        target = Image.new('RGBA', (round((r[2]-left-right)*scale), round((r[3]-top-bottom)*scale)))
        tile = image.resize((200,200), Image.Resampling.LANCZOS)
        for y in range(0, target.height, 200):
            for x in range(0, target.width, 200):
                target.paste(tile, (x,y))
        canvas.alpha_composite(target, (round((r[0]+left)*scale), round((r[1]+top)*scale)))
    if w.kind == 'Texture' and w.texture:
        image = image_asset(w.texture[1])
        if w.uv:
            u1,u2,v1,v2 = list(w.uv.values())
            image = image.crop((round(min(u1,u2)*image.width), round(min(v1,v2)*image.height),
                                round(max(u1,u2)*image.width), round(max(v1,v2)*image.height)))
            if u1 > u2:
                image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        composite(image, r)
    if w.kind == 'StatusBar' and w.value and w.value > 0:
        color = tuple(round(c*255) for c in w.barColor.values())+(255,)
        image = Image.new('RGBA', (2, 2), color)
        composite(image, (r[0], r[1], r[2]*w.value, r[3]))
    if w.kind == 'Button' and w.normalTexture:
        composite(image_asset(w.normalTexture), r)
    if w.kind == 'FontString' and w.text:
        font, text, _, _ = text_size(w)
        color = tuple(round(c*255) for c in w.color.values()) if w.color else (220, 213, 190)
        xy = (round(r[0]*scale), round(r[1]*scale))
        draw.text((xy[0]+2,xy[1]+2), text, font=font, fill=(0,0,0), anchor='lt')
        current, x = color, xy[0]
        for segment in re.split(r'(\|c[0-9a-fA-F]{8}|\|r)', str(w.text)):
            if segment == '|r':
                current = color
            elif segment.startswith('|c'):
                current = tuple(int(segment[i:i+2], 16) for i in (4, 6, 8))
            else:
                draw.text((x, xy[1]), segment, font=font, fill=current, anchor='lt')
                x += font.getlength(segment)
    layers = {'BACKGROUND':0, 'BORDER':1, 'ARTWORK':2, 'OVERLAY':3}
    cs = children(w)
    regions = [c for c in cs if c.kind in ('Texture', 'FontString')]
    for child in sorted(regions, key=lambda c:layers.get(c.layer, 1)):
        render(child, rect(child, r))
    for child in cs:
        if child.kind not in ('Texture', 'FontString'):
            render(child, rect(child, r))


panel = lua.globals().WarscapeSkillsFrame
render(panel, (25, 12, panel.width, panel.height))
args.output.parent.mkdir(parents=True, exist_ok=True)
canvas.convert('RGB').save(args.output)
print('Local Lua-layout preview:', args.output)
