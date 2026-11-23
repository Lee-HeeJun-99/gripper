"""Evidence and analysis-scope regressions;NOT product physical gates."""
import json,unittest
import numpy as np
from analyse import BASE,sha
from b3_lift_assess import evaluation_masks
def load(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class OriginLiftTests(unittest.TestCase):
 def test_read_only_actual_origin_observer_purity(self):
  d=load('b3_origin_observer1075');self.assertTrue(d['observer_purity_1e12_pass']);self.assertEqual(len(d['records']),24);self.assertAlmostEqual(d['maximum_origin_vs_root_error_m'],.0001)
 def test_driven_origin_uses_same_binary_not_purity_claim(self):
  d=load('b3_origin_motion1076');old=load('b3_origin_observer1075');self.assertEqual(d['binary_sha256'],old['binary_sha256']);self.assertEqual(sha(d['binary']),d['binary_sha256']);self.assertFalse(d['observer_purity_1e12_pass']);self.assertLessEqual(d['maximum_origin_vs_root_error_m'],1e-12)
 def test_lift_does_not_include_intentional_release(self):
  t=np.array([1.5,1.6,1.95,2.,2.5,3.]);end,active=evaluation_masks(t,dict(reference_s=1.6,end_window_s=[1.95,2.]));self.assertEqual(active.tolist(),[False,True,True,True,False,False]);self.assertEqual(end.tolist(),[False,False,True,True,False,False])
 def test_radius_correction_preserves_original(self):
  old=load('b3_lift50_assess1079');new=load('b3_lift50_corrected1085');self.assertAlmostEqual(old['minimum_support_gap_mm']-new['minimum_support_gap_mm'],30);self.assertTrue((BASE/'results/b3_lift50_assess1079/GEOMETRY_CORRECTION.json').is_file())
 def test_actual_lift_only_no_physical_certificate(self):
  d=load('b3_lift_release_corrected1091');self.assertEqual(d['status'],'PASS_EXPLORATORY_LIFT_ONLY');self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertTrue(all(d['tests'].values()));self.assertIsNone(d['root_fixture_work'])
 def test_bad_window_original_fail_preserved(self):
  self.assertEqual(load('b3_lift_release_lift1088')['status'],'FAIL_EXPLORATORY_LIFT');self.assertTrue((BASE/'results/b3_lift_release_lift1088/WINDOW_CORRECTION.json').is_file())
 def test_release_and_prefix_are_actual_bounded_observations(self):
  d=load('b3_release_recovery1089');self.assertTrue(d['prefix_API_1e12_pass']);self.assertTrue(all(v==0 for v in d['late_maximum_contact_resultants_N'].values()));self.assertIn('NOT QUALIFIED',d['full_recovery'])
 def test_75g_short_entry_not_holding(self):
  d=load('b3_mass75_entry1084');self.assertEqual(d['steps'],120);self.assertEqual(d['holding_window'],'NOT RUN_SHORT_ENTRY_ONLY')
 def test_short_gravity_reference_failure_preserved(self):
  d=load('b3_recovery_reference1093');self.assertEqual(d['status'],'FAIL_GRAVITY_REFERENCE_RECOVERY_COMPARISON');self.assertFalse(all(r['reference_stability'] for r in d['records']))
 def test_settled_gravity_match_is_not_material_recovery_certificate(self):
  d=load('b3_recovery_settled1095');self.assertEqual(d['status'],'PASS_GRAVITY_REFERENCE_RECOVERY_COMPARISON_ONLY');self.assertIsNone(d['absolute_floor']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertTrue(all(r['reference_stability'] and r['relative_gate'] for r in d['records']))
 def test_object_momentum_is_not_whole_energy_certification(self):
  d=load('b3_lift_momentum_pose1097');self.assertEqual(d['first800_object_state_impulse_prefix_vs1077_error'],0);self.assertEqual(d['whole_coupled_energy'],'NOT MEASURED');self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
