"""Extract Blizzard's Dwarf end cap and action-bar rail detail; never redraw it.

Usage: py addons/WarscapeHUD/tools/build_art.py --client <effective-game-dir>
Pillow and mpyq are development dependencies. Runtime art is TGA; source PNGs stay in the authoring tree.
"""
from argparse import ArgumentParser
from collections import defaultdict, deque
from io import BytesIO
from pathlib import Path
from statistics import median
import hashlib
import json
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from client_assets import ClientAssets

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
STOPS = [(0, (12, 11, 9)), (64, (48, 39, 26)), (128, (115, 98, 69)),
         (192, (192, 180, 156)), (255, (244, 240, 224))]


def grade_with_stops(image, stops):
    # A pointwise color transform: no resampling, warping, redrawing or alpha edits.
    tables = [[], [], []]
    for value in range(256):
        for (lo, a), (hi, b) in zip(stops, stops[1:]):
            if lo <= value <= hi:
                fraction = (value - lo) / (hi - lo)
                for channel in range(3):
                    tables[channel].append(round(a[channel] + fraction * (b[channel] - a[channel])))
                break
    gray = ImageOps.grayscale(image)
    result = Image.merge('RGB', [gray.point(table) for table in tables]).convert('RGBA')
    result.putalpha(image.getchannel('A'))
    return result


def grade(image):
    # Keep the Blizzard rail's already-approved bronze treatment unchanged.
    return grade_with_stops(image, STOPS)


def luma(rgb):
    return round(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])


def _palette_samples(reference):
    """Build material swatches from the actual, alpha-matted panel ornament."""
    groups = {name: defaultdict(list) for name in ('shadow', 'bronze', 'silver')}
    reference_lumas = []
    for y in range(reference.height):
        for x in range(reference.width):
            r, g, b, alpha = reference.getpixel((x, y))
            if alpha < 128 or (169 <= x <= 183 and 56 <= y <= 70):
                continue  # Eye is sampled separately below.
            color = (r, g, b)
            value = luma(color)
            reference_lumas.append(value)
            bucket = value // 8
            if value <= 72:
                groups['shadow'][bucket].append((value, color))
            if r - g >= 8 and g - b >= 4 and max(r, g, b) - min(r, g, b) <= 120:
                groups['bronze'][bucket].append((value, color))
            if max(r, g, b) - min(r, g, b) <= 36:
                groups['silver'][bucket].append((value, color))

    palettes = {}
    for name, bins in groups.items():
        swatches = []
        for samples in bins.values():
            channel_medians = tuple(median(color[i] for _, color in samples) for i in range(3))
            # Keep a real sampled panel colour, rather than inventing an RGB stop.
            value, color = min(samples, key=lambda item: sum(
                (item[1][i] - channel_medians[i]) ** 2 for i in range(3)))
            swatches.append((value, color))
        if not swatches:
            raise ValueError(f'Warscape panel texture has no {name} palette samples')
        palettes[name] = sorted(swatches)
    return palettes, sorted(reference_lumas)


def _sample_palette(palette, target_luma):
    if target_luma <= palette[0][0]:
        return palette[0][1]
    if target_luma >= palette[-1][0]:
        return palette[-1][1]
    for (lo_luma, lo), (hi_luma, hi) in zip(palette, palette[1:]):
        if lo_luma <= target_luma <= hi_luma:
            t = (target_luma - lo_luma) / max(1, hi_luma - lo_luma)
            return tuple(round(lo[i] + (hi[i] - lo[i]) * t) for i in range(3))
    raise AssertionError('unreachable palette lookup')


def _panel_eye(reference):
    # The luminous eye in the upper-corner Dragon art is centred at (176, 63).
    core = reference.getpixel((176, 63))[:3]
    halo_samples = []
    for y in range(57, 70):
        for x in range(169, 184):
            distance = ((x - 176.5) ** 2 + (y - 63) ** 2) ** 0.5
            color = reference.getpixel((x, y))
            r, g, b, alpha = color
            if (alpha >= 128 and 2 <= distance <= 5 and r - g > 10 and g - b > 10
                    and max(r, g, b) - min(r, g, b) < 170):
                halo_samples.append(color[:3])
    if not halo_samples:
        raise ValueError('Warscape panel eye halo could not be sampled')
    halo = tuple(round(median(color[i] for color in halo_samples)) for i in range(3))
    return core, halo


