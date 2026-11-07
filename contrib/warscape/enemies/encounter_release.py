"""Additive script/item bindings for the ordered desert/druid release."""
import hashlib,json,re
from family_catalogue import ROOT
from expansion_release import artifacts

def encounter_artifacts(pack,prior):
    result=artifacts(pack,prior)
    sql_path=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    spec_path=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sql_path];spec=json.loads(result[spec_path]);checks=[];pre=[]
    for enemy in pack['enemies']:
        if enemy.get('behaviour'):
            entry=enemy['entry'];sql+=f"UPDATE creature_template SET AIName='',ScriptName='npc_warscape_enemy' WHERE entry={entry};\n"
            # The base artifact expects native AI; substitute the reviewed scripted AI contract.
            spec['verify_sql'],matched=re.subn(rf"(FROM creature_template WHERE entry={entry} AND .*?)AIName='AggressorAI'",r"\1AIName=''",spec['verify_sql'],count=1)
            if matched!=1:raise ValueError('Missing native AI verification contract')
            checks.append(f"(SELECT COUNT(*) FROM creature_template WHERE entry={entry} AND AIName='' AND ScriptName='npc_warscape_enemy')=1")
    cooler=next(i for i in pack['items'] if i['name']=='Ice cooler')['entry']
    spell=pack['client_spells'][0]['entry']
    sql+=f"UPDATE item_template SET class=0,ScriptName='item_warscape_ice_cooler',spellid_1={spell},spelltrigger_1=0,spellcharges_1=0 WHERE entry={cooler};\n"
    # Base item check has class=15; retain every other identity/display/stack assertion.
    spec['verify_sql']=re.sub(rf"(WHERE entry={cooler} .*?)AND class=15",r"\1AND class=0",spec['verify_sql'],count=1)
    checks.append(f"(SELECT COUNT(*) FROM item_template WHERE entry={cooler} AND class=0 AND ScriptName='item_warscape_ice_cooler' AND spellid_1={spell} AND spelltrigger_1=0 AND spellcharges_1=0)=1")
    for id,name in ((900701,'spell_warscape_enemy_magic'),(900702,'spell_warscape_enemy_poison')):
        sql+=f"INSERT INTO spell_script_names (spell_id,ScriptName) VALUES ({id},'{name}');\n"
        pre.append(f"(SELECT COUNT(*) FROM spell_script_names WHERE ScriptName='{name}')=0")
        checks.append(f"(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={id} AND ScriptName='{name}')=1")
    spec['precondition_sql']=spec['precondition_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(pre)+',1,0)'
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(checks)+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sql_path:sql,spec_path:json.dumps(spec,indent=2)+'\n'}
