import unittest
import numpy as np
from guide_cylinder_bound import cylinder_support
class SupportFunction(unittest.TestCase):
 def test_coaxial_and_lateral_exact(self):
  self.assertEqual(cylinder_support(1,1.5,1),1)
  self.assertEqual(cylinder_support(0,1.5,1),1.5)
  self.assertAlmostEqual(2.3-2*cylinder_support(1,1.5,1),.3)
  self.assertAlmostEqual(3.4-2*cylinder_support(0,1.5,1),.4)
 def test_continuous_support_encloses_faceted_cylinder(self):
  theta=np.arange(128)*2*np.pi/128
  vertices=np.array([[x,1.5*np.cos(t),1.5*np.sin(t)] for x in (-1,1) for t in theta]);rng=np.random.default_rng(42);n=rng.normal(size=(1000,3));n/=np.linalg.norm(n,axis=1)[:,None];exact=cylinder_support(n[:,0],1.5,1);faceted=(n@vertices.T).max(axis=1);self.assertLessEqual(float((faceted-exact).max()),1e-12)
if __name__=='__main__':unittest.main()
