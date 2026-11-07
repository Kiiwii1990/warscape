"""Append-only ranged/hybrid script bindings and precise Slayer reference metadata."""
import hashlib,json,re
from family_catalogue import ROOT
from expansion_release import artifacts

def ranged_artifacts(pack,prior):
    result=artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sqlpath];spec=json.loads(result[specpath]);checks=[]
    first,rest=sql.split('\n',1)
    sql=first+'\nALTER TABLE warscape_enemy_variant ADD COLUMN source_slayer_xp_tenths INT UNSIGNED NOT NULL DEFAULT 0;\n'+rest
    for e in pack['enemies']:
        entry=e['entry'];xp=e['source_slayer_xp_tenths']
        sql+=f'UPDATE warscape_enemy_variant SET source_slayer_xp_tenths={xp} WHERE creature_entry={entry};\n'
        checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND source_slayer_xp_tenths={xp})=1')
        if e.get('behaviour'):
            sql+=f"UPDATE creature_template SET AIName='',ScriptName='npc_warscape_enemy' WHERE entry={entry};\n"
            spec['verify_sql'],count=re.subn(rf"(FROM creature_template WHERE entry={entry} AND .*?)AIName='AggressorAI'",r"\1AIName=''",spec['verify_sql'],count=1)
            if count!=1:raise ValueError('Missing native AI contract')
            checks.append(f"(SELECT COUNT(*) FROM creature_template WHERE entry={entry} AND ScriptName='npc_warscape_enemy' AND AIName='')=1")
    for spell in (900710,900711,900712):
        sql+=f"INSERT INTO spell_script_names (spell_id,ScriptName) VALUES ({spell},'spell_warscape_enemy_ranged_hybrid');\n"
        checks.append(f"(SELECT COUNT(*) FROM spell_script_names WHERE spell_id={spell} AND ScriptName='spell_warscape_enemy_ranged_hybrid')=1")
    column="(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name='source_slayer_xp_tenths')"
    pre=[column+'=0',"(SELECT COUNT(*) FROM spell_script_names WHERE spell_id IN (900710,900711,900712))=0"]
    checks.append("(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name='source_slayer_xp_tenths' AND data_type='int' AND column_type LIKE '%unsigned%' AND is_nullable='NO' AND column_default='0')=1")
    ids=','.join(str(e['entry']) for e in prior['enemies'])
    checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry IN ({ids}) AND source_slayer_xp_tenths=0)={len(prior["enemies"])}')
    spec['precondition_sql']=spec['precondition_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(pre)+',1,0)'
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+' AND '.join(checks)+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