def grade_gryphon(image, reference):
    """Transfer the panel's actual material palette by source-luminance rank."""
    if reference.size != (256, 512):
        raise ValueError(f'Expected the shared Warscape panel Dragon texture, got {reference.size}')
    source_pixels = image.load()
    palettes, reference_lumas = _palette_samples(reference)
    histogram = [0] * 256
    for y in range(image.height):
        for x in range(image.width):
            pixel = source_pixels[x, y]
            if pixel[3] > 0:
                histogram[luma(pixel[:3])] += 1
    source_count = sum(histogram)
    if not source_count:
        raise ValueError('Blizzard gryphon texture has no visible pixels')
    target_lumas = [0] * 256
    seen = 0
    for source_luma, count in enumerate(histogram):
        if count:
            rank = (seen + count / 2) / source_count
            # Match the panel's deeper shadows, while its upper tonal shoulder
            # gives engraved silver edges room to read at HUD scale.
            if rank > 0.70:
                rank += 0.50 * (rank - 0.70) * (1 - rank) / 0.30
                rank = min(rank, 1.0)
            target_lumas[source_luma] = reference_lumas[round(rank * (len(reference_lumas) - 1))]
            seen += count
    previous = 0
    for source_luma in range(256):
        if histogram[source_luma]:
            previous = target_lumas[source_luma]
        else:
            target_lumas[source_luma] = previous

    result = Image.new('RGBA', image.size)
    pixels = result.load()
    for y in range(image.height):
        for x in range(image.width):
            original = source_pixels[x, y]
            if original[3] == 0:
                pixels[x, y] = original
                continue
            source_luma = luma(original[:3])
            target_luma = target_lumas[source_luma]
            if target_luma < 42:
                category = 'shadow'
            elif target_luma < 132:
                category = 'bronze'
            else:
                category = 'silver'
            swatch = _sample_palette(palettes[category], target_luma)
            # Correct only the sampled swatch's small luminance mismatch. Its
            # reference hue/chroma stays intact while source detail ordering remains.
            correction = target_luma - luma(swatch)
            pixels[x, y] = tuple(max(0, min(255, channel + correction)) for channel in swatch) + (original[3],)

    pixels = result.load()
    source_alpha = image.getchannel('A')
    eye_x, eye_y, radius = 108.0, 65.0, 2.5
    eye_light, halo = _panel_eye(reference)
    for y in range(int(eye_y-radius), int(eye_y+radius)+1):
        for x in range(int(eye_x-radius), int(eye_x+radius)+1):
            if source_alpha.getpixel((x, y)) == 0:
                continue
            distance = ((x-eye_x)**2 + (y-eye_y)**2)**0.5
            if distance > radius:
                continue
            halo_amount = 0.22 * (1 - distance/radius)
            r, g, b, a = pixels[x, y]
            r = round(r*(1-halo_amount) + halo[0]*halo_amount)
            g = round(g*(1-halo_amount) + halo[1]*halo_amount)
            b = round(b*(1-halo_amount) + halo[2]*halo_amount)
            core_amount = 0.88 * max(0, 1-distance/1.15)**2
            r = round(r*(1-core_amount) + eye_light[0]*core_amount)
            g = round(g*(1-core_amount) + eye_light[1]*core_amount)
            b = round(b*(1-core_amount) + eye_light[2]*core_amount)
            pixels[x, y] = (r, g, b, a)
    return result


