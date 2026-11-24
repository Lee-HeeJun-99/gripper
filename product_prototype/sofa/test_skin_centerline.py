import unittest
import numpy as np
from b3_skin_centerline import metrics
class CenterlineTest(unittest.TestCase):
 def test_straight(self):
  m=metrics(np.array([[0.,0,0],[.01,0,0],[.02,0,0]]));self.assertEqual(m['total_unsigned_turn_deg'],0);self.assertEqual(m['max_discrete_centerline_curvature_per_m'],0)
 def test_polygon_not_continuum_angle(self):
  a=np.linspace(0,np.pi/3,5);m=metrics(np.column_stack([np.cos(a),np.sin(a),np.zeros(5)]));self.assertAlmostEqual(m['total_unsigned_turn_deg'],45,places=10)
if __name__=='__main__':unittest.main()
