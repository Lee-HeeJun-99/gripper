import json,unittest
from analyse import BASE
class TestInterface(unittest.TestCase):
 def test_limit_not_claimed_as_jamming(self):
  d=json.loads((BASE/'results/layer_interface_assess1240/summary.json').read_text())
  self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertLess(d['free_to_tied_displacement_ratio'],1.01)
  for r in d['records']:
   self.assertEqual(r['strict_overlap_witnesses'],0);self.assertGreater(r['minimum_volume_ratio'],0);self.assertIsNone(r['effective_EI']);self.assertIsNone(r['energy_work'])
 def test_same_model_inputs(self):
  a=json.loads((BASE/'results/layer_free1189/preflight.json').read_text());b=json.loads((BASE/'results/layer_interface_limit1239/preflight.json').read_text())
  for k in ('E_Pa','density_kg_m3','dimensions_m','pressure_Pa','dt_s','tip_bending_load_N'):self.assertEqual(a[k],b[k])
if __name__=='__main__':unittest.main()
