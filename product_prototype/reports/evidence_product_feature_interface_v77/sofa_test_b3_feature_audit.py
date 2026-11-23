import json,unittest
from analyse import BASE
class TestHistoricalFeatureAudit(unittest.TestCase):
 def test_historical_load_partition_scope(self):
  d=json.loads((BASE/'results/b3_feature_load_audit1254/summary.json').read_text());a,b=d['records'];self.assertEqual(a['duplicate_skin_response_row_ids'],0);self.assertEqual(a['mean_skin_force_by_feature_N']['LineCollisionModel1'],[0.,0.,0.]);self.assertGreater(a['mean_skin_force_by_feature_N']['PointCollisionModel1'][2],.49);self.assertLess(sum(x[2] for x in b['mean_skin_force_by_feature_N'].values()),0);self.assertIsNone(b['new_holding_verdict'])
 def test_early_contact_deficit_not_hidden_by_late_failure(self):
  d=json.loads((BASE/'results/b3_feature_withdrawal1255/summary.json').read_text());b=[r for r in d['records'] if r['case']=='b3_mass100_explore1059' and r['accepted_window_s']==[1.,1.2]][0];total=sum(v[2] for v in b['mean_skin_force_by_feature_N'].values());self.assertGreater(total,.70);self.assertLess(total,.981);self.assertIsNone(b['contact_area'])
if __name__=='__main__':unittest.main()
