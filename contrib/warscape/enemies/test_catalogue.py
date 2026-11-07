import copy,importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('catalogue_compiler',Path(__file__).with_name('compile.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def prior_to(filename):
    prior=json.loads(Path(__file__).with_name('goblins.json').read_text())
    prior.update(families=[],native_references=[])
    for release in json.loads(Path(__file__).with_name('releases.json').read_text()):
        if release['data']==filename:return prior
        pack=json.loads(Path(__file__).with_name(release['data']).read_text())
        for key in ('enemies','items','native_references'):prior[key].extend(pack.get(key,[]))
        prior['families'].extend(f for f in pack['families'] if f['id'] not in {old['id'] for old in prior['families']})
    raise ValueError('Unknown release')

class CatalogueTests(unittest.TestCase):
    def setUp(self):self.c=json.loads(Path(__file__).with_name('goblins.json').read_text())
    def test_bad_distribution_refused(self):
        self.c['enemies'][0]['outcomes'][0]['weight']+=1
        with self.assertRaises(ValueError):m.compile_data(self.c)
    def test_duplicate_item_id_refused(self):
        self.c['items'][1]['entry']=self.c['items'][0]['entry']
        with self.assertRaises(ValueError):m.compile_data(self.c)
    def test_unsupported_variant_refused(self):
        self.c['enemies'][0]['variant']='goblin_4'
        with self.assertRaises(ValueError):m.compile_data(self.c)
    def test_source_stats_and_coin_outcomes(self):
        v=self.c['variants'][0];self.assertEqual(v['stats'],[1,1,1,1,1,5]);self.assertEqual(v['attack_ticks'],4)
        self.assertEqual([(x['quantity'],x['weight']) for x in self.c['enemies'][0]['outcomes'] if x['item']=='Coins'],[(15,28),(20,2),(1,1)])
class FamilyCatalogueTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module = family_catalogue
        self.pack = json.loads(family_catalogue.DATA.read_text(encoding='utf-8'))
        self.old = json.loads(Path(__file__).with_name('goblins.json').read_text())
    def test_regular_rat_is_empty_and_stronghold_rat_has_bones(self):
        rat = next(e for e in self.pack['enemies'] if e['subcategory'] == 'regular' and e['family_id'] == 3)
        security = next(e for e in self.pack['enemies'] if e['subcategory'] == 'stronghold')
        self.assertEqual(rat['guaranteed'], [])
        self.assertEqual(security['guaranteed'], [{'item':'Bones','quantity':1}])
        self.assertEqual(rat['source_max_hit'], 0)
    def test_cow_drops_and_giant_rat_tiers(self):
        cow = next(e for e in self.pack['enemies'] if e['family_id'] == 2)
        self.assertEqual({d['item'] for d in cow['guaranteed']}, {'Bones','Raw beef','Cowhide'})
        giants = [e for e in self.pack['enemies'] if e['subcategory'].startswith('giant_')]
        self.assertEqual([(e['combat_level'],e['stats'][5]) for e in giants], [(3,5),(6,10),(26,25)])
        self.assertTrue(all(e['family_id'] == 3 for e in giants))
        self.assertEqual(giants[-1]['guaranteed'], [{'item':'Bones','quantity':1}])
    def test_bad_max_hit_refused(self):
        self.pack['enemies'][1]['source_max_hit'] = 1
        with self.assertRaisesRegex(ValueError,'maximum hit'):
            self.module.validate(self.pack,self.old)
    def test_shared_bones_identity_cannot_change(self):
        self.pack['shared_items'][0]['entry'] = 999
        with self.assertRaisesRegex(ValueError,'Shared item'):
            self.module.validate(self.pack,self.old)
    def test_loot_collisions_with_deployed_goblin_refused(self):
        self.pack['enemies'][0]['loot_base'] = 901000
        with self.assertRaisesRegex(ValueError,'Loot ID collision'):
            self.module.validate(self.pack,self.old)
    def test_oversized_loot_quantity_refused(self):
        self.pack['enemies'][0]['guaranteed'][0]['quantity'] = 256
        with self.assertRaisesRegex(ValueError,'count'):
            self.module.validate(self.pack,self.old)

class WildlifeTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module = family_catalogue
        self.pack = json.loads(Path(__file__).with_name('wildlife.json').read_text(encoding='utf-8'))
        self.prior = json.loads(Path(__file__).with_name('goblins.json').read_text())
        previous = json.loads(Path(__file__).with_name('farm_animals_rats.json').read_text())
        self.prior['items'].extend(previous['items'])
        self.prior['enemies'].extend(previous['enemies'])
    def test_twenty_one_variants_five_families(self):
        self.module.validate(self.pack, self.prior)
        self.assertEqual(len(self.pack['enemies']),21)
        self.assertEqual({e['family_id'] for e in self.pack['enemies']},{4,5,6,7,8})
    def test_explicit_caps_preserve_published_values(self):
        values={e['entry']:e['source_max_hit'] for e in self.pack['enemies']}
        self.assertEqual((values[901033],values[901035],values[901041],values[901042]),(3,5,0,1))
    def test_directional_scorpion_defence(self):
        source=next(e for e in self.pack['enemies'] if e['entry']==901049)
        self.assertEqual(source['defence_bonuses'],{'stab':35,'slash':15,'crush':15})
    def test_no_saddled_wolf_or_unimplemented_poison(self):
        for e in self.pack['enemies']:
            self.assertNotIn('Riding',e['model_path'])
            self.assertTrue(e['native_attack_animation'])
        self.assertNotIn(5242,[int(i) for e in self.pack['enemies'] for i in e['source_npc_ids'].split(',')])
    def test_members_style_wolf_bones_are_explicit(self):
        wolves=[e for e in self.pack['enemies'] if e['family_id']==6]
        self.assertEqual(len(wolves),5)
        self.assertTrue(all(e['guaranteed']==[{'item':'Wolf bones','quantity':1}] for e in wolves))
        self.assertIn('members-world',self.pack['loot_policy'])
    def test_spider_scorpion_have_no_unconditional_loot(self):
        self.assertTrue(all(not e['guaranteed'] for e in self.pack['enemies'] if e['family_id'] in (7,8)))
    def test_missing_defence_lane_refused(self):
        del self.pack['enemies'][0]['defence_bonuses']['slash']
        with self.assertRaisesRegex(ValueError,'directional defence'):
            self.module.validate(self.pack,self.prior)
    def test_oversized_cap_refused(self):
        self.pack['enemies'][0]['source_max_hit']=1000001
        with self.assertRaisesRegex(ValueError,'maximum hit'):
            self.module.validate(self.pack,self.prior)


class CoastalTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module = family_catalogue
        self.pack = json.loads(Path(__file__).with_name('coastal_wildlife.json').read_text())
        self.prior = json.loads(Path(__file__).with_name('goblins.json').read_text())
        self.prior['families'] = []
        for name in ('farm_animals_rats.json', 'wildlife.json'):
            old = json.loads(Path(__file__).with_name(name).read_text())
            for key in ('enemies', 'items', 'families'):
                self.prior[key].extend(old[key])
    def enemy(self, entry):
        return next(e for e in self.pack['enemies'] if e['entry'] == entry)
    def test_batch_has_28_distinct_variants_seven_families(self):
        self.module.validate(self.pack, self.prior)
        self.assertEqual(len(self.pack['enemies']), 28)
        self.assertEqual({e['family_id'] for e in self.pack['enemies']}, set(range(9,16)))
        self.assertEqual(len({e['source_npc_ids'] for e in self.pack['enemies']}), 28)
    def test_chicken_exact_feather_chances(self):
        e = self.enemy(901062)
        self.assertEqual(e['denominator'], 128)
        self.assertEqual([(o['item'], o['quantity'], o['weight']) for o in e['outcomes']], [('Feather',5,64),('Feather',15,32),('Nothing',1,32)])
        self.assertEqual([d['item'] for d in e['guaranteed']], ['Bones','Raw chicken'])
        self.assertEqual(e['source_max_hit'], 0)
    def test_ducks_no_loot(self):
        for entry in (901068,901069):
            e = self.enemy(entry)
            self.assertFalse(e['guaranteed'])
            self.assertEqual(e['outcomes'][0]['item'], 'Nothing')
    def test_gem_chances_and_pre_quest_talisman(self):
        from fractions import Fraction
        for entry in range(901071,901075):
            e = self.enemy(entry)
            chances = lambda n: sum(Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if o['item']==n)
            self.assertEqual(chances('Uncut sapphire'), Fraction(32,16384))
            self.assertEqual(chances('Nature talisman'), Fraction(4,16384))
            self.assertEqual(chances('Rune javelin'), Fraction(1,16384))
    def test_ammonite_minerals_are_one_paired_roll(self):
        e=self.enemy(901074)
        mineral=[o for o in e['outcomes'] if o['item']=='Calcite']
        self.assertEqual(len(mineral),1)
        self.assertEqual(mineral[0]['additional'],[{'item':'Pyrophosphite','quantity':1}])
        self.assertEqual(mineral[0]['weight']*128,e['denominator'])
        self.assertFalse(any(o['item']=='Pyrophosphite' for o in e['outcomes']))
    def test_quantity_ranges_emitted_without_probability_expansion(self):
        from expansion_release import artifacts
        sql=next(v for k,v in artifacts(self.pack,self.prior).items() if k.suffix=='.sql')
        e=self.enemy(901073)
        row=next(o for o in e['outcomes'] if o['item']=='Coins' and o['quantity']==4)
        self.assertEqual(row['quantity_max'],10)
        loot=e['loot_base']+e['outcomes'].index(row)
        self.assertIn(f'VALUES ({loot},902006,100,4,10,',sql)
    def test_bad_range_and_duplicate_paired_items_refused(self):
        e=self.enemy(901074)
        o=next(o for o in e['outcomes'] if o['item']=='Calcite')
        o['additional'][0]['quantity_max']=0
        with self.assertRaisesRegex(ValueError,'count'):self.module.validate(self.pack,self.prior)
        o['additional']=[{'item':'Calcite','quantity':1}]
        with self.assertRaisesRegex(ValueError,'Duplicate item'):self.module.validate(self.pack,self.prior)
    def test_swamp_bloom_and_monkey_quest_drops_not_unconditional(self):
        self.assertFalse(self.enemy(901073)['guaranteed'])
        for entry in (901080,901081):
            self.assertEqual(self.enemy(entry)['guaranteed'],[{'item':'Monkey bones','quantity':1}])
    def test_land_crocodile_herb_table(self):
        e=self.enemy(901075)
        self.assertEqual(e['source_npc_ids'],'11582')
        self.assertEqual(e['defence_bonuses'],{'stab':20,'slash':12,'crush':22})
        herbs=[o for o in e['outcomes'] if o['item']!='Nothing']
        self.assertEqual(sum(o['weight'] for o in herbs)*20,e['denominator'])
        self.assertEqual(next(o['weight'] for o in herbs if o['item']=='Grimy guam leaf'),32)


class DungeonTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module=family_catalogue
        self.pack=json.loads(Path(__file__).with_name('dungeon_humanoids.json').read_text())
        self.prior=json.loads(Path(__file__).with_name('goblins.json').read_text())
        self.prior['families']=[]
        for name in ('farm_animals_rats.json','wildlife.json','coastal_wildlife.json'):
            old=json.loads(Path(__file__).with_name(name).read_text())
            for key in ('enemies','items','families'):self.prior[key].extend(old[key])
    def enemy(self,entry):return next(e for e in self.pack['enemies'] if e['entry']==entry)
    def chance(self,e,name,quantity=None):
        from fractions import Fraction
        return sum(Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if (o['item']==name and (quantity is None or o['quantity']==quantity)) or (quantity is None and any(d['item']==name for d in o.get('additional',[]))))
    def test_39_variants_eight_families_and_prior_release_preserved(self):
        self.module.validate(self.pack,self.prior)
        self.assertEqual(len(self.pack['enemies']),39)
        self.assertEqual({e['family_id'] for e in self.pack['enemies']},set(range(16,24)))
        self.assertEqual(len({e['source_npc_ids'] for e in self.pack['enemies']}),39)
    def test_dwarf_timing_and_source_defence_variants(self):
        self.assertEqual([self.enemy(i)['attack_ticks'] for i in (901100,901104,901107)],[5,4,6])
        self.assertEqual(self.enemy(901106)['defence_bonuses'],{'stab':0,'slash':10,'crush':10})
        self.assertNotIn('292',[e['source_npc_ids'] for e in self.pack['enemies']])
    def test_skeleton_loot_flavours_and_negative_crush(self):
        from fractions import Fraction
        for entry in (901119,901121,901123,901124,901126):
            self.assertEqual(self.enemy(entry)['denominator'],1)
            self.assertEqual(self.enemy(entry)['outcomes'][0]['item'],'Nothing')
        self.assertEqual(self.enemy(901118)['defence_bonuses']['crush'],-5)
        self.assertEqual(self.chance(self.enemy(901118),'Grimy guam leaf'),Fraction(21*32,128*128))
        self.assertEqual(self.chance(self.enemy(901122),'Air rune',12),Fraction(3,256))
        self.assertEqual(self.chance(self.enemy(901122),'Air rune',15),Fraction(3,256))
    def test_zombie_member_coins_and_herbs(self):
        from fractions import Fraction
        self.assertEqual(self.chance(self.enemy(901127),'Coins',10),Fraction(11,128))
        self.assertEqual(self.chance(self.enemy(901129),'Coins',10),Fraction(10,128))
        self.assertEqual(self.chance(self.enemy(901127),'Grimy guam leaf'),Fraction(25*32,128*128))
        self.assertEqual(self.enemy(901128)['denominator'],1)
    def test_ghosts_empty_ghoul_bones(self):
        for i in (901130,901131,901132):
            self.assertFalse(self.enemy(i)['guaranteed'])
            self.assertEqual(self.enemy(i)['outcomes'][0]['item'],'Nothing')
        self.assertEqual(self.enemy(901133)['guaranteed'],[{'item':'Bones','quantity':1}])
    def test_hellhound_independent_stone_and_rune_marginals(self):
        from fractions import Fraction
        e=self.enemy(901134)
        self.assertEqual(self.chance(e,'Smouldering stone'),Fraction(1,32768))
        for q,rate in ((10,6),(20,3),(50,1)):self.assertEqual(self.chance(e,'Death rune',q),Fraction(rate,50))
        self.assertTrue(any(o['item']=='Death rune' and o.get('additional') for o in e['outcomes']))
        self.assertEqual(self.chance(self.enemy(901136),'Smouldering stone'),Fraction(1,16384))
        self.assertEqual(self.enemy(901135)['denominator'],1)
        for i in (901134,901135,901136):self.assertEqual(self.enemy(i)['guaranteed'],[{'item':'Vile ashes','quantity':1}])
    def test_minotaur_101_table_and_explicit_unlisted_slot(self):
        from fractions import Fraction
        e=self.enemy(901137)
        self.assertEqual(e['defence_bonuses']['stab'],-21)
        self.assertEqual(self.chance(e,'Right skull half'),Fraction(3,101))
        self.assertEqual(self.chance(e,'Pure essence'),Fraction(5,101))
        self.assertEqual(self.chance(e,'Nature talisman'),Fraction(4,101*128))
        self.assertTrue(any(o['item']=='Nothing' and Fraction(o['weight'],e['denominator'])==Fraction(1,101) for o in e['outcomes']))
    def test_equipment_rows_are_additive_and_verified(self):
        from expansion_release import artifacts
        result=artifacts(self.pack,self.prior)
        sql=next(v for k,v in result.items() if k.suffix=='.sql')
        spec=json.loads(next(v for k,v in result.items() if k.suffix=='.json'))
        self.assertIn('VALUES (901122,1,2131,2129,0)',sql)
        self.assertIn('creature_equip_template WHERE CreatureID IN',spec['precondition_sql'])
        self.assertIn('CreatureID=901122 AND ID=1 AND ItemID1=2131 AND ItemID2=2129 AND ItemID3=0',spec['verify_sql'])
    def test_explicit_empty_hands_do_not_generate_empty_sql_list(self):
        from expansion_release import artifacts
        for e in self.pack['enemies']:
            if 'equipment' in e:e['equipment']=[0,0,0]
        result=artifacts(self.pack,self.prior)
        spec=json.loads(next(v for k,v in result.items() if k.suffix=='.json'))
        self.assertNotIn('IN ()',spec['precondition_sql'])
    def test_runtime_weight_bounds_and_equipment_shape_rejected(self):
        e=self.pack['enemies'][0];e['denominator']=0x100000000
        with self.assertRaisesRegex(ValueError,'distribution'):self.module.validate(self.pack,self.prior)
        e['denominator']=16384;e['equipment']=[2901,0]
        with self.assertRaisesRegex(ValueError,'equipment'):self.module.validate(self.pack,self.prior)
    def test_exact_probability_helpers_reject_invalid_tables(self):
        from loot_tables import compile_weights,independent_bonus
        from fractions import Fraction
        with self.assertRaises(ValueError):compile_weights([({'item':'Nothing'},Fraction(1,2))])
        with self.assertRaisesRegex(ValueError,'uint64'):compile_weights([({'item':'Nothing'},Fraction(1,0x10000000000000001)),({'item':'Bones'},Fraction(0x10000000000000000,0x10000000000000001))])
        with self.assertRaises(ValueError):independent_bonus([],{'item':'Bones'},0)


class MartialTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module=family_catalogue
        self.pack=json.loads(Path(__file__).with_name('martial_families.json').read_text())
        self.prior=json.loads(Path(__file__).with_name('goblins.json').read_text())
        self.prior['families']=[]
        for n in ('farm_animals_rats.json','wildlife.json','coastal_wildlife.json','dungeon_humanoids.json'):
            d=json.loads(Path(__file__).with_name(n).read_text())
            for k in ('items','enemies','families'):self.prior[k].extend(d[k])
    def e(self,entry):return next(e for e in self.pack['enemies'] if e['entry']==entry)
    def chance(self,entry,name,quantity=None):
        from fractions import Fraction
        e=self.e(entry)
        return sum(Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if o['item']==name and (quantity is None or o['quantity']==quantity))
    def test_53_variants_seven_families(self):
        self.module.validate(self.pack,self.prior)
        self.assertEqual(len(self.pack['enemies']),53)
        self.assertEqual({e['family_id'] for e in self.pack['enemies']},set(range(24,31)))
        self.assertEqual(sum(e['family_id']==24 for e in self.pack['enemies']),24)
        self.assertEqual(len({e['source_npc_ids'] for e in self.pack['enemies']}),53)
    def test_unsupported_source_roles_excluded(self):
        ids={int(n) for e in self.pack['enemies'] for n in e['source_npc_ids'].split(',')}
        self.assertTrue(ids.isdisjoint({3068,6605,6603}))
        self.assertTrue(all(e['attack_style'] in ('stab','slash','crush') for e in self.pack['enemies']))
    def test_town_warriors_and_pollnivneach_have_only_combat_bones(self):
        for entry in (*range(901217,901223),901250,901251):
            e=self.e(entry)
            self.assertEqual(e['guaranteed'],[{'item':'Bones','quantity':1}])
            self.assertEqual(e['denominator'],1)
            self.assertEqual(e['outcomes'][0]['item'],'Nothing')
    def test_general_seed_first_tier_exact_and_guarded(self):
        from fractions import Fraction
        from loot_tables import general_seed_table,compile_weights
        rows=general_seed_table(Fraction(1),33)
        self.assertEqual(sum(r for _,r in rows),1)
        self.assertEqual(rows[0],({'item':'Potato seed','quantity':4},Fraction(368,1008)))
        self.assertEqual(rows[-1],({'item':'Snape grass seed','quantity':2},Fraction(8,1008)))
        for level in (0,256,True):
            with self.assertRaises(ValueError):general_seed_table(1,level)
        self.assertEqual(self.chance(901224,'Potato seed'),Fraction(18,128)*Fraction(368,1008))
    def test_uncommon_seeds_preserve_listed_chances_and_explicit_gap(self):
        from fractions import Fraction
        from loot_tables import uncommon_seed_table
        rows=uncommon_seed_table(1)
        self.assertEqual(sum(r for _,r in rows),1)
        self.assertEqual(next(r for d,r in rows if d['item']=='Limpwurt seed'),Fraction(137,1048))
        self.assertEqual(next(r for d,r in rows if d['item']=='Nothing'),Fraction(2,1048))
        self.assertEqual(self.chance(901246,'Torstol seed'),Fraction(19,128*1048))
        self.assertEqual(self.chance(901237,'Torstol seed'),Fraction(12,128*1048))
    def test_white_knight_members_substitutions_and_ranges(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901228,'Coins',8),Fraction(10,128))
        self.assertEqual(self.chance(901230,'Coins',10),Fraction(10,128))
        e=self.e(901234);o=next(o for o in e['outcomes'] if o['item']=='Water rune')
        self.assertEqual((o['quantity'],o['quantity_max']),(40,47))
        self.assertEqual(self.chance(901224,'Coins',1),Fraction(14,128))
    def test_hobgoblin_members_rates_no_location_currency_stacking(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901236,'Coins',28),Fraction(12,128))
        self.assertEqual(self.chance(901236,'Goblin mail'),Fraction(2,128))
        self.assertEqual(self.chance(901237,'Coins',5),Fraction(12,128))
        self.assertEqual(self.chance(901237,'Coins',1),Fraction(4,128))
        self.assertFalse(any(o['item']=='Trading sticks' for e in self.pack['enemies'] for o in e['outcomes']))
    def test_flesh_crawler_main_roll_not_guaranteed_ashes(self):
        from fractions import Fraction
        for entry in (901243,901244,901245):
            self.assertFalse(self.e(entry)['guaranteed'])
            self.assertEqual(self.e(entry)['source_max_hit'],1)
            self.assertEqual(self.chance(entry,'Ashes'),Fraction(4,100))
            self.assertEqual(self.chance(entry,'Bottom of sceptre'),Fraction(3,100))
            self.assertEqual(self.chance(entry,'Grimy guam leaf'),Fraction(35*32,100*128))
    def test_ogre_big_bones_and_human_shared_table(self):
        from fractions import Fraction
        for entry in (901246,901247,901248):self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Big bones','quantity':1}])
        for entry in (901223,901252):
            self.assertEqual(self.chance(entry,'Bronze bolts'),Fraction(22,128))
            self.assertEqual(self.chance(entry,'Grimy guam leaf'),Fraction(23*32,128*128))
    def test_unique_native_pool_reservations_and_equipment(self):
        for e in self.pack['enemies']:
            self.assertLess(len(e['outcomes']),100)
            self.assertTrue(e['native_attack_animation'])
        self.assertEqual(self.e(901237)['equipment'],[39202,0,0])
        self.assertNotIn('equipment',self.e(901236))
        self.assertEqual(self.e(901252)['equipment'],[2764,2764,0])


class GiantDemonTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module=family_catalogue
        self.pack=json.loads(Path(__file__).with_name('giants_demons.json').read_text())
        self.prior=json.loads(Path(__file__).with_name('goblins.json').read_text())
        self.prior['families']=[]
        for n in ('farm_animals_rats.json','wildlife.json','coastal_wildlife.json','dungeon_humanoids.json','martial_families.json'):
            d=json.loads(Path(__file__).with_name(n).read_text())
            for k in ('items','enemies','families'):self.prior[k].extend(d[k])
    def e(self,entry):return next(e for e in self.pack['enemies'] if e['entry']==entry)
    def chance(self,entry,name,quantity=None):
        from fractions import Fraction
        e=self.e(entry)
        return sum(Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if o['item']==name and (quantity is None or o['quantity']==quantity))
    def test_57_variants_six_families(self):
        self.module.validate(self.pack,self.prior)
        self.assertEqual(len(self.pack['enemies']),57)
        self.assertEqual({e['family_id'] for e in self.pack['enemies']},set(range(31,37)))
        self.assertEqual(len({e['source_npc_ids'] for e in self.pack['enemies']}),57)
    def test_monster_zero_ranged_magic_preserved_melee_hp_guarded(self):
        self.assertEqual(self.e(901349)['stats'],[40,75,40,0,0,90])
        self.assertEqual(self.e(901350)['stats'],[40,90,25,0,0,90])
        self.e(901349)['stats'][5]=0
        with self.assertRaisesRegex(ValueError,'stats'):self.module.validate(self.pack,self.prior)
    def test_rare_table_totals_and_pre_legends_branch(self):
        from fractions import Fraction
        from loot_tables import rare_table,gem_table
        rows=rare_table(Fraction(1))
        self.assertEqual(sum(r for _,r in rows),1)
        chance=lambda n:sum(r for d,r in rows if d['item']==n)
        self.assertEqual(chance('Coins'),Fraction(21,128))
        self.assertEqual(chance('Rune spear'),Fraction(15*8,128*128))
        self.assertEqual(sum(r for d,r in gem_table(1) if d['item']=='Rune spear'),0)
        self.assertEqual(sum(r for _,r in rare_table(Fraction(1,128),Fraction(5,128))),Fraction(6,128))
    def test_source_cave_talismans_and_individual_ash_types(self):
        self.assertEqual(self.chance(901317,'Nature talisman'),0)
        self.assertGreater(self.chance(901317,'Chaos talisman'),0)
        self.assertGreater(self.chance(901314,'Nature talisman'),0)
        self.assertEqual(self.e(901314)['guaranteed'],[{'item':'Vile ashes','quantity':1}])
        self.assertEqual(self.e(901323)['guaranteed'],[{'item':'Malicious ashes','quantity':1}])
    def test_native_fixed_coin_reference_3000_and_remainder_450(self):
        from expansion_release import artifacts
        result=artifacts(self.pack,self.prior)
        sql=next(v for k,v in result.items() if k.suffix=='.sql')
        spec=json.loads(next(v for k,v in result.items() if k.suffix=='.json'))
        self.assertIn('VALUES (970000,902006,100,200,200,',sql)
        for entry,q,loops,remainder in ((901323,3000,15,0),(901314,450,2,50)):
            e=self.e(entry);index=next(i for i,o in enumerate(e['outcomes']) if o['item']=='Coins' and o['quantity']==q);loot=e['loot_base']+index
            self.assertIn(f'VALUES ({loot},0,970000,100,1,{loops},',sql)
            if remainder:self.assertIn(f'VALUES ({loot},902006,100,{remainder},{remainder},',sql)
            self.assertEqual(loops*200+remainder,q)
        self.assertIn('reference_loot_template WHERE Entry=970000',spec['precondition_sql'])
        self.assertIn('entry=902006 AND stackable=200',spec['precondition_sql'])
    def test_native_slot_budget_and_non_fixed_large_counts_refused(self):
        e=self.e(901323);o=next(o for o in e['outcomes'] if o['item']=='Coins' and o['quantity']==3000)
        o['quantity_max']=3001
        with self.assertRaisesRegex(ValueError,'count'):self.module.validate(self.pack,self.prior)
        del o['quantity_max'];o['quantity']=3600
        with self.assertRaisesRegex(ValueError,'slot limit'):self.module.validate(self.pack,self.prior)
    def test_reference_collision_and_bad_stack_contract_refused(self):
        self.prior['native_references']=[{'id':970000}]
        with self.assertRaisesRegex(ValueError,'collision'):self.module.validate(self.pack,self.prior)
        self.prior['native_references']=[];self.pack['native_references'][0]['count']=100
        with self.assertRaisesRegex(ValueError,'Invalid native reference'):self.module.validate(self.pack,self.prior)
    def test_ice_cave_unlisted_main_slot_is_explicit(self):
        from fractions import Fraction
        e=self.e(901307)
        self.assertTrue(any(o['item']=='Nothing' and Fraction(o['weight'],e['denominator'])==Fraction(1,62) for o in e['outcomes']))
    def test_werewolf_ash_free_wolf_bones_and_tools_rewards(self):
        for i in range(901327,901349):self.assertEqual(self.e(i)['guaranteed'],[{'item':'Wolf bones','quantity':1}])
        self.assertEqual(self.e(901352)['guaranteed'],[{'item':'Iron battleaxe','quantity':1}])
        self.assertEqual(self.e(901354)['guaranteed'],[{'item':'Iron pickaxe','quantity':1}])
        self.assertEqual(self.e(901356)['guaranteed'],[{'item':'Spade','quantity':1}])
        self.assertEqual(self.chance(901353,'Rune battleaxe'),__import__('fractions').Fraction(1,500))
    def test_mammoth_rare_coins_and_seeds_exact(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901351,'Coins',3000),Fraction(2*21,128*128))
        self.assertEqual(self.chance(901351,'Potato seed'),Fraction(30,640))
        self.assertEqual(self.chance(901351,'Papaya tree seed'),Fraction(1,640))
        self.assertEqual(self.e(901351)['guaranteed'],[{'item':'Big bones','quantity':1}])



