import json,unittest
from analyse import BASE
from contact_layer_union import exterior
def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class ContactLayerTests(unittest.TestCase):
 def test_reinforcement_contacts_are_skin_tip_not_backing(self):
  d=result('proximal_reinforcement_material1378');self.assertEqual(d['mapped_material_station_span_mm'],[100,100]);self.assertEqual(len(d['records']),9);self.assertTrue(all(r['material_label']=='Skin' for r in d['records']));self.assertEqual(d['unmapped_active_rows'],[])
 def test_reinforcement_readonly_purity(self):
  d=result('proximal_reinforcement_provenance1374');self.assertEqual(d['status'],'PASS_READ_ONLY_PREFIX');self.assertEqual(len(d['exact_record_equality']),9);self.assertTrue(all(d['exact_record_equality'].values()))
 def test_reinforcement_asymmetric_comparison_not_assumed_uniform(self):
  d=result('proximal_reinforcement_compare1376');self.assertFalse(d['all_three_endpoint_tip_angles_worse']);self.assertFalse(d['all_three_endpoint_tip_angles_better']);self.assertEqual(len(d['records']),6);self.assertEqual(result('proximal_reinforcement_compare1375')['status'],'FAIL_ANALYSIS_ASSERTION')
 def test_reinforcement_added_mass_not_equal_volume(self):
  d=result('proximal_reinforcement_geometry1364');self.assertEqual(d['interface_triangles_cancelled'],56);self.assertTrue(all(r['mass_kg']>0 and r['unchanged_guide_anchors']==36 for r in d['records']))
 def test_reinforcement_independent_coupon(self):
  d=result('proximal_reinforcement_coupon1365');self.assertLessEqual(d['max_velocity_reference_error_m_s'],1e-12);self.assertLessEqual(d['max_position_reference_error_m'],1e-12)
 def test_reinforcement_graph_and_valid_entry_not_holding(self):
  self.assertTrue(result('proximal_reinforcement_audit1368')['original_physical_graph_equal_after_declared_collision_and_observer_changes'])
  d=result('proximal_reinforcement_entry1369');self.assertEqual(d['outputs'],[[240,240]]*3);self.assertEqual(d['maximum_bond_position_error_m'],0);self.assertTrue(all(r['minimum_saved_volume_ratio']>0 for r in d['qualities']));self.assertEqual(d['holding'],'NOT MEASURED')
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
 def test_proximal_candidate_preserves_real_anchors_or_rejects(self):
  d=result('proximal_rail_footprint_gate1362');self.assertEqual(d['status'],'REJECT_FIXED_ANCHOR_RAIL_REDISTRIBUTION');self.assertEqual(d['anchors_checked'],108);self.assertEqual(d['anchors_outside'],12);self.assertEqual(d['candidate']['original_nominal_one_rail_volume_mm3'],d['candidate']['candidate_nominal_one_rail_volume_mm3']);self.assertTrue(all(r['original_rail_inner_margin_mm']>=0 for r in d['records']))
if __name__=='__main__':unittest.main()
