import unittest,numpy as np
from wire_local_collision_mesh import surface
class LocalSurface(unittest.TestCase):
 def test_mapping_never_indexes_nonexistent_beam(self):
  q,p,f,x=surface();self.assertTrue(np.all(np.floor(p[:,0])<10));self.assertEqual(p[-1,0],9.999999999999998);self.assertEqual(len(x),193);self.assertEqual(len(q),3088);self.assertEqual(len(f),6144);self.assertEqual(len(np.unique(x)),len(x));self.assertGreater(np.diff(x).min(),0)
 def test_exact_physical_radius_and_nonzero_faces(self):
  q,p,f,x=surface();np.testing.assert_allclose(np.linalg.norm(q[:,1:],axis=1),.00025,rtol=0,atol=1e-19);np.testing.assert_array_equal(q[:,1:],p[:,1:]);self.assertGreater(np.linalg.norm(np.cross(q[f[:,1]]-q[f[:,0]],q[f[:,2]]-q[f[:,0]]),axis=1).min(),0);self.assertAlmostEqual(x[-1],.02,places=17)
if __name__=='__main__':unittest.main()
