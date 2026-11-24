import json,unittest
from analyse import BASE
def result():return json.loads((BASE/'results/contact_adaptation_profile1388/summary.json').read_text())
class ProfileGateTests(unittest.TestCase):
 def test_initial_overlap_rejected(self):
  d=result();self.assertEqual(d['status'],'REJECT_INITIAL_SKIN_FEM_GATE');self.assertTrue(all(r['minimum_initial_surface_gap_mm']<0 for r in d['records']))
 def test_no_invalid_native_run(self):
  d=result();self.assertEqual(d['Native_grasp'],'NOT RUN');self.assertEqual(d['wire_guide_clearance'],'NOT MEASURED')
 def test_geometry_failure_is_not_tet_inversion(self):
  self.assertTrue(all(r['minimum_signed_tet_determinant_mm3']>0 for r in result()['records']))
if __name__=='__main__':unittest.main()
