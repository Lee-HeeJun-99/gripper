"""Dual drum and catalog drive CAD guards,not physical qualification."""
import json,math,unittest
import numpy as np
import trimesh
from manufacturing_assembly import BASE
from assembly_recipe_io import resolve_recipe
from drum_rotation_envelope import rotation_bound

def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())

class DualDrumTests(unittest.TestCase):
 def test_c1_independent_channel_retains_c0_and_all_other_parts(self):
  d=result('product_drum_second_channel1041');self.assertEqual(d['target_cable'],1);self.assertEqual(d['candidate_part_count'],300)
  self.assertFalse(d['solid_intersections']);parts,_=resolve_recipe(BASE/'results/product_drum_second_channel1041/assembly_delta_recipe.json');names={p['name'] for p in parts}
  self.assertTrue(all(f'f0_c{c}_drum_{s}' in names for c in (0,1) for s in ('pressure_pad','adjuster_M1p6','nut_M1p6')))
 def test_c1_actual_source_and_service_direction_not_c0_mirror_assumption(self):
  d=result('product_drum_second_service1042');self.assertEqual(d['target_cable'],1)
  self.assertIn('results/product_supplier_second_full_wire887/summary.json',d['input_hashes'])
  self.assertEqual(d['free_end_reference_route_mm'],[[50,0,59.25],[50,6,59.25]])
  self.assertFalse(any(r['intersections'] for r in d['service_records']+d['free_end_wire_records']))
  self.assertEqual(d['service_records'][-1]['translation_Y_mm'],10)
 def test_rotation_bound_circumscribed_not_inscribed_polygon(self):
  m=trimesh.creation.box(extents=[2,4,6]);shape,b=rotation_bound([m],[0,0],128)
  self.assertAlmostEqual(b['maximum_source_vertex_radius_mm'],math.sqrt(5))
  self.assertAlmostEqual(shape['radius']*math.cos(math.pi/128),math.sqrt(5))
  self.assertEqual(b['envelope_Z_mm'],[-3,3])
  with self.assertRaises(ValueError):rotation_bound([m],[float('nan'),0])
 def test_actual_full_turn_bound_not_wire_or_native_motion(self):
  d=result('product_drum_rotation1043');self.assertEqual(len(d['moving_names']),7);self.assertEqual(len(d['fixed_names']),293)
  self.assertFalse(d['solid_intersections']);self.assertFalse(d['physical_dynamic_clearance_qualified']);self.assertFalse(d['actual_motor_axis_qualified'])
 def test_catalog_data_has_no_invented_tolerance_torque_or_mass(self):
  d=json.loads((BASE/'config/root_retaining_screw_v61.json').read_text())
  self.assertEqual(d['nominal_socket_AF_mm'],2.5);self.assertEqual(d['catalog_drive_depth_mm'],1.3)
  self.assertIsNone(d['socket_tolerance_mm']);self.assertIsNone(d['assembly_torque_Nm']);self.assertIsNone(d['actual_mass_kg'])
 def test_own_indexed_drive_contact_faces_kept_review(self):
  d=result('product_root_catalog_drive1045');self.assertEqual(d['candidate_part_count'],300)
  self.assertEqual(d['status'],'CATALOG_ROOT_DRIVE_GEOMETRY_REVIEW');self.assertEqual(len(d['records']),6)
  self.assertFalse(any(r['indexed_shank_vs_other_hardware'] for r in d['records']))
  self.assertTrue(all(r['indexed_shank_vs_own_drive'] for r in d['records']))
  self.assertTrue(all(r['actual_purchased_drive_fit'] is None for r in d['records']))
 def test_candidate_presence_does_not_automatically_execute_service(self):
  d=result('product_current_service_plan1046');self.assertIsNone(d['first_missing_mechanism']);self.assertEqual(len(d['candidate_mechanisms_present']),6)
  self.assertEqual(d['physical_steps_executed'],0);self.assertTrue(all(r['status']=='BLOCKED_NOT_PHYSICALLY_EXECUTED' for r in d['records']))
 def test_new_drum_physical_schema_has_no_fabricated_measurements(self):
  d=result('product_drum_joint_protocol1047');self.assertEqual(len(d['tests']),8);self.assertEqual(len(d['measurement_fields']),34)
  self.assertEqual(d['physical_tests_executed'],0);self.assertTrue(all(r['value'] is None and r['status']=='NOT MEASURED' for r in d['measurement_fields']))
 def test_latest_pack_uses_socket_candidate_not_old_proxy(self):
  d=result('product_root_socket_pack1049');self.assertEqual(d['source_case'],'product_root_catalog_drive1045')
  self.assertTrue(d['root_retaining_catalog_drive_present']);self.assertEqual(d['saved_STL_count'],13)
  self.assertFalse(d['STEP_generated']);self.assertFalse(d['fabrication_ready'])
