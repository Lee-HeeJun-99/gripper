import json,unittest,numpy as np
from analyse import BASE
def load(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class NormalPhaseContract(unittest.TestCase):
 def test_direct_observer_pure_and_actual_free_phase(self):
  d=load('spinning_phase_observer1610');self.assertEqual(d['maximum_observer_q_v_impulse_error'],0);self.assertEqual(d['maximum_measured_free_orientation_vs_independent_error'],0);self.assertLessEqual(d['maximum_measured_free_rotated_lever_vs_actual_normal_J_error_m'],1e-12)
 def test_same_native_normal_failure_not_adapter_arithmetic(self):
  r=load('spinning_normal_reference1607')['records'];self.assertTrue(r[0]['physical_radial_normal_torque_gate']);self.assertFalse(r[1]['physical_radial_normal_torque_gate']);self.assertTrue(np.array_equal(r[1]['actual_normal_J_angular_m'],r[2]['actual_normal_J_angular_m']))
  for x in r:self.assertLessEqual(x['maximum_prediction_error_m'],1e-12)
 def test_chamfer_failure_not_promoted(self):
  d=load('chamfer_holding_goal1596');self.assertEqual(d['status'],'FAIL_EXPLORATORY_FUNCTIONAL_GRASP');self.assertFalse(d['tests']['speed']);self.assertGreater(load('chamfer_holding_pairs1597')['hold_nonzero_rows'],0)
 def test_penalty_is_not_an_accepted_whole_grasp_fix(self):
  d=load('force_contact_phase1609');self.assertEqual(d['records'][1]['status'],'FAIL_FORCE_CONTACT_PHASE_CONTRACT');self.assertEqual(load('force_contact_phase1608')['records'][0]['outputs'],0)
if __name__=='__main__':unittest.main()
