import csv,json,unittest
import numpy as np
from analyse import BASE
def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class ContinuationTests(unittest.TestCase):
 def test_wire_provenance_and_sliding(self):
  r=result('wire_eyelet_assess1437')['records'][-1];self.assertTrue(r['observer_state_journal_exact']);self.assertEqual(r['response_partition_max_error_Ns_Nms'],0);self.assertGreater(r['endpoint']['root_axial_motion_mm'],5);self.assertGreater(r['minimum_saved_surface_vertex_gap_mm'],0);self.assertTrue(all('/finiteEyelet/'in k and '/wire/wireSurface/'in k for k in r['response_pairs']))
 def test_collapsed_surface_not_contact_pass(self):
  row=list(csv.DictReader((BASE/'results/wire_eyelet1428/surface.csv').open()))[-1];q=np.fromstring(row['q'],sep=' ').reshape(-1,3);self.assertEqual(np.ptp(q[:,0]),0);self.assertEqual(result('wire_eyelet1428')['active_constraint_outputs'],0)
 def test_clearance_compensation_explicit(self):
  d=json.loads((BASE/'results/nonuniform_hold1001438/geometry.json').read_text());self.assertEqual(d['original_radius_mm'],50);self.assertGreater(d['candidate_radius_mm'],53);self.assertTrue(all(r['skin_gap_mm']>=.3 for r in d['final_initial_gate']));self.assertTrue(all(r['skin_gap_mm']<0 for r in d['initial_at_original_radius']))
 def test_failed_grasp_not_promoted(self):
  d=result('nonuniform_hold_assess1439');self.assertEqual(d['status'],'FAIL_EXPLORATORY_FUNCTIONAL_GRASP');self.assertGreater(d['slip_mm'],40);self.assertGreater(d['force_partition']['support']['mean_force_N'][2],d['gravity_load_N']);self.assertLess(d['maximum_hold_momentum_residual_Ns'],1e-10);self.assertFalse(d['tests']['direct_skin_detector_and_force'])
if __name__=='__main__':unittest.main()
