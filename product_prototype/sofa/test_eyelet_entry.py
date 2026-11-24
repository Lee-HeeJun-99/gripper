import unittest
import numpy as np
from eyelet_entry_geometry import solid_distance,fillet
class EntryTests(unittest.TestCase):
    def test_solid_signed_distance(self):
        np.testing.assert_allclose(solid_distance([[0,0],[1,1],[3,1]],[[0,0],[2,0],[2,2],[0,2]]),[0,-1,1])
    def test_fillet_radius_tangency(self):
        u=np.array([1.,0,0]);v=np.array([.8,.6,0]);p=np.zeros(3);arc,trim,step=fillet(p,u,v)
        centre=arc[0]+np.array([0.,5,0]);np.testing.assert_allclose(np.linalg.norm(arc-centre,axis=1),5,atol=1e-14)
        np.testing.assert_allclose(arc[-1],trim*v,atol=1e-14);self.assertLessEqual(step,.005)
    def test_straight_path(self):
        arc,trim,step=fillet(np.zeros(3),np.array([1.,0,0]),np.array([1.,0,0]));self.assertEqual(trim,0);self.assertEqual(len(arc),1)
if __name__=='__main__':unittest.main()
