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

if __name__=='__main__':unittest.main()
