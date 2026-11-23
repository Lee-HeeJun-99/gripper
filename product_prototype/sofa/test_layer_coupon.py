import json,unittest
import numpy as np
from analyse import BASE
from layer_pressure_coupon import mesh
from layer_coupon_assess import overlap
class LayerCouponTests(unittest.TestCase):
 def test_overlap_witness(self):
  q,t,_=mesh();self.assertEqual(overlap(np.array([q,q+np.array([0,0,.000202])]),t),0);self.assertGreater(overlap(np.array([q,q+np.array([0,0,.00005])]),t),0)
 def test_failure_not_stiffness_success(self):
  d=json.loads((BASE/'results/layer_coupon_assess1192/summary.json').read_text())
  for case in ('layer_pressure_slip1190','layer_pressure_friction1191'):
   r=d['records'][case];self.assertEqual(r['status'],'FAIL_INTERLAYER_INTERSECTION');self.assertIsNone(r['effective_stiffness']);self.assertIsNone(r['contact_force'])
  self.assertEqual(d['layer_jamming'],'NOT VALIDATED')
 def test_ramp_not_cure(self):
  d=json.loads((BASE/'results/layer_ramp_assess1194/summary.json').read_text());self.assertEqual(d['records']['layer_ramp_pilot1193']['status'],'FAIL_INTERLAYER_INTERSECTION')
 def test_rigid_control_does_not_validate_friction(self):
  d=json.loads((BASE/'results/layer_rigid_failure_audit1197/summary.json').read_text());self.assertEqual(d['status'],'FAIL_COMPONENT_CONTACT_GEOMETRY')
  for r in d['records'].values():self.assertIsNotNone(r['first_entire_body_below_support_bottom_s'])
 def test_orientation_fixture_not_contact_cure(self):
  d=json.loads((BASE/'results/layer_fixture_phase_audit1208/summary.json').read_text())
  for r in d['records'].values():self.assertEqual(r['maximum_angular_speed_rad_s'],0);self.assertLess(r['minimum_centre_z_m'],-.4);self.assertLess(r['maximum_translational_impulse_residual_Ns'],1e-18)
 def test_detector_clock_is_not_accepted_position(self):
  d=json.loads((BASE/'results/layer_detection_phase1209/summary.json').read_text())
  for r in d['records'].values():self.assertEqual(r['RMS_vertex_Z_error_m']['previous_z'],0);self.assertGreater(r['RMS_vertex_Z_error_m']['free_z'],1e-5)
  self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
