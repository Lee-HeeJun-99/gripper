"""Design/analysis regressions,NOT new physical product qualification Gates."""
import ast,csv,json,math,unittest
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,box,cyl,cut,root_frame,load_design
from generate import world,reference_local
from drive_requirements import requirement
from prototype_protocol import validate_measurement,measurement_unit
from wire_bore_audit import radial_extent

def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
def design(name):return json.loads((BASE/'meshes'/name/'assembly_recipe.json').read_text())
def overlaps(name):return json.loads((BASE/'meshes'/name/'checks.json').read_text())['interference']['positive_overlaps']

class ManufacturingTests(unittest.TestCase):
 def test_root_mount_retention_failure_and_new_boss_service_are_separate(self):
  before=result('product_root_mount785');self.assertEqual(len(before['records']),18);self.assertFalse(before['wire_intersections']);self.assertEqual(len(before['solid_intersections']),6);self.assertTrue(all(h['volume_mm3']==0 for h in before['solid_intersections']))
  old=result('product_root_retention786');self.assertTrue(all(r['nut_tool_intersections'] for r in old['records']));self.assertFalse(any(r['swept_intersections'] for r in old['records']))
  self.assertTrue(result('product_root_boss787')['status'].startswith('FAIL'))
  new=result('product_root_canonical788');self.assertTrue(new['canonical_sector']);self.assertEqual(len(new['records']),12);self.assertEqual(new['full_part_count'],292);self.assertFalse(new['fabrication_ready']);self.assertFalse(new['wire_intersections'])
  service=result('product_root_boss_service791');self.assertTrue(service['threaded_boss']);self.assertFalse(any(r['swept_intersections'] or r['tool_intersections'] for r in service['records']))
  self.assertTrue(all(r['sufficient_exclusion'] for r in result('product_root_boss_palm792')['records']))
 def test_root_motion_bound_includes_finite_wire_radius_and_old_state_scope(self):
  from root_motion_alignment import tangent,side_envelope
  t=tangent(np.array([4.,0]),2.,np.array([1.,2.]));self.assertAlmostEqual(t@t,4);self.assertAlmostEqual(t@(t-[4,0]),0.)
  self.assertAlmostEqual(side_envelope(np.array([4.,0,0]),t),.25)
  with self.assertRaises(ValueError):tangent(np.array([1.,0]),2.,np.array([1.,2.]))
  d=result('product_root_motion793');self.assertEqual(d['centreline_radial_screen_mm'],d['flange_outer_radius_mm']+d['wire_radius_mm']);self.assertEqual(sum(r['saved_frames'] for r in d['records']),7200);self.assertTrue(all(r['worst']['axial_bound_mm']<.4 for r in d['records']));self.assertIn('OLD_MOTION',d['status']);self.assertFalse(d['fabrication_ready'])
 def test_root_service_keeps_inward_failure_and_outboard_sweep_scope(self):
  old=result('product_root_service782');self.assertEqual(sum(bool(r['intersections']) for r in old['records']),6)
  new=result('product_root_outboard783');self.assertTrue(new['conservative_linear_swept_volume']);self.assertEqual(len(new['records']),6);self.assertFalse(any(r['intersections'] for r in new['records']));self.assertFalse(new['fabrication_ready'])
  self.assertTrue(all(r['axis_sign']==(1 if '_c0_' in r['pin'] else -1) for r in new['records']))
 def test_root_redirect_preserves_contact_review_and_new_path_origin(self):
  d=result('product_root_redirect778');self.assertEqual(len(d['records']),6);self.assertFalse(d['solid_intersections']);self.assertTrue(all(r['wire_intersections'] for r in d['records']));self.assertFalse(d['fabrication_ready'])
  for r in d['records']:
   self.assertAlmostEqual(r['turn_angle_deg'],76.);self.assertAlmostEqual(r['path_length_change_mm'],-.47227571452119)
  ref=result('product_root_reference779');self.assertEqual(ref['degenerate_cases_rejected'],2);self.assertTrue(ref['right_angle_reference'])
  self.assertTrue(all(r['arc_radius_max_abs_error_mm']<1e-13 for r in ref['records']));self.assertTrue(all(r['mount_reaction_N'] is None for r in ref['records']))
 def test_root_corner_rejects_undefined_geometry(self):
  from root_redirect_candidate import corner_frame
  for a,b,c,r in (([0,0,0],[0,0,0],[1,0,0],2),([0,0,0],[1,0,0],[2,0,0],2),([0,0,0],[1,0,0],[1,1,0],0)):
   with self.assertRaises(ValueError):corner_frame(np.array(a,dtype=float),np.array(b,dtype=float),np.array(c,dtype=float),r)
 def test_bridge_size_and_stiffness_remain_unqualified_tradeoffs(self):
  d=result('product_bridge_review774');self.assertEqual(d['part_instances'],280);self.assertGreater(d['new_maximum_radial_extent_mm'],d['baseline_maximum_radial_extent_mm']);self.assertFalse(d['fabrication_ready'])
  e=result('product_bridge_stiffness776');self.assertIsNone(e['actual_material_modulus_MPa']);self.assertIsNone(e['actual_frame_displacement_mm']);r=e['records'];self.assertGreater(r[0]['deflection_divided_by_length'],.5);self.assertGreater(r[0]['ideal_EB_tip_deflection_mm'],r[-1]['ideal_EB_tip_deflection_mm'])
 def test_CAD_renderer_honors_candidate_title_and_part_count(self):
  from unittest.mock import patch
  from release_pack import render
  with patch('matplotlib.axes.Axes.set_title',autospec=True) as title,patch('matplotlib.figure.Figure.text',autospec=True) as footer,patch('matplotlib.figure.Figure.savefig',autospec=True):
   render([dict(group='finger')],[evaluate(box([0,0,0],[1,1,1]))],'/tmp/regrip_mock_no_file.png',title='CUSTOM_BRIDGE',footer='280_PART_PROXIES')
   self.assertEqual(title.call_args.args[1],'CUSTOM_BRIDGE');self.assertEqual(footer.call_args.args[3],'280_PART_PROXIES')
 def test_revised_bridge_retains_full_service_distances(self):
  d=result('product_bridge_service767');self.assertTrue(d['dependencies_unchanged']);self.assertFalse(d['analysis']['wire_intersections']);self.assertEqual(len(d['analysis']['records']),67)
  service=result('product_bridge_service768');self.assertEqual(len(service['pin_withdrawal_samples']),54);self.assertEqual(max(r['negative_axis_withdrawal_mm'] for r in service['pin_withdrawal_samples']),10);self.assertFalse(any(r['intersections'] for r in service['pin_withdrawal_samples']));self.assertFalse(any(r['intersections'] for r in service['mount_driver_access']))
  self.assertTrue(all(r['all_bits_exclude_palm_open_interior'] for r in result('product_bridge_service_mating769')['records']))
 def test_axial_stack_and_real_shims_do_not_claim_tolerance_or_friction_PASS(self):
  from pulley_stack_budget import stack
  self.assertFalse(stack(0.)['strict_nonbinding_and_alignment']);self.assertTrue(stack(.4)['strict_nonbinding_and_alignment']);self.assertFalse(stack(.4,.05,.05,.02)['strict_nonbinding_and_alignment'])
  d=result('product_thrust_shims771');self.assertEqual(len(d['records']),36);self.assertFalse(d['wire_intersections']);self.assertTrue(d['intersections']);self.assertFalse(d['fabrication_ready'])
 def test_bridge_failures_are_preserved_and_not_upgraded(self):
  direct=result('product_bridge_direct761');self.assertTrue(direct['wire_intersections']);self.assertTrue(direct['nonempty_solid_intersections'])
  self.assertTrue(result('product_bridge_tower762')['status'].startswith('FAIL'))
  before=result('product_bridge_connected763');self.assertTrue(before['wire_intersections'])
  new=result('product_bridge_backroute764');self.assertTrue(new['dependencies_unchanged']);self.assertEqual(new['status'],'REFERENCE_GEOMETRY_INTERSECTIONS_REMAIN');self.assertFalse(new['analysis']['wire_intersections']);self.assertEqual(len(new['analysis']['nonempty_solid_intersections']),6)
 def test_nominal_mating_proof_does_not_hide_service_failure(self):
  d=result('product_bridge_mating766');self.assertEqual(len(d['records']),6);self.assertTrue(all(r['all_bits_exclude_palm_open_interior'] for r in d['records']))
  service=result('product_bridge_assembly765');self.assertFalse(any(r['intersections'] for r in service['hole_gauges']));self.assertFalse(any(r['intersections'] for r in service['mount_driver_access']));self.assertEqual(sum(bool(r['intersections']) for r in service['pin_withdrawal_samples']),3)
 def test_all_finite_drive_module_pairs_checked_without_assembly_upgrade(self):
  d=result('product_drive_modules759');self.assertEqual(d['module_count'],54);self.assertEqual(d['possible_pairs'],1431);self.assertEqual(len(d['actual_STL_readbacks']),54);self.assertFalse(d['nonempty_intersections']);self.assertFalse(d['full_drive_assembly'])
 def test_pulley_force_budget_is_idealized_and_does_not_select_material(self):
  from pulley_load_budget import budget
  r=budget(1.5,math.pi/2,1.,1.,3.,5.,2.8,1.);self.assertAlmostEqual(r['conditional_turn_load_N'],1.5*math.sqrt(2));self.assertAlmostEqual(r['double_shear_pin_average_MPa'],r['conditional_turn_load_N']/(math.pi/2))
  self.assertIsNone(result('product_pulley_budget757')['approved_material'])
  with self.assertRaises(ValueError):budget(1.5,0,1.,1.,3.,5.,2.8,1.)
 def test_event_worst_finite_hardware_is_sampled_not_CCD(self):
  d=result('product_event_hardware753');self.assertTrue(d['dependencies_unchanged']);a=d['analysis'];self.assertEqual(len(a['selected_times_s']),22);self.assertEqual(len(a['records']),132);self.assertTrue(a['hardware_pair_check']);self.assertFalse(a['interfinger_hardware_intersections']);self.assertFalse(any(r.get('intersections') for r in a['records']))
 def test_forks_and_pins_are_finite_but_not_mounted_drive(self):
  d=result('product_pulley_fork754');self.assertEqual(len(d['records']),36);self.assertFalse(d['solid_intersections']);self.assertFalse(d['wire_envelope_intersections']);self.assertEqual(d['pin_diameter_mm'],1.);self.assertEqual(d['fork_bore_mm'],1.2);self.assertFalse(d['fabrication_ready']);self.assertIn('NOT_MOUNTED',d['status'])
 def test_motor_lead_in_keeps_intended_drum_contact_and_rejects_direct_route(self):
  d=result('product_motor_lead748');direct=[r for r in d['records'] if r['model']=='direct_unrouted_diagnostic'];perimeter=[r for r in d['records'] if r['model']=='perimeter_rounded_candidate'];self.assertEqual(len(direct),6);self.assertEqual(len(perimeter),6)
  self.assertTrue(any(h['classification']=='UNRESOLVED_OBSTACLE' for r in direct for h in r['intersections']));self.assertFalse(any(h['classification']=='UNRESOLVED_OBSTACLE' for r in perimeter for h in r['intersections']));self.assertTrue(any(r['intersections'] for r in perimeter));self.assertIsNone(d['wire_supplier_minimum_radius_mm'])
 def test_finite_turn_wheel_is_closed_and_matches_polygon_volume(self):
  from lead_pulley_candidate import wheel_recipe
  s=evaluate(wheel_recipe());expected=32*math.sin(2*math.pi/64)*(.8*(1.75**2-.6**2)+(3.**2-.6**2))
  self.assertLess(abs(s.volume-expected)/expected,2e-7)
  d=result('product_pulley751');self.assertEqual(len(d['records']),18);self.assertTrue(all(r['watertight_readback'] for r in d['records']));self.assertFalse(d['fabrication_ready']);self.assertIsNone(d['supplier_minimum_bend_radius_mm'])
 def test_sphere_gap_has_analytic_segment_reference_and_rejects_zero_path(self):
  from deformed_wire_screen import segment_sphere_gap
  route=np.array([[-2.,0,0],[2.,0,0]])
  self.assertAlmostEqual(segment_sphere_gap(route,np.array([0.,3,0]),1.,.25,.01),1.74)
  with self.assertRaises(ValueError):segment_sphere_gap(np.zeros((2,3)),np.zeros(3),1.,.25,0.)
 def test_all_saved_object_frames_not_continuous_or_full_hardware(self):
  d=result('product_wire_object_all746');self.assertTrue(d['object_only_all_frames']);self.assertFalse(d['film_included']);self.assertEqual(len(d['records']),7200);self.assertEqual(len(d['selected_times_s']),1200);self.assertTrue(all(r['sphere_gap_lower_bound_mm']>0 for r in d['records']))
 def test_frozen_source_deformed_worker_retains_identity(self):
  d=result('product_deformed_frozen747');self.assertTrue(d['dependencies_unchanged']);self.assertEqual(d['process']['exit_code'],0);self.assertEqual(d['executed_worker_sha256'],d['analysis']['producer_sha256']);self.assertTrue(d['analysis']['film_included']);self.assertEqual(len(d['analysis']['deformed_surface_quality']),24)
 def test_frozen_native_bore_replay_is_not_candidate_dynamics(self):
  d=result('product_wire_replay742');self.assertIn('NOT_CANDIDATE_DYNAMICS',d['status']);self.assertEqual(len(d['records']),36);self.assertFalse(any(r['failed_frames'] for r in d['records']));self.assertLess(max(r['maximum_required_bore_radius_mm'] for r in d['records']),.7)
 def test_circular_fillet_reference_and_overlap_rejection(self):
  from rounded_wire_path import fillet
  p=np.array([[0.,0,0],[10.,0,0],[10.,10,0]]);q,s,t=fillet(p,2.)
  self.assertAlmostEqual(t[0],2.);self.assertTrue(np.allclose(q[1],[8,0,0]));self.assertTrue(np.allclose(q[-2],[10,2,0]));self.assertGreater(s,0.)
  for point in q[1:-1]:self.assertAlmostEqual(np.linalg.norm(point-[8,2,0]),2.)
  with self.assertRaises(ValueError):fillet(p,6.)
 def test_full_reference_wire_and_new_service_not_complete_qualification(self):
  full=result('product_wire_full736')['full_assembly'][0];self.assertEqual(full['segments'],36);self.assertEqual(full['nonempty_intersections'],[])
  service=result('product_bore_service732');self.assertEqual(len(service['records']),12);self.assertFalse(any(r['positive_intersections'] for r in service['records']))
  self.assertEqual(len(result('product_bore_stl734')['records']),160)
  self.assertTrue(result('product_drive_gate737')['qualification']['status'].startswith('BLOCKED'));self.assertIsNone(result('product_drive_gate737')['qualification']['motor_selected'])
 def test_axis_then_bore_are_separate_and_do_not_certify_moving_wire(self):
  a,b=result('product_wire_solid731')['candidates'];self.assertEqual(a['necessary_condition_failures'],6);self.assertGreater(a['positive_solid_intersections'],0);self.assertEqual(b['necessary_condition_failures'],0);self.assertEqual(b['positive_solid_intersections'],0)
  self.assertIsNone(result('product_wire_solid731')['minimum_bend_radius_mm'])
  old=design('b3_manufacturing_service_v19');new=design('b3_manufacturing_bore_v21')
  self.assertEqual(old['baseline_config']['tendon']['guide_hole_radius'],.6);self.assertEqual(new['baseline_config']['tendon']['guide_hole_radius'],.7)
  for p,q in zip(old['parts'],new['parts']):
   if p['group'] not in ('eyelet',):self.assertEqual(p,q)
 def test_service_slot_fixes_detected_sampled_removal_not_CCD(self):
  old=result('product_cartridge_service717');new=result('product_cartridge_service721');self.assertEqual(sum(bool(r['positive_intersections']) for r in old['records']),3);self.assertEqual(len(new['records']),12);self.assertFalse(any(r['positive_intersections'] for r in new['records']));self.assertIn('NOT_SWEPT',new['status'])
 def test_finite_bore_condition_exposes_unmodeled_wire_conflict(self):
  self.assertAlmostEqual(radial_extent([1,0,0],[1,0,0],1,.25),.25);self.assertAlmostEqual(radial_extent([1,0,0],[1,1,0],1,.25),1+.25*math.sqrt(2))
  d=result('product_wire_bore723');self.assertEqual(sum(r['status'].startswith('FAIL') for r in d['records'] if r['axis_model']=='existing_manufactured_tangent'),12);self.assertIsNone(d['physical_wire_minimum_bend_radius_mm'])
 def test_final_STLs_are_closed_positive_NOT_strength_or_STEP(self):
  root=BASE/'meshes/b3_manufacturing_service_v19_stl_ascii';data=result('product_stl_roundtrip726');self.assertEqual(len(data['records']),160)
  for p in data['records']:
   shape=trimesh.load_mesh(root/(p['part']+'.stl'));self.assertTrue(shape.is_watertight);self.assertGreater(shape.volume,0.);self.assertEqual(shape.body_count,1)
  self.assertEqual(sum(not r['original_saved_STL_watertight'] for r in data['records']),3);self.assertFalse(data['fabrication_ready']);self.assertIn('CHANGES',data['scope'])
 def test_failed_topology_attempt_and_numeric_representation_scope_preserved(self):
  self.assertEqual(result('product_manufacturing_regression724')['status'],'FAIL_DESIGN_REGRESSION');self.assertIn('FAIL',result('product_stl_roundtrip725')['status']);d=json.loads((BASE/'drawings/b3_manufacturing_service_v19_stl_ascii/QUALIFICATION_SCOPE_CORRECTION.json').read_text());self.assertFalse(d['digital_geometry_identity_verified'])
 def test_primitive_box_exact_volume(self):self.assertEqual(evaluate(box([0,0,0],[2,3,4])).volume,24.)
 def test_mesh_annulus_matches_polygon_reference(self):
  m=evaluate(cut(cyl(3,0,2),cyl(1,-1,3)));expected=64*math.sin(2*math.pi/64)*(9-1)
  self.assertLess(abs(m.volume-expected)/expected,2e-7) # numerical mesh check,NOT physical Gate
 def test_root_frame_is_proper_and_matches_shared_curved_geometry(self):
  cfg=design('b3_manufacturing_spotface_v18')['baseline_config']
  for angle in cfg['palm']['angles_deg']:
   m=root_frame(cfg,angle);np.testing.assert_allclose(m[:3,:3].T@m[:3,:3],np.eye(3),atol=1e-12,rtol=0);self.assertAlmostEqual(np.linalg.det(m[:3,:3]),1.)
   for p in ([7,3,-.5],[90,0,0]):np.testing.assert_allclose((m@np.r_[reference_local(cfg,p),1])[:3],world(cfg,p,angle),atol=1e-12,rtol=0)
 def test_all_manufacturing_revisions_preserve_B3_finger_geometry(self):
  names=['b3_manufacturing_v12','b3_manufacturing_saddle_v13','b3_manufacturing_mount_v14','b3_manufacturing_holes_v15','b3_manufacturing_fasteners_v16','b3_manufacturing_access_v17','b3_manufacturing_spotface_v18','b3_manufacturing_service_v19'];reference=None
  for name in names:
   parts={p['name']:p['shape'] for p in design(name)['parts'] if p['group']=='finger'}
   if reference is None:reference=parts
   self.assertEqual(reference,parts);self.assertEqual(len(parts),9)
 def test_support_saddle_removes_detected_rail_volume_overlap(self):
  relevant=lambda name:[r for r in overlaps(name) if any('_rail_' in p for p in r['parts']) and any(p.endswith('_support') for p in r['parts'])]
  self.assertEqual(len(relevant('b3_manufacturing_v12')),36);self.assertEqual(relevant('b3_manufacturing_saddle_v13'),[])
 def test_shorter_mount_removes_first_support_interference(self):
  relevant=lambda name:[r for r in overlaps(name) if any(p.endswith('_mount') for p in r['parts']) and any(p.endswith('_support') for p in r['parts'])]
  self.assertEqual(len(relevant('b3_manufacturing_saddle_v13')),6);self.assertEqual(relevant('b3_manufacturing_mount_v14'),[])
 def test_world_contact_seam_artifacts_not_promoted_to_clearance_pass(self):
  rows=result('product_interface_audit708')['seams'];self.assertGreater(max(r['world_frame_intersection_mm3'] for r in rows),1e-5);self.assertLess(max(abs(r['common_root_frame_intersection_mm3']) for r in rows),1e-10);self.assertFalse(result('product_interface_audit708')['BRep_clearance_verified'])
 def test_missing_palm_holes_are_independently_detected_and_fixed(self):
  self.assertEqual(sum(h['status']=='BLOCKED_PALM_HOLE' for h in result('product_interface_audit708')['deck_hole_gauges']),6)
  self.assertTrue(all(h['status']=='MESH_HOLE_PASSAGE_SCOPE_ONLY' for h in result('product_fastener_hole_audit711')['deck_hole_gauges']))
 def test_adding_actual_fastener_envelopes_exposes_old_conflicts(self):
  self.assertTrue(any(r['volume_mm3']>50 for r in overlaps('b3_manufacturing_fasteners_v16') if 'UNRESOLVED' in r['classification']))
 def test_access_revision_removes_large_fastener_crossings(self):
  rows=[r for r in overlaps('b3_manufacturing_access_v17') if 'UNRESOLVED' in r['classification']];self.assertTrue(rows);self.assertLess(max(r['volume_mm3'] for r in rows),.008)
 def test_spotface_removes_real_head_lip_not_by_tolerance_change(self):
  old=[r for r in overlaps('b3_manufacturing_access_v17') if any('_retaining_bolt_' in p for p in r['parts'])];new=[r for r in overlaps('b3_manufacturing_spotface_v18') if any('_retaining_bolt_' in p for p in r['parts'])]
  self.assertGreater(max(r['volume_mm3'] for r in old),.007);self.assertLess(max(r['volume_mm3'] for r in new),4e-6)
 def test_final_candidate_keeps_seam_and_invalid_kernel_evidence(self):
  d=json.loads((BASE/'meshes/b3_manufacturing_spotface_v18/checks.json').read_text());self.assertTrue(d['interference']['invalid_or_boundary_kernel_results']);self.assertFalse(d['fabrication_ready']);self.assertFalse(d['STEP_generated'])
 def test_BOM_counts_actual_instances_without_duplicate_mount_and_deck_bolts(self):
  pack=result('product_release_pack715');self.assertEqual(pack['CAD_instances'],160);self.assertEqual(pack['fastener_proxy_instances'],48)
  with (BASE/'drawings/b3_manufacturing_spotface_v18/REGRIP_BOM.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len([r for r in rows if r['group']!='NOT_MODELED']),160);self.assertEqual(len([r for r in rows if 'deck_bolt_' in r['CAD_instance']]),12)
 def test_driver_approach_limit_is_not_hidden(self):
  pack=result('product_release_pack715');self.assertEqual(len(pack['driver_shank_checks']),24);self.assertEqual(sum(bool(t['intersections']) for t in pack['driver_shank_checks']),6);self.assertFalse(pack['fabrication_ready'])
 def test_conditional_torque_work_and_speed_units(self):
  r=requirement(1.5,4,8,.5,.5,2);self.assertAlmostEqual(r['conditional_design_torque_Nm'],.096);self.assertAlmostEqual(r['cable_work_constant_tension_J'],.012);self.assertAlmostEqual(r['drum_turns'],4/(16*math.pi));self.assertIsNone(r['minimum_additional_gear_ratio'])
 def test_catalog_stall_not_continuous_rating(self):
  d=result('product_drive707');self.assertEqual(len(d['scenarios']),36);self.assertIsNone(d['motor_selected']);self.assertIsNone(d['measured_required_stroke_mm'])
  for s in d['scenarios']:
   for m in s['motor_screening']:self.assertEqual(m['continuous_operation_verdict'],'BLOCKED_NOT_MEASURED')
 def test_actual_old_stroke_recomputed_not_command(self):
  rows=result('product_drive707')['actual_old_SOFA_stroke'];self.assertEqual(len(rows),6);self.assertGreater(min(r['maximum_geometric_shortening_mm'] for r in rows),2.6);self.assertLess(max(r['maximum_geometric_shortening_mm'] for r in rows),3.);self.assertGreater(max(r['maximum_internal_vs_geometric_difference_mm'] for r in rows),.1)
 def test_freecad_source_syntax_is_not_kernel_execution(self):
  ast.parse((BASE/'cad/export_recipe_freecad.py').read_text());self.assertFalse(result('product_release_pack715')['STEP_generated'])
 def test_prototype_template_values_remain_null(self):
  d=result('product_prototype_protocol718');self.assertEqual(d['physical_tests_executed'],0);self.assertEqual(len(d['tests']),10)
  for field in d['measurement_fields']:self.assertIsNone(field['value']);self.assertTrue(validate_measurement(field))
 def test_correct_physical_measurement_units(self):
  self.assertEqual(measurement_unit('object_speed_mm_s'),'mm/s');self.assertEqual(measurement_unit('distributed_curvature_per_mm'),'1/mm');self.assertEqual(measurement_unit('skin_load_fraction'),'1')
  old=result('product_prototype_protocol716');self.assertTrue(any(f['metric']=='object_speed_mm_s' and f['units']=='s' for f in old['measurement_fields'])) # preserved draft schema defect,NOT measured physical data
 def test_simulation_cannot_be_physical_measurement(self):
  with self.assertRaises(ValueError):validate_measurement(dict(status='MEASURED',origin='SIMULATION',value=1))
  with self.assertRaises(ValueError):validate_measurement(dict(status='PASS',origin='PHYSICAL',value=1))
  with self.assertRaises(ValueError):validate_measurement(dict(status='NOT MEASURED',value=0))
 def test_multistep_is_not_a_new_constrained_integration_contract(self):
  d=result('b3_native_multistep_contract713');self.assertEqual(d['records'][0]['status'],'PASS_FREE_ODE_SCOPE_ONLY');self.assertEqual(d['records'][1]['status'],'FAIL_CABLE_INTEGRATION_CONTRACT');self.assertTrue(d['records'][1]['actual_positions_and_velocities_identically_zero'])
if __name__=='__main__':unittest.main()
