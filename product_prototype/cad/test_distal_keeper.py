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
