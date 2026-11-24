import unittest,numpy as np
from rounded_bore_wire import geometry,inside
from rounded_wire_surface_contract import cells,clip,intersections
class WedgeClipping(unittest.TestCase):
 def test_cell_union_matches_independent_ring_membership(self):
  m,inner=geometry();p=np.random.default_rng(1651).uniform([-1.1,-1.6,-1.6],[1.1,1.6,1.6],(2000,3));union=np.zeros(len(p),dtype=bool)
  for A,b,_,_ in cells(inner):union|=np.all(p@A.T+b<=0,axis=1)
  np.testing.assert_array_equal(union,inside(p,inner));np.testing.assert_array_equal(union,m.contains(p))
 def test_triangle_in_bore_and_crossing_wall(self):
  m,inner=geometry();parts=cells(inner);faces=np.array([[0,1,2]]);_,good=intersections(np.array([[0,0,0],[.5,.3,0],[-.5,.3,.1]]),faces,parts,inner);self.assertEqual(good,[]);_,bad=intersections(np.array([[0,.5,0],[.5,.8,0],[-.5,.8,.1]]),faces,parts,inner);self.assertTrue(any(h['centroid_strictly_inside_solid'] for h in bad))
if __name__=='__main__':unittest.main()