class SlayerPrototypeTests(unittest.TestCase):
    def setUp(self):
        import family_catalogue
        self.module=family_catalogue
        self.pack=json.loads(Path(__file__).with_name('slayer_prototypes.json').read_text())
        self.prior=prior_to('slayer_prototypes.json')
    def e(self,entry):return next(e for e in self.pack['enemies'] if e['entry']==entry)
    def chance(self,entry,name):
        from fractions import Fraction
        e=self.e(entry)
        return sum((Fraction(o['weight'],e['denominator']) for o in e['outcomes']
                    if o['item']==name or any(a['item']==name for a in o.get('additional',[]))),Fraction())
    def test_batch_and_existing_family_references(self):
        from expansion_release import artifacts
        self.module.validate(self.pack,self.prior)
        self.assertEqual(len(self.pack['enemies']),70)
        self.assertEqual(len(self.pack['items']),85)
        self.assertEqual([f['id'] for f in self.pack['families'] if f.get('existing')],[31,32])
        result=artifacts(self.pack,self.prior,add_slayer_column=True)
        sql=next(v for p,v in result.items() if p.suffix=='.sql')
        self.assertEqual(sql.count('INSERT INTO warscape_enemy_family '),14)
        f=self.pack['families'][-1];f['name']='Different identity'
        with self.assertRaisesRegex(ValueError,'identity'):artifacts(self.pack,self.prior)
    def test_implicit_existing_family_collision_rejected(self):
        from expansion_release import artifacts
        del self.pack['families'][-1]['existing']
        with self.assertRaisesRegex(ValueError,'overlaps'):artifacts(self.pack,self.prior)
    def test_uint64_weight_compiler_and_guard(self):
        from fractions import Fraction
        from loot_tables import compile_weights
        rows,total=compile_weights([(dict(item='a'),Fraction(1,2**32+1)),(dict(item='b'),Fraction(2**32,2**32+1))])
        self.assertEqual(total,2**32+1);self.assertEqual(rows[1]['weight'],2**32)
        with self.assertRaisesRegex(ValueError,'uint64'):
            compile_weights([(dict(item='a'),Fraction(1,2**64+1)),(dict(item='b'),Fraction(2**64,2**64+1))])
        self.assertGreater(self.e(901405)['denominator'],2**32)
        self.assertGreater(self.e(901409)['denominator'],2**32)
    def test_full_general_and_rare_seed_tiers(self):
        from fractions import Fraction
        from loot_tables import general_seed_table,rare_seed_table
        rows=general_seed_table(1,79)
        self.assertEqual(sum(p for _,p in rows),1)
        self.assertEqual(sum(p for d,p in rows if d['item']=='Potato seed'),Fraction(485*368,790*1008))
        self.assertEqual(sum(p for d,p in rows if d['item']=='Barley seed'),Fraction(243*229,790*1000))
        self.assertEqual(sum(p for d,p in rows if d['item']=='Marigold seed'),Fraction(62*376,790*1000))
        for level in (1,48,79,100,255):self.assertEqual(sum(p for _,p in general_seed_table(1,level)),1)
        self.assertEqual(sum(p for _,p in rare_seed_table(1)),1)
        self.assertEqual(next((d['quantity'],p) for d,p in rare_seed_table(1) if d['item']=='Snape grass seed'),(3,Fraction(20,1090)))
    def test_tortoise_paired_loot_marginals(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901405,'Steel arrow'),Fraction(20,128))
        self.assertEqual(self.chance(901405,'Cabbage'),Fraction(20,128))
        for o in self.e(901405)['outcomes']:
            if 'seed' in o['item'] and 'additional' in o:self.assertEqual(o['additional'],[{'item':'Steel arrow','quantity':12,'quantity_max':23}])
            if o['item'].startswith('Grimy'):self.assertEqual(o['additional'],[{'item':'Cabbage','quantity':20,'quantity_max':59}])
    def test_ankou_location_specific_tables(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901400,'Left skull half'),Fraction(3,100))
        self.assertEqual(self.chance(901403,'Left skull half'),0)
        self.assertEqual(self.chance(901404,'Dark fishing bait'),Fraction(38,100))
        self.assertEqual(self.chance(901400,'Law rune'),Fraction(4,100))
        self.assertEqual(self.chance(901403,'Law rune'),Fraction(7,100))
        self.assertEqual(self.chance(901404,'Law rune'),Fraction(3,100))
    def test_abyssal_independent_rare_marginals(self):
        from fractions import Fraction
        for entry in (901409,901410,901411):
            self.assertEqual(self.chance(entry,'Abyssal whip'),Fraction(1,512))
            self.assertEqual(self.chance(entry,'Abyssal dagger'),Fraction(1,32000))
            self.assertEqual(self.e(entry)['source_slayer_level'],85)
        # The native 3000-coin outcome plus both bonuses and ash fits all 18 slots.
        o=next(o for o in self.e(901409)['outcomes'] if o['item']=='Coins' and o['quantity']==3000 and len(o.get('additional',[]))==2)
        self.assertEqual(15+len(o['additional'])+len(self.e(901409)['guaranteed']),18)
    def test_magical_melee_and_bloodveld_paired_bones(self):
        from fractions import Fraction
        for entry in (*range(901416,901432),):self.assertEqual(self.e(entry)['attack_style'],'m_melee')
        e=self.e(901423)
        self.assertEqual(e['guaranteed'],[{'item':'Vile ashes','quantity':1}])
        self.assertEqual(self.chance(901423,'Bones'),Fraction(10,128))
        for o in e['outcomes']:
            if o['item']=='Big bones':self.assertEqual(o['additional'],[{'item':'Bones','quantity':1}])
        self.assertEqual(self.e(901416)['source_slayer_level'],52)
        self.assertEqual(e['source_slayer_level'],50)
    def test_slayer_schema_is_additive_with_prior_defaults(self):
        from expansion_release import artifacts
        result=artifacts(self.pack,self.prior,add_slayer_column=True)
        sql=next(v for p,v in result.items() if p.suffix=='.sql')
        spec=json.loads(next(v for p,v in result.items() if p.suffix=='.json'))
        self.assertIn('ADD COLUMN source_slayer_level TINYINT UNSIGNED NOT NULL DEFAULT 0',sql)
        self.assertIn("column_name='source_slayer_level')=0",spec['precondition_sql'])
        self.assertIn("is_nullable='NO' AND column_default='0'",spec['verify_sql'])
        self.assertIn('AND source_slayer_level=0)=205',spec['verify_sql'])
        self.assertNotIn('DELETE ',sql);self.assertNotIn('TRUNCATE ',sql)
    def test_simple_bones_ashes_keys_and_dust(self):
        from fractions import Fraction
        for entry in range(901442,901455):self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Baby dragon bones','quantity':1}])
        for entry in range(901455,901468):self.assertEqual(self.chance(entry,'Giant key'),Fraction(1,128))
        for entry in (901435,901436):
            self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Vampyre dust','quantity':1}])
            self.assertEqual(self.chance(entry,'Nothing'),1)
        for entry in (901468,901469):self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Fiendish ashes','quantity':1}])
    def test_invalid_slayer_requirement_rejected(self):
        for value in (-1,100,True):
            self.pack['enemies'][0]['source_slayer_level']=value
            with self.assertRaisesRegex(ValueError,'Slayer reference'):self.module.validate(self.pack,self.prior)



