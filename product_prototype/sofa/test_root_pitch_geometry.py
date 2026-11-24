import json,unittest
from analyse import BASE
class RootPitchTest(unittest.TestCase):
 def test_existing_pitch_and_penetration_rejection(self):
  c=json.loads((BASE/'results/b3_railback_grasp1001298/config.json').read_text());self.assertEqual(c['palm']['root_angle_deg'],14)
  d=json.loads((BASE/'results/b3_root_pitch_geometry1323/summary.json').read_text());self.assertEqual(d['status'],'REJECT_SKIN_INITIAL_GEOMETRY');self.assertTrue(all(r['minimum_initial_skin_sphere_gap_m']<0 for r in d['records'] if r['pitch_deg']==14));self.assertEqual(d['Native_scene'],'NOT CREATED_UNTIL_ALL_INITIAL_PARTS_TRANSFORMED_AND_CHECKED')
 def test_local_derivative_not_certified_range(self):
  d=json.loads((BASE/'results/b3_root_pitch_margin1324/summary.json').read_text());self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertTrue(all(r['derivative_absolute_difference']<1e-10 and r['local_gap_derivative_m_per_rad']<0 and r['first_order_additional_pitch_to_contact_margin_deg']<1 for r in d['records']))
if __name__=='__main__':unittest.main()
