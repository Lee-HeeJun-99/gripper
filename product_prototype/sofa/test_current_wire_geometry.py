import unittest,numpy as np
import trimesh
from current_turn_wire_assess import polygon_ring_distance
from finite_guide_coupon import eyelet
class FiniteBoreDistance(unittest.TestCase):
 def test_exact_extruded_polygon_matches_actual_triangles(self):
  m,_=eyelet({'tendon':{'guide_outer_radius':1.5,'guide_hole_radius':.6}},32);tri=m.triangles
  points=np.array([[0,0,0],[0,.0008,0],[0,.0017,0],[.0013,.0008,0],[.0012,.0018,.0001],[0,.0002,.0002]])
  expected=[]
  # Installed trimesh absolute tolerances misclassify skinny triangles in m.
  # Evaluate the independent reference in mm,convert result back;same solid.
  for p in points:expected.append(np.linalg.norm(trimesh.triangles.closest_point(tri,np.repeat((p*1000)[None],len(tri),axis=0))-p*1000,axis=1).min()*.001)
  actual=polygon_ring_distance(points);self.assertLessEqual(float(abs(abs(actual)-expected).max()),1e-12);self.assertLess(actual[1],0)
  for i in (0,2,3,4,5):self.assertGreater(actual[i],0)
 def test_distance_not_circular_bore_approximation(self):
  gap=polygon_ring_distance(np.zeros((1,3)))[0];self.assertAlmostEqual(gap,.0006*np.cos(np.pi/32),places=15);self.assertLess(gap,.0006)
 def test_unscaled_triangle_reference_limit_is_visible(self):
  m,_=eyelet({'tendon':{'guide_outer_radius':1.5,'guide_hole_radius':.6}},32);tri=m.triangles*.001;p=np.array([0,.0008,0]);raw=np.linalg.norm(trimesh.triangles.closest_point(tri,np.repeat(p[None],len(tri),axis=0))-p,axis=1).min();self.assertGreater(abs(raw-.0002),1e-6);self.assertAlmostEqual(polygon_ring_distance(p[None])[0],-.0002,places=15)
if __name__=='__main__':unittest.main()