class SpectralTests(unittest.TestCase):
    def setUp(self):
        self.pack=json.loads(Path(__file__).with_name('spectral.json').read_text())
        self.prior=prior_to('spectral.json')
    def test_two_neutral_spectral_enemies_exact_stats_and_ids(self):
        import family_catalogue
        family_catalogue.validate(self.pack,self.prior)
        self.assertEqual(len(self.prior['enemies']),275)
        a,b=self.pack['enemies']
        self.assertEqual((a['entry'],a['source_npc_ids'],a['stats'],a['source_max_hit'],a['flat_armour']),(901500,'2843',[56,56,46,1,1,66],7,-2))
        self.assertEqual((b['entry'],b['source_npc_ids'],b['stats'],b['source_max_hit'],b['flat_armour']),(901501,'7258',[130,136,100,50,50,115],15,-3))
        self.assertTrue(all(not e['aggressive'] and not e['guaranteed'] for e in self.pack['enemies']))
    def test_otherworldly_exact_loot_and_empty_subtable(self):
        from fractions import Fraction
        e=self.pack['enemies'][0]
        def chance(name):return sum(Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if o['item']==name)
        self.assertEqual(chance('Coins'),Fraction(59,128))
        self.assertEqual(chance('Nature rune'),Fraction(9,128))
        self.assertEqual(chance('Grimy guam leaf'),Fraction(10*32,128*128))
        self.assertEqual(chance('Nothing'),Fraction(18,128)+Fraction(3*63,128*128))
        self.assertEqual(chance('Nature talisman'),Fraction(3*4,128*128))
        self.assertEqual(chance('Rune spear'),0)
        self.assertEqual(chance('Ruby ring'),Fraction(2,128))
    def test_shade_members_robes_and_explicit_no_loot(self):
        from fractions import Fraction
        e=self.pack['enemies'][1]
        self.assertEqual({o['item']:Fraction(o['weight'],e['denominator']) for o in e['outcomes']},{'Shade robe top':Fraction(1,4),'Shade robe':Fraction(1,4),'Nothing':Fraction(1,2)})
    def test_additive_flat_armour_sql_schema_and_prior_defaults(self):
        from expansion_release import artifacts
        import hashlib
        result=artifacts(self.pack,self.prior,add_flat_armour_column=True)
        sql=next(v for p,v in result.items() if p.suffix=='.sql');spec=json.loads(next(v for p,v in result.items() if p.suffix=='.json'))
        self.assertIn('ADD COLUMN flat_armour INT NOT NULL DEFAULT 0',sql)
        self.assertIn("column_name='flat_armour')=0",spec['precondition_sql'])
        self.assertIn("column_type NOT LIKE '%unsigned%'",spec['verify_sql'])
        self.assertIn('AND flat_armour=0)=275',spec['verify_sql'])
        self.assertEqual(hashlib.sha1(sql.encode()).hexdigest().upper(),spec['sha1'])
        self.assertEqual(sql.count('UPDATE warscape_enemy_variant'),2)
        self.assertNotIn('DELETE ',sql);self.assertNotIn('TRUNCATE ',sql)
    def test_invalid_flat_armour_metadata_refused(self):
        import family_catalogue
        for value in (-1000001,1000001,True,1.5):
            self.pack['enemies'][0]['flat_armour']=value
            with self.assertRaisesRegex(ValueError,'flat armour'):family_catalogue.validate(self.pack,self.prior)
    def test_native_empty_outcomes_have_no_loot_rows(self):
        from expansion_release import artifacts
        sql=next(v for p,v in artifacts(self.pack,self.prior,add_flat_armour_column=True).items() if p.suffix=='.sql')
        for e in self.pack['enemies']:
            for i,o in enumerate(e['outcomes']):
                if o['item']=='Nothing':self.assertNotIn(f'VALUES ({e["loot_base"]+i},',sql)
    def test_four_new_items_without_redefining_shared_items(self):
        self.assertEqual([i['entry'] for i in self.pack['items']],list(range(902357,902361)))
        self.assertNotIn('Mithril mace',{i['name'] for i in self.pack['items']})
        self.assertIn('Mithril mace',{i['name'] for i in self.pack['shared_items']})



