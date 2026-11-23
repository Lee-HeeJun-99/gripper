"""Analytic geometry regressions, not physical assembly qualification."""
import unittest
import numpy as np
import trimesh
from rail_continuous_service import envelope,surface_sweep
from clamp_stack_contract import closure

class SweptServiceTests(unittest.TestCase):
 def test_stack_free_closure_not_preload(self):
  r=closure(-.55,-.5,.1,.11,.14,.15)
  self.assertAlmostEqual(r['ideal_free_stack_closure_travel_mm'],.07)
  self.assertIsNone(r['actual_preload_N'])
 def test_invalid_stack_rejected(self):
  with self.assertRaises(ValueError):closure(-.55,-.5,.1,.09,.14,.15)
  with self.assertRaises(ValueError):closure(-.55,-.5,.1,.11,.14,np.nan)
 def test_convex_box_sweep_volume(self):
  body=trimesh.creation.box(extents=[1,2,3]);s=envelope(body,[4,0,0])
  self.assertAlmostEqual(s.volume,30)
 def test_middle_only_collision_not_missed(self):
  body=trimesh.creation.box();obstacle=trimesh.creation.box(extents=[.2,.2,.2]);obstacle.apply_translation([2,0,0])
  self.assertTrue(surface_sweep(body,np.array([4,0,0]),[('middle',obstacle)])['intersections'])
 def test_clear_parallel_motion(self):
  body=trimesh.creation.box();obstacle=trimesh.creation.box();obstacle.apply_translation([2,3,0])
  self.assertFalse(surface_sweep(body,np.array([4,0,0]),[('away',obstacle)])['intersections'])
 def test_concave_hull_hit_not_actual_collision(self):
  left=trimesh.creation.box();right=left.copy();right.apply_translation([0,4,0]);body=trimesh.util.concatenate([left,right])
  obstacle=trimesh.creation.box(extents=[.2,.2,.2]);obstacle.apply_translation([2,2,0])
  hull=envelope(body,[4,0,0]);self.assertTrue(hull.contains([obstacle.centroid])[0])
  self.assertFalse(surface_sweep(body,np.array([4,0,0]),[('gap',obstacle)])['intersections'])
 def test_rigid_transform_preserves_sweep_volume(self):
  body=trimesh.creation.box();d=np.array([4.,1,0]);original=envelope(body,d).volume
  M=trimesh.transformations.rotation_matrix(.7,[1,2,3]);M[:3,3]=[5,-2,7];body.apply_transform(M)
  self.assertAlmostEqual(envelope(body,M[:3,:3]@d).volume,original)
 def test_invalid_delta_rejected(self):
  for delta in ([1,2],[np.nan,0,0]):
   with self.assertRaises(ValueError):envelope(trimesh.creation.box(),delta)
if __name__=='__main__':unittest.main()
