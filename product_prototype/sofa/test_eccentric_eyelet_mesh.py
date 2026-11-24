import unittest
import numpy as np
from eccentric_eyelet_mesh import solid
class MeshTests(unittest.TestCase):
    def test_eccentric_volume_invariant(self):
        a=solid(np.array([0.,0,0]));b=solid(np.array([.31,0,0]));self.assertTrue(b.is_watertight);self.assertTrue(b.is_winding_consistent);self.assertAlmostEqual(a.volume,b.volume,places=12)
    def test_bore_chamfer_and_outer_size(self):
        mesh=solid(np.array([.3,0,0]));v=mesh.vertices.reshape(8,128,3)
        np.testing.assert_allclose(np.linalg.norm(v[:4,:,:2],axis=2),1.5,atol=1e-14)
        np.testing.assert_allclose(np.linalg.norm(v[4:,:,:2]-[.3,0],axis=2),np.repeat([[.8],[.6],[.6],[.8]],128,axis=1),atol=1e-14)
    def test_refinement_reduces_volume_error(self):
        a=solid(np.array([.3,0,0]),64).volume;b=solid(np.array([.3,0,0]),128).volume;c=solid(np.array([.3,0,0]),256).volume;self.assertGreater(b,a);self.assertLess(c-b,b-a)
if __name__=='__main__':unittest.main()
