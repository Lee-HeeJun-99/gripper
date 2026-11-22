import json,unittest
from manufacturing_assembly import BASE,sha
from termination_contract import fit
from termination_installation import threading

def case(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class TerminationTests(unittest.TestCase):
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
