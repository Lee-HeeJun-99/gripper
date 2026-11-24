import unittest
import numpy as np
import trimesh
from capillary_bored_support import bore_surface_min
from capillary_guide_candidate import SPEC,support_bore_radial_min

class Bore(unittest.TestCase):
 def test_unobstructed_offset_box(self):
  mesh=trimesh.creation.box(extents=[.004,.002,.0004]);mesh.vertices += [0,0,.001]
  d,_=bore_surface_min(mesh.vertices,mesh.faces)
  self.assertAlmostEqual(d,.0008,places=14)
  self.assertAlmostEqual(support_bore_radial_min(mesh.vertices,mesh.faces,np.zeros(3),np.eye(3)),d,places=14)
 def test_axis_intersection_rejected(self):
  mesh=trimesh.creation.box(extents=[.004,.0004,.0004])
  # Axis lies INSIDE solid: surface radius alone cannot certify open bore.
  self.assertTrue(mesh.contains([[0,0,0]])[0])
  self.assertLess(bore_surface_min(mesh.vertices,mesh.faces)[0],.0006)
 def test_ring_hole_surfaces(self):
  from finite_guide_coupon import eyelet
  cfg={'tendon':dict(guide_outer_radius=.8255,guide_hole_radius=.5969,guide_length_mm=2.)};m,_=eyelet(cfg,32)
  d,_=bore_surface_min(m.vertices*.001,m.faces)
  self.assertAlmostEqual(d,.0005969*np.cos(np.pi/32),places=14)
 def test_supplier_units_not_stock_claim(self):
  self.assertAlmostEqual(SPEC['OD_in']*25.4,1.651,places=14)
  self.assertEqual(SPEC['bond_strength'],'NOT MEASURED')

if __name__=='__main__':unittest.main()