def prepare_design5(source, texture_size=128):
    """Remove the source's charcoal backdrop and fit its subject to the HUD UV crop.

    RGB values are never graded. A conservative exterior flood fill keys only
    near-neutral charcoal connected to the image border, preserving enclosed
    near-black feather and armor shadows. The silhouette is fitted
    proportionally into the existing normalized HUD UV region. The optional
    512 canvas retains source detail in a 512 x 304 visible region.
    """
    source = source.convert('RGBA')
    width, height = source.size
    total = width * height
    candidate = bytearray(total)
    source_pixels = source.load()
    for y in range(height):
        for x in range(width):
            r, g, b, _alpha = source_pixels[x, y]
            dr, dg, db = r - 14, g - 14, b - 13
            if (dr * dr + dg * dg + db * db <= 12 * 12
                    and max(r, g, b) - min(r, g, b) <= 8):
                candidate[y * width + x] = 1

    background = bytearray(total)
    queue = deque()

    def seed(index):
        if candidate[index] and not background[index]:
            background[index] = 1
            queue.append(index)

    for x in range(width):
        seed(x)
        seed((height - 1) * width + x)
    for y in range(height):
        seed(y * width)
        seed(y * width + width - 1)
    while queue:
        index = queue.popleft()
        y, x = divmod(index, width)
        for dy in (-1, 0, 1):
            ny = y + dy
            if not 0 <= ny < height:
                continue
            for dx in (-1, 0, 1):
                nx = x + dx
                if not 0 <= nx < width:
                    continue
                neighbor = ny * width + nx
                if candidate[neighbor] and not background[neighbor]:
                    background[neighbor] = 1
                    queue.append(neighbor)

    # Discard isolated backdrop specks; the gryphon is one connected silhouette.
    visited = bytearray(total)
    largest = []
    for start in range(total):
        if background[start] or visited[start]:
            continue
        visited[start] = 1
        component = [start]
        queue.append(start)
        while queue:
            index = queue.popleft()
            y, x = divmod(index, width)
            for dy in (-1, 0, 1):
                ny = y + dy
                if not 0 <= ny < height:
                    continue
                for dx in (-1, 0, 1):
                    nx = x + dx
                    if not 0 <= nx < width:
                        continue
                    neighbor = ny * width + nx
                    if not background[neighbor] and not visited[neighbor]:
                        visited[neighbor] = 1
                        component.append(neighbor)
                        queue.append(neighbor)
        if len(component) > len(largest):
            largest = component

    mask_data = bytearray(total)
    for index in largest:
        mask_data[index] = 255
    mask = Image.frombytes('L', (width, height), bytes(mask_data))
    mask = mask.filter(ImageFilter.GaussianBlur(0.45))
    cutout = source.copy()
    cutout.putalpha(mask)
    bounds = mask.point(lambda value: 255 if value > 8 else 0).getbbox()
    cutout = cutout.crop(bounds)

    if texture_size not in (128, 512):
        raise ValueError('Expected the legacy 128 or full-source 512 texture canvas')
    factor=texture_size//128
    visible_height, top = 76*factor, 52*factor
    scale = min(texture_size / cutout.width, visible_height / cutout.height)
    fitted_size = (round(cutout.width * scale), round(cutout.height * scale))
    fitted = cutout.resize(fitted_size, Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (texture_size, texture_size), (0, 0, 0, 0))
    x = (texture_size - fitted.width) // 2
    y = top + (visible_height - fitted.height) // 2
    canvas.alpha_composite(fitted, (x, y))
    return canvas


def main():
    parser = ArgumentParser()
    parser.add_argument('--client', required=True, type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    assets = ClientAssets(args.client)
    panel_reference = Image.open(ROOT.parent / 'WarscapeSkills' / 'art' / 'Dragon.tga').convert('RGBA')
    records = []
    images = []
    design_source_path = ART / 'WarscapeGryphonDesign5Source.png'
    design_source = Image.open(design_source_path).convert('RGBA')
    design_texture = prepare_design5(design_source)
    design_output = 'WarscapeGryphonDesign5.tga'
    design_texture.save(ART / design_output)
    records.append(dict(asset=design_source_path.name,
                        sha256=hashlib.sha256(design_source_path.read_bytes()).hexdigest(),
                        source_size=list(design_source.size),
                        operation='Remove exterior charcoal backdrop; proportional fit to 128 x 76 HUD UV crop',
                        runtime=design_output))
    for name, original, output, crop in [
        ('UI-MainMenuBar-EndCap-Dwarf', 'WarscapeGryphonOriginal.blp', 'WarscapeGryphonWarscape.tga', None),
        ('UI-MainMenuBar-Dwarf', 'WarscapeRailOriginal.blp', 'WarscapeRail.tga', (64, 85, 256, 128)),
    ]:
        path = 'Interface\\MainMenuBar\\' + name + '.blp'
        data, archive = assets.get(path)
        (ART / original).write_bytes(data)
        image = Image.open(BytesIO(data)).convert('RGBA')
        raw = image.crop(crop) if crop else image
        colored = grade_gryphon(raw, panel_reference) if not crop else grade(raw)
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
        if crop:
            # Keep the complete source rail's bronze top bevel and clear its
            # brown fill so the Prayer panel's tiled Stone backdrop shows below.
            trim = Image.new('RGBA', (256, 64), (0, 0, 0, 0))
            trim.alpha_composite(canvas.crop((0, 0, 256, 5)), (0, 0))
            trim_name = 'WarscapeRailTrim.tga'
            trim.save(ART / trim_name)
            records.append(dict(asset=path, archive=archive, sha256=hashlib.sha256(data).hexdigest(),
                                source_size=list(image.size), crop=crop,
                                operation='Preserve original top five rail rows; clear brown center',
                                runtime=trim_name))
        if not crop:
            images = [raw, colored]
    # Compile directly from the supplied high-resolution source. Do not upscale
    # the legacy runtime texture, recolour it or apply a sharpening filter.
    hd_output='WarscapeGryphonDesign5HD.tga'
    prepare_design5(design_source,512).save(ART/hd_output)
    records.append(dict(asset=design_source_path.name,
                        sha256=hashlib.sha256(design_source_path.read_bytes()).hexdigest(),
                        source_size=list(design_source.size),texture_size=[512,512],
                        visible_region=[0,208,512,512],
                        operation='Same source RGB and exterior matte; direct fit to 512 x 304 HUD crop; no sharpening',
                        runtime=hd_output))
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
