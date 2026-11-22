import json,unittest
from manufacturing_assembly import BASE,sha
from termination_contract import fit
from termination_installation import threading
from motor_interface_gate import missing_dimensions
from distal_web_section import line_intervals

def case(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class TerminationTests(unittest.TestCase):
 def test_explicit_basal_geometry_not_material_tuning(self):
  old=case('product_distal_seat992');new=case('product_distal_basal1000')
  self.assertIsNotNone(new['design_basal_web_local_box_mm']);self.assertEqual(new['candidate_part_count'],289)
  before={r['part']:r['new_volume_mm3'] for r in old['support_changes']}
  self.assertTrue(all(r['new_volume_mm3']>before[r['part']] for r in new['support_changes']))
  self.assertEqual(len(new['solid_intersections']),6);self.assertTrue(all('eyelet' in r['parts'][1] for r in new['solid_intersections']));self.assertFalse(new['fabrication_ready'])
 def test_local_sections_are_not_global_strength(self):
  old=[r['total_Z_material_thickness_mm'] for r in case('product_distal_web999')['records'] if r['model']=='candidate']
  new=[r['total_Z_material_thickness_mm'] for r in case('product_distal_basal_section1001')['records'] if r['model']=='candidate']
  self.assertLess(min(old),.02);self.assertEqual(len(new),4);self.assertGreater(min(new),.94)
  self.assertIsNone(case('product_distal_basal_section1001')['actual_strength_N'])
 def test_basal_pack_actual_source_and_outputs(self):
  d=case('product_terminal_basal_pack1002');self.assertEqual(len(d['records']),18);self.assertFalse(d['STEP_generated'])
  self.assertIn('results/product_distal_basal1000/assembly_delta_recipe.json',d['input_hashes'])
  for name,digest in d['outputs'].items():self.assertEqual(sha(BASE/name),digest)
 def test_motor_family_does_not_qualify_fit(self):
  d=case('product_motor_interface1004');self.assertEqual(d['status'],'BLOCKED_MOTOR_DIMENSIONAL_INTERFACE');self.assertTrue(d['catalog_family_compatibility']);self.assertFalse(d['bore_to_horn_fit_qualified']);self.assertIsNone(d['actual_motor_test'])
  self.assertEqual(len(missing_dimensions({})),7)
 def test_section_cube_reference(self):
  import trimesh
  body=trimesh.creation.box(extents=[2,2,2]);self.assertEqual(line_intervals(body,0),[[-1.,1.]]);self.assertEqual(line_intervals(body,3),[])
 def test_catalog_rejects_drum_and_ball_retention(self):
  d=case('product_termination_actual997');r={x['item']:x for x in d['records']}
  self.assertTrue(all(not x['all_sizes_fit_channel'] for x in r.values()));self.assertGreater(r['NI000001']['minimum_retaining_radial_shoulder_mm'],.4);self.assertFalse(r['KU000016']['positive_shoulder_all_sizes'])
  self.assertTrue((BASE/'results/product_termination_contract988/CORRECTION.json').is_file())
 def test_failed_original_exit_not_hidden(self):
  d=case('product_distal_terminal989');h=[x for x in d['solid_intersections'] if 'support' in x['parts'][1]]
  self.assertEqual(len(h),6);self.assertTrue(all(x['signed_volume_mm3']>.68 for x in h))
  self.assertTrue(all(r['original_intersection_mm3']>2.13 for r in case('product_distal_interface991')['records']))
 def test_seat_remains_review_not_loadpath_pass(self):
  d=case('product_distal_seat992');self.assertEqual(d['candidate_part_count'],289);self.assertEqual(len(d['support_changes']),6);self.assertTrue(d['eyelet_seat_relief']);self.assertFalse(d['fabrication_ready'])
  self.assertEqual(len(d['solid_intersections']),6);self.assertTrue(all('eyelet' in r['parts'][1] for r in d['solid_intersections']))
 def test_mating_reference_does_not_delete_CSG(self):
  self.assertTrue(all(r['open_interiors_excluded'] for r in case('product_terminal_mating993')['records']))
  self.assertTrue(case('product_distal_seat992')['solid_intersections'])
 def test_partial_pack_and_actual_new_pack(self):
  self.assertEqual(case('product_terminal_pack994')['status'],'FAIL_SECTION_PLANE_NO_SUPPORT')
  d=case('product_terminal_pack996');self.assertEqual(len(d['records']),18);self.assertFalse(d['STEP_generated']);self.assertFalse(d['fabrication_ready'])
  for name,digest in d['outputs'].items():self.assertEqual(sha(BASE/name),digest)
 def test_installation_uses_distal_mesh_not_Root_assumption(self):
  d=case('product_termination_install995');self.assertEqual(len(d['distal_mesh_openings']),6)
  self.assertGreater(min(r['mesh_minimum_central_hole_diameter_mm'] for r in d['distal_mesh_openings']),1.39)
  self.assertTrue(d['records'][0]['positive_clearance']);self.assertFalse(d['records'][1]['positive_clearance']);self.assertIsNone(d['actual_threading_trial'])
 def test_finite_strict_fit_and_thread(self):
  self.assertFalse(threading(1.4,2.8,1.4)['positive_clearance'])
  for bad in (0,float('inf'),float('nan')):
   with self.assertRaises(ValueError):fit([1,bad],2,1)
   with self.assertRaises(ValueError):threading(bad,2,1)
