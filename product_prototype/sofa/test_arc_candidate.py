import json,unittest
from analyse import BASE
class ArcCandidateTests(unittest.TestCase):
 def test_single_variable_and_rejection(self):
  folder=BASE/'results/b3_arc_start_candidate1187';b=json.loads((folder/'baseline70/config.json').read_text());c=json.loads((folder/'distributed60/config.json').read_text());c['finger']['precurve']['start_mm']=70;self.assertEqual(b,c);d=json.loads((folder/'summary.json').read_text());self.assertEqual(d['records']['distributed60']['initial_checks']['status'],'REJECT_INITIAL_GEOMETRY');self.assertEqual(d['Holding'],'NOT RUN');self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
