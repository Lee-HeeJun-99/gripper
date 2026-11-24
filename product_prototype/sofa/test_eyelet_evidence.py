import json,unittest
from analyse import BASE
def evidence(name):return json.loads((BASE/'results'/name/'summary.json').read_text())
class EvidenceTests(unittest.TestCase):
    def test_chamfer_failure_is_actual_not_negative_bound_only(self):
        d=evidence('eyelet_arc_support1413');self.assertEqual(len(d['local_bore_collision_witnesses']),4);self.assertTrue(all(r['actual_sample_wire_solid_gap_mm']<0 for r in d['local_bore_collision_witnesses']))
    def test_finite_placement_not_dynamic_pass(self):
        d=evidence('eccentric_eyelet_assembly1417');self.assertEqual(d['part_count'],20);self.assertGreater(d['minimum_finite_mesh_clearance_lower_bound_mm'],0);self.assertEqual(d['Native'],'NOT RUN');self.assertEqual(d['STEP'],'NOT GENERATED')
    def test_fixed_arc_motion_rejected(self):
        d=evidence('eyelet_arc_replay1418');self.assertEqual(d['status'],'REJECT_FIXED_ARC_C1_REPLAY_PROXY');self.assertLess(d['initial_tangent_mismatch_deg'],1e-6);self.assertGreater(d['maximum_tangent_mismatch_deg'],7);self.assertEqual(d['new_Native'],'NOT RUN')
if __name__=='__main__':unittest.main()
