"""Gargoyle finisher item binding; previous releases stay immutable."""
import hashlib,json,re
from family_catalogue import ROOT
from elemental_release import elemental_artifacts

def stalker_artifacts(pack,prior):
    result=elemental_artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sqlpath];spec=json.loads(result[specpath])
    item=next(i['entry'] for i in pack['items'] if i['name']=='Rock hammer')
    sql+=f"UPDATE item_template SET class=0,ScriptName='item_warscape_rock_hammer',spellid_1=900750,spelltrigger_1=0,spellcharges_1=0 WHERE entry={item};\n"
    spec['verify_sql'],n=re.subn(rf"(WHERE entry={item} AND name=.*?)class=15",r"\1class=0",spec['verify_sql'],count=1)
    if n!=1:raise ValueError('Missing hammer verification')
    check=f"(SELECT COUNT(*) FROM item_template WHERE entry={item} AND class=0 AND ScriptName='item_warscape_rock_hammer' AND spellid_1=900750 AND spelltrigger_1=0 AND spellcharges_1=0)=1"
    spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+check+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
