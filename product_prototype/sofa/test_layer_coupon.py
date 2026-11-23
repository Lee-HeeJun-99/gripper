import json,unittest
import numpy as np
from analyse import BASE
from layer_pressure_coupon import mesh
from layer_coupon_assess import overlap
class LayerCouponTests(unittest.TestCase):
 def test_overlap_witness(self):
  q,t,_=mesh();self.assertEqual(overlap(np.array([q,q+np.array([0,0,.000202])]),t),0);self.assertGreater(overlap(np.array([q,q+np.array([0,0,.00005])]),t),0)
 def test_failure_not_stiffness_success(self):
  d=json.loads((BASE/'results/layer_coupon_assess1192/summary.json').read_text())
  for case in ('layer_pressure_slip1190','layer_pressure_friction1191'):
   r=d['records'][case];self.assertEqual(r['status'],'FAIL_INTERLAYER_INTERSECTION');self.assertIsNone(r['effective_stiffness']);self.assertIsNone(r['contact_force'])
  self.assertEqual(d['layer_jamming'],'NOT VALIDATED')
if __name__=='__main__':unittest.main()
