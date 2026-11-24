import unittest,numpy as np
from wire_edge_facet_contract import segment_triangle
from raytrace_finite_surface import close_wire
from wire_local_collision_mesh import surface
class SurfaceContracts(unittest.TestCase):
 def test_strict_segment_triangle_crossing(self):
  tri=np.array([[[0.,0.,0.],[1,0,0],[0,1,0]]]);ids,p,t,s,r=segment_triangle(np.array([.2,.3,-1]),np.array([.2,.3,1]),tri);np.testing.assert_array_equal(ids,[0]);np.testing.assert_allclose(p[0],[.2,.3,0],atol=1e-15);self.assertEqual(t[0],.5);self.assertAlmostEqual(s[0],.2);self.assertAlmostEqual(r[0],.3)
 def test_no_infinite_plane_false_positive(self):
  tri=np.array([[[0.,0.,0.],[1,0,0],[0,1,0]]]);ids,*_=segment_triangle(np.array([1.,1,-1]),np.array([1.,1,1]),tri);self.assertEqual(len(ids),0)
 def test_caps_preserve_original_surface_and_volume(self):
  q,_,f,_=surface();old=q.copy();oldf=f.copy();new,faces,volume=close_wire(q,f);np.testing.assert_array_equal(q,old);np.testing.assert_array_equal(f,oldf);np.testing.assert_array_equal(new[:len(q)],q);np.testing.assert_array_equal(faces[:len(f)],f);self.assertEqual(len(new),len(q)+2);self.assertEqual(len(faces),len(f)+32);expected=20*.5*16*.25**2*np.sin(2*np.pi/16);self.assertAlmostEqual(volume,expected,places=12)
if __name__=='__main__':unittest.main()
