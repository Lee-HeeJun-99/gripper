"""Candidate geometry/provenance guards, never physical joint qualification."""
import json,unittest
from manufacturing_assembly import BASE,evaluate,box
from distal_keeper import axial,keeper_shapes

class DistalKeeperTests(unittest.TestCase):
 def test_axial_frame_matches_real_distal_not_root_bore(self):
  m=evaluate(axial(1.55,-1.05,6.2))
  self.assertAlmostEqual(m.bounds[0,0],-1.05,places=5)
  self.assertAlmostEqual(m.bounds[1,0],6.2,places=5)
 def test_finite_parts_and_unknown_physical_properties(self):
  cfg=json.loads((BASE/'config/distal_keeper_v52.json').read_text())
  shapes=keeper_shapes(box([-1,-1,-3],[1,1,-2]),cfg)
  self.assertEqual(len(shapes),6)
  self.assertTrue(all(evaluate(s).is_volume for s in shapes))
  self.assertIsNone(cfg['actual_preload_N']);self.assertIsNone(cfg['actual_retention_N'])
  self.assertFalse(cfg['fabrication_ready']);self.assertIsNone(cfg['screw']['length_tolerance_mm'])
 def test_world_mating_artifacts_are_preserved_not_passed(self):
  d=json.loads((BASE/'results/product_distal_keeper1005/summary.json').read_text())
  self.assertEqual(d['status'],'DISTAL_KEEPER_STATIC_REVIEW')
  self.assertEqual(d['candidate_part_count'],294)
  self.assertEqual(len(d['solid_intersections']),3)
  self.assertTrue(all(r['signed_volume_mm3']>0 for r in d['solid_intersections']))
  self.assertFalse(d['fabrication_ready'])
 def test_alternative_paths_keep_actual_collisions(self):
  for case,part in (('product_distal_diagonal1008','f0_c0_s5_eyelet'),('product_distal_shallow1009','f1_c1_distal_NI000001_MAX_ENVELOPE')):
   d=json.loads((BASE/'results'/case/'summary.json').read_text())
   self.assertEqual(d['status'],'DISTAL_KEEPER_SERVICE_REVIEW')
   self.assertTrue(any(h['part']==part and h['signed_volume_mm3']>.001 for r in d['service_records'] for h in r['intersections']))
 def test_actual_pack_not_step_or_qualified_hardware(self):
  d=json.loads((BASE/'results/product_distal_keeper_pack1010/summary.json').read_text())
  self.assertEqual(d['saved_STL_count'],6);self.assertFalse(d['STEP_generated']);self.assertFalse(d['fabrication_ready'])
 def test_slot_change_does_not_hide_adjacent_service_obstacles(self):
  d=json.loads((BASE/'results/product_distal_slot_service1014/summary.json').read_text())
  self.assertTrue(d['fasteners_only']);self.assertEqual(d['status'],'DISTAL_KEEPER_SERVICE_REVIEW')
  names={h['part'] for r in d['service_records'] for h in r['intersections']}
  self.assertIn('f0_c0_s4_support',names);self.assertIn('f0_c0_s5_support',names)
  self.assertFalse(any(r['operation']=='COVER_WITHDRAWAL_SAMPLED_ONLY' for r in d['service_records']))
 def test_nut_hull_warning_refined_with_actual_sampled_solid(self):
  d=json.loads((BASE/'results/product_distal_nut_actual1016/summary.json').read_text())
  rows=[r for r in d['service_records'] if r['operation']=='ACTUAL_NUT_TRANSLATION_SAMPLED_ONLY']
  self.assertEqual(len(rows),14)
  self.assertFalse(any(r['intersections'] for r in rows if r['translation_local_Y_mm']==0))
  self.assertTrue(all(any(r['intersections'] for r in rows if r['bolt']==i) for i in (0,1)))
