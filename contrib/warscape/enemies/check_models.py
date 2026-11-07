"""Read-only WotLK model capability audit; known Cow animation gap is explicit."""
import argparse
import json
import struct
from pathlib import Path
from build_assets import ClientAssets, dbc


def audit(client):
    releases = json.loads(Path(__file__).with_name('releases.json').read_text())
    enemies = [enemy for release in releases for enemy in json.loads(Path(__file__).with_name(release['data']).read_text(encoding='utf-8'))['enemies']]
    assets = ClientAssets(client)
    try:
        def table(name):
            data = assets.get('DBFilesClient\\' + name + '.dbc')[0]
            return dbc(data, struct.unpack_from('<I', data, 8)[0])
        displays, _ = table('CreatureDisplayInfo')
        models, strings = table('CreatureModelData')
        items, _ = table('Item')
        checked = {}
        for enemy in enemies:
            for equipped in enemy.get('equipment', []):
                if equipped and (equipped not in items or items[equipped][6] not in {13,14,15,17,21,22,23,25,26}):
                    raise ValueError('Enemy equipment is absent from Item.dbc or not hand-equipable')
            display = enemy['model']
            model = models[displays[display][1]]
            offset = model[2]
            path = strings[offset:strings.index(b'\0', offset)].decode().replace('.mdx', '.m2')
            if path.lower() != enemy['model_path'].lower():
                raise ValueError(f"Display {display}: expected {enemy['model_path']}; found {path}")
            if display in checked:
                if checked[display] != enemy['native_attack_animation']:
                    raise ValueError('Repeated display has inconsistent animation metadata')
                continue
            raw = assets.get(path)[0]
            if raw[:4] != b'MD20':
                raise ValueError('Unexpected model format')
            count, offset = struct.unpack_from('<II', raw, 28)
            if offset + count * 64 > len(raw):
                raise ValueError('Model sequence array is out of bounds')
            ids = {struct.unpack_from('<H', raw, offset + i * 64)[0] for i in range(count)}
            has_attack = bool(ids & {16, 17, 18})
            if not {0, 1, 4, 5}.issubset(ids) or has_attack != enemy['native_attack_animation']:
                raise ValueError('Model animation capability differs from reviewed expectation')
            checked[display] = has_attack
            print(f"Display {display}: {path}; movement/death verified; native attack: {has_attack}")
        print('Known limitation: stock Cow lacks an attack clip; Rat attack clips are present.')
    finally:
        for _, archive in assets.archives:
            archive.file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', type=Path, required=True)
    audit(parser.parse_args().client)
