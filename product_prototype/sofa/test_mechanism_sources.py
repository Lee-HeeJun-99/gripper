import unittest
from mechanism_contact_inventory import identify

class Sources(unittest.TestCase):
 def test_foreign_hardware_not_only_eyelets(self):
  self.assertEqual(identify('/guides2/cable0/support5/PointCollisionModel1'),(2,'hardware'))
 def test_all_finger_surfaces(self):
  self.assertEqual(identify('/finger1/skinCollision/surface'),(1,'skin'))
  self.assertEqual(identify('/finger0/railCollision/surface'),(0,'rail'))
  self.assertEqual(identify('/finger2/newSurface/TriangleCollisionModel1'),(2,'other_finger'))
 def test_object_and_malformed_not_finger(self):
  for path in ('/object/collision/SphereCollisionModel1','/guidesX/cable0','/floor/surface'):self.assertIsNone(identify(path))
if __name__=='__main__':unittest.main()
