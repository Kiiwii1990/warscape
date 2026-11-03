"""Backup-first, append-only local map-905 deployment. No database operations."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

from briarbrook import CLIENT, SERVER, Assets
from deploy_sandbox import archive_entries
from generate import archive


def digest(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file,'sha256').hexdigest()


def assert_dbc_append(old,new,fields,size):
    magic,n,f,s,ss=struct.unpack_from('<4s4I',old)
    magic2,n2,f2,s2,ss2=struct.unpack_from('<4s4I',new)
    if ((magic,f,s)!=(b'WDBC',fields,size) or (magic2,f2,s2)!=(magic,f,s) or n2!=n+1 or
            len(old)!=20+n*s+ss or len(new)!=20+n2*s+ss2):
        raise ValueError('DBC must append exactly one correctly sized record')
    if new[20:20+n*s]!=old[20:20+n*s] or not new[20+n2*s:].startswith(old[20+n*s:]):
        raise ValueError('Existing DBC rows or strings were altered')


def preservation_snapshot():
    result={}
    for kind in ('maps','vmaps','mmaps'):
        for p in (SERVER/kind).iterdir():
            if p.is_file() and (any(p.name.startswith(str(i)) for i in range(901,905)) or
                                any(p.name.startswith(f'warscape{i}_') for i in range(901,905))):
                result[str(p)]=digest(p)
    return result


def prepare_refinement(output,manifest):
    """Replace only the explicitly identified baseline of the existing map 905."""
    cfg=manifest['configuration'];report=manifest['refinement']
    if (cfg['map_id'],cfg['directory'],cfg['tiles'])!=(905,'WarscapeBriarbrook',[[32,32]]):
        raise ValueError('Refinement must stay on the existing one-tile Briarbrook map')
    baseline=Path(report['baseline'])
    if digest(baseline/'manifest.json')!=report['baseline_source_hash']:raise ValueError('Approved baseline manifest changed')
    build=json.loads((output/'build-validation.json').read_text())
    validation=json.loads((output/'artifact-validation.json').read_text())
    if build['terrain_tiles']!=1 or build['nav_tiles']!=1 or validation['road_navigation_issues']:
        raise ValueError('Refinement terrain/collision/navigation validation is incomplete')
    if (len(validation.get('interior_entrances',[]))!=7 or
            not all(x['entrance_connected'] for x in validation['interior_entrances']) or
            validation.get('cellar_and_stair_probes')!=[True]*4 or
            not validation.get('refinement',{}).get('all_material_resources_resolved')):
        raise ValueError('Refinement entrance/cellar/material checks must pass')
    old_build=json.loads((baseline/'build-validation.json').read_text())
    for name,expected in build['files'].items():
        if digest(output/'extracted'/name)!=expected:raise ValueError('Validated refinement artifact changed')
    for name,expected in old_build['files'].items():
        if digest(SERVER/name)!=expected:raise ValueError('Deployed map-905 baseline artifact changed: '+name)
    server_map=(SERVER/'dbc/Map.dbc').read_bytes()
    if digest(SERVER/'dbc/Map.dbc')!=manifest['base_server_map_sha256'] or (output/'runtime/Map.dbc').read_bytes()!=server_map:
        raise ValueError('Refinement must preserve Map.dbc byte-for-byte')
    old_client=archive_entries(CLIENT/'Data/patch-Z.MPQ');new_client=archive_entries(output/'runtime/patch-Z.MPQ')
    old_locale=archive_entries(CLIENT/'Data/enUS/patch-enUS-Z.MPQ');new_locale=archive_entries(output/'runtime/patch-enUS-Z.MPQ')
    allowed={'World\\Maps\\WarscapeBriarbrook\\WarscapeBriarbrook.wdt',
             'World\\Maps\\WarscapeBriarbrook\\WarscapeBriarbrook_32_32.adt'}
    if set(new_client)!=allowed:raise ValueError('Refinement patch must contain only Briarbrook WDT/ADT')
    adt_name=next(n for n in allowed if n.endswith('.adt'));wdt_name=next(n for n in allowed if n.endswith('.wdt'))
    if hashlib.sha256(old_client[adt_name]).hexdigest()!=report['baseline_adt_sha256']:
        raise ValueError('Current client map differs from the approved refinement baseline')
    if old_client[wdt_name]!=new_client[wdt_name]:raise ValueError('Briarbrook tile topology changed')
    if old_locale.get('DBFilesClient\\Map.dbc')!=server_map or any(old_locale.get(n)!=p for n,p in new_locale.items()):
        raise ValueError('Refinement attempted to change a DBC')
    prepared=output/'deploy-prepared';prepared.mkdir(exist_ok=True)
    archive(prepared/'patch-Z.MPQ',{**old_client,**new_client})
    check=archive_entries(prepared/'patch-Z.MPQ')
    if any(check.get(n)!=p for n,p in old_client.items() if n not in allowed):
        raise ValueError('An unrelated client patch entry changed')
    pairs=[(prepared/'patch-Z.MPQ',CLIENT/'Data/patch-Z.MPQ')]
    for name in sorted(build['files']):
        kind,filename=name.replace('\\','/').split('/')
        if kind not in ('maps','vmaps','mmaps') or not filename.startswith(('905','warscape905_')):
            raise ValueError('Refinement artifact escaped map-905 allowlist')
        target=SERVER/kind/filename
        if target.exists() and name not in old_build['files']:
            raise ValueError('Unexpected existing map-905 artifact: '+filename)
        pairs.append((output/'extracted'/name,target))
    before=preservation_snapshot()
    for path in [SERVER/'dbc/Map.dbc',CLIENT/'Data/enUS/patch-enUS-Z.MPQ']:
        before[str(path)]=digest(path)
    return pairs,len(old_client)-len(allowed),before


def prepare(output,replace_existing=False):
    manifest=json.loads((output/'manifest.json').read_text());cfg=manifest['configuration']
    if manifest.get('refinement'):
        if not replace_existing:raise ValueError('Existing map refinement requires --replace-existing')
        return prepare_refinement(output,manifest)
    if (cfg['map_id'],cfg['directory'],cfg['tiles'])!=(905,'WarscapeBriarbrook',[[32,32]]):
        raise ValueError('This deployment is restricted to the new one-tile Briarbrook map')
    build=json.loads((output/'build-validation.json').read_text())
    validation=json.loads((output/'artifact-validation.json').read_text())
    if build['terrain_tiles']!=1 or build['nav_tiles']!=1 or validation['road_navigation_issues']:
        raise ValueError('Automated terrain/collision/navigation validation is incomplete')
    if len(validation.get('interior_entrances',[]))!=7 or not all(x['entrance_connected'] for x in validation['interior_entrances']):
        raise ValueError('All seven interior entrance probes must connect before deployment')
    if not all(validation.get('cellar_and_stair_probes',[])):
        raise ValueError('Inn cellar/stair probes must connect before deployment')
    for name,expected in build['files'].items():
        if digest(output/'extracted'/name)!=expected:raise ValueError('Extracted artifact changed after validation')
    if digest(SERVER/'dbc/Map.dbc')!=manifest['base_server_map_sha256']:
        raise ValueError('Server map registration changed after generation; rebuild against current data')
    server_map=(SERVER/'dbc/Map.dbc').read_bytes();new_map=(output/'runtime/Map.dbc').read_bytes()
    assert_dbc_append(server_map,new_map,66,264)
    if struct.unpack_from('<I',new_map,20+struct.unpack_from('<I',server_map,4)[0]*264)[0]!=905:
        raise ValueError('The appended map record is not map 905')
    old_client=archive_entries(CLIENT/'Data/patch-Z.MPQ')
    old_locale=archive_entries(CLIENT/'Data/enUS/patch-enUS-Z.MPQ')
    new_client=archive_entries(output/'runtime/patch-Z.MPQ')
    new_locale=archive_entries(output/'runtime/patch-enUS-Z.MPQ')
    if old_locale.get('DBFilesClient\\Map.dbc')!=server_map:
        raise ValueError('Current client and server map registrations differ')
    prefix='world\\maps\\warscapebriarbrook\\'
    if len(new_client)!=2 or any(not name.lower().startswith(prefix) for name in new_client):
        raise ValueError('Client update contains assets outside the isolated map')
    folded={n.lower() for n in old_client}
    if any(n.lower() in folded for n in new_client):raise ValueError('Map assets already exist; refusing overwrite')
    if set(new_locale)!={'DBFilesClient\\Map.dbc','DBFilesClient\\Light.dbc'} or new_locale['DBFilesClient\\Map.dbc']!=new_map:
        raise ValueError('Unexpected client DBC changes')
    assets=Assets()
    try:old_light=old_locale.get('DBFilesClient\\Light.dbc') or assets.read('DBFilesClient\\Light.dbc')
    finally:assets.close()
    assert_dbc_append(old_light,new_locale['DBFilesClient\\Light.dbc'],15,60)
    prepared=output/'deploy-prepared';prepared.mkdir(exist_ok=True)
    archive(prepared/'patch-Z.MPQ',{**old_client,**new_client})
    archive(prepared/'patch-enUS-Z.MPQ',{**old_locale,**new_locale})
    # Independently read back every existing entry. Only the two appended DBCs change.
    check=archive_entries(prepared/'patch-Z.MPQ')
    if any(check.get(name)!=payload for name,payload in old_client.items()):
        raise ValueError('A prior map/addon/client patch entry changed')
    check_locale=archive_entries(prepared/'patch-enUS-Z.MPQ')
    if any(check_locale.get(name)!=payload for name,payload in old_locale.items() if name not in new_locale):
        raise ValueError('An unrelated locale patch entry changed')
    pairs=[(prepared/'patch-Z.MPQ',CLIENT/'Data/patch-Z.MPQ'),
           (prepared/'patch-enUS-Z.MPQ',CLIENT/'Data/enUS/patch-enUS-Z.MPQ'),
           (output/'runtime/Map.dbc',SERVER/'dbc/Map.dbc')]
    for name in sorted(build['files']):
        kind,filename=name.replace('\\','/').split('/')
        if kind not in ('maps','vmaps','mmaps') or not filename.startswith(('905','warscape905_')):
            raise ValueError('Server artifact escaped map-905 allowlist')
        target=SERVER/kind/filename
        if target.exists():raise ValueError('New map-905 target already exists')
        pairs.append((output/'extracted'/name,target))
    return pairs,len(old_client),preservation_snapshot()


def deploy(output,prepare_only=False,replace_existing=False):
    pairs,preserved_count,before=prepare(output,replace_existing)
    if prepare_only:
        print(f'Prepared {len(pairs)} runtime files; {preserved_count} unrelated client entries and {len(before)} protected runtime files preserved.')
        return
    result=subprocess.run(['powershell','-NoProfile','-Command',
                           '@(Get-Process -Name WowClient64,worldserver,authserver -ErrorAction SilentlyContinue).Count'],
                          capture_output=True,text=True,check=True)
    if result.stdout.strip()!='0':raise SystemExit('Custom client and both local servers must be stopped')
    if not (CLIENT/'WowClient64.exe').is_file():raise ValueError('Verified wowdecomp launch path is missing')
    backup=Path(r'C:\WoWDev\Backups')/('Warscape-Briarbrook-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    records=[]
    for i,(source,target) in enumerate(pairs):
        saved=None
        if target.exists():
            saved=backup/f'{i:04}-{target.name}';shutil.copy2(target,saved)
            if digest(saved)!=digest(target):raise ValueError('Deployment backup verification failed')
        records.append(dict(source=str(source),target=str(target),backup=str(saved) if saved else None,sha256=digest(source)))
    record_path=backup/'deployment.json'
    record_path.write_text(json.dumps(dict(files=records,preserved=before),indent=2)+'\n')
    written=[]
    try:
        for record in records:
            source,target=Path(record['source']),Path(record['target'])
            target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_name(target.name+'.briarbrook-pending')
            if temporary.exists():raise ValueError('A pending deployment file already exists')
            shutil.copy2(source,temporary)
            if digest(temporary)!=record['sha256']:raise ValueError('Staged runtime bytes do not match validated output')
            os.replace(temporary,target);written.append(record)
            if digest(target)!=record['sha256']:raise ValueError('Deployed runtime verification failed')
        if any(not Path(path).is_file() or digest(path)!=expected for path,expected in before.items()):
            raise ValueError('A protected prior map or registration file changed')
    except BaseException:
        for record in reversed(written):
            target=Path(record['target'])
            if record['backup']:shutil.copy2(record['backup'],target)
            else:target.unlink(missing_ok=True)
        raise
    protected_maps=sum(Path(path).parent.name in ('maps','vmaps','mmaps') for path in before)
    result=dict(runtime_files=len(records),backup=str(backup),preserved_client_entries=preserved_count,
                preserved_server_artifacts=protected_maps,preserved_registration_files=len(before)-protected_maps,
                client_executable=str(CLIENT/'WowClient64.exe'),
                game_directory=str(CLIENT),datadir_override=None,
                database_changes=False,manual_acceptance=False)
    (output/'deployment-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--replace-existing',action='store_true');args=parser.parse_args()
    if os.name!='nt':raise SystemExit('Local Windows execution only')
    deploy(args.output.resolve(),args.prepare_only,args.replace_existing)
