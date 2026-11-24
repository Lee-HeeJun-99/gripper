import json,unittest
from analyse import BASE
class RailbackResultsTest(unittest.TestCase):
 def test_valid_elements_do_not_imply_holding(self):
  d=json.loads((BASE/'results/b3_railback_hold_assess1300/summary.json').read_text());self.assertEqual(d['status'],'FAIL_EXPLORATORY_HOLD');self.assertTrue(d['tests']['valid_saved_elements']);self.assertFalse(d['tests']['slip']);self.assertLess(d['forces']['skin']['mean_force_N'][2],0)
 def test_larger_force_not_reported_as_improvement(self):
  d=json.loads((BASE/'results/b3_railback_force_hold_assess1307/summary.json').read_text());self.assertEqual(d['status'],'FAIL_EXPLORATORY_HOLD');self.assertFalse(d['tests']['speed']);self.assertLess(d['forces']['rail']['mean_force_N'][2],0);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_strict_complete_prefix(self):
  d=json.loads((BASE/'results/b3_force_prefix_strict1311/summary.json').read_text());self.assertEqual(d['status'],'PASS_STRICT_PREFIX_ONLY');self.assertEqual(len(d['records']),9);self.assertTrue(all(r['max_numeric_error']==0 and r['text_fields_equal'] for r in d['records']))
if __name__=='__main__':unittest.main()
