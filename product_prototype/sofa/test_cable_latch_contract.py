import csv,json,unittest
import numpy as np
from analyse import BASE
def rows(case,name):return list(csv.DictReader((BASE/'results'/case/name).open()))
def result(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class LatchContractTests(unittest.TestCase):
 def test_straight_C2_command_reference(self):
  active=[r for r in rows('cable_ramp_coupon1456','latch.csv') if int(r['latched'])];initial=[float(active[0][f'target{j}_m']) for j in range(2)]
  for r in active:
   u=np.clip((float(r['time_s'])-.1)/.05,0,1);s=u**3*(10+u*(-15+6*u))
   for j,final in enumerate((.0012,.0013)):self.assertLessEqual(abs(float(r[f'target{j}_m'])-(initial[j]+s*(final-initial[j]))),1e-17)
  self.assertLess(result('cable_ramp_coupon1456')['maximum_geometric_latch_error_m'],1e-12)
 def test_matched_native_prefix(self):
  d=result('latch_purity1452');self.assertTrue(d['straight_coupon_prefix_exact']);self.assertEqual(d['straight_coupon_prefix_rows'],39);self.assertTrue(all(x['exact'] and x['rows']==240 for x in d['prefix'].values()))
 def test_curved_constraint_failure_not_relaxed(self):
  self.assertFalse(result('latch_purity1452')['geometric_hold_error_le_1e12_m']);d=result('rest_target_purity1460');self.assertFalse(d['geometric_hold_error_le_1e12_m']);self.assertGreater(d['maximum_geometric_hold_error_m'],.002)
 def test_partial_not_full_holding(self):
  for case in ('fixed_length_pilot1453','rest_target_pilot1459'):
   d=result(case);self.assertEqual(d['full1_6_to2s_holding'],'NOT MEASURED');self.assertGreater(d['samples'][-1]['downward_from_1s_mm'],12)
if __name__=='__main__':unittest.main()
