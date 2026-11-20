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
