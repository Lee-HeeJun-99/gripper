import json,unittest
from analyse import BASE
class TestScale(unittest.TestCase):
 def test_corrected_link_does_not_change_prefix(self):
  d=json.loads((BASE/'results/layer_explicit_link1271/summary.json').read_text());self.assertEqual(d['status'],'PASS_EXPLICIT_LINK_PURITY_ONLY');self.assertTrue(all(x==0 for x in d['errors_vs_old_auto_link_scaled'].values()))
 def test_common_window_and_scope(self):
  d=json.loads((BASE/'results/layer_constraint_comparison1275/summary.json').read_text());self.assertEqual(d['scaled']['outputs'],100);self.assertEqual(d['unscaled']['outputs'],100);self.assertEqual(d['scaled']['actual_last_time_s'],d['unscaled']['actual_last_time_s']);self.assertTrue(all(x==0 for x in d['explicit_link_vs_auto_link_unscaled_purity'].values()));self.assertGreater(d['position_residual_reduction_factor'],1000);self.assertGreater(d['velocity_residual_reduction_factor'],1000);self.assertFalse(d['numeric_tolerance_relaxed']);self.assertEqual(d['time_convergence'],'NOT TESTED_BY_THIS_CONTRAST')
 def test_old_warning_failure_preserved(self):
  d=json.loads((BASE/'results/layer_constraint_scale1270/summary.json').read_text());self.assertEqual(d['status'],'FAIL_EXECUTION');self.assertEqual(d['process']['exit_code'],0)
if __name__=='__main__':unittest.main()
