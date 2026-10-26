"""Check texture compatibility and opacity without launching the WoW client."""
from pathlib import Path
from PIL import Image

art = Path(__file__).resolve().parents[1] / 'art'
files = sorted(art.glob('*.tga'))
assert len(files) == 12
for path in files:
    header = path.read_bytes()[:18]
    assert header[2] == 2, f'{path.name}: must be uncompressed true-color TGA'
    assert header[16] == 32 and header[17] & 15 == 8, f'{path.name}: missing 8-bit alpha'
    image = Image.open(path)
    assert image.mode == 'RGBA'
    for dimension in image.size:
        assert 0 < dimension <= 1024 and dimension & (dimension - 1) == 0
assert Image.open(art / 'Stone.tga').getchannel('A').getextrema() == (255, 255)
for name in ('Dragon', 'Foot', 'Icon'):
    assert Image.open(art / (name+'.tga')).getchannel('A').getextrema() == (0, 255)
assert Image.open(art / 'Cell.tga').getpixel((200, 70))[3] == 255
assert Image.open(art / 'Total.tga').getpixel((400, 60))[3] == 255
print('PASS: 12 WoW-compatible RGBA TGA textures, opaque stone/cells, transparent ornament mattes')
