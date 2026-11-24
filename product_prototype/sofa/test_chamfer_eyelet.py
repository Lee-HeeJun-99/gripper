import unittest,numpy as np
from chamfer_eyelet_grasp import ring
class ChamferEyelet(unittest.TestCase):
 def test_finite_closed_and_nominal_envelope(self):
  m=ring();self.assertTrue(m.is_watertight);self.assertTrue(m.is_winding_consistent);self.assertGreater(m.volume,0);self.assertAlmostEqual(np.ptp(m.vertices[:,0]),2)
  radius=np.linalg.norm(m.vertices[:,1:],axis=1);self.assertAlmostEqual(radius.min(),.6);self.assertAlmostEqual(radius.max(),1.5)
 def test_end_wall_and_removed_volume_are_explicit(self):
  m=ring();end=np.isclose(abs(m.vertices[:,0]),1);r=np.linalg.norm(m.vertices[end,1:],axis=1);self.assertAlmostEqual(r.max()-r.min(),.6);self.assertLess(m.volume,11.799062675535438)
if __name__=='__main__':unittest.main()
