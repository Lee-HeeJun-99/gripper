"""Small producer contracts, not Native physics validation."""
import unittest
import numpy as np
import trimesh
from sector_clutch_native import sensed_gap
from dorsal_yoke_candidate import capsule_separation,bar
from finite_support_sat import sat
from guide_swing_twist_diagnosis import swing_twist
from captured_prismatic_moving_cable import reference
from scipy.spatial.transform import Rotation
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad'))
from captured_carriage_candidate import wire

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
 def test_swing_twist_reconstruction(self):
  swing=Rotation.from_rotvec([0,0,.3]);twist=Rotation.from_rotvec([.2,0,0]);s,t=swing_twist((swing*twist).as_quat(),[1,0,0]);self.assertLess(abs(s.as_matrix()-swing.as_matrix()).max(),1e-14);self.assertAlmostEqual(t,.2,places=14)
 def test_stopper_reference_transfers_to_free_root(self):
  q,v,_=reference()[-1];self.assertAlmostEqual(q[1],.002,places=14);self.assertGreater(q[0],0);self.assertAlmostEqual(v[0],.04*.01/.006,places=14);self.assertAlmostEqual(v[1],0,places=14)
 def test_finite_wire_caps_survive_metre_scaling(self):
  tube=wire(np.zeros(3),np.array([.004,.003,.002]),.00025);self.assertTrue(tube.is_volume);self.assertTrue(tube.is_watertight)

if __name__=='__main__':unittest.main()
