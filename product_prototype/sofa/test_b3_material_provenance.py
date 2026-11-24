import json,unittest
from analyse import BASE
class B3MaterialProvenanceTest(unittest.TestCase):
 def test_frozen_observer_prefix(self):
  d=json.loads((BASE/'results/b3_existing_provenance1315/summary.json').read_text());self.assertEqual(d['status'],'PASS_BOUNDED_READ_ONLY_B3_PROVENANCE');self.assertTrue(all(v==0 for v in d['max_numeric_errors'].values()));self.assertTrue(all(d['all_record_fields_exact'].values()))
 def test_unique_native_features(self):
  d=json.loads((BASE/'results/b3_provenance_join1316/summary.json').read_text());self.assertEqual(d['normal_rows'],114);self.assertTrue(d['all_unique']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_material_clock_not_next_state(self):
  d=json.loads((BASE/'results/b3_active_material_line1318/summary.json').read_text());self.assertEqual(len(d['records']),6);self.assertEqual(d['unmapped_active_skin_rows'],[]);self.assertEqual({r['feature_type'] for r in d['records']},{'Point','Line'});self.assertTrue(all(r['detector_vs_previous_accepted_parent_error_m']<=1e-12 for r in d['records']));self.assertTrue(all(r['detector_vs_next_accepted_parent_error_m']>1e-5 for r in d['records']))
if __name__=='__main__':unittest.main()
