import json,unittest
from analyse import BASE
class FirstModeTests(unittest.TestCase):
 def test_actual_native_discrete_only(self):
  for case in ('b3_first_mode_base1184','b3_first_mode_half1185'):
   d=json.loads((BASE/'results'/case/'summary.json').read_text());self.assertLess(d['maximum_native_BE_relative'],.001);self.assertGreater(d['maximum_native_continuous_relative'],.8);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_time_failure_and_bad_factory_preserved(self):
  d=json.loads((BASE/'results/b3_first_mode_pair1186/summary.json').read_text());self.assertEqual(d['relative_gate'],.001);self.assertGreater(d['maximum_relative'],.29);self.assertEqual(len(d['failures']),2)
if __name__=='__main__':unittest.main()
