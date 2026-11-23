import json,unittest
from analyse import BASE
class TestNativeReference(unittest.TestCase):
 def test_failed_mesh_not_promoted_by_reference_agreement(self):
  d=json.loads((BASE/'results/layer_native_reference_assess1262/summary.json').read_text());self.assertEqual(d['status'],'FAIL_NATIVE_LAYER_MESH_GATE');self.assertGreater(d['mesh_pair_relative'],.9)
  for c in d['records']:
   self.assertEqual(c['maximum_contact_impulse_Ns'],0.);self.assertEqual(c['strict_tet_centroid_overlap_witnesses'],0)
   for r in c['records']:self.assertGreater(r['minimum_volume_ratio'],0)
 def test_native_formulation_residual_scope(self):
  d=json.loads((BASE/'results/layer_native_reference_assess1262/summary.json').read_text());a=d['records'][0]['records'][0];b=d['records'][2]['records'][0];self.assertLess(b['linear_reference_residual_relative'],a['linear_reference_residual_relative']);self.assertIsNone(d['records'][2]['native_internal_force']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
