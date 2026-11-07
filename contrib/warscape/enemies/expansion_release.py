"""Append-only catalogue release extensions; older SQL and verification files are frozen."""
import hashlib
import json
from family_catalogue import ROOT, release_artifacts


def artifacts(pack, prior, *, add_combat_columns=False):
    old_families = prior.get('families', [])
    if {f['id'] for f in pack['families']} & {f['id'] for f in old_families}:
        raise ValueError('Family ID overlaps an earlier release')
    if {f['key'] for f in pack['families']} & {f['key'] for f in old_families}:
        raise ValueError('Family key overlaps an earlier release')
    result = release_artifacts(pack, prior, create_schema=False, include_legacy=False)
    sql_path = ROOT / f"sql/updates/world/3.3.5/{pack['release']}.sql"
    spec_path = ROOT / f"contrib/warscape/verifications/{pack['release']}.json"
    sql = result[sql_path]
    spec = json.loads(result[spec_path])
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
        updates.append(f'UPDATE warscape_enemy_variant SET {values} WHERE creature_entry={entry};')
        checks.append(f"(SELECT COUNT(*) FROM warscape_enemy_variant WHERE creature_entry={entry} AND " + values.replace(',', ' AND ') + ')=1')
    sql += '\n'.join(updates) + '\n'
    columns = "(SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='warscape_enemy_variant' AND column_name IN ('defence_stab','defence_slash','defence_crush','use_source_combat'))"
    family_ids = ','.join(str(f['id']) for f in pack['families'])
    family_keys = ','.join("'" + f['key'].replace("'", "''") + "'" for f in pack['families'])
    pre = [columns + ('=0' if add_combat_columns else '=4'), f'(SELECT COUNT(*) FROM warscape_enemy_family WHERE id IN ({family_ids}) OR family_key IN ({family_keys}))=0']
    spec['precondition_sql'] = spec['precondition_sql'].removesuffix(',1,0)') + ' AND ' + ' AND '.join(pre) + ',1,0)'
    spec['verify_sql'] = spec['verify_sql'].removesuffix(',1,0)') + ' AND ' + ' AND '.join(checks + [columns+'=4']) + ',1,0)'
    spec['sha1'] = hashlib.sha1(sql.encode()).hexdigest().upper()
    return {sql_path: sql, spec_path: json.dumps(spec, indent=2)+'\n'}
