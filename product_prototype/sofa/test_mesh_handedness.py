"""Saved Native reflection and independent conforming/QR checks,not graspPASS."""
import json,unittest
import numpy as np
from analyse import BASE
from mirror_conforming_mesh import generate
def data(case,name='summary.json'):return json.loads((BASE/'results'/case/name).read_text())
def frame(q):
 x=q[1]-q[0];x=x/np.linalg.norm(x);z=np.cross(q[1]-q[0],q[2]-q[0]);z=z/np.linalg.norm(z);return np.column_stack([x,np.cross(z,x),z])
class HandednessTests(unittest.TestCase):
 def test_mesh_reference_and_foot_preserved(self):
  pre=data('centreline_paired1527','preflight.json');self.assertEqual(pre['geometry']['nodes'],294);self.assertTrue(pre['geometry']['boundary_edge_incidence_exactly2']);self.assertTrue(pre['geometry']['tetra_set_reflection_invariant']);self.assertEqual(pre['adaptation'][0]['mapped_anchor_count'],36);self.assertLess(abs(pre['adaptation'][0]['volume_ratio']-1),1e-12);self.assertLess(pre['adaptation'][0]['old_existing_node_reference_error_m'],1e-12)
 def test_oriented_QR_parity(self):
  q=np.array([[.2,.1,.3],[1.4,.3,.2],[.1,1.1,.8],[.3,.2,1.4]]);S=np.diag([1.,-1,1]);other=(q@S)[[1,0,2,3]];self.assertLess(abs(frame(other)-S@frame(q)@np.diag([-1.,1,1])).max(),1e-12)
 def test_small_velocity_failure_not_rounded_to_pass(self):
  d=data('paired_order_assess1528');self.assertEqual(d['status'],'FAIL_SYMMETRIC_MESH_REFLECTION_API');r=d['records'][-1];self.assertLess(r['q_reflection_error_m'],1e-12);self.assertGreater(r['v_reflection_error_m_s'],1e-12);self.assertFalse(r['API_1e12_pass'])
 def test_actual_reflection_and_torque_provenance(self):
  d=data('mirror_assess1523');a,b=d['records'];self.assertLess(a['tip_lateral_min_max_end_mm'][-1],-1);self.assertGreater(b['tip_lateral_min_max_end_mm'][-1],1);self.assertLess(d['maximum_reflected_q_prediction_error_m'],1e-12);w=data('sequenced_wrench1520');self.assertLess(w['maximum_angular_momentum_residual_Nms'],1e-10);self.assertTrue(all(w['hold_wrench_by_source'][f'skin{i}']['mean_torque_Nm'][2]<0 for i in range(3)))
if __name__=='__main__':unittest.main()
