"""Append-only catalogue release extensions; older SQL and verification files are frozen."""
import hashlib
import json
from family_catalogue import ROOT, release_artifacts, quote


def artifacts(pack, prior, *, add_combat_columns=False, add_slayer_column=False):
    old_families = {f['id']:f for f in prior.get('families', [])}
    for family in pack['families']:
        old = old_families.get(family['id'])
        if family.get('existing',False):
            if not old or any(family[k] != old[k] for k in ('key','name','model_note')):
                raise ValueError('Existing family reference differs from its deployed identity')
        elif old or family['key'] in {f['key'] for f in old_families.values()}:
            raise ValueError('Family ID/key overlaps an earlier release')
    result = release_artifacts(pack, prior, create_schema=False, include_legacy=False)
    sql_path = ROOT / f"sql/updates/world/3.3.5/{pack['release']}.sql"
    spec_path = ROOT / f"contrib/warscape/verifications/{pack['release']}.json"
    sql = result[sql_path]
    spec = json.loads(result[spec_path])
    if add_slayer_column:
        first,rest=sql.split('\n',1)
        sql=first+'\nALTER TABLE warscape_enemy_variant ADD COLUMN source_slayer_level TINYINT UNSIGNED NOT NULL DEFAULT 0;\n'+rest
    checks = []
    updates = []
    if add_combat_columns:
        ddl = ('ALTER TABLE warscape_enemy_variant '
               'ADD COLUMN defence_stab INT NOT NULL DEFAULT 0, '
               'ADD COLUMN defence_slash INT NOT NULL DEFAULT 0, '
               'ADD COLUMN defence_crush INT NOT NULL DEFAULT 0, '
               'ADD COLUMN use_source_combat TINYINT UNSIGNED NOT NULL DEFAULT 0;\n')
        first, rest = sql.split('\n', 1)
        sql = first + '\n' + ddl + rest
        # Populate prior source metadata without changing their accepted runtime policies.
        for enemy in prior['enemies']:
            bonus = enemy.get('defence_bonus', prior['variants'][0]['defence_bonuses']['dstab'])
            entry = enemy['entry']
            updates.append(f'UPDATE warscape_enemy_variant SET defence_stab={bonus},defence_slash={bonus},defence_crush={bonus} WHERE creature_entry={entry};')
            checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND defence_stab={bonus} AND defence_slash={bonus} AND defence_crush={bonus} AND use_source_combat=0)=1')
    for enemy in pack['enemies']:
        lanes = enemy.get('defence_bonuses', dict.fromkeys(('stab','slash','crush'), enemy['defence_bonus']))
        entry = enemy['entry']
        enabled = int(enemy.get('source_combat_overrides', False))
        values = f"defence_stab={lanes['stab']},defence_slash={lanes['slash']},defence_crush={lanes['crush']},use_source_combat={enabled}"
        if 'source_slayer_level' in enemy:
            values += f",source_slayer_level={enemy['source_slayer_level']}"
        updates.append(f'UPDATE warscape_enemy_variant SET {values} WHERE creature_entry={entry};')
        checks.append(f"(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND " + values.replace(',', ' AND ') + ')=1')
    sql += '\n'.join(updates) + '\n'
    columns = "(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name IN ('defence_stab','defence_slash','defence_crush','use_source_combat'))"
    new_families=[f for f in pack['families'] if not f.get('existing',False)]
    pre=[columns+('=0' if add_combat_columns else '=4')]
    if new_families:
        family_ids=','.join(str(f['id']) for f in new_families)
        family_keys=','.join("'"+f['key'].replace("'","''")+"'" for f in new_families)
        pre.append(f'(SELECT COUNT(*) FROM warscape_enemy_family WHERE id IN ({family_ids}) OR family_key IN ({family_keys}))=0')
    for f in pack['families']:
        if f.get('existing',False):
            pre.append(f"(SELECT COUNT(*) FROM warscape_enemy_family WHERE id={f['id']} AND family_key={quote(f['key'])} AND name={quote(f['name'])})=1")
    if add_slayer_column or any('source_slayer_level' in e for e in pack['enemies']):
        slayer="(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name='source_slayer_level')"
        pre.append(slayer+('=0' if add_slayer_column else '=1'))
        checks.append("(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name='source_slayer_level' AND data_type='tinyint' AND column_type LIKE '%unsigned%' AND is_nullable='NO' AND column_default='0')=1")
        if add_slayer_column:
            previous_ids=','.join(str(e['entry']) for e in prior['enemies'])
            checks.append(f'(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry IN ({previous_ids}) AND source_slayer_level=0)={len(prior["enemies"])}')
    spec['precondition_sql'] = spec['precondition_sql'].removesuffix(',1,0)') + ' AND ' + ' AND '.join(pre) + ',1,0)'
    spec['verify_sql'] = spec['verify_sql'].removesuffix(',1,0)') + ' AND ' + ' AND '.join(checks + [columns+'=4']) + ',1,0)'
    spec['sha1'] = hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sql_path: sql, spec_path: json.dumps(spec, indent=2)+'\n'}
