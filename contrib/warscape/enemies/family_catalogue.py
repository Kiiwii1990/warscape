"""Second immutable enemy release and combined runtime catalogue.
Native combat/loot remain authoritative; JSON supplies reviewed family metadata.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).with_name('farm_animals_rats.json')
HEADER = ROOT / 'src/server/game/Entities/Unit/WarscapeEnemyCatalogue.h'


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def normalized_legacy(old):
    enemy = dict(old['enemies'][0])
    variant = old['variants'][0]
    enemy.update(family_id=1, subcategory='regular_2', source='Goblin',
                 source_npc_ids=variant['source_npc_ids'], combat_level=2,
                 attack_style='crush', slayer_xp=5, respawn_ticks=35,
                 source_poison_resistance=0, source_max_hit=1, native_attack_animation=True,
                 defence_bonus=variant['defence_bonuses']['dstab'],
                 guaranteed=[{'item': 'Bones', 'quantity': 1}])
    return enemy


def outcome_drops(enemy, outcome):
    """One selected outcome can contain paired items; native loot rolls quantity ranges."""
    return enemy['guaranteed'] + ([] if outcome['item'] == 'Nothing' else [outcome]) + outcome.get('additional', [])


def validate(pack, old):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    refs = pack.get('native_references', [])
    require(len({r['id'] for r in refs}) == len(refs) and len({r['item'] for r in refs}) == len(refs), 'Duplicate native reference')
    require(not ({r['id'] for r in refs} & {r['id'] for r in old.get('native_references', [])}), 'Native reference collision')
    require(all(type(r['id']) is int and 1 <= r['id'] <= 0xFFFFFFFF and type(r['count']) is int and r['count'] == 200 for r in refs), 'Invalid native reference')
    references = {r['item']:r for r in refs}
    items = pack['shared_items'] + pack['items']
    for key in ('entry', 'name'):
        require(len({x[key] for x in items}) == len(items), 'Duplicate item identity')
    old_items = {x['name']: x['entry'] for x in old['items']}
    for item in pack['shared_items']:
        require(old_items.get(item['name']) == item['entry'], 'Shared item differs from deployed release')
    require(not ({x['entry'] for x in pack['items']} & set(old_items.values())), 'New item collides with deployed item')
    family_ids = {f['id'] for f in pack['families']}
    require(len(family_ids) == len(pack['families']), 'Duplicate family ID')
    require(len({f['key'] for f in pack['families']}) == len(family_ids), 'Duplicate family key')
    names = {x['name'] for x in items}
    require(set(references).issubset(names), 'Unknown native reference item')
    used_loot = {enemy['loot_base'] + i for enemy in old['enemies'] for i in range(len(enemy['outcomes']))}
    for key in ('entry', 'profile_id'):
        require(len({e[key] for e in pack['enemies']}) == len(pack['enemies']), 'Duplicate enemy/profile ID')
        require(not ({e[key] for e in pack['enemies']} & {e[key] for e in old['enemies']}), 'Enemy/profile collides with deployed release')
    for enemy in pack['enemies']:
        require(enemy['family_id'] in family_ids, 'Unknown family')
        require(enemy['source'] in pack['sources'], 'Missing Wiki source')
        require(pack['sources'][enemy['source']]['url'].startswith('https://oldschool.runescape.wiki/w/'), 'Invalid Wiki provenance')
        require(len(enemy['stats']) == 6 and all(type(n) is int and (0 if i in (3,4) else 1) <= n <= 1000000 for i,n in enumerate(enemy['stats'])), 'Invalid combat stats')
        require(1 <= enemy['combat_level'] <= 255 and 2 <= enemy['attack_ticks'] <= 12, 'Unsupported level/speed')
        require(enemy['attack_style'] in ('stab', 'slash', 'crush'), 'Unsupported melee style')
        require(0 < enemy['scale'] <= 10 and type(enemy['aggressive']) is bool, 'Invalid model/aggression')
        require(all(-64 <= enemy[k] <= 1000000 for k in ('attack_bonus', 'strength_bonus', 'defence_bonus')), 'Invalid combat bonus')
        require(len(enemy.get('equipment', [0,0,0])) == 3 and all(type(i) is int and 0 <= i <= 0xFFFFFFFF for i in enemy.get('equipment', [])), 'Invalid equipment display items')
        # Existing OSRS max-hit formula, checked against the published source value.
        require(type(enemy.get('source_combat_overrides', False)) is bool, 'Invalid source combat policy')
        if enemy.get('source_combat_overrides', False):
            require(type(enemy['source_max_hit']) is int and 0 <= enemy['source_max_hit'] <= 1000000, 'Invalid source maximum hit')
            require(set(enemy['defence_bonuses']) == {'stab', 'slash', 'crush'} and all(type(v) is int and -64 <= v <= 1000000 for v in enemy['defence_bonuses'].values()), 'Invalid directional defence')
        else:
            require(((enemy['stats'][1] + 8) * (enemy['strength_bonus'] + 64) + 320) // 640 == enemy['source_max_hit'], 'Source maximum hit does not match combat formula')
        require(type(enemy['denominator']) is int and 0 < enemy['denominator'] <= 0xFFFFFFFF and sum(o['weight'] for o in enemy['outcomes']) == enemy['denominator'], 'Invalid loot distribution')
        for i, outcome in enumerate(enemy['outcomes']):
            require(type(outcome['weight']) is int and 0 < outcome['weight'] <= enemy['denominator'], 'Invalid weight')
            drops = outcome_drops(enemy, outcome)
            require(len({d['item'] for d in drops}) == len(drops), 'Duplicate item in one outcome')
            require(all(d['item'] in names and type(d['quantity']) is int and type(d.get('quantity_max', d['quantity'])) is int and 1 <= d['quantity'] <= d.get('quantity_max', d['quantity']) <= (3600 if d['item'] in references and d['quantity'] == d.get('quantity_max', d['quantity']) else 255) for d in drops), 'Invalid loot item/count')
            if refs:
                require(sum((d.get('quantity_max', d['quantity']) + 199)//200 for d in drops) <= 18, 'Native loot slot limit')
            loot = enemy['loot_base'] + i
            require(loot not in used_loot, 'Loot ID collision')
            used_loot.add(loot)


def runtime_header(pack, old):
    enemies = [normalized_legacy(old)] + pack['enemies']
    families = {f['id']: f['name'] for f in pack['families']}
    pools, outcomes, metadata = [], [], []
    for enemy in enemies:
        first = len(outcomes)
        for i, outcome in enumerate(enemy['outcomes']):
            has_items = bool(outcome_drops(enemy, outcome))
            outcomes.append((outcome['weight'], enemy['loot_base'] + i if has_items else 0))
        pools.append((enemy['entry'], first, len(enemy['outcomes']), enemy['denominator']))
        metadata.append((enemy['entry'], enemy['family_id'], families[enemy['family_id']], enemy['subcategory'], enemy['attack_style'], enemy['slayer_xp'], enemy['respawn_ticks'], enemy['native_attack_animation'], enemy['source_max_hit'], *[enemy.get('defence_bonuses', {}).get(lane, enemy.get('defence_bonus', 0)) for lane in ('stab', 'slash', 'crush')], ('stab','slash','crush').index(enemy['attack_style']), enemy.get('source_combat_overrides', False)))
    text = '''// Generated by contrib/warscape/enemies/compile.py from immutable releases.
#ifndef WARSCAPE_ENEMY_CATALOGUE_H
#define WARSCAPE_ENEMY_CATALOGUE_H
#include <array>
#include <cstdint>
namespace Warscape {
struct EnemyLootOutcome { std::uint32_t Weight, Loot; };
struct EnemyLootPool { std::uint32_t Entry, First, Count, Total; };
struct EnemyVariant { std::uint32_t Entry, FamilyId; char const* Family; char const* Subcategory; char const* AttackStyle; std::uint32_t SlayerXP, RespawnTicks; bool NativeAttackAnimation; std::uint32_t MaximumHit; std::int32_t DefenceStab, DefenceSlash, DefenceCrush; std::uint8_t MeleeLane; bool SourceCombat; };
'''
    def array(kind, name, rows):
        return f'inline constexpr std::array<{kind}, {len(rows)}> {name} = {{{{\n' + ',\n'.join('    {' + ', '.join(json.dumps(v) for v in row) + '}' for row in rows) + '\n}};\n'
    text += array('EnemyLootOutcome', 'EnemyLootOutcomes', outcomes)
    text += array('EnemyLootPool', 'EnemyLootPools', pools)
    text += array('EnemyVariant', 'EnemyVariants', metadata)
    text += '''inline EnemyVariant const* FindEnemyVariant(std::uint32_t entry) {
    for (auto const& variant : EnemyVariants) if (variant.Entry == entry) return &variant;
    return nullptr;
}
inline std::uint32_t EnemyMaximumHit(std::uint32_t entry, std::uint32_t fallback) {
    auto const* variant = FindEnemyVariant(entry);
    return variant && variant->SourceCombat ? variant->MaximumHit : fallback;
}
inline std::int32_t EnemyMeleeDefence(std::uint32_t entry, std::uint8_t lane, std::int32_t fallback) {
    auto const* variant = FindEnemyVariant(entry);
    if (!variant || !variant->SourceCombat) return fallback;
    switch (lane) {
        case 0: return variant->DefenceStab;
        case 1: return variant->DefenceSlash;
        case 2: return variant->DefenceCrush;
        default: return fallback;
    }
}
inline EnemyLootPool const* FindEnemyLootPool(std::uint32_t entry) {
    for (auto const& pool : EnemyLootPools) if (pool.Entry == entry) return &pool;
    return nullptr;
}
inline std::uint32_t SelectEnemyLoot(std::uint32_t entry, std::uint32_t roll) {
    auto const* pool = FindEnemyLootPool(entry);
    if (!pool || roll >= pool->Total) return 0;
    for (std::uint32_t i = pool->First; i < pool->First + pool->Count; ++i) {
        auto const& outcome = EnemyLootOutcomes[i];
        if (roll < outcome.Weight) return outcome.Loot;
        roll -= outcome.Weight;
    }
    return 0;
}
}
#endif
'''
    return text


def release_artifacts(pack, old, *, create_schema=True, include_legacy=True):
    validate(pack, old)
    items = {x['name']: x for x in pack['shared_items'] + pack['items']}
    metadata_enemies = ([normalized_legacy(old)] if include_legacy else []) + pack['enemies']
    sources = dict(pack['sources'], Goblin=old['source'])
    sql = ['-- Generated enemy families release 2. Additive; release 1 is immutable.',
           'CREATE TABLE `warscape_enemy_family` (`id` INT UNSIGNED NOT NULL, `family_key` VARCHAR(64) NOT NULL, `name` VARCHAR(80) NOT NULL, `model_direction` VARCHAR(255) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY (`family_key`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;',
           'CREATE TABLE `warscape_enemy_variant` (`creature_entry` INT UNSIGNED NOT NULL, `family_id` INT UNSIGNED NOT NULL, `subcategory` VARCHAR(64) NOT NULL, `source_url` VARCHAR(255) NOT NULL, `source_npc_ids` VARCHAR(255) NOT NULL, `source_sha256` CHAR(64) NOT NULL, `attack_style` VARCHAR(8) NOT NULL, `source_max_hit` INT UNSIGNED NOT NULL, `slayer_xp` INT UNSIGNED NOT NULL, `respawn_ticks` INT UNSIGNED NOT NULL, `source_poison_resistance` INT UNSIGNED NOT NULL, PRIMARY KEY (`creature_entry`), KEY (`family_id`, `subcategory`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;']
    if not create_schema:
        sql = [f"-- Generated enemy release {pack['release']}; additive to prior releases."]
    checks = []
    for family in pack['families']:
        sql.append(f"INSERT INTO warscape_enemy_family VALUES ({family['id']},{quote(family['key'])},{quote(family['name'])},{quote(family['model_note'])});")
        checks.append(f"(SELECT COUNT(*) FROM warscape_enemy_family WHERE id={family['id']} AND family_key={quote(family['key'])} AND name={quote(family['name'])})=1")
    for item in pack['items']:
        sql.append(f"INSERT INTO item_template (entry,class,subclass,name,displayid,Quality,BuyCount,stackable,AllowableClass,AllowableRace,description,Material) SELECT {item['entry']},15,0,{quote(item['name'])},displayid,1,1,200,-1,-1,'OSRS enemy catalogue collectible; gameplay use is not implemented.',Material FROM item_template WHERE entry={item['display_source']};")
        checks.append(f"(SELECT COUNT(*) FROM item_template WHERE entry={item['entry']} AND name={quote(item['name'])} AND class=15 AND stackable=200 AND displayid=(SELECT displayid FROM item_template WHERE entry={item['display_source']}))=1")
    references = {r['item']:r for r in pack.get('native_references', [])}
    for name, ref in references.items():
        item = items[name]['entry']
        sql.append(f"INSERT INTO reference_loot_template (Entry,Item,Chance,MinCount,MaxCount,Comment) VALUES ({ref['id']},{item},100,{ref['count']},{ref['count']},'OSRS fixed stack reference');")
        checks.append(f"(SELECT COUNT(*) FROM reference_loot_template WHERE Entry={ref['id']})=1")
        checks.append(f"(SELECT COUNT(*) FROM reference_loot_template WHERE Entry={ref['id']} AND Item={item} AND Reference=0 AND Chance=100 AND MinCount={ref['count']} AND MaxCount={ref['count']})=1")
    expected_loot = []
    for enemy in pack['enemies']:
        entry, profile = enemy['entry'], enemy['profile_id']
        faction = 14 if enemy['aggressive'] else 31
        loot_id = enemy['loot_base'] if outcome_drops(enemy, enemy['outcomes'][0]) else 0
        sql.append(f"INSERT INTO creature_template (entry,modelid1,name,minlevel,maxlevel,faction,scale,speed_walk,speed_run,BaseAttackTime,RangeAttackTime,unit_class,type,lootid,AIName,ExperienceModifier,RegenHealth) VALUES ({entry},{enemy['model']},{quote(enemy['name'])},{enemy['combat_level']},{enemy['combat_level']},{faction},{enemy['scale']},1,1.14286,{enemy['attack_ticks']*600},2400,1,{enemy['creature_type']},{loot_id},'AggressorAI',0,1);")
        stats = ','.join(map(str, enemy['stats']))
        sql.append(f"INSERT INTO warscape_monster_profile (id,name,base_attack,base_strength,base_defence,base_ranged,base_magic,base_hitpoints,growth_attack,growth_strength,growth_defence,growth_ranged,growth_magic,growth_hitpoints,attack_bonus,strength_bonus,defence_bonus) VALUES ({profile},{quote(enemy['name'])},{stats},0,0,0,0,0,0,{enemy['attack_bonus']},{enemy['strength_bonus']},{enemy['defence_bonus']});")
        sql.append(f'INSERT INTO warscape_monster_template (entry,profile_id) VALUES ({entry},{profile});')
        sql.append(f"INSERT INTO warscape_monster_attack_speed VALUES ({entry},{enemy['attack_ticks']});")
        checks.append(f"(SELECT COUNT(*) FROM creature_template WHERE entry={entry} AND modelid1={enemy['model']} AND minlevel={enemy['combat_level']} AND maxlevel={enemy['combat_level']} AND faction={faction} AND ABS(scale-{enemy['scale']})<0.001 AND type={enemy['creature_type']} AND lootid={loot_id} AND AIName='AggressorAI' AND mingold=0 AND maxgold=0)=1")
        stat_checks = ' AND '.join(f'base_{key}={value} AND growth_{key}=0' for key, value in zip(('attack','strength','defence','ranged','magic','hitpoints'), enemy['stats']))
        checks.append(f"(SELECT COUNT(*) FROM warscape_monster_profile WHERE id={profile} AND {stat_checks} AND attack_bonus={enemy['attack_bonus']} AND strength_bonus={enemy['strength_bonus']} AND defence_bonus={enemy['defence_bonus']})=1")
        checks.append(f'(SELECT COUNT(*) FROM warscape_monster_template WHERE entry={entry} AND profile_id={profile})=1')
        checks.append(f"(SELECT COUNT(*) FROM warscape_monster_attack_speed WHERE creature_entry={entry} AND attack_speed_ticks={enemy['attack_ticks']})=1")
        if 'equipment' in enemy:
            hand, offhand, ranged = enemy['equipment']
            sql.append(f'INSERT INTO creature_equip_template (CreatureID,ID,ItemID1,ItemID2,ItemID3) VALUES ({entry},1,{hand},{offhand},{ranged});')
            checks.append(f'(SELECT COUNT(*) FROM creature_equip_template WHERE CreatureID={entry})=1')
            checks.append(f'(SELECT COUNT(*) FROM creature_equip_template WHERE CreatureID={entry} AND ID=1 AND ItemID1={hand} AND ItemID2={offhand} AND ItemID3={ranged})=1')

        for i, outcome in enumerate(enemy['outcomes']):
            loot = enemy['loot_base'] + i
            drops = outcome_drops(enemy, outcome)
            expected_loot.append(loot)
            row_count = sum(1 + int(d['quantity'] % references[d['item']]['count'] > 0) if d['quantity'] > 255 else 1 for d in drops)
            checks.append(f'(SELECT COUNT(*) FROM creature_loot_template WHERE Entry={loot})={row_count}')
            for drop in drops:
                item, count = items[drop['item']]['entry'], drop['quantity']
                maximum = drop.get('quantity_max', count)
                if count > 255:
                    ref = references[drop['item']]
                    loops, remainder = divmod(count, ref['count'])
                    sql.append(f"INSERT INTO creature_loot_template (Entry,Item,Reference,Chance,MinCount,MaxCount,Comment) VALUES ({loot},0,{ref['id']},100,1,{loops},'OSRS fixed count via native reference');")
                    checks.append(f"(SELECT COUNT(*) FROM creature_loot_template WHERE Entry={loot} AND Item=0 AND Reference={ref['id']} AND Chance=100 AND MinCount=1 AND MaxCount={loops})=1")
                    if not remainder:
                        continue
                    count = maximum = remainder
                sql.append(f"INSERT INTO creature_loot_template (Entry,Item,Chance,MinCount,MaxCount,Comment) VALUES ({loot},{item},100,{count},{maximum},'OSRS family catalogue guaranteed outcome');")
                checks.append(f'(SELECT COUNT(*) FROM creature_loot_template WHERE Entry={loot} AND Item={item} AND Chance=100 AND MinCount={count} AND MaxCount={maximum})=1')
    for enemy in metadata_enemies:
        source = sources[enemy['source']]
        values = [enemy['entry'], enemy['family_id'], enemy['subcategory'], source['url'], enemy['source_npc_ids'], source['raw_sha256'], enemy['attack_style'], enemy['source_max_hit'], enemy['slayer_xp'], enemy['respawn_ticks'], enemy['source_poison_resistance']]
        prefix = 'INSERT INTO warscape_enemy_variant' + ('' if create_schema else ' (creature_entry,family_id,subcategory,source_url,source_npc_ids,source_sha256,attack_style,source_max_hit,slayer_xp,respawn_ticks,source_poison_resistance)') + ' VALUES ('
        sql.append(prefix + ','.join(str(x) if isinstance(x, int) else quote(x) for x in values) + ');')
        columns = ['creature_entry','family_id','subcategory','source_url','source_npc_ids','source_sha256','attack_style','source_max_hit','slayer_xp','respawn_ticks','source_poison_resistance']
        checks.append('(SELECT COUNT(*) FROM warscape_enemy_variant WHERE ' + ' AND '.join(k+'='+ (str(v) if isinstance(v,int) else quote(v)) for k,v in zip(columns,values)) + ')=1')
    pre = ["(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name IN ('warscape_enemy_family','warscape_enemy_variant'))=0"]
    if not create_schema:
        pre = ["(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name IN ('warscape_enemy_family','warscape_enemy_variant') AND engine='InnoDB')=2"]
    def ids(values): return ','.join(map(str, values))
    for table, key, values in [('creature_template','entry',[e['entry'] for e in pack['enemies']]),('creature','id',[e['entry'] for e in pack['enemies']]),('warscape_monster_profile','id',[e['profile_id'] for e in pack['enemies']]),('warscape_monster_template','entry',[e['entry'] for e in pack['enemies']]),('warscape_monster_attack_speed','creature_entry',[e['entry'] for e in pack['enemies']]),('item_template','entry',[i['entry'] for i in pack['items']]),('creature_loot_template','Entry',expected_loot)]:
        pre.append(f'(SELECT COUNT(*) FROM {table} WHERE {key} IN ({ids(values)}))=0')
    for item in pack['shared_items']:
        pre.append(f"(SELECT COUNT(*) FROM item_template WHERE entry={item['entry']} AND name={quote(item['name'])})=1")
    for item in pack['items']:
        pre.append(f"(SELECT COUNT(*) FROM item_template WHERE entry={item['display_source']})=1")
    for name, ref in references.items():
        pre.append(f"(SELECT COUNT(*) FROM reference_loot_template WHERE Entry={ref['id']})=0")
        pre.append(f"(SELECT COUNT(*) FROM item_template WHERE entry={items[name]['entry']} AND stackable=200)=1")
    pre.append('(SELECT COUNT(*) FROM creature_template WHERE entry=901000)=1')
    checks.append("(SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name IN ('warscape_enemy_family','warscape_enemy_variant') AND engine='InnoDB')=2")
    text = '\n'.join(sql) + '\n'
    equipped = [e for e in pack['enemies'] if 'equipment' in e]
    if equipped:
        pre.append('(SELECT COUNT(*) FROM creature_equip_template WHERE CreatureID IN (' + ids([e['entry'] for e in equipped]) + '))=0')
        equipment_items = sorted({i for e in equipped for i in e['equipment'] if i})
        if equipment_items:
            pre.append('(SELECT COUNT(*) FROM item_template WHERE entry IN (' + ids(equipment_items) + '))=' + str(len(equipment_items)))
    spec = {'sha1': hashlib.sha1(text.encode()).hexdigest().upper(), 'precondition_sql': 'SELECT IF('+' AND '.join(pre)+',1,0)', 'verify_sql':'SELECT IF('+' AND '.join(checks)+',1,0)'}
    return {ROOT / f"sql/updates/world/3.3.5/{pack['release']}.sql":text,
            ROOT / f"contrib/warscape/verifications/{pack['release']}.json":json.dumps(spec,indent=2)+'\n'}
