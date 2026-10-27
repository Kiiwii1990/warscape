"""Extract Blizzard's Dwarf end cap and blank action-bar rail; never redraw them.

Usage: py addons/WarscapeHUD/tools/build_art.py --client <effective-game-dir>
Pillow and mpyq are development dependencies. Only the two TGAs are runtime art.
"""
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageOps, ImageDraw
from client_assets import ClientAssets

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
STOPS = [(0, (12, 11, 9)), (64, (48, 39, 26)), (128, (115, 98, 69)),
         (192, (192, 180, 156)), (255, (244, 240, 224))]


def grade(image):
    # A pointwise color transform: no resampling, warping, redrawing or alpha edits.
    tables = [[], [], []]
    for value in range(256):
        for (lo, a), (hi, b) in zip(STOPS, STOPS[1:]):
            if lo <= value <= hi:
                fraction = (value - lo) / (hi - lo)
                for channel in range(3):
                    tables[channel].append(round(a[channel] + fraction * (b[channel] - a[channel])))
                break
    gray = ImageOps.grayscale(image)
    result = Image.merge('RGB', [gray.point(table) for table in tables]).convert('RGBA')
    result.putalpha(image.getchannel('A'))
    return result


def main():
    parser = ArgumentParser()
    parser.add_argument('--client', required=True, type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    assets = ClientAssets(args.client)
    records = []
    images = []
    for name, original, output, crop in [
        ('UI-MainMenuBar-EndCap-Dwarf', 'WarscapeGryphonOriginal.blp', 'WarscapeGryphonWarscape.tga', None),
        ('UI-MainMenuBar-Dwarf', 'WarscapeRailOriginal.blp', 'WarscapeRail.tga', (64, 85, 256, 128)),
    ]:
        path = 'Interface\\MainMenuBar\\' + name + '.blp'
        data, archive = assets.get(path)
        (ART / original).write_bytes(data)
        image = Image.open(BytesIO(data)).convert('RGBA')
        raw = image.crop(crop) if crop else image
        colored = grade(raw)
        if crop:
            # Power-of-two canvas; Lua crops only the 192 x 43 source region.
            canvas = Image.new('RGBA', (256, 64))
            canvas.paste(colored, (0, 0))
        else:
            canvas = colored
        canvas.save(ART / output)
        records.append(dict(asset=path, archive=archive, sha256=hashlib.sha256(data).hexdigest(),
                            source_size=list(image.size), crop=crop,
                            visible_bounds=list(raw.getchannel('A').getbbox()), runtime=output))
        if not crop:
            images = [raw, colored]
    (ART / 'sources.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    if args.evidence:
        sheet = Image.new('RGB', (840, 290), (27, 29, 27))
        draw = ImageDraw.Draw(sheet)
        for index, image in enumerate(images):
            crop = image.crop((0, 52, 128, 128)).resize((384, 228), Image.Resampling.NEAREST)
            sheet.paste(crop, (20 + index * 420, 30), crop)
        draw.text((20, 10), 'Original Blizzard Dwarf end cap', fill='white')
        draw.text((440, 10), 'Same source pixels and alpha; Warscape palette', fill='white')
        draw.text((20, 266), 'Visible source region: 128 x 76. Identical UV crop and uniform display scale on both sides.', fill='white')
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.evidence)
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
