"""Generate custom creature metadata alongside the unchanged catalogue pipeline."""
import hashlib
import json
from family_catalogue import ROOT
from elemental_release import elemental_artifacts


def custom_artifacts(pack, prior):
    out = elemental_artifacts(pack, prior)
    sqlpath = ROOT/f"sql/updates/world/3.3.5/{pack['release']}.sql"
    specpath = ROOT/f"contrib/warscape/verifications/{pack['release']}.json"
    manifest = json.loads((ROOT/'contrib/warscape/enemies'/pack['custom_model_manifest']).read_text())
    display = manifest['display_id']
    radius, reach = manifest['bounding_radius'], manifest['combat_reach']
    sql = out[sqlpath]+f"INSERT INTO creature_model_info (DisplayID,BoundingRadius,CombatReach,Gender,DisplayID_Other_Gender) VALUES ({display},{radius},{reach},2,0);\n"
    spec = json.loads(out[specpath])
    spec['precondition_sql'] = spec['precondition_sql'].removesuffix(',1,0)')+f' AND (SELECT COUNT(*) FROM creature_model_info WHERE DisplayID={display})=0,1,0)'
    spec['verify_sql'] = spec['verify_sql'].removesuffix(',1,0)')+f' AND (SELECT COUNT(*) FROM creature_model_info WHERE DisplayID={display} AND ABS(BoundingRadius-{radius})<0.001 AND ABS(CombatReach-{reach})<0.001 AND Gender=2 AND DisplayID_Other_Gender=0)=1,1,0)'
    spec['sha1'] = hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sqlpath: sql, specpath: json.dumps(spec, indent=2)+'\n'}
