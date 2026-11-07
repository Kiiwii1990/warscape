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
if __name__=='__main__':unittest.main()
