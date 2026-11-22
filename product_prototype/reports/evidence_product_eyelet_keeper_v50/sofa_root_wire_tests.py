"""Software/reference regression only;not new SOFA physical evidence."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad'))
from root_load_requirements import root_load
from root_wire_reference import circular_path

class WireReferenceTests(unittest.TestCase):
 def test_quarter_arc_and_gradient(self):
  length,_,_,da,db=circular_path([.002,-.01],[-.01,.002],.002)
  self.assertAlmostEqual(length,.02+.002*np.pi/2,15)
  np.testing.assert_allclose(da,[0,-1],atol=1e-14);np.testing.assert_allclose(db,[-1,0],atol=1e-14)
 def test_degenerate_rejected(self):
  for r in (0,-1):
   with self.assertRaises(ValueError):circular_path([1,0],[0,1],r)
  with self.assertRaises(ValueError):circular_path([0,0],[0,1],.002)
 def test_load_scaling_and_moment(self):
  record=dict(part='reference',route_mm=[[2,-10,0],[2,0,0],[0,2,0],[-10,2,0]],centre_mm=[0,0,0],turn_angle_deg=90)
  result=root_load(record,1.5)
  np.testing.assert_allclose(result['force_N'],[-1.5,-1.5,0],atol=1e-14)
  self.assertLess(result['force_reference_error_N'],1e-14);self.assertEqual(result['ideal_moment_norm_Nm'],0)
 def test_native_value_is_impulse_not_force(self):
  source=(Path(__file__).parent/'root_wire_coupon.py').read_text()
  self.assertIn('value=str(tension*dt)',source)
  self.assertIn('physical_sliding_qualified=False',source)
if __name__=='__main__':unittest.main()
