import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_surface_distance import point_triangles
class TestSurfaceDistance(unittest.TestCase):
    def test_regions_and_objectivity(self):
        triangle=np.array([[[0.,0,0],[1,0,0],[0,1,0]]])
        for p,expected in (([.2,.2,1],1),([2,0,0],1),([.6,.6,0],np.sqrt(.02))):
            d,closest,degenerate=point_triangles(p,triangle);self.assertAlmostEqual(d[0],expected,places=12);self.assertEqual(degenerate,0)
            Q=np.array([[0,-1,0],[0,0,1],[-1,0,0.]]) # orthogonal, determinant+1
            shift=np.array([7,-3,2]);dd,cc,_=point_triangles(Q@p+shift,triangle@Q.T+shift)
            self.assertAlmostEqual(dd[0],d[0],places=12);np.testing.assert_allclose(cc,closest@Q.T+shift,atol=1e-12)
    def test_degenerate_segment(self):
        d,_,n=point_triangles([1,.2,0],np.array([[[0.,0,0],[1,0,0],[2,0,0]]]))
        self.assertEqual(n,1);self.assertAlmostEqual(d[0],.2)
if __name__=='__main__':unittest.main()
