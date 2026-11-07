"""Data-driven bindings for Waterfiend/Banshee/Revenant encounter checkpoint."""
import hashlib,json,re
from family_catalogue import ROOT
from expansion_release import artifacts

def spirit_artifacts(pack,prior):
    result=artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sqlpath];spec=json.loads(result[specpath]);checks=[];pre=[]
    for e in pack['enemies']:
        entry=e['entry'];xp=e['source_slayer_xp_tenths']
        sql+=f"UPDATE warscape_enemy_variant SET source_slayer_xp_tenths={xp} WHERE creature_entry={entry};\n"
        checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND source_slayer_xp_tenths={xp})=1')
        if e.get('behaviour'):
            sql+=f"UPDATE creature_template SET AIName='',ScriptName='npc_warscape_enemy' WHERE entry={entry};\n"
            spec['verify_sql'],n=re.subn(rf"(FROM creature_template WHERE entry={entry} AND .*?)AIName='AggressorAI'",r"\1AIName=''",spec['verify_sql'],count=1)
            if n!=1:raise ValueError('Missing native AI contract')
            checks.append(f"(SELECT COUNT(*) FROM creature_template WHERE entry={entry} AND AIName='' AND ScriptName='npc_warscape_enemy')=1")
    for item in pack['items']:
        if item.get('inventory_type')!=1:continue
        entry=item['entry']
        sql+=f"UPDATE item_template SET class=4,subclass=1,InventoryType=1,stackable=1,description='Protects against Banshee screams when worn on your head.' WHERE entry={entry};\n"
        spec['verify_sql'],n=re.subn(rf"(WHERE entry={entry} AND name=.*?)class=15 AND stackable=200",r"\1class=4 AND stackable=1",spec['verify_sql'],count=1)
        if n!=1:raise ValueError('Missing headgear contract')
        checks.append(f'(SELECT COUNT(*) FROM item_template WHERE entry={entry} AND class=4 AND subclass=1 AND InventoryType=1 AND stackable=1)=1')
    for spell in pack['client_spells']:
        if not spell.get('script'):continue
        entry,name=spell['entry'],spell['script']
        sql+=f"INSERT INTO spell_script_names (spell_id,ScriptName) VALUES ({entry},'{name}');\n"
        pre.append(f'(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={entry})=0')
        checks.append(f"(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={entry} AND ScriptName='{name}')=1")
    pre.append('(SELECT COUNT(*) FROM item_template WHERE entry=902006 AND stackable=2147483647)=1')
    spec['precondition_sql']=spec['precondition_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(pre)+',1,0)'
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(checks)+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
