"""Owned Nechryael summon binding with explicit historical verification replacement."""
import json,hashlib,re
from family_catalogue import ROOT
from elemental_release import elemental_artifacts

def summon_artifacts(pack,prior):
    out=elemental_artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=out[sqlpath]+"UPDATE creature_template SET AIName='',ScriptName='npc_warscape_death_spawn' WHERE entry=902500;\nUPDATE creature_template SET AIName='',ScriptName='npc_warscape_nechryael' WHERE entry=902400;\n"
    spec=json.loads(out[specpath])
    # This release has shared loot only, so there are no new item/display IDs.
    spec['precondition_sql']=re.sub(r'\(SELECT COUNT\(\*\) FROM item_template WHERE entry IN \(\)\)=0','1=1',spec['precondition_sql'])
    spec['verify_sql']=spec['verify_sql'].replace("AIName='AggressorAI'","AIName='' AND ScriptName='npc_warscape_death_spawn'")
    parent="(SELECT COUNT(*) FROM creature_template WHERE entry=902400 AND AIName='' AND ScriptName='npc_warscape_nechryael')=1"
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+parent+',1,0)'
    spec['precondition_sql']=spec['precondition_sql'].removesuffix(',1,0)')+" AND (SELECT COUNT(*) FROM creature_template WHERE entry=902400 AND AIName='AggressorAI' AND ScriptName='')=1,1,0)"
    old=json.loads((ROOT/'contrib/warscape/verifications/2026_11_08_04_world.json').read_text())
    replacement,n=re.subn(r"(FROM creature_template WHERE entry=902400 AND .*?)AIName='AggressorAI'",r"\1AIName='' AND ScriptName='npc_warscape_nechryael'",old['verify_sql'],count=1)
    if n!=1:raise ValueError('Missing parent verification')
    spec['supersedes']=[dict(migration='2026_11_08_04_world.sql',migration_sha1=old['sha1'],original_verify_sha256=hashlib.sha256(old['verify_sql'].encode()).hexdigest(),verify_sql=replacement,reason='Only Nechryael AI binding changes for owned death spawns; all historical data checks retained.')]
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
