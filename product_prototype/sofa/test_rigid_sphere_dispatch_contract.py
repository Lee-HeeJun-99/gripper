"""Regression against saved actual Native evidence; does not rerun physics."""
import json,unittest
from analyse import BASE
def load(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class DispatchContract(unittest.TestCase):
 def test_stock_equivalence_and_mesh_noop(self):
  d=load('rigid_sphere_dispatch_contract1581');self.assertEqual(d['status'],'PASS_NATIVE_DISPATCH_COUPONS_ONLY');self.assertEqual(len(d['records']),5)
  for r in d['records']:self.assertLessEqual(r['maximum_q_v_impulse_error_vs_stock_Min'],1e-12)
  self.assertEqual(d['mesh_only']['maximum_mesh_only_q_v_impulse_error_vs_stock_Local'],0)
 def test_radius_geometry_not_just_force_balance(self):
  r={x['policy']:x for x in load('mixed_sphere_gravity1582')['records']}
  for name in ('Min','Dispatch'):self.assertLessEqual(r[name]['maximum_rest_position_error_m'],1e-12);self.assertAlmostEqual(r[name]['mean_rest_contact_vertical_force_N'],.981,places=12)
  self.assertGreater(r['New']['maximum_rest_position_error_m'],.029);self.assertAlmostEqual(r['New']['mean_rest_contact_vertical_force_N'],.981,places=12)
 def test_pilot_not_unbraced_holding(self):
  self.assertEqual(load('dispatch_finite_hardware1583')['holding'],'NOT ASSESSED');self.assertGreater(load('dispatch_guide_pairs1585')['nonzero_rows'],0)
 def test_failed_load_evidence_retained(self):
  self.assertNotEqual(load('rigid_sphere_dispatch_contract1579')['status'],'PASS_NATIVE_DISPATCH_COUPONS_ONLY')
if __name__=='__main__':unittest.main()
