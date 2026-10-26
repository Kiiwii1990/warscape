"""Safely back up and deploy only the one-tile Warscape map-904 sandbox."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

import mpyq

from generate import archive as write_archive


def archive_entries(path):
    archive = mpyq.MPQArchive(str(path), listfile=True)
    try:
        listing = archive.read_file('(listfile)')
        if listing is None:
            raise ValueError(f'MPQ has no readable listfile: {path}')
        entries = {}
        for raw_name in listing.splitlines():
            name = raw_name.decode('utf-8')
            if not name or name.lower() == '(listfile)':
                continue
            payload = archive.read_file(name)
            if payload is None:
                raise ValueError(f'Cannot preserve unreadable MPQ entry {name!r} in {path}')
            entries[name] = payload
        return entries
    finally:
        archive.file.close()


def merge_archive(existing, update, destination):
    """Merge a generated archive into an existing client MPQ without dropping entries."""
    entries = archive_entries(existing) if existing.is_file() else {}
    entries.update(archive_entries(update))
    write_archive(destination, entries)


def map_registration(data, map_id, directory):
    magic, count, fields, row_size, strings_size = struct.unpack_from('<4s4I', data)
    if (magic, fields, row_size) != (b'WDBC', 66, 264) or len(data) != 20 + count * row_size + strings_size:
        raise ValueError('Map.dbc has an unexpected 3.3.5a layout')
    strings_start = 20 + count * row_size
    found = False
    for index in range(count):
        row = 20 + index * row_size
        if struct.unpack_from('<I', data, row)[0] != map_id:
            continue
        offset = struct.unpack_from('<I', data, row + 4)[0]
        if offset >= strings_size:
            raise ValueError('Map.dbc sandbox directory string offset is out of bounds')
        end = data.find(b'\0', strings_start + offset)
        if end < 0 or data[strings_start + offset:end].decode('ascii') != directory:
            raise ValueError('Map.dbc sandbox directory does not match package')
        found = True
        break
    if not found:
        raise ValueError(f'Map.dbc does not register map {map_id}')
    return count, row_size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if os.name != 'nt':
        raise SystemExit('Windows only')

    output = args.output.resolve()
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    cfg = manifest['configuration']
    if (cfg['map_id'], cfg['directory']) != (904, 'WarscapeDevSandbox'):
        raise SystemExit('This deployer is restricted to the map-904 development sandbox')
    if cfg['tiles'] != [[32, 32]] or cfg['placements'] or cfg.get('terrain_mode'):
        raise SystemExit('Sandbox package must contain one flat terrain tile and no placements')

    processes = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True, check=True).stdout.strip()
    if processes != '0':
        raise SystemExit('Custom client and both local game servers must be stopped')

    repo = Path(__file__).resolve().parents[3]
    client = Path(r'C:\WoWDev\wowdecomp\bin\Win')
    server = Path(r'C:\WoWDev\TrinityServer')
    backups = Path(r'C:\WoWDev\Backups')
    if any(output.is_relative_to(path.resolve()) for path in (repo, client, server)):
        raise SystemExit('Build output must remain outside the repository, client and server')
    if not (client / 'WowClient64.exe').is_file():
        raise SystemExit('Verified custom wowdecomp executable is missing')

    runtime_map = (output / 'runtime/Map.dbc').read_bytes()
    runtime_count, row_size = map_registration(runtime_map, cfg['map_id'], cfg['directory'])
    server_map_path = server / 'dbc/Map.dbc'
    server_map = server_map_path.read_bytes()
    _, server_count, fields, server_row_size, _ = struct.unpack_from('<4s4I', server_map)
    if fields != 66 or server_row_size != row_size or runtime_count != server_count + 1:
        raise ValueError('Sandbox Map.dbc must append exactly one row to the existing server registrations')
    if runtime_map[20:20 + server_count * row_size] != server_map[20:20 + server_count * row_size]:
        raise ValueError('Existing server map registrations changed in generated Map.dbc')

    prepared = output / 'deploy-prepared'
    prepared.mkdir(exist_ok=True)
    client_archive = client / 'Data/patch-Z.MPQ'
    locale_archive = client / 'Data/enUS/patch-enUS-Z.MPQ'
    merged_client = prepared / 'patch-Z.MPQ'
    merged_locale = prepared / 'patch-enUS-Z.MPQ'
    merge_archive(client_archive, output / 'runtime/patch-Z.MPQ', merged_client)
    merge_archive(locale_archive, output / 'runtime/patch-enUS-Z.MPQ', merged_locale)

    locale_entries = archive_entries(merged_locale)
    if locale_entries.get('DBFilesClient\\Map.dbc') != runtime_map:
        raise ValueError('Client patch registration differs from the server runtime Map.dbc')

    pairs = [(merged_client, client_archive), (merged_locale, locale_archive),
             (output / 'runtime/Map.dbc', server_map_path)]
    for kind in ('maps', 'vmaps', 'mmaps'):
        for source in (output / 'extracted' / kind).iterdir():
            if source.is_file() and source.name.startswith('904'):
                pairs.append((source, server / kind / source.name))
    if len([source for source, _ in pairs if source.suffix == '.map']) != 1:
        raise ValueError('Expected exactly one extracted terrain tile')
    if len([source for source, _ in pairs if source.suffix == '.mmtile']) != 1:
        raise ValueError('Expected exactly one navigation tile')
    if not any(source.name == '904.vmtree' for source, _ in pairs):
        raise ValueError('Empty terrain collision tree is missing')

    backup = backups / ('Warscape-DevSandbox-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    records = []
    for index, (source, target) in enumerate(pairs):
        previous = None
        if target.exists():
            previous = backup / f'{index:04}-{target.name}'
            shutil.copy2(target, previous)
            if previous.read_bytes() != target.read_bytes():
                raise SystemExit(f'Backup mismatch for {target}; deployment stopped')
        records.append({'target': str(target), 'backup': str(previous) if previous else None,
                        'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    (backup / 'deployment.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')

    for source, target in pairs:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if source.read_bytes() != target.read_bytes():
            raise SystemExit(f'Deployment verification failed for {target}; see {backup}')

    print(f'Verified {len(pairs)} runtime files deployed for map 904.')
    print(f'Backup directory: {backup}')
    print('Client and server Map.dbc registrations match; existing rows were preserved.')


if __name__ == '__main__':
    main()
