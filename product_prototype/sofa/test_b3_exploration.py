"""Preserve negative grasp and bounded fixture results; no new physics PASS."""
import json,unittest
from analyse import BASE
def load(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class ExplorationTests(unittest.TestCase):
 def test_only_mass_changed(self):self.assertTrue(load('b3_mass_lift_contract1060')['scene_equivalent_except_mass'])
 def test_100g_failure_not_relabelled(self):
  d=load('b3_mass100_holding1062');self.assertEqual(d['status'],'FAIL');self.assertGreater(d['vertical_slip_mm'],40);self.assertFalse(d['tests']['support_reaction'])
 def test_support_not_skin_holds_failed_object(self):
  d=load('b3_mass100_partition1063');self.assertLess(d['hold']['skin']['mean_force_N'][2],0);self.assertGreater(d['hold']['support']['mean_force_N'][2],1)
 def test_solver_limit_not_hidden(self):
  d=load('b3_mass100_solver1064');self.assertEqual(d['hold_outputs_at_or_above_iteration_limit'],d['hold_outputs'])
 def test_terminal_release_failure_and_repair_separate(self):
  self.assertFalse(load('b3_root_endclock1066')['root_position_API_1e12_pass'])
  d=load('b3_root_terminal_hold1068');self.assertTrue(d['root_position_API_1e12_pass']);self.assertEqual(d['functional_lift'],'NOT RUN_NO_OBJECT')
 def test_force_control_not_displacement_target(self):
  d=load('b3_mass100_path1072');self.assertEqual(len(d['records']),6);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
