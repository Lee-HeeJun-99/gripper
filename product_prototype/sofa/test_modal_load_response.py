import json,csv,unittest
from analyse import BASE
class ModalLoadTests(unittest.TestCase):
    def test_actual_load_not_spectrum_only(self):
        d=json.loads((BASE/'results/b3_modal_load_response1181/summary.json').read_text());self.assertGreater(d['top_gravity_compliance_modes'][0]['fraction'],.98);self.assertGreater(d['top_native_time_error_modes'][0]['native_pair_fraction'],.8);self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertGreater(d['reference_chart_limits'][0]['max_chart_body_error_m'],.002)
    def test_modal_partition(self):
        with (BASE/'results/b3_modal_load_response1181/modes.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertAlmostEqual(sum(float(r['native_pair_fraction']) for r in rows),1,places=12)
    def test_deformed_load_not_rest_load(self):
        d=json.loads((BASE/'results/b3_modal_state_samples1199/summary.json').read_text());self.assertGreater(d['deformed_Cable_load']['top_rest_compliance_modes'][0]['fraction'],.88);self.assertIsNone(d['energy_work'])
if __name__=='__main__':unittest.main()
