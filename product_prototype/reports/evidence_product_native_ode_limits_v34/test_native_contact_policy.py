"""Regression checks of measured validity limits;not relaxed physics Gates."""
import csv,json,unittest
from analyse import BASE
def summary(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class ContactPolicyTest(unittest.TestCase):
 def test_reuse_build_and_correct_parameter_name_are_state_pure(self):
  data=summary('b3_native_newmark_reuse_regression690');self.assertIsNone(data['configure']);self.assertIsNone(data['compile'])
  for r in data['records']:
   name='newmark_'+format(r['dt_s'],'.7f')
   with (BASE/'results/b3_native_plane_newmark683'/name/'probe.csv.point.csv').open() as f:old=list(csv.DictReader(f))
   with (BASE/'results/b3_native_newmark_reuse_regression690'/name/'probe.csv.point.csv').open() as f:new=list(csv.DictReader(f))
   self.assertEqual(old,new)
 def test_position_and_momentum_do_not_certify_impact_velocity(self):
  data=summary('b3_native_plane_policy661')
  for r in data['records']:
   self.assertLess(r['maximum_position_reference_error_m'],1e-12);self.assertLess(r['maximum_momentum_residual_Ns'],1e-12);self.assertGreater(r['maximum_velocity_reference_error_m_s'],.1)
 def test_exact_discrete_reference_and_physical_gate_separate(self):
  data=summary('b3_native_plane_reference662');self.assertTrue(all(r['strict_API_pass'] for r in data['reference_checks']));self.assertEqual(data['time_gate_status'],'FAIL');self.assertLess(data['velocity_first_vs_position_first_max_absolute_difference'],1e-12)
 def test_frozen_same_trajectory_is_not_time_accuracy(self):
  self.assertEqual(summary('b3_native_variational_validity678')['status'],'FAIL_PRECONTACT_KINEMATICS_NOT_TIME_QUALIFIED');self.assertEqual(summary('b3_native_penalty_variational_reference673')['common_time_gate_status'],'PASS') # old diagnostic is preserved,not silently rewritten
 def test_partial_trajectories_are_not_analyzed_as_complete(self):
  self.assertEqual(summary('b3_native_penalty_incremental_reference677')['status'],'BLOCKED_INCOMPLETE_NATIVE_INPUT')
 def test_bdf1_equations_pass_bdf2_reference_counterexample(self):
  data=summary('b3_native_plane_ode_reference684')
  for r in data['cases']:
   if r['mode']=='bdf1':self.assertLess(r['maximum_position_equation_residual_m_s'],1e-12);self.assertLess(r['maximum_dynamic_equation_residual_N'],1e-12)
   if r['mode']=='bdf2':self.assertGreater(r['maximum_position_equation_residual_m_s'],.004);self.assertGreater(r['maximum_velocity_reference_error_m_s'],.007)
  self.assertFalse(any(data['time_gate_by_mode'].values()))
 def test_actual_penalty_metadata_not_force_evaluation(self):
  data=summary('b3_native_penalty_reference667');self.assertEqual(data['strict_observer_state_error'],0.)
  for r in data['cases']:
   self.assertEqual(r['stored_penetration_snapshot_nonzero_count'],0);self.assertGreater(r['maximum_velocity_reference_error_m_s'],0)
 def test_correct_force_multiplier_does_not_certify_newmark_state(self):
  data=summary('b3_native_newmark_cable685')
  for r in data['records']:self.assertEqual(r['maximum_multiplier_error_Ns'],0.);self.assertGreater(r['maximum_position_reference_error_m'],1e-6)
 def test_factor_only_candidate_does_not_fix_free_prediction(self):
  old=summary('b3_native_newmark_cable685');new=summary('b3_native_newmark_factors687')
  for x,y in zip(old['records'],new['records']):
   self.assertGreater(y['maximum_position_reference_error_m'],1e-6)
   if x['channel']=='external_force':self.assertEqual(x['frames'],y['frames'])
if __name__=='__main__':unittest.main()
