import json,unittest
from analyse import BASE
class LayerPocketTests(unittest.TestCase):
 def test_actual_gaps_and_no_pressure_claim(self):
  d=json.loads((BASE/'results/layer_pocket_audit1200/summary.json').read_text());self.assertGreater(d['minimum_actual_STL_layer_gap_mm'],.04999);self.assertGreater(d['actual_polygon_bore_tube_clearance_mm'],.009);self.assertIsNone(d['actual_pressure_stiffness']);self.assertEqual(d['ideal_bonded_to_free_ratio'],64);self.assertFalse(d['fabrication_ready'])
 def test_component_assembly_not_boolean(self):
  d=json.loads((BASE/'results/layer_pocket_scene1201/summary.json').read_text());self.assertEqual(d['reloaded_components'],15);self.assertTrue(d['all_reloaded_components_watertight']);self.assertEqual(d['STEP'],'NOT GENERATED');self.assertFalse(d['fabrication_ready'])
if __name__=='__main__':unittest.main()