class OrderedEnemyTests(unittest.TestCase):
    def setUp(self):
        self.pack=json.loads(Path(__file__).with_name('ordered_desert_druids.json').read_text())
        self.prior=prior_to('ordered_desert_druids.json')
    def chance(self,entry,name,quantity=None):
        from fractions import Fraction
        e=next(e for e in self.pack['enemies'] if e['entry']==entry)
        return sum((Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if any(d['item']==name and (quantity is None or d['quantity']==quantity) for d in [o]+o.get('additional',[]))),Fraction())
    def test_order_and_existing_dwarf_identity(self):
        import family_catalogue
        family_catalogue.validate(self.pack,self.prior)
        self.assertEqual([e['source'] for e in self.pack['enemies']],['Small_Lizard','Desert_Lizard','Lizard','Scarab_Swarm','Druid','Dwarf'])
        self.assertEqual(len(self.prior['enemies']),277)
        self.assertTrue(self.pack['families'][-1]['existing'])
        self.assertEqual(self.pack['enemies'][-1]['source_npc_ids'],'292')
    def test_lizard_paired_marginals_and_glove_bonus(self):
        from fractions import Fraction
        for entry in (901600,901601,901602):
            self.assertEqual(self.chance(entry,'Fire rune',42),Fraction(14,128))
            self.assertEqual(self.chance(entry,'Energy potion(3)'),Fraction(13,128))
            self.assertEqual(self.chance(entry,'Mystic gloves (light)'),Fraction(1,512))
            self.assertEqual(self.chance(entry,'Grimy guam leaf'),Fraction(10*32,128*128))
    def test_double_gem_roll_keeps_duplicate_quantity(self):
        from fractions import Fraction
        for entry in (901600,901601,901602):
            self.assertEqual(self.chance(entry,'Uncut sapphire',2),Fraction(2,128)*Fraction(32,128)**2)
            self.assertEqual(self.chance(entry,'Rune spear'),0)
    def test_behaviour_configuration_and_source_speed(self):
        e=self.pack['enemies'];self.assertTrue(all(x['behaviour']=={'finisher_item':902361} for x in e[:3]))
        self.assertEqual(e[3]['behaviour'],{'poison_max_hit':3});self.assertEqual(e[3]['attack_ticks'],1)
        self.assertEqual(e[4]['behaviour'],{'magic_max_hit':5});self.assertEqual(e[4]['source_max_hit'],4)
        self.assertEqual(e[5]['source_max_hit'],3)
    def test_dwarf_inferred_coin_slots_and_total(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901605,'Coins',4),Fraction(23,128))
        self.assertEqual(self.chance(901605,'Coins',10),Fraction(12,128))
        self.assertEqual(round(128/23,2),5.57);self.assertEqual(round(128/12,1),10.7)
    def test_script_and_cooler_bindings_additive(self):
        from encounter_release import encounter_artifacts
        r=encounter_artifacts(self.pack,self.prior);sql=next(v for p,v in r.items() if p.suffix=='.sql');spec=json.loads(next(v for p,v in r.items() if p.suffix=='.json'))
        self.assertEqual(sql.count("ScriptName='npc_warscape_enemy'"),5)
        self.assertIn("WHERE entry=902361 AND name='Ice cooler' AND class=0",spec['verify_sql'])
        self.assertIn("entry=901605",spec['verify_sql']);self.assertIn("AIName='AggressorAI'",spec['verify_sql'])
        self.assertIn("(900701,'spell_warscape_enemy_magic')",sql);self.assertIn("(900702,'spell_warscape_enemy_poison')",sql)
        self.assertNotIn('UPDATE spell_',sql);self.assertNotIn('DELETE ',sql)
    def test_script_verification_targets_identity_not_pack_order(self):
        from encounter_release import encounter_artifacts
        import re
        self.pack['enemies'].insert(0,self.pack['enemies'].pop())
        result=encounter_artifacts(self.pack,self.prior)
        spec=json.loads(next(v for p,v in result.items() if p.suffix=='.json'))
        dwarf=re.search(r"FROM creature_template WHERE entry=901605 AND (.*?) AND mingold=0",spec['verify_sql'])[1]
        self.assertIn("AIName='AggressorAI'",dwarf)
    def test_invalid_behaviours_and_speed_rejected(self):
        import family_catalogue
        self.pack['enemies'][0]['behaviour']={'finisher_item':1}
        with self.assertRaisesRegex(ValueError,'finisher'):family_catalogue.validate(self.pack,self.prior)
        self.pack['enemies'][0]['behaviour']={'bad':1}
        with self.assertRaisesRegex(ValueError,'behaviour'):family_catalogue.validate(self.pack,self.prior)
    def test_druid_and_scarab_guaranteed_bones(self):
        for e in self.pack['enemies'][3:]:self.assertEqual(e['guaranteed'],[{'item':'Bones','quantity':1}])
        self.assertEqual(len(self.pack['items']),8)
    def test_additive_spell_layout_and_collision_guards(self):
        import struct
        from dbc_records import append_spells,dbc
        rows=[]
        for source in (30455,5176,2818):
            r=[0]*234;r[0]=source;rows.append(r)
        data=struct.pack('<4s4I',b'WDBC',3,234,936,1)+b''.join(struct.pack('<234I',*r) for r in rows)+b'\0'
        result=append_spells(data,self.pack['client_spells']);after,strings=dbc(result,234)
        self.assertEqual(len(after),6)
        for r in rows:self.assertEqual(after[r[0]],r)
        self.assertEqual(strings[:1],b'\0')
        self.assertEqual(after[900701][7]&0x40000,0x40000)
        self.assertEqual(strings[after[900700][136]:].split(b'\0')[0],b'Ice cooler')
        with self.assertRaisesRegex(ValueError,'collision'):append_spells(result,self.pack['client_spells'])
        with self.assertRaises(ValueError):append_spells(data[:-1],self.pack['client_spells'])



