import json,unittest
from analyse import BASE
from layer_interface_reference import tied_reference
class TestInterfaceReference(unittest.TestCase):
 def test_coarse_native_ratio_agreement_is_not_jamming(self):
  d=json.loads((BASE/'results/layer_interface_reference1264/summary.json').read_text());self.assertLess(d['coarse_native_ratio_difference'],1e-7);self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertGreater(d['records'][-1]['free_to_tied_ratio'],d['records'][0]['free_to_tied_ratio'])
 def test_actual_dof_identification_error(self):
  d=tied_reference(9);self.assertEqual(d['interface_displacement_error_m'],0.);self.assertLess(d['reduced_free_residual_N'],1e-12)
if __name__=='__main__':unittest.main()
