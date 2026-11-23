import json,unittest
from analyse import BASE
class ContactGapTests(unittest.TestCase):
 def test_actual_probe_purity(self):
  d=json.loads((BASE/'results/contact_gap_probe1212/summary.json').read_text());self.assertEqual(max(d['errors'].values()),0);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_zero_separation_normal_change(self):
  d=json.loads((BASE/'results/contact_gap_assess1215/summary.json').read_text());r=min(d['rows'],key=lambda r:abs(r['time_s']-.0004));self.assertLess(r['free_lower_face_z_m'],-7e-6);self.assertTrue(all(x[2]==0 for x in r['normal_row_parent_translation_J']))
 def test_no_policy_upgrade(self):
  d=json.loads((BASE/'results/normal_policy_rejection1218/summary.json').read_text());self.assertEqual(d['status'],'REJECT_NORMAL_POLICIES_FOR_PRODUCT');self.assertEqual(d['records']['surface_normals_mu0']['status'],'FAIL_FRICTIONLESS_COMPONENT_EXPECTATION')
  for case in ('layer_local_slip1216','layer_local_friction1217'):self.assertIsNotNone(d['records'][case]['first_nonfinite_accepted_time_s'])
if __name__=='__main__':unittest.main()
