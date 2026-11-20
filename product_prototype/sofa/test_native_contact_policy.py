"""Regression checks of measured validity limits;not relaxed physics Gates."""
import csv,json,unittest
from analyse import BASE
def summary(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class ContactPolicyTest(unittest.TestCase):
 def test_potential_only_adapter_preserves_actual_newton_acceptance(self):
  data=summary('b3_native_spring_newton_purity702');self.assertEqual(data['status'],'PASS_NEWTON_API_PURITY_NOT_TIME_OR_B3')
  for r in data['records']:self.assertTrue(r['actual_state_force_slot_Newton_status_residualGraph_identity_exact']);self.assertLess(r['maximum_potential_reference_error_J'],1e-12)
 def test_loop_only_intervention_identifies_native_ode_not_cable_compatibility(self):
  records=summary('b3_native_loop_intervention692')['records']
  for r in records:
   if r['loop']=='DefaultAnimationLoop':
    if r['channel']=='external_force':self.assertEqual(r['status'],'PASS_DISCRETE_STATE_SCOPE');self.assertLess(r['maximum_velocity_reference_error_m_s'],1e-12)
    else:self.assertEqual(r['status'],'FAIL_DISCRETE_STATE');self.assertTrue(all(z==0. and v==0. for z,v in r['frames']))
   else:self.assertEqual(r['status'],'FAIL_NATIVE_EXECUTION');self.assertNotEqual(r['process']['exit_code'],0)
 def test_old_tangent_elastic_reference_is_not_physical_time_gate(self):
  data=summary('b3_native_elastic_tangent694')
  for r in data['records']:
   if r['mode']=='taut_release':self.assertTrue(r['strict_old_tangent_reference_pass']);self.assertLess(r['old_tangent_predicted_acceleration_at_slack_m_s2'],-9.)
   else:self.assertTrue(r['strict_zero_motion'])
  self.assertFalse(any(p['pass_time_gate'] for p in data['pairs']))
 def test_native_nonlinear_be_fixes_slack_acceleration_not_time_accuracy(self):
  data=summary('b3_native_elastic_newton_reference696')
  for r in data['records']:
   if r['mode']=='taut_release':self.assertTrue(r['strict_discrete_reference_pass']);self.assertEqual(r['discrete_acceleration_at_slack_m_s2'],0.)
  self.assertFalse(any(p['pass_time_gate'] for p in data['pairs']))
 def test_actual_native_slack_energy_api_and_force_are_inconsistent(self):
  data=summary('b3_native_spring_potential_fd698');self.assertEqual(data['status'],'FAIL_NATIVE_UNILATERAL_FORCE_POTENTIAL_CONSISTENCY');self.assertAlmostEqual(data['actual_native_potential_gradient_z_N'],1.,places=10)
  for r in data['records']:self.assertTrue(all(x==0. for v in r['actual_native_force_slot_N'] for x in v));self.assertTrue(all(x==0. for v in r['v'] for x in v))
  for r in summary('b3_native_spring_energy697')['records']:self.assertTrue(r['observer_state_purity_exact'])
 def test_potential_only_adapter_is_state_pure_and_not_a_time_fix(self):
  data=summary('b3_native_spring_potential_adapter699');self.assertEqual(data['status'],'PASS_POTENTIAL_ONLY_NOT_TIME_OR_B3');self.assertEqual(data['slack_actual_potential_FD_gradient_N'],0.)
  for r in data['records']:self.assertTrue(r['actual_q_v_force_slot_identity_exact']);self.assertLess(r['maximum_potential_reference_error_J'],1e-12)
  data=summary('b3_native_elastic_tangent694');self.assertFalse(any(p['pass_time_gate'] for p in data['pairs']))
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
