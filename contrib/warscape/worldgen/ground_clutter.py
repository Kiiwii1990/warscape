"""Reusable, deterministic vegetation patches with explicit exclusion geometry.

Layout is controlled by named elliptical patches and weighted native assets.
Sampling order is stable per patch; roads, buildings, props and encounter spaces
are tested before acceptance. This module never writes runtime or database data.
"""
import hashlib
import math
import random


def patch_points(patches, profiles, acceptable):
    """Yield (patch, asset settings, east, north, yaw, scale), respecting density.

    accepted(e,n,radius,patch) is supplied by the world's authoring code so this
    placement method can be reused without coupling it to Briarbrook geography.
    """
    for patch in patches:
        seed=int.from_bytes(hashlib.blake2b(patch['name'].encode(),digest_size=8).digest(),'little')^patch['seed']
        rng=random.Random(seed);profile=profiles[patch['profile']]
        weights=[entry.get('weight',1) for entry in profile];placed=[];attempts=0
        while len(placed)<patch['count'] and attempts<patch['count']*180:
            attempts+=1
            # Patches have a slightly denser heart and irregular, open edges.
            angle=rng.uniform(0,math.tau);radius=math.sqrt(rng.random())
            e=patch['center'][0]+math.cos(angle)*radius*patch['radii'][0]
            n=patch['center'][1]+math.sin(angle)*radius*patch['radii'][1]
            if radius>.72 and rng.random()<.32:continue
            asset=rng.choices(profile,weights=weights,k=1)[0]
            scale=rng.uniform(*asset.get('scale',[.85,1.15]))
            footprint=asset.get('radius',.3)*scale
            spacing=patch.get('spacing',.65)
            if any(math.hypot(e-x,n-y)<max(spacing,footprint+r)*.8 for x,y,r in placed):continue
            if not acceptable(e,n,footprint,patch):continue
            placed.append((e,n,footprint))
            yield patch,asset,e,n,rng.uniform(0,360),scale
        if len(placed)<patch['count']:
            raise ValueError(f"Clutter patch {patch['name']} placed {len(placed)}/{patch['count']}; adjust its footprint or exclusions")
