import unittest
import numpy as np
from layer_face_load import tip_load
from layer_section_reference import mesh

class FaceLoadTest(unittest.TestCase):
 def test_force_moment_and_affine_virtual_work(self):
  for dims in ((9,2,2),(17,3,5),(9,5,3)):
   q,t=mesh(*dims);F,A,faces=tip_load(q,t,[0,0,-5e-5])
   self.assertAlmostEqual(A,2e-6,places=18)
   np.testing.assert_allclose(F.sum(axis=0),[0,0,-5e-5],atol=1e-19)
   np.testing.assert_allclose(np.cross(q,F).sum(axis=0),[0,2e-6,0],atol=1e-19)
   # Affine virtual displacement is integrated exactly over each triangle.
   M=np.array([[1,2,3],[4,5,6],[7,8,9.]])
   u=q@M.T+[.1,.2,.3];centre=np.array([.04,0,.0001])
   self.assertAlmostEqual(float((F*u).sum()),float(np.dot([0,0,-5e-5],M@centre+[.1,.2,.3])),places=18)
 def test_not_original_equal_four_point_load(self):
  q,t=mesh(9,2,2);F,_,_=tip_load(q,t,[0,0,-5e-5])
  self.assertGreater(np.ptp(F[q[:,0]==.04,2]),1e-6)
if __name__=='__main__':unittest.main()
