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

if __name__=='__main__':unittest.main()
