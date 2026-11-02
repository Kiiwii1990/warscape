"""Back up and deploy an explicitly allowlisted Warscape map experiment."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import mpyq

from generate import archive as write_archive


def archive_entries(path):
    """Read every named MPQ entry or fail without producing a partial merge."""
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


def merged_archive(existing, update, destination):
    """Overlay package entries on an existing archive, retaining all other files."""
    entries = archive_entries(existing) if existing.is_file() else {}
    entries.update(archive_entries(update))
    write_archive(destination, entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if os.name != 'nt':
        raise SystemExit('Windows only')
    processes = subprocess.run(['powershell','-NoProfile','-Command',
        "@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count"],
        capture_output=True,text=True,check=True).stdout.strip()
    if processes != '0':
        raise SystemExit('Client and both game servers must be stopped')
    output = args.output.resolve()
    manifest = json.loads((output / 'manifest.json').read_text())
    cfg = manifest['configuration']
    allowed = {901: 'WarscapeTest1', 903: 'WarscapeLumbridgeAlpha'}
    if cfg['map_id'] not in allowed or cfg['directory'] != allowed[cfg['map_id']]:
        raise SystemExit('Deployment is limited to approved map 901 and map 903 experiments')
    client = Path(r'C:\WoWDev\wowdecomp\bin\Win')
    server = Path(r'C:\WoWDev\TrinityServer')
    # Client::SetPaths uses the executable directory when -datadir is absent.
    if not (client / 'WowClient64.exe').is_file():
        raise SystemExit('Verified launch executable missing')
    prepared = output / 'deploy-prepared'
    prepared.mkdir(exist_ok=True)
    client_archive = client/'Data/patch-Z.MPQ'
    locale_archive = client/'Data/enUS/patch-enUS-Z.MPQ'
    merged_client = prepared/'patch-Z.MPQ'
    merged_locale = prepared/'patch-enUS-Z.MPQ'
    merged_archive(client_archive, output/'runtime/patch-Z.MPQ', merged_client)
    merged_archive(locale_archive, output/'runtime/patch-enUS-Z.MPQ', merged_locale)
    pairs = [(merged_client,client_archive), (merged_locale,locale_archive)]
    # Preserve the working registration byte-for-byte for Test 2.
    if (output/'runtime/Map.dbc').read_bytes() != (server/'dbc/Map.dbc').read_bytes():
        raise SystemExit('Map.dbc differs; registration changes require separate review')
    for kind in ['maps','vmaps','mmaps']:
        for source in (output/'extracted'/kind).iterdir():
            if source.is_file() and source.name.startswith((f'{cfg["map_id"]:03}',
                                                               f'warscape{cfg["map_id"]}_')):
                pairs.append((source,server/kind/source.name))
    if len([p for p,d in pairs if p.suffix=='.map']) != len(cfg['tiles']):
        raise SystemExit('Terrain tiles are incomplete')
    if len([p for p,d in pairs if p.suffix=='.mmtile']) != len(cfg['tiles']):
        raise SystemExit('Navigation tiles are incomplete')
    backup = Path(r'C:\WoWDev\Backups') / ('Worldgen-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir()
    records = []
    for index,(source,target) in enumerate(pairs):
        previous = None
        if target.exists():
            previous = backup / f'{index:04}-{target.name}'
            shutil.copy2(target,previous)
            if previous.read_bytes() != target.read_bytes():
                raise SystemExit('Backup mismatch; deployment stopped')
        records.append({'target':str(target),'backup':str(previous) if previous else None,
                        'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    (backup/'deployment.json').write_text(json.dumps(records,indent=2)+'\n')
    for source,target in pairs:
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        if source.read_bytes() != target.read_bytes():
            raise SystemExit('Deployment verification failed; see external backup')
    print('Verified runtime files deployed:',len(pairs))
    print('Backup directory:',backup)
    print('Map.dbc registration preserved; client launch has no datadir override.')


if __name__ == '__main__':
    main()
