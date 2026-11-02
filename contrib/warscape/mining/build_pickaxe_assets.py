"""Stage additive pickaxe assets; never write to the installed client/server."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'addons/WarscapeHUD/tools'))
from client_assets import ClientAssets as BaseClientAssets
from copper_depletion_assets import encode_raw_blp, _dds_header, validate_skin_profile
from deploy_sandbox import archive_entries
from generate import archive

CLIENT = Path(r'C:\WoWDev\wowdecomp\bin\Win')
SERVER = Path(r'C:\WoWDev\TrinityServer')
WEAPON = 'Item\\ObjectComponents\\Weapon\\'
MODEL = WEAPON + 'Axe_1H_Pick_A_01.m2'
SKIN = WEAPON + 'Axe_1H_Pick_A_0100.skin'
DIFFUSE = WEAPON + 'Axe_1H_Pick_A_01Brown.blp'
ICON = r'Interface\Icons\INV_Pick_02.blp'
TIERS = ((900220, 'Bronze'), (900221, 'Iron'), (900222, 'Steel'))


class ClientAssets(BaseClientAssets):
    def __init__(self, game):
        super().__init__(game)
        # Warscape letter patches override Blizzard numeric patches. Keep this
        # correction local; other sessions may be using the shared reader.
        def custom_priority(pair):
            path = pair[0]
            suffix = path.stem.rsplit('-', 1)[-1].lower()
            rank = ord(suffix) if path.stem.lower().startswith('patch-') and len(suffix) == 1 and suffix.isalpha() else 0
            return rank, path.parent.name.lower() == 'enus' if rank else False
        self.archives.sort(key=custom_priority, reverse=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dbc(data, fields):
    magic, count, actual, width, length = struct.unpack_from('<4s4I', data)
    if magic != b'WDBC' or actual != fields or width != fields * 4 or len(data) != 20 + count * width + length:
        raise ValueError('Unexpected DBC format or length')
    rows = {}
    for index in range(count):
        row = list(struct.unpack_from(f'<{fields}I', data, 20 + index * width))
        if row[0] in rows:
            raise ValueError('Duplicate DBC ID')
        rows[row[0]] = row
    return rows, data[20 + count * width:]


def string(strings, offset):
    end = strings.find(b'\0', offset)
    if offset >= len(strings) or end < 0:
        raise ValueError('DBC string offset out of range')
    return strings[offset:end].decode('ascii')


def append_dbc(data, fields, source_id):
    rows, strings = dbc(data, fields)
    count = len(rows)
    base = rows[source_id]
    added = bytearray()
    for entry, tier in TIERS:
        if entry in rows:
            raise ValueError(f'DBC ID already occupied: {entry}')
        row = base.copy()
        row[0] = entry
        if fields == 8:
            row[5] = entry  # Item.displayInfoID
        else:
            for field, value in ((3, f'WarscapePickaxe{tier}'), (5, f'INV_Warscape_Pickaxe_{tier}')):
                row[field] = len(strings)
                strings += value.encode('ascii') + b'\0'
        added += struct.pack(f'<{fields}I', *row)
    result = struct.pack('<4s4I', b'WDBC', count + 3, fields, fields * 4, len(strings))
    result += data[20:20 + count * fields * 4] + added + strings
    checked, checked_strings = dbc(result, fields)
    assert all(checked[key] == value for key, value in rows.items())
    assert checked_strings.startswith(dbc(data, fields)[1])
    return result


def decode(payload):
    if len(payload) < 1172 or payload[:4] != b'BLP2' or struct.unpack_from('<I', payload, 4)[0] != 1:
        raise ValueError('Expected BLP2 version 1')
    encoding, alpha, preferred, flags = payload[8:12]
    w, h = struct.unpack_from('<II', payload, 12)
    if not w or not h or max(w, h) > 16384:
        raise ValueError('Invalid BLP dimensions')
    levels = max(w, h).bit_length() if flags & 1 else 1
    result = []
    for level in range(levels):
        width, height = max(1, w >> level), max(1, h >> level)
        offset = struct.unpack_from('<I', payload, 20 + level * 4)[0]
        size = struct.unpack_from('<I', payload, 84 + level * 4)[0]
        if offset < 1172 or offset + size > len(payload):
            raise ValueError('Invalid BLP mip range')
        raw = payload[offset:offset + size]
        if encoding == 3:
            if size != width * height * 4:
                raise ValueError('Invalid raw BLP mip size')
            image = Image.frombytes('RGBA', (width, height), raw, 'raw', 'BGRA')
        elif encoding == 2 and preferred in (0, 1, 7):
            fourcc = {0: b'DXT1', 1: b'DXT3', 7: b'DXT5'}[preferred]
            expected = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * (8 if preferred == 0 else 16)
            if size != expected:
                raise ValueError('Invalid compressed BLP mip size')
            image = Image.open(io.BytesIO(_dds_header(width, height, fourcc) + raw)).convert('RGBA')
        else:
            raise ValueError('Unsupported BLP encoding')
        result.append(image)
    return result, alpha


def metal_mask(image, icon):
    mask = Image.new('L', image.size)
    if icon:
        # Main pick head, plus the small metal socket where it meets the handle.
        # Keep the wooden handle and its bindings outside both masks.
        ImageDraw.Draw(mask).polygon([(4,45),(25,20),(35,11),(44,7),(49,8),
                                      (46,18),(33,27),(24,48),(12,53)], fill=255)
        ImageDraw.Draw(mask).polygon([(32,27),(35,24),(38,25),(40,28),
                                      (40,31),(38,34),(35,34),(32,31)], fill=255)
    else:
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = image.getpixel((x,y))
                if y < 32 or (max(r,g,b) - min(r,g,b) < 24 and r > 40):
                    mask.putpixel((x,y), 255)
        # This UV island is the narrow metal socket at the head/handle joint.
        # The neighboring lower-left UV island is the wrapped handle binding;
        # leave it unchanged. Keep this polygon to the socket's x=50..61 region.
        ImageDraw.Draw(mask).polygon([(50,36),(53,34),(58,35),(61,39),
                                      (61,48),(58,52),(53,52),(50,48)], fill=255)
    return mask


def recolor(mips, tier, icon):
    palettes = {'Bronze': ('#281b10', '#d6a364'),
                'Iron': ('#16191c', '#a6acb1'),
                'Steel': ('#30383e', '#f4f7fb')}
    mask = metal_mask(mips[0], icon)
    output = []
    for source in mips:
        colored = ImageOps.colorize(ImageOps.grayscale(source.convert('RGB')), *palettes[tier]).convert('RGBA')
        mixed = Image.composite(colored, source, mask.resize(source.size, Image.Resampling.BOX))
        mixed.putalpha(source.getchannel('A'))
        output.append(mixed)
    return output


def merge(existing, updates, destination):
    values = archive_entries(existing)
    originals = {name: sha(data) for name, data in values.items()}
    for name, data in updates.items():
        # Avoid differently-cased duplicate MPQ keys.
        previous = next((key for key in values if key.lower() == name.lower()), None)
        if previous:
            del values[previous]
        values[name] = data
    archive(destination, values)
    readback = archive_entries(destination)
    changed = {name.lower() for name in updates}
    assert all(sha(readback[name]) == digest for name, digest in originals.items() if name.lower() not in changed)
    return {'source_sha256': sha(existing.read_bytes()), 'preserved_entries': len(originals) - sum(name.lower() in changed for name in originals)}


def build(output, client=CLIENT, server=SERVER):
    output.mkdir(parents=True, exist_ok=False)
    assets = ClientAssets(client)
    try:
        model = assets.get(MODEL)[0]
        profile = validate_skin_profile(assets.get(SKIN)[0], model)
        # Validate every static model texture dependency; type 2 is the tier diffuse.
        count, offset = struct.unpack_from('<II', model, 80)
        dependencies = [MODEL, SKIN]
        for i in range(count):
            kind, _, length, start = struct.unpack_from('<4I', model, offset + i * 16)
            if kind == 0 and length:
                if start + length > len(model):
                    raise ValueError('M2 texture filename outside model')
                name = model[start:start + length].rstrip(b'\0').decode('ascii')
                assets.get(name)
                dependencies.append(name)
        icon_mips, icon_alpha = decode(assets.get(ICON)[0])
        skin_mips, skin_alpha = decode(assets.get(DIFFUSE)[0])
        if icon_mips[0].size != (64, 64) or skin_mips[0].size != (128, 64):
            raise ValueError('Original pickaxe dimensions changed; inspect before applying metal masks')
        updates = {}
        proof = Image.new('RGB', (640, 270), '#171717')
        draw = ImageDraw.Draw(proof)
        for index, (entry, tier) in enumerate(TIERS):
            for is_icon, mips, alpha, name in (
                (True, icon_mips, icon_alpha, f'Interface\\Icons\\INV_Warscape_Pickaxe_{tier}.blp'),
                (False, skin_mips, skin_alpha, WEAPON + f'WarscapePickaxe{tier}.blp')):
                colored = recolor(mips, tier, is_icon)
                updates[name] = encode_raw_blp(colored, alpha)
                decoded, _ = decode(updates[name])
                assert len(decoded) == len(mips)
                assert all(a.tobytes() == b.tobytes() for a,b in zip(decoded, colored))
                assert all(a.getchannel('A').tobytes() == b.getchannel('A').tobytes() for a,b in zip(decoded, mips))
                target = output / 'payload' / Path(name.replace('\\', '/'))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(updates[name])
                colored[0].save(output / f'{tier}-{ "icon" if is_icon else "weapon"}.png')
                preview = colored[0].resize((128,128) if is_icon else (192,96), Image.Resampling.NEAREST)
                proof.paste(preview, (index * 212 + 8, 28 if is_icon else 168), preview)
            draw.text((index * 212 + 8, 8), f'{tier} ({entry})', fill='white')
        proof.save(output / 'pickaxe-art-review.png')
        tables = {}
        server_sources = {}
        for name, fields, base in (('Item', 8, 2901), ('ItemDisplayInfo', 25, 6568)):
            source = assets.get(f'DBFilesClient\\{name}.dbc')[0]
            table = append_dbc(source, fields, base)
            tables[f'DBFilesClient\\{name}.dbc'] = table
            (output / f'{name}.dbc').write_bytes(table)
            server_source = (server / 'dbc' / f'{name}.dbc').read_bytes()
            server_sources[f'{name}.dbc'] = sha(server_source)
            (output / f'server-{name}.dbc').write_bytes(append_dbc(server_source, fields, base))
        archive(output / 'patch-WarscapePickaxes.MPQ', updates)
        archive(output / 'patch-enUS-WarscapePickaxes.MPQ', tables)
        root_merge = merge(client / 'Data/patch-Z.MPQ', updates, output / 'patch-Z.MPQ')
        locale_merge = merge(client / 'Data/enUS/patch-enUS-Z.MPQ', tables, output / 'patch-enUS-Z.MPQ')
        manifest = {'tiers': TIERS, 'dependencies': dependencies, 'skin': profile,
                    'server_source_sha256': server_sources,
                    'source_icon_sha256': sha(assets.get(ICON)[0]),
                    'source_diffuse_sha256': sha(assets.get(DIFFUSE)[0]),
                    'root_merge': root_merge, 'locale_merge': locale_merge,
                    'files': {name: sha(data) for name,data in {**updates, **tables}.items()}}
        (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        return manifest
    finally:
        for _, opened in assets.archives:
            opened.file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.output)
    print(f'Staged {len(result["tiers"])} tiers; six textures, additive DBCs, two preserved MPQ merges. No deployment.')
