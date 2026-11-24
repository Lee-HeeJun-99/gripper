import json,unittest
from analyse import BASE
from contact_layer_union import exterior
def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class ContactLayerTests(unittest.TestCase):
 def test_finite_geometry(self):
  d=result('b3_contact_layer_geometry1336');self.assertEqual(d['status'],'PASS_LIMITED_INITIAL_GEOMETRY')
  self.assertTrue(all(r['minimum_initial_pad_object_gap_m']>.0002 and r['mass_kg']>0 for r in d['records']))
 def test_exact_internal_interface_cancellation(self):
  mesh=json.loads((BASE/'results/b3_railback_grasp1001298/mesh.json').read_text());g=json.loads((BASE/'results/b3_contact_layer_geometry1336/mesh.json').read_text());d=exterior(mesh,g)
  self.assertEqual(d['interface_triangles_cancelled'],24);self.assertEqual(d['original_exterior_retained'],d['original_exterior_triangles']-24);self.assertEqual(d['new_layer_exterior_triangles'],52);self.assertEqual(d['closed_edge_incidence'],2)
 def test_linear_reference_and_perfect_bond(self):
  d=result('contact_layer_linear_coupon1338');self.assertEqual(d['status'],'PASS_LINEAR_MAPPED_COUPON_ONLY');self.assertLessEqual(d['max_velocity_reference_error_m_s'],1e-12);self.assertEqual(d['max_position_reference_error_m'],0)
 def test_failed_full_contact_not_promoted(self):
  d=result('b3_contact_layer_pilot1337');self.assertEqual(d['status'],'FAIL_EXECUTION_ELEMENTS_OR_BOND');self.assertEqual(d['process']['exit_code'],-6);self.assertEqual(d['outputs'],[[0,0]]*3)
 def test_no_contact_control_not_grasp(self):
  d=result('b3_contact_layer_no_contact1343');self.assertEqual(d['status'],'BOUNDED_EXECUTION_ONLY');self.assertEqual(d['maximum_bond_position_error_m'],0);self.assertEqual(d['holding'],'NOT MEASURED')
 def test_earlier_phase_observer_purity(self):
  d=result('contact_layer_phase_control1345');self.assertEqual(d['status'],'PASS_ONE_STEP_OBSERVER_PURITY');self.assertTrue(all(d['baseline_one_step_exact'].values()));self.assertEqual(len(d['baseline_one_step_exact']),9)
 def test_vtu_precision_not_state_api(self):
  d=result('contact_layer_initial_assess1349');self.assertEqual(d['status'],'PASS_QUANTIZED_INITIAL_EXPORT_DIAGNOSTIC_ONLY');self.assertEqual(d['strict_API_identity'],'NOT MEASURED_BY_VTU');self.assertTrue(all(r['max_absolute_q_error_m']>1e-12 for r in d['records']))
 def test_all_modeled_initial_parts(self):
  d=result('contact_layer_initial_clearance1350');self.assertEqual(d['status'],'PASS_MODELED_INITIAL_NEW_PART_SEPARATION');self.assertTrue(all(r['minimum_all_wire_segment_AABB_capsule_lower_bound_m']>0 for r in d['records']))
 def test_union_dynamic_elements_and_bond(self):
  d=result('b3_contact_layer_union_withdraw1352');self.assertEqual(d['outputs'],[[480,480]]*3);self.assertEqual(d['maximum_bond_position_error_m'],0);self.assertTrue(all(r['minimum_saved_volume_ratio']>0 for r in d['qualities']));self.assertEqual(d['holding'],'NOT MEASURED')
 def test_composite_point_provenance_not_distributed(self):
  d=result('contact_layer_material1355');self.assertEqual(d['status'],'PASS_COMPOSITE_MATERIAL_PROVENANCE_ONLY');self.assertEqual(d['mapped_material_station_span_mm'],[100,100]);self.assertEqual(d['unmapped_active_rows'],[]);self.assertTrue(all(r['material_label']=='layer' for r in d['records']))
 def test_momentum_is_not_bare_skin_holding(self):
  d=result('contact_layer_response1357');self.assertLess(d['linear_momentum_max_residual_Ns'],1e-12);self.assertLess(d['response_partition_max_error_Ns_Nms'],1e-12);self.assertLess(d['endpoint']['composite_Fz_N'],d['weight_N']);self.assertGreater(d['endpoint']['support_Fz_N'],1e-5)
 def test_profile_rays_preserve_limitation(self):
  d=result('contact_layer_profile_rays1358');self.assertEqual(len(d['records']),40);self.assertEqual(sum(r['frozen_profile_within_initial_budget'] is False for r in d['records']),30);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_proximal_rotation_is_diagnostic(self):
  d=result('contact_layer_segment_rotation1360');r=[r for r in d['records'] if r['case']=='b3_contact_layer_union_withdraw1352' and r['finger']==0 and not r['reference']];a,b=r;self.assertGreater(abs((b['proximal_signed_turn_deg']-a['proximal_signed_turn_deg'])/(b['tip_segment_angle_deg']-a['tip_segment_angle_deg'])),.8);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
