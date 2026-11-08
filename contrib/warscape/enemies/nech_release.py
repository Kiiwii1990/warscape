"""Consumable finisher bindings for the regular cave checkpoint."""
import hashlib,json,re
from family_catalogue import ROOT
from elemental_release import elemental_artifacts

def nech_artifacts(pack,prior):
    result=elemental_artifacts(pack,prior)
    sqlpath=ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath=ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    sql=result[sqlpath];spec=json.loads(result[specpath])
    for name,spell,script in [('Bag of salt',900773,'item_warscape_salt'),('Fungicide spray dose',900774,'item_warscape_fungicide_dose')]:
        entry=next(i['entry'] for i in pack['items'] if i['name']==name)
        sql+=f"UPDATE item_template SET class=0,ScriptName='{script}',spellid_1={spell},spelltrigger_1=0,spellcharges_1=0 WHERE entry={entry};\n"
        spec['verify_sql'],n=re.subn(rf"(WHERE entry={entry} AND name=.*?)class=15",r"\1class=0",spec['verify_sql'],count=1)
        if n!=1:raise ValueError('Missing finisher verification')
        check=f"(SELECT COUNT(*) FROM item_template WHERE entry={entry} AND class=0 AND ScriptName='{script}' AND spellid_1={spell} AND spelltrigger_1=0 AND spellcharges_1=0)=1"
        spec['verify_sql']=spec['verify_sql'].removesuffix(',1,0)')+' AND '+check+',1,0)'
    spec['sha1']=hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath:sql,specpath:json.dumps(spec,indent=2)+'\n'}
