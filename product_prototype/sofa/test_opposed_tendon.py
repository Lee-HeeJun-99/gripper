import json,unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class OpposedTendonTests(unittest.TestCase):
 def test_finite_proxy_initial_gate(self):
  for case in ('opposed_geometry1390','opposed_nonuniform_geometry1396'):
   d=result(case);self.assertEqual(d['status'],'PASS_INITIAL_OPPOSED_PROXY_SKIN_CLEARANCE');self.assertTrue(all(r['minimum_support_capsule_skin_lower_bound_mm']>0 for r in d['records']))
 def test_actual_direction_not_prescribed_pose(self):
  d=result('opposed_assess1395');front,back=d['records'];self.assertGreater(front['endpoint']['tip_angle_minus_reference_deg'],0);self.assertLess(back['endpoint']['tip_angle_minus_reference_deg'],0);self.assertEqual(front['endpoint']['command_force_N'],back['endpoint']['command_force_N'])
 def test_moment_sign_and_native_impulse_units(self):
  d=result('opposed_assess1395');front,back=d['records'];self.assertTrue(all(r['max_force_impulse_vs_command_error_Ns']==0 for r in d['records']));self.assertGreater(front['reference_rest_moment_per_cable'][0][0]['reference_bending_moment_y_Nm_per_N'],0);self.assertLess(back['reference_rest_moment_per_cable'][0][0]['reference_bending_moment_y_Nm_per_N'],0)
 def test_native_saved_element_quality(self):
  for case in ('opposed_control_mid1393','opposed_open_mid1394','opposed_nonuniform_mid1398','opposed_release1401','opposed_zero_reference1403'):
   d=result(case);self.assertEqual(d['status'],'BOUNDED_NO_OBJECT_ACTUATION_ONLY');self.assertGreater(d['minimum_saved_core_volume_ratio'],0);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_new_reference_really_used_without_sphere(self):
  src=BASE/'results/opposed_nonuniform_mid1398';root=ET.parse(src/'scene.scn').getroot();self.assertIsNone(root.find("Node[@name='object']"));q=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);wanted=np.array(json.loads((BASE/'results/contact_adaptation_profile1388/candidate_q0_finger0_mm.json').read_text()))*.001;self.assertLess(abs(q-wanted).max(),1e-15)
 def test_virtual_insertion_is_not_actual_contact(self):
  d=result('opposed_insertion1399');self.assertEqual(d['status'],'PASS_SINGLE_FINGER_VIRTUAL_INSERTION_ENVELOPE_ONLY');self.assertEqual(d['window_outputs'],41);self.assertGreater(d['window_minimum_skin_gap_m'],.0002);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_release_and_prefix_are_not_time_gate(self):
  d=result('opposed_recovery1404');self.assertEqual(d['late_max_cable_impulse_Ns'],0);self.assertTrue(all(d['first_240_record_equality'].values()));self.assertGreater(d['endpoint']['max_q_minus_gravity_reference_m'],0);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_strain_measured_invariants_not_allowable_material(self):
  d=result('opposed_strain1405');self.assertTrue(all(r['allowable_material_strain'] is None and r['minimum_determinant_ratio']>0 for r in d['records']));self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
