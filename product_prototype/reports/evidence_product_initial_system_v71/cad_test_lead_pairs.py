import json,unittest
import numpy as np
from lead_pair_distance import closest_polylines
from manufacturing_assembly import BASE

class LeadPairTests(unittest.TestCase):
 def test_completed_leads_and_finger_chains_keep_scope(self):
  for case,count in [('product_completed_leads982',705),('product_finger_chains985',11)]:
   d=json.loads((BASE/'results'/case/'summary.json').read_text());self.assertEqual(d['assembly_part_count'],283)
   self.assertEqual(len(d['lead_results']),6);self.assertTrue(all(r['probe_count']==count and r['unresolved']==0 for r in d['lead_results']))
   self.assertFalse(d['fabrication_ready'])
 def test_combined_pair_witnesses_and_scope(self):
  d=json.loads((BASE/'results/product_fullchain_pairs986/summary.json').read_text())
  self.assertEqual(d['finger_chain_case'],'product_finger_chains985');self.assertEqual(len(d['records']),15);self.assertFalse(d['fabrication_ready'])
  for r in d['records']:
   self.assertAlmostEqual(np.linalg.norm(np.diff(r['closest_points_mm'],axis=0)),r['distance_mm'])
   self.assertAlmostEqual(r['distance_mm']-2*.22522275007459786,r['sagitta_expanded_gap_mm'])
 def test_crossing_and_parallel(self):
  self.assertEqual(closest_polylines([[-1,0,0],[1,0,0]],[[0,-1,0],[0,1,0]])['distance_mm'],0)
  self.assertEqual(closest_polylines([[0,0,0],[2,0,0]],[[1,3,0],[4,3,0]])['distance_mm'],3)
 def test_skew_and_endpoints(self):
  r=closest_polylines([[-1,0,0],[1,0,0]],[[0,-1,2],[0,1,2]])
  self.assertEqual(r['distance_mm'],2);self.assertEqual(r['parameters'],[.5,.5])
  self.assertAlmostEqual(closest_polylines([[0,0,0],[1,0,0]],[[2,1,0],[3,2,0]])['distance_mm'],2**.5)
 def test_rigid_motion_and_invalid(self):
  p=np.array([[0,0,0],[3,0,0]]);q=np.array([[1,1,0],[1,2,2]]);R=np.array([[0,-1,0],[1,0,0],[0,0,1]])
  self.assertAlmostEqual(closest_polylines(p,q)['distance_mm'],closest_polylines(p@R.T+8,q@R.T+8)['distance_mm'])
  with self.assertRaises(ValueError):closest_polylines([[0,0,0],[0,0,0]],q)
