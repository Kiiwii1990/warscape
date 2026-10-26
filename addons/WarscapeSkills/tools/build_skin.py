"""Slice the user-supplied Stage 2A reference locally into reusable WoW textures.

Usage: python build_skin.py <approved-reference.png>
Requires Pillow. Produces uncompressed 32-bit, power-of-two TGA assets, not a
flattened UI. No generated icons, labels, levels, bars or fake skill data remain.
"""
from pathlib import Path
import sys
from PIL import Image, ImageDraw

output = Path(__file__).resolve().parents[1] / 'art'
output.mkdir(exist_ok=True)
source = Image.open(sys.argv[1]).convert('RGBA')
assert source.size == (1312, 1199), 'Use the approved, full-resolution reference'


def save(name, image, size=None):
    if size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    image.save(output / (name + '.tga'), compression=None)


stone = source.crop((420, 680, 538, 753))
stone.putalpha(255)
save('Stone', stone, (128, 128))


def blank_frame(box, edge, name, canvas_size):
    image = source.crop(box)
    w, h = image.size
    # Replace the entire interior (including all illustrated text/icons/XP).
    interior = stone.resize((w - 2 * edge, h - 2 * edge), Image.Resampling.LANCZOS)
    image.paste(interior, (edge, edge))
    canvas = Image.new('RGBA', canvas_size)
    canvas.paste(image, (0, 0))
    save(name, canvas)


blank_frame((144, 488, 550, 643), 16, 'Cell', (512, 256))
blank_frame((143, 980, 974, 1082), 20, 'Total', (1024, 128))

# Each polygon traces only the metal silhouette, removing the screenshot scene.
# Supersample the matte for clean antialiased edges at normal UI scale.
def ornament(box, points, name, size):
    image = source.crop(box)
    mask = Image.new('L', (image.width * 4, image.height * 4))
    ImageDraw.Draw(mask).polygon([((x-box[0])*4, (y-box[1])*4) for x, y in points], fill=255)
    mask = mask.resize(image.size, Image.Resampling.LANCZOS)
    image.putalpha(mask)
    if name == 'Dragon':
        # Remove residual blue scene pixels just outside the thin wing silhouette.
        pixels = image.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if b-r > 6 and b > g*0.95:
                    pixels[x, y] = (r, g, b, 0)
    save(name, image, size)


ornament((38, 15, 320, 365), [
    (169,18),(157,43),(134,49),(109,62),(79,90),(58,112),(85,103),
    (65,132),(52,163),(40,207),(63,186),(43,236),(43,281),(57,258),
    (61,303),(68,351),(83,362),(98,333),(102,248),(118,192),
    (145,164),(181,164),(181,144),(216,165),(227,166),(237,159),
    (242,149),(241,141),(238,142),(235,148),(223,148),(209,140),
    (198,130),(194,115),(200,101),(215,96),(236,102),(250,97),(272,85),(289,80),
    (314,44),(295,52),(274,54),(256,49),(246,43),(235,39),
    (222,46),(206,45),(185,41),(167,46)
], 'Dragon', (256, 512))
ornament((60, 928, 284, 1150), [
    (76,930),(104,932),(112,972),(124,1001),(136,1033),(155,1050),
    (179,1067),(197,1055),(188,1077),(220,1104),(275,1145),
    (248,1149),(94,1143),(63,1110),(65,1065),(61,1028),(67,989),(73,965)
], 'Foot', (256, 256))
save('Side', source.crop((74, 350, 144, 930)), (128, 1024))
save('TopRail', source.crop((320, 64, 800, 91)), (512, 32))
save('HeaderRail', source.crop((290, 149, 802, 172)), (512, 32))
save('BottomRail', source.crop((282, 1081, 831, 1145)), (512, 64))

# Native icons will be drawn inside a separate empty silver/bronze socket.
icon = source.crop((157, 665, 285, 794)).resize((128, 128), Image.Resampling.LANCZOS)
ImageDraw.Draw(icon).rectangle((10, 10, 117, 117), fill=(0, 0, 0, 0))
save('Icon', icon)

# The reference close glyph is artwork only; the Lua button owns its behaviour.
save('Close', source.crop((970, 86, 1030, 153)), (64, 64))
track = source.crop((294, 594, 531, 626))
ImageDraw.Draw(track).rectangle((4, 4, track.width-5, track.height-5), fill=(5, 7, 5, 255))
save('Track', track, (256, 32))
print('Built 12 separate reference-derived skin textures locally')
