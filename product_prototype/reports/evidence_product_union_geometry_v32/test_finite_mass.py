"""Independent analytic geometry and torque-free reference regressions."""
import unittest
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from finite_mass_reference import moments
from finite_free_spin_reference import axisymmetric_state

class FiniteMassTest(unittest.TestCase):
 def test_box_exact(self):
  m=trimesh.creation.box(extents=[2,3,4]);V,c,I=moments(m.vertices,m.faces)
  self.assertAlmostEqual(V,24);np.testing.assert_allclose(c,0,atol=1e-15);exact=np.diag([25/12,20/12,13/12]);self.assertLess(np.linalg.norm(I-exact)/np.linalg.norm(exact),1e-14)
 def test_moment_units(self):
  m=trimesh.creation.box(extents=[2,3,4]);V,c,I=moments(m.vertices,m.faces)
  for scale in (1e-3,1e3):
   Vs,cs,Is=moments(m.vertices*scale,m.faces);self.assertLess(abs(Vs/(V*scale**3)-1),1e-14);self.assertLess(np.linalg.norm(Is-I*scale**2)/np.linalg.norm(I*scale**2),1e-14)
 def test_free_spin_objectivity(self):
  n=np.array([1.,0,0]);L=np.array([.3,.5,.7]);Q=Rotation.from_rotvec([.3,-.7,.4]).as_matrix()
  for t in (0,.1,1.):
   x,w,I=axisymmetric_state(t,L,n,1.3,.98);y,z,J=axisymmetric_state(t,Q@L,Q@n,1.3,.98);np.testing.assert_allclose(y,Q@x,rtol=1e-13,atol=1e-14);np.testing.assert_allclose(z,Q@w,rtol=1e-13,atol=1e-14);np.testing.assert_allclose(J,Q@I@Q.T,rtol=1e-13,atol=1e-14);np.testing.assert_allclose(I@w,L,rtol=1e-13)
 def test_stationary_and_principal(self):
  n=np.array([1.,0,0]);x,w,I=axisymmetric_state(5,np.zeros(3),n,1.3,.98);np.testing.assert_array_equal(x,n);np.testing.assert_array_equal(w,np.zeros(3))
  x,w,I=axisymmetric_state(5,n*2,n,1.3,.98);np.testing.assert_allclose(x,n,atol=1e-14);np.testing.assert_allclose(w,n*2/1.3,atol=1e-14)
 def test_invalid_inertia_rejected(self):
  with self.assertRaises(ValueError):axisymmetric_state(0,np.ones(3),np.array([1.,0,0]),-1,1)
if __name__=='__main__':unittest.main()
