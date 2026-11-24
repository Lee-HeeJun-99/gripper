"""Small producer contracts, not Native physics validation."""
import unittest
import numpy as np
import trimesh
from sector_clutch_native import sensed_gap
from dorsal_yoke_candidate import capsule_separation,bar
from finite_support_sat import sat

class Contracts(unittest.TestCase):
 def test_sensor_uses_rotated_geometry_not_centre(self):
  q=np.array([[0.,0.,0.,0.,0.,np.sqrt(.5),np.sqrt(.5)]]);local=np.array([[.002,0.,0.]]);owners=np.array([0]);normals=np.array([[0.,1.,0.],[0.,-1.,0.]])
  self.assertAlmostEqual(sensed_gap(q,local,owners,normals),-.002,places=15)
 def test_sat_argument_contract_and_crossbar(self):
  a=bar(np.array([0.,0.,0.]),np.array([0.,.01,0.]),.0008);b=a.copy();b.apply_translation([.002,0,0]);gap,status=sat(a.vertices,b.vertices,a.faces,b.faces,a.edges_unique,b.edges_unique)
  self.assertEqual(status,'SEPARATED');self.assertAlmostEqual(gap,.0012,places=14)
 def test_finite_wire_radius_included(self):
  cube=trimesh.creation.box([.001,.001,.001]);gap=capsule_separation(cube,np.array([.002,-.001,0]),np.array([.002,.001,0]),.00025)
  self.assertAlmostEqual(gap,.00125,places=14)
 def test_crossbar_positive_volume(self):
  cube=bar(np.array([0.,0.,0.]),np.array([0.,.01,0.]),.0008)
  self.assertTrue(cube.is_watertight);self.assertGreater(cube.volume,0)

if __name__=='__main__':unittest.main()
