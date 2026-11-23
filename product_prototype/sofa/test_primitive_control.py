import unittest
from primitive_sphere_assess import assess
class TestPrimitive(unittest.TestCase):
 def test_face_interior_controls(self):
  for c in ('primitive_offset_slip1230','primitive_offset_stick1231','primitive_offset_sliding1232'):
   with self.subTest(c=c):self.assertEqual(assess(c)['status'],'PASS_PRIMITIVE_COMPONENT_SCOPE_ONLY')
 def test_old_failure_not_promoted(self):
  r=assess('primitive_sphere_slip1225');self.assertEqual(r['status'],'FAIL_COMPONENT_EXPECTATIONS');self.assertFalse(r['criteria']['no_iteration_saturation'])
 def test_contact_disappearance_is_failure_not_missing_ratio_crash(self):
  r=assess('primitive_local_slip1250');self.assertEqual(r['status'],'FAIL_COMPONENT_EXPECTATIONS');self.assertIsNone(r['friction_ratio_range']);self.assertFalse(r['criteria']['positive_normal_support'])
if __name__=='__main__':unittest.main()
