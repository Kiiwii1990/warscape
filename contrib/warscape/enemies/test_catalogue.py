import copy,importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('catalogue_compiler',Path(__file__).with_name('compile.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
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
        with self.assertRaisesRegex(ValueError,'uint32'):compile_weights([({'item':'Nothing'},Fraction(1,0x100000001)),({'item':'Bones'},Fraction(0x100000000,0x100000001))])
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
        for level in (0,49,True):
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

if __name__=='__main__':unittest.main()