class ElfAvianSuqahTests(unittest.TestCase):
    def setUp(self):
        self.pack=json.loads(Path(__file__).with_name('elves_aviansie_suqah.json').read_text())
        self.prior=prior_to('elves_aviansie_suqah.json')
    def e(self,entry):return next(e for e in self.pack['enemies'] if e['entry']==entry)
    def chance(self,entry,name):
        from fractions import Fraction
        e=self.e(entry)
        return sum((Fraction(o['weight'],e['denominator']) for o in e['outcomes'] if o['item']==name),Fraction())
    def test_six_entries_three_new_families_no_duplicate_hobgoblins(self):
        import family_catalogue
        family_catalogue.validate(self.pack,self.prior)
        self.assertEqual(len(self.prior['enemies']),283)
        self.assertEqual([e['entry'] for e in self.pack['enemies']],list(range(901700,901706)))
        self.assertEqual([f['id'] for f in self.pack['families']],[56,57,58])
        old=[e for e in self.prior['enemies'] if e.get('source')=='Hobgoblin']
        self.assertEqual([e['entry'] for e in old],list(range(901236,901243)))
        self.assertEqual([e['source_npc_ids'] for e in old],['3049','3050','3286','3287','3288','3289','2241'])
    def test_fractional_slayer_reference_not_truncated(self):
        self.assertEqual([e['source_slayer_xp_tenths'] for e in self.pack['enemies']],[1075,1075,700,1390,1076,1076])
        self.assertEqual(self.e(901700)['slayer_xp'],107)
        self.assertEqual(self.e(901705)['slayer_xp'],107)
    def test_precise_metadata_bounds_and_mismatch_refused(self):
        import family_catalogue
        for value in (-1,True,10000001,1069):
            self.pack['enemies'][0]['source_slayer_xp_tenths']=value
            with self.assertRaisesRegex(ValueError,'precise Slayer'):family_catalogue.validate(self.pack,self.prior)
    def test_source_ranged_stats_and_flight_config(self):
        self.assertEqual(self.e(901702)['stats'],[1,1,70,71,1,70])
        self.assertEqual(self.e(901703)['stats'],[1,1,160,151,1,139])
        for entry,maximum in ((901702,8),(901703,16)):
            e=self.e(entry);self.assertEqual(e['attack_style'],'ranged')
            self.assertEqual(e['behaviour'],{'ranged_max_hit':maximum,'airborne':1,'attack_spell':900710})
    def test_feather_quantity_range_and_elf_bones(self):
        for entry in (901700,901701):self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Bones','quantity':1}])
        for entry in (901702,901703):self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Bones','quantity':1},{'item':'Feather','quantity':1,'quantity_max':6}])
    def test_elf_main_marginals(self):
        from fractions import Fraction
        self.assertEqual(self.chance(901700,'Crystal teleport seed'),Fraction(25,128))
        self.assertEqual(self.chance(901701,'Teleport crystal (1)'),Fraction(1,128))
        self.assertEqual(self.chance(901700,'Coins'),Fraction(44,128))
    def test_suqah_129_slot_table_and_quest_preroll_excluded(self):
        from fractions import Fraction
        for entry in (901704,901705):
            self.assertEqual(self.chance(entry,'Suqah tooth'),Fraction(69,129))
            self.assertEqual(self.chance(entry,'Grimy guam leaf'),Fraction(30,129))
            self.assertEqual(self.chance(entry,'Grimy marrentill'),Fraction(25,129))
            self.assertEqual(self.chance(entry,'A special tiara'),0)
            self.assertEqual(self.e(entry)['guaranteed'],[{'item':'Big bones','quantity':1},{'item':'Suqah hide','quantity':1}])
    def test_suqah_melee_and_hybrid_source_image_ids(self):
        self.assertEqual(self.e(901704)['source_npc_ids'],'790')
        self.assertNotIn('behaviour',self.e(901704))
        self.assertEqual(self.e(901705)['source_npc_ids'],'787')
        self.assertEqual(self.e(901705)['behaviour']['magic_melee_only'],1)
        self.assertEqual(self.e(901705)['behaviour']['alternate_spell'],900712)
    def test_additive_schema_preserves_legacy_metadata(self):
        from ranged_release import ranged_artifacts
        import hashlib
        result=ranged_artifacts(self.pack,self.prior);sql=next(v for p,v in result.items() if p.suffix=='.sql');spec=json.loads(next(v for p,v in result.items() if p.suffix=='.json'))
        self.assertIn('ADD COLUMN source_slayer_xp_tenths INT UNSIGNED NOT NULL DEFAULT 0',sql)
        self.assertIn('AND source_slayer_xp_tenths=0)=283',spec['verify_sql'])
        self.assertEqual(hashlib.sha1(sql.encode()).hexdigest().upper(),spec['sha1'])
        self.assertEqual(sql.count("ScriptName='npc_warscape_enemy'"),3)
        self.assertNotIn('DELETE ',sql);self.assertNotIn('MODIFY COLUMN',sql)
        self.assertNotIn('UPDATE warscape_enemy_variant SET slayer_xp=',sql)
    def test_root_spell_contains_no_periodic_damage(self):
        import struct
        from dbc_records import append_spells,dbc
        sources=(6660,31707,30455,339);rows=[]
        for source in sources:
            row=[0]*234;row[0]=source;row[71]=6;row[72]=6;row[95]=26;row[96]=3;rows.append(row)
        data=struct.pack('<4s4I',b'WDBC',4,234,936,1)+b''.join(struct.pack('<234I',*r) for r in rows)+b'\0'
        result=append_spells(data,self.pack['client_spells']);after,strings=dbc(result,234)
        self.assertEqual(after[900713][71:74],[6,0,0]);self.assertEqual(after[900713][95:98],[26,0,0])
        for source,row in zip(sources,rows):self.assertEqual(after[source],row)
        self.assertTrue(after[900710][7]&0x40000)

if __name__=='__main__':unittest.main()
