"""Refine the approved map-905 package in place without re-authoring its layout.

The input manifest/ADT are immutable baselines. Existing UIDs, XY coordinates,
rotations, scales, seven buildings, roads, village furniture and cellar are
retained. Only outer terrain, terrain metadata, ecology and the new farm change.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import struct

import mpyq
import numpy as np

from briarbrook import (Assets, CLIENT, SERVER, HALF, Village, smooth, spline,
                       path_distance, rotation, audit, preview, ELWYNN, GENERIC)
from ground_clutter import patch_points
from generate import TILE, archive, map_dbc
from lumbridge import adt, placements
from native_preview import chunks
from deploy_sandbox import archive_entries


def selected_texture(name, flags, specular):
    """Mirror wowdecomp CMapArea::LoadTerrainTexture, including its suffix rule."""
    return name if flags&1 or not specular else name[:-4]+'_s.blp'


def check_materials(assets, cfg):
    records=[]
    for name,flags in zip(cfg['textures'],cfg['texture_flags']):
        resolved=[]
        for enabled in [False,True]:
            effective=selected_texture(name,flags,enabled);data=assets.read(effective)
            if data[:4]!=b'BLP2':raise ValueError('Unsupported terrain texture '+effective)
            resolved.append(dict(specular=enabled,resource=effective,sha256=hashlib.sha256(data).hexdigest()))
        records.append(dict(base=name,mtxf=flags,resolved=resolved))
    return records


def field_sample(field,e,n):
    x=np.clip((np.asarray(e)+HALF)/TILE*1024,0,1024)
    y=np.clip((HALF-np.asarray(n))/TILE*1024,0,1024)
    ix,iy=x.astype(int),y.astype(int);jx,jy=np.minimum(ix+1,1024),np.minimum(iy+1,1024)
    fx,fy=x-ix,y-iy
    return (field[iy,ix]*(1-fx)+field[iy,jx]*fx)*(1-fy)+(field[jy,ix]*(1-fx)+field[jy,jx]*fx)*fy


def soften_terrain(v, old, settings):
    e,n=v.e,v.n;radius=np.sqrt(((e-4)/1.04)**2+((n-8)/1.12)**2)
    h=30.6+.023*n+.008*e+1.3*np.sin(e/65+.4)*np.cos(n/59)+.6*np.sin(e/31+n/47)
    h+=settings['outer_rise']*smooth((radius-125)/145)
    for x,y,rx,ry,z in [(-133,35,48,70,22),(121,103,50,40,18),(-65,153,65,47,24),
                         (135,-86,52,50,27),(-110,-126,55,48,18)]:
        rx*=settings['hill_width'];ry*=settings['hill_width']
        h+=z*settings['hill_scale']*np.exp(-2*(((e-x)/rx)**2+((n-y)/ry)**2))
    a,b,c,d=settings['protected_bounds']
    outside=np.hypot(np.maximum(np.maximum(a-e,e-c),0),np.maximum(np.maximum(b-n,n-d),0))
    blend=smooth(outside/settings['transition'])
    h=old*(1-blend)+h*blend
    # Preserve the actual building pads and basement, including their feather.
    for building in v.buildings:
        preserve=1-smooth(v.pad_distance(building,e,n)/12)
        h=h*(1-preserve)+old*preserve
    h=np.where(outside==0,old,h)
    return h


def slope_metrics(height, e, n):
    dy,dx=np.gradient(height,TILE/1024)
    slope=np.hypot(dx,dy);outer=np.hypot(e,n)>140
    return dict(maximum=float(height.max()),outer_slope_p95=float(np.percentile(slope[outer],95)),
                outer_slope_p99=float(np.percentile(slope[outer],99)))


def exclusion_for_props(v):
    boxes=[]
    for p in v.placed:
        if p['asset'].lower().endswith('.wmo') or p.get('landmark') in {
                'oak','tree','fir','pine','bush','bush2','grass','rock','flowers','flowers2'}:continue
        b=p['bounds']
        boxes.append((b[0]-17333.333333,17333.333333-b[5],b[3]-17333.333333,17333.333333-b[2]))
    return boxes


def create_refinement(baseline, output):
    if output.exists():raise ValueError('Choose a NEW external output directory')
    repo=Path(__file__).resolve().parents[3]
    if any(output.is_relative_to(p) for p in (repo,CLIENT,SERVER)):raise ValueError('Output must stay outside repo/client/server')
    base=json.loads((baseline/'manifest.json').read_text())
    settings=json.loads(Path(__file__).with_name('briarbrook-refinement.json').read_text())
    if (base['configuration']['map_id'],base['configuration']['directory'])!=(905,'WarscapeBriarbrook'):
        raise ValueError('Expected approved Briarbrook baseline')
    old_archive=archive_entries(baseline/'runtime/patch-Z.MPQ')
    prefix='World\\Maps\\WarscapeBriarbrook\\WarscapeBriarbrook'
    deployed=archive_entries(CLIENT/'Data/patch-Z.MPQ')
    for name,payload in old_archive.items():
        if deployed.get(name)!=payload:raise ValueError('Deployed Briarbrook differs from the approved input package')
    a=Assets();cfg=copy.deepcopy(base['configuration'])
    cfg['texture_flags']=[1,0,0,1];cfg['refinement']=settings['revision']
    material_report=check_materials(a,cfg)
    # Initialize just the data model; do not run Village.author_objects or reroll ecology.
    v=Village.__new__(Village);v.cfg=cfg;v.assets=a;v.buildings=[]
    for source in cfg['buildings']:
        b=copy.deepcopy(source);b['r']=rotation(b['yaw']);b['origin']=np.array(b['foot'])-b['r']@np.array(b['entry_local'][:2])
        b['bounds']=a.bounds(b['asset']);v.buildings.append(b)
    axis=np.linspace(-HALF,HALF,1025);v.e,v.n=np.meshgrid(axis,axis[::-1])
    saved=np.load(baseline/'authoring.npz');old_height=saved['height'];v.alphas=saved['alpha'].copy()
    v.heights=soften_terrain(v,old_height,settings['terrain']);v.holes=base['cellar_holes']
    old_terrain_stats=slope_metrics(old_height,v.e,v.n)
    farm=settings['farm'];cfg['combat_farm']=farm;ruin=copy.deepcopy(farm['ruin'])
    ruin['r']=rotation(ruin['yaw']);ruin['origin']=np.array(ruin['foot'])-ruin['r']@np.array(ruin['entry_local'][:2])
    ruin['bounds']=a.bounds(ruin['asset'])
    ruin['ground']=float(field_sample(v.heights,*ruin['foot']))
    weight=1-smooth(v.pad_distance(ruin,v.e,v.n)/9)
    v.heights=v.heights*(1-weight)+ruin['ground']*weight
    v.buildings.append(ruin)
    cfg['buildings'].append({key:value for key,value in ruin.items() if key not in ('r','origin','bounds')})
    cfg['roads'].extend(copy.deepcopy(farm['roads']))
    v.roads=[(r,spline(r['points'])) for r in cfg['roads']]
    v.sources=[];v.placed=[];removed=[]
    natural={'oak','fir','tree','pine','bush','bush2','grass','rock'}
    for source in base['placements']:
        p=copy.deepcopy(source);e,n=p['osrs'];c=farm['clearing']
        inside=((e-c['center'][0])/c['radii'][0])**2+((n-c['center'][1])/c['radii'][1])**2<1
        if p.get('landmark') in natural and inside:
            removed.append(p['uid']);continue
        delta=0 if p['asset'].lower().endswith('.wmo') else float(field_sample(v.heights,e,n)-field_sample(old_height,e,n))
        if abs(delta)<1e-10:delta=0
        p['z']+=delta;p['bounds'][1]+=delta;p['bounds'][4]+=delta
        v.placed.append(p)
    uid=max(p['uid'] for p in base['placements'])+1
    def add(name,asset,e,n,yaw=0,scale=1,offset=0,landmark='farm_detail',absolute_z=None):
        nonlocal uid
        p=dict(name=name,asset=asset,osrs=[float(e),float(n)],z=float(v.height(e,n)+offset if absolute_z is None else absolute_z),
               yaw=yaw,scale=scale,landmark=landmark)
        result=placements(dict(cfg,placements=[p],uid_base=uid),a)[0];v.placed.append(result);uid+=1
        return result
    add(ruin['name'],ruin['asset'],*ruin['origin'],yaw=ruin['yaw'],landmark='ruined_farm',
        absolute_z=ruin['ground']-ruin['entry_local'][2])
    broken='World\\Azeroth\\Duskwood\\PassiveDoodads\\Fence\\DuskwoodFenceBottomBroken.m2'
    split_top='World\\Azeroth\\Duskwood\\PassiveDoodads\\Fence\\DuskwoodFenceTopBroken.m2'
    intact=ELWYNN+'ElwynnFences\\ElwynnWoodFence01.m2'
    for i,(e,n,yaw) in enumerate([(127,84,0),(128,89,0),(130,96,90),(135,98,90),(140,98,90),
                                  (151,98,90),(156,97,75),(129,78,0),(153,84,65)]):
        asset=broken if i%3 else intact
        add('Breached field boundary',asset,e,n,yaw,.8)
        if i in (1,4,6):add('Splintered upper rail',split_top,e,n,yaw,.8)
    props=[
        ('Overturned supply cart','World\\Azeroth\\Westfall\\PassiveDoodads\\BrokenCart\\BrokenCart.m2',132,82,45,1),
        ('Abandoned harvest wagon','World\\Azeroth\\Westfall\\PassiveDoodads\\RakeCart\\RakeCart.m2',175,78,112,.75),
        ('Scattered crate',GENERIC+'Crate01\\Crate01.m2',158,85,15,1),
        ('Scattered crate',GENERIC+'Crate01\\Crate01.m2',160,87,72,1),
        ('Raid spoils barrel',GENERIC+'Barrel\\Barrel01.m2',159,82,29,1),
        ('Discarded grain',GENERIC+'Furniture\\Containers\\Sack02.m2',156,83,33,1),
        ('Discarded grain',GENERIC+'Furniture\\Containers\\Sack02.m2',153,82,146,1),
        ('Abandoned shovel',ELWYNN+'Shovel\\Shovel.m2',137,91,48,1),
        ('Abandoned shovel',ELWYNN+'Shovel\\Shovel.m2',172,77,119,1),
        ('Overgrown crop rows',ELWYNN+'Detail\\ElwynnWheat\\ElwynnWheat01.m2',141,91,4,.26),
        ('Ruined field pumpkin','World\\Azeroth\\Duskwood\\PassiveDoodads\\Bush\\Pumpkin01.m2',145,91,32,.7),
        ('Ruined field pumpkin','World\\Azeroth\\Duskwood\\PassiveDoodads\\Bush\\Pumpkin01.m2',139,88,75,.66),
        ('Discarded planks','World\\Generic\\DarkIronDwarf\\Passive Doodads\\WoodPiles\\DarkIronWoodPile01.m2',166,80,35,.8),
        ('Sapling boundary',ELWYNN+'Trees\\ElwynnTreeMid01.m2',174,55,19,1.1),
        ('Sapling boundary',ELWYNN+'Trees\\ElwynnTreeMid01.m2',130,103,119,1.2),
        ('Rubble boundary',ELWYNN+'Detail\\ElwynnRock1\\ElwynnRock1.m2',168,51,41,.65)]
    for name,asset,e,n,yaw,scale in props:add(name,asset,e,n,yaw,scale)
    fallen='World\\Azeroth\\Duskwood\\PassiveDoodads\\Trees\\DuskWoodFallenTree02.m2'
    for e,n,yaw,scale in [(122,96,95,.65),(180,63,12,.8),(-91,-40,65,.55),(65,117,104,.6)]:
        add('Fallen woodland branch',fallen,e,n,yaw,scale,offset=-a.bounds(fallen)[2]*scale)
    # Apply local wear and the two new routes; prior road/cobble weights stay exact.
    ee=v.e[:-1,:-1]+TILE/2048;nn=v.n[:-1,:-1]-TILE/2048
    wear=np.zeros((1024,1024));noise=.35*np.sin(ee*.37+np.sin(nn*.21))+.25*np.cos(nn*.45-ee*.13)
    for road in farm['roads']:
        d=path_distance(ee,nn,spline(road['points']))-road['width']/2+noise
        wear=np.maximum(wear,1-smooth((d+.8)/2.6))
    for center,radii,strength in [(farm['crop_patch']['center'],farm['crop_patch']['radii'],.88),([158,81],[17,10],.6)]:
        dist=np.hypot((ee-center[0])/radii[0],(nn-center[1])/radii[1])+noise*.04
        wear=np.maximum(wear,strength*(1-smooth((dist-.68)/.6)))
    old_alpha=v.alphas.astype(float)/255;dirt,cobble,leaf=[old_alpha[:,:,i] for i in range(3)]
    new_dirt=np.maximum(dirt,wear*(1-cobble));remaining=np.maximum(0,1-cobble-new_dirt)
    leaf_new=leaf*remaining/np.maximum(1-cobble-dirt,1/255)
    changed=wear>dirt
    v.alphas[changed]=np.floor(np.stack([new_dirt,cobble,leaf_new],axis=-1)[changed]*255).astype('u1')
    props_boxes=exclusion_for_props(v);combat=farm['combat_space']
    def acceptable(e,n,radius,patch):
        if v.road_clearance(e,n)<radius+.75:return False
        if min(float(v.pad_distance(b,e,n)) for b in v.buildings)<radius+.65:return False
        if np.hypot((e+2)/18,(n-8)/17)<1:return False
        if np.hypot((e-combat['center'][0])/combat['radii'][0],(n-combat['center'][1])/combat['radii'][1])<1.05:return False
        for left,bottom,right,top in props_boxes:
            d=math.hypot(max(left-e,0,e-right),max(bottom-n,0,n-top))
            if d<radius+.6:return False
        return True
    clutter_counts={}
    for patch,entry,e,n,yaw,scale in patch_points(settings['patches'],settings['profiles'],acceptable):
        add(patch['name'],entry['asset'],e,n,yaw,scale,landmark='ground_clutter')
        clutter_counts[patch['name']]=clutter_counts.get(patch['name'],0)+1
    current={p['uid']:p for p in v.placed};unchanged=0
    for p in base['placements']:
        if p['uid'] in removed:continue
        after=current[p['uid']]
        for key in ['asset','osrs','x','y','yaw','scale']:
            if after[key]!=p[key]:raise ValueError('Approved placement transform changed: '+p['name'])
        if after['z']==p['z']:unchanged+=1
        if p['asset'].lower().endswith('.wmo') and after!=p:raise ValueError('Village building changed')
    output.mkdir(parents=True)
    audit(v,output)
    terrain=bytearray(adt(cfg,32,32,a,v.placed,height_sampler=lambda x,y:v.height(-y-HALF,x+HALF),surface_sampler=v.alpha,detail_applied=True))
    mcin=next(body for tag,body in chunks(terrain) if tag=='MCIN')
    for gx,gy in v.holes:
        offset=struct.unpack_from('<I',mcin,((gy//4)*16+gx//4)*16)[0]
        old=struct.unpack_from('<H',terrain,offset+68)[0]
        struct.pack_into('<H',terrain,offset+68,old|(1<<((gy%4)*4+gx%4)))
    files={prefix+'.wdt':old_archive[prefix+'.wdt'],prefix+'_32_32.adt':bytes(terrain)}
    server_map=(SERVER/'dbc/Map.dbc').read_bytes()
    if server_map!=(baseline/'runtime/Map.dbc').read_bytes():raise ValueError('Map registration changed after approved baseline')
    archive(output/'runtime/patch-Z.MPQ',files)
    locale=archive_entries(CLIENT/'Data/enUS/patch-enUS-Z.MPQ')
    unchanged_dbc={name:locale[name] for name in ['DBFilesClient\\Map.dbc','DBFilesClient\\Light.dbc']}
    archive(output/'runtime/patch-enUS-Z.MPQ',unchanged_dbc)
    (output/'runtime/Map.dbc').write_bytes(server_map)
    staged=output/'extract-input/Data'
    for source in (CLIENT/'Data').rglob('*.MPQ'):
        if source.name.lower() in ('patch-z.mpq','patch-enus-z.mpq'):continue
        target=staged/source.relative_to(CLIENT/'Data');target.parent.mkdir(parents=True,exist_ok=True);os.link(source,target)
    archive(staged/'patch-Z.MPQ',files)
    original=a.read('DBFilesClient\\Map.dbc')
    archive(staged/'enUS/patch-enUS-Z.MPQ',{'DBFilesClient\\Map.dbc':map_dbc(original,cfg,only_custom=True),
            'DBFilesClient\\GameObjectDisplayInfo.dbc':struct.pack('<4s4I',b'WDBC',0,19,76,1)+b'\0'})
    farm['inspection_z']=v.height(*farm['inspection_point'])+2.0
    report=dict(baseline=str(baseline),baseline_adt_sha256=hashlib.sha256(old_archive[prefix+'_32_32.adt']).hexdigest(),
                baseline_source_hash=hashlib.sha256((baseline/'manifest.json').read_bytes()).hexdigest(),
                existing_placement_count=len(base['placements']),retained_existing=len(base['placements'])-len(removed),
                unchanged_existing_z=unchanged,removed_ecology_uids=removed,clutter_patches=clutter_counts,
                old_terrain=old_terrain_stats,new_terrain=slope_metrics(v.heights,v.e,v.n),farm=farm,materials=material_report,
                existing_roads_preserved=cfg['roads'][:len(base['configuration']['roads'])]==base['configuration']['roads'])
    manifest=dict(configuration=cfg,placements=v.placed,cellar_holes=v.holes,
                  base_server_map_sha256=hashlib.sha256(server_map).hexdigest(),
                  height_range=[float(v.heights.min()),float(v.heights.max())],refinement=report,
                  validation='Automated authoring checks only; updated live appearance is pending user inspection')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (output/'refinement-report.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(output/'authoring.npz',height=v.heights,alpha=v.alphas)
    preview(v,output)
    a.close()
    print(json.dumps({k:report[k] for k in ['existing_placement_count','retained_existing','unchanged_existing_z','old_terrain','new_terrain']}))
    print('Added ground clutter:',sum(clutter_counts.values()),'Removed ecology inside the new farm:',len(removed))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    parser.add_argument('--baseline',type=Path,default=Path(r'C:\WoWDev\Worldgen\Briarbrook-905-005'))
    args=parser.parse_args()
    if os.name!='nt':raise SystemExit('Local Windows execution only')
    create_refinement(args.baseline.resolve(),args.output.resolve())
