"""Additive custom creature DBC/MPQ preparation; no live installation or DB writes."""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from dbc_records import dbc


def bits(value):
    return struct.unpack('<I', struct.pack('<f', value))[0]


def append_row(data, fields, row, added_string=b''):
    rows, strings = dbc(data, fields)
    if len(row) != fields or row[0] in rows:
        raise ValueError('Custom creature DBC ID collision or invalid row')
    if added_string and not added_string.endswith(b'\0'):
        raise ValueError('Unterminated DBC string')
    result = (struct.pack('<4s4I', b'WDBC', len(rows)+1, fields, fields*4,
                          len(strings)+len(added_string))
              + data[20:20+len(rows)*fields*4]
              + struct.pack('<'+'I'*fields, *row) + strings + added_string)
    checked, names = dbc(result, fields)
    if any(checked[k] != v for k, v in rows.items()) or names[:len(strings)] != strings:
        raise ValueError('Existing DBC content changed')
    return result


def validate_files(directory, manifest):
    """Check dependencies and basic model arrays before packing user assets."""
    files = {}
    for entry in manifest['files']:
        name, target = entry['file'], entry['path']
        if Path(name).name != name or '..' in target or not target.startswith('Creature\\'):
            raise ValueError('Invalid asset path')
        raw = (directory/name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry['sha256'] or target in files:
            raise ValueError('Asset hash mismatch or duplicate path')
        files[target] = raw
    model_path = manifest['model_path'].replace('.mdx', '.m2')
    raw = files[model_path]
    if raw[:4] != b'MD20' or struct.unpack_from('<I', raw, 4)[0] != 264:
        raise ValueError('Expected WotLK M2 version 264')
    count, offset = struct.unpack_from('<II', raw, 28)
    if offset+count*64 > len(raw):
        raise ValueError('Invalid animation array')
    clips = set()
    for i in range(count):
        anim, _, _, _, flags = struct.unpack_from('<HHIfI', raw, offset+i*64)
        if not flags & 0x20:
            raise ValueError('External animation dependencies require explicit support')
        clips.add(anim)
    if not {0, 1, 4, 5, 16}.issubset(clips):
        raise ValueError('Required creature animation missing')
    views = struct.unpack_from('<I', raw, 68)[0]
    for i in range(views):
        skin = files[model_path[:-3]+f'{i:02}.skin']
        if skin[:4] != b'SKIN':
            raise ValueError('Invalid skin file')
    count, offset = struct.unpack_from('<II', raw, 80)
    if offset+count*16 > len(raw):
        raise ValueError('Invalid texture array')
    for i in range(count):
        kind, _, length, start = struct.unpack_from('<4I', raw, offset+i*16)
        if kind != 0 or not length or start+length > len(raw):
            raise ValueError('Unsupported or invalid model texture dependency')
        name = raw[start:start+length].rstrip(b'\0').decode('ascii')
        if files[name][:4] != b'BLP2':
            raise ValueError('Missing BLP2 texture')
    return files


def creature_tables(model_data, display_data, manifest, model):
    models, strings = dbc(model_data, 28)
    displays, _ = dbc(display_data, 16)
    row = models[manifest['model_source']][:]
    row[0] = manifest['model_id']
    row[2] = len(strings)
    row[4] = bits(1)
    row[14] = bits(manifest['collision_width'])
    row[15] = bits(manifest['collision_height'])
    row[16] = bits(0)  # Unmountable creature.
    bounds = struct.unpack_from('<6f', model, 188)
    if not all(math.isfinite(v) for v in bounds) or any(bounds[i] >= bounds[i+3] for i in range(3)):
        raise ValueError('Invalid model collision bounds')
    row[17:23] = [bits(v) for v in bounds]
    model_data = append_row(model_data, 28, row, manifest['model_path'].encode()+b'\0')
    row = displays[manifest['display_source']][:]
    row[0:4] = [manifest['display_id'], manifest['model_id'], 0, 0]
    row[4] = bits(1)
    row[6:10] = [0]*4  # Model uses its embedded explicit texture; no donor skin paths.
    return model_data, append_row(display_data, 16, row)


def main():
    from build_assets import ClientAssets, append, append_spells, merge
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--server-data', type=Path, required=True)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    files = validate_files(args.manifest.parent, manifest)
    pack = json.loads(args.catalogue.read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    assets = ClientAssets(args.client)
    try:
        updates = dict(files)
        model = files[manifest['model_path'].replace('.mdx', '.m2')]
        for source in ('server', 'client'):
            def load(name):
                return ((args.server_data/'dbc'/f'{name}.dbc').read_bytes() if source == 'server'
                        else assets.get(f'DBFilesClient\\{name}.dbc')[0])
            models, displays = creature_tables(load('CreatureModelData'), load('CreatureDisplayInfo'), manifest, model)
            tables = {'CreatureModelData': models, 'CreatureDisplayInfo': displays,
                      'Item': append(load('Item'), pack['items'])}
            if pack.get('client_spells'):
                tables['Spell'] = append_spells(load('Spell'), pack['client_spells'])
            for name, raw in tables.items():
                if source == 'server':
                    (args.output/f'{name}.dbc').write_bytes(raw)
                else:
                    updates[f'DBFilesClient\\{name}.dbc'] = raw
        # Check globally loaded client assets too, including assets outside our patch.
        for path in files:
            try:
                assets.get(path)
            except FileNotFoundError:
                continue
            raise ValueError('Custom asset path already exists in client')
        merge(args.client/'Data/enUS/patch-enUS-Z.MPQ', updates, args.output/'patch-enUS-Z.MPQ')
        print('Prepared additive custom creature, items and patch; original records preserved.')
    finally:
        for _, archive in assets.archives:
            archive.file.close()


if __name__ == '__main__':
    main()
