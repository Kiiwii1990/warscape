"""Additive draconic encounters: full-count runtime drops, native shields and spells."""
import hashlib,json,re
from family_catalogue import ROOT
from expansion_release import artifacts

def draconic_artifacts(pack,prior):
    result=artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sqlpath];spec=json.loads(result[specpath]);checks=[];pre=[]
    for e in pack['enemies']:
        entry=e['entry'];xp=e['source_slayer_xp_tenths']
        sql+=f'UPDATE warscape_enemy_variant SET source_slayer_xp_tenths={xp} WHERE creature_entry={entry};\n'
        checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND source_slayer_xp_tenths={xp})=1')
        if e.get('behaviour'):
            sql+=f"UPDATE creature_template SET AIName='',ScriptName='npc_warscape_enemy' WHERE entry={entry};\n"
            spec['verify_sql'],n=re.subn(rf"(FROM creature_template WHERE entry={entry} AND .*?)AIName='AggressorAI'",r"\1AIName=''",spec['verify_sql'],count=1)
            if n!=1:raise ValueError('Missing native AI contract')
            checks.append(f"(SELECT COUNT(*) FROM creature_template WHERE entry={entry} AND ScriptName='npc_warscape_enemy' AND AIName='')=1")
    for item in pack['items']:
        if item.get('inventory_type')!=14:continue
        entry=item['entry']
        sql+=f"UPDATE item_template SET class=4,subclass=6,InventoryType=14,stackable=1,description='Equip in your off hand for Warscape breath protection.' WHERE entry={entry};\n"
        spec['verify_sql'],n=re.subn(rf"(WHERE entry={entry} AND name=.*?)class=15 AND stackable=200",r"\1class=4 AND stackable=1",spec['verify_sql'],count=1)
        if n!=1:raise ValueError('Missing shield contract')
        checks.append(f'(SELECT COUNT(*) FROM item_template WHERE entry={entry} AND class=4 AND subclass=6 AND InventoryType=14 AND stackable=1)=1')
    bindings=[(sp['entry'],'spell_warscape_enemy_poison' if sp['entry']==900721 else 'spell_warscape_enemy_breath' if sp['entry'] in (900725,900727) else 'spell_warscape_enemy_ranged_hybrid') for sp in pack['client_spells'] if sp['entry']!=900728]
    for entry,name in bindings:
        sql+=f"INSERT INTO spell_script_names (spell_id,ScriptName) VALUES ({entry},'{name}');\n"
        pre.append(f'(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={entry})=0')
        checks.append(f"(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={entry} AND ScriptName='{name}')=1")
    pre.append("(SELECT COUNT(*) FROM item_template WHERE entry=902006 AND stackable=2147483647)=1")
    spec['precondition_sql']=spec['precondition_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(pre)+',1,0)'
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(checks)+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
