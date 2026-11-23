import json,unittest
from analyse import BASE
class TestRefinedInterface(unittest.TestCase):
 def test_endpoint_not_qualified_as_stiffness(self):
  d=json.loads((BASE/'results/layer_refined_interface_assess1267/summary.json').read_text());self.assertIsNone(d['effective_stiffness_ratio']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertLess(abs(d['accepted_endpoint_displacement_ratio_NOT_stiffness']-d['independent_CST_ratio']),1e-4);self.assertGreater(d['records'][1]['final_max_node_speed_m_s'],1e-5)
 def test_complete_accepted_geometry(self):
  d=json.loads((BASE/'results/layer_refined_interface_assess1267/summary.json').read_text())
  for r in d['records']:self.assertTrue(r['complete_100ms']);self.assertEqual(r['accepted_outputs'],500);self.assertGreater(r['minimum_volume_ratio'],0);self.assertEqual(r['strict_centroid_overlap_witnesses'],0)
if __name__=='__main__':unittest.main()
