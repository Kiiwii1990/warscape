"""Isolated native terrain/VMAP/MMap build for the map-905 one-tile village."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

from build import validate_navigation_tile

SERVER=Path(r'C:\WoWDev\TrinityServer')


def namespace_models(source, destination, map_id):
    """Rewrite ModelSpawn filenames, retaining every transform and embedded prop.

    dir_bin layout is defined by ModelSpawn::readFromFile plus map/tile prefixes.
    Shared model basenames never overwrite another map's VMAP geometry.
    """
    destination.mkdir()
    data=(source/'dir_bin').read_bytes();result=bytearray();pos=0;names=set();count=0
    while pos<len(data):
        start=pos
        if pos+50>len(data):raise ValueError('Truncated collision placement')
        mid,tx,ty,flags=struct.unpack_from('<4I',data,pos)
        if mid!=map_id or (tx,ty)!=(32,32):raise ValueError('Collision extraction escaped configured map/tile')
        length_pos=pos+12+38+(24 if flags&4 else 0)
        length=struct.unpack_from('<I',data,length_pos)[0]
        if length>500 or length_pos+4+length>len(data):raise ValueError('Invalid collision filename')
        old=data[length_pos+4:length_pos+4+length].decode('ascii')
        if Path(old).name!=old or '/' in old or '\\' in old:raise ValueError('Unexpected raw model path')
        new=f'warscape{map_id}_'+old
        result+=data[start:length_pos]+struct.pack('<I',len(new))+new.encode()
        names.add((old,new));count+=1
        pos=length_pos+4+length
    for old,new in names:
        src=source/old
        if not src.is_file() or src.stat().st_size<=8:raise ValueError('Missing native collision model: '+old)
        shutil.copy2(src,destination/new)
    (destination/'dir_bin').write_bytes(result)
    return count,len(names)


def run(command,cwd,log):
    with log.open('wb') as f:
        subprocess.run([str(p) for p in command],cwd=cwd,stdout=f,stderr=f,check=True)


def build(output):
    manifest=json.loads((output/'manifest.json').read_text());cfg=manifest['configuration']
    if cfg['map_id']!=905 or cfg['tiles']!=[[32,32]]:raise ValueError('Expected isolated one-tile map 905')
    extracted=output/'extracted';extracted.mkdir(exist_ok=True)
    run([SERVER/'mapextractor.exe','-i',output/'extract-input','-o',extracted,'-e','1','-f','0'],output,output/'extractor.log')
    maps=list((extracted/'maps').glob('*.map'))
    if [p.name for p in maps]!=['9053232.map']:raise ValueError('Terrain extractor emitted wrong map/tile set')
    data=maps[0].read_bytes();header=struct.unpack_from('<4s10I',data)
    if header[:2]!=(b'MAPS',10):raise ValueError('Unexpected server terrain format')
    magic,flags,low,high=struct.unpack_from('<4sIff',data,header[5])
    if magic!=b'MHGT' or flags!=0 or not 20<low<high<120:raise ValueError('Variable terrain extraction failed')
    collision=output/'collision';collision.mkdir(exist_ok=True)
    run([SERVER/'vmap4extractor.exe','-l','-d',output/'extract-input'],collision,output/'vmap-extractor.log')
    instances,models=namespace_models(collision/'Buildings',collision/'namespaced',905)
    run([SERVER/'vmap4assembler.exe',collision/'namespaced',extracted/'vmaps'],output,output/'vmap-assembler.log')
    vmaps=extracted/'vmaps'
    if not (vmaps/'905.vmtree').exists() or not (vmaps/'905_32_32.vmtile').exists():raise ValueError('Native collision assembly incomplete')
    tile=(vmaps/'905_32_32.vmtile').read_bytes()
    if tile[:8]!=b'VMAP_4.8' or struct.unpack_from('<I',tile,8)[0]<len(cfg['buildings']):raise ValueError('Collision tile has no building instances')
    dbc=extracted/'dbc';dbc.mkdir(exist_ok=True)
    shutil.copy2(SERVER/'dbc/LiquidType.dbc',dbc/'LiquidType.dbc')
    run([SERVER/'mmaps_generator.exe','905','--threads','2','--silent'],extracted,output/'mmaps.log')
    nav=list((extracted/'mmaps').glob('*.mmtile'))
    if [p.name for p in nav]!=['9053232.mmtile']:raise ValueError('Navigation tile set is incomplete')
    polygons,vertices=validate_navigation_tile(nav[0])
    result=dict(terrain_tiles=1,terrain_range=[low,high],collision_instances=instances,
                collision_models=models,nav_tiles=1,nav_polygons=polygons,nav_vertices=vertices,
                live_visual_acceptance=False)
    result['files']={str(p.relative_to(extracted)):hashlib.sha256(p.read_bytes()).hexdigest()
                     for kind in ('maps','vmaps','mmaps') for p in (extracted/kind).iterdir() if p.is_file()}
    (output/'build-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if os.name!='nt':raise SystemExit('Local Windows execution only')
    build(args.output.resolve())
