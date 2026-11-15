"""Contracts and independent checks; numeric evidence comes from real SOFA files."""
import json,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from grasp_trial import Config,run
from grasp_evaluate import verify_record
from grasp_common import OUT,sha

class GraspContracts(unittest.TestCase):
    def test_invalid_config(self):
        cases=[dict(dt=0),dict(mu=-1),dict(dt=float('nan')),dict(nodes=42),dict(samples=0),dict(stride=20.),dict(axis=0.),dict(shape=True),dict(duration=25),dict(dt=1e-8)]
        for change in cases:
            with self.subTest(change=change),self.assertRaises(ValueError):replace(Config(),**change).validate()
    def test_resource_and_path_guards(self):
        for name,wall in [('../escape',240),('',240),('x',float('inf')),('x',481)]:
            with self.subTest(name=name,wall=wall),self.assertRaises(ValueError):run(name,wall=wall)
    def test_hash_injection(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'data.csv').write_text('x\n1\n');(p/'metrics.json').write_text(json.dumps(dict(artifacts={'data.csv':sha(p/'data.csv')})))
            verify_record(p);(p/'data.csv').write_text('x\nbroken\n')
            with self.assertRaises(ValueError):verify_record(p)
    def test_actual_zero_mu_is_physical_failure_not_crash(self):
        p=OUT/'trials/mu_zero_fixed/metrics.json'
        if not p.exists():self.skipTest('real campaign not present')
        r=json.loads(p.read_text());self.assertTrue(r['execution_completed']);self.assertFalse(r['bounded_hold_pass']);self.assertEqual(r['status'],'FAIL')
    def test_actual_six_directions_identical_conditions(self):
        paths=[OUT/'trials'/('final_sphere_'+a+s)/'metrics.json' for a in 'xyz' for s in ('plus','minus')]
        if not all(p.exists() for p in paths):self.skipTest('real campaign not present')
        configs=[]
        for p in paths:
            r=verify_record(p.parent);c=dict(r['config']);c.pop('axis');c.pop('load');configs.append(c)
            self.assertEqual(r['config']['object_constraints'],[]);self.assertFalse(r['grasp_certified']);self.assertTrue(r['execution_completed'])
        self.assertTrue(all(c==configs[0] for c in configs))
    def test_pressure_off_not_automatically_rejected(self):
        p=OUT/'trials/pressure_off/metrics.json'
        if not p.exists():self.skipTest('real campaign not present')
        r=json.loads(p.read_text());self.assertEqual(r['config']['pressure'],0);self.assertTrue(r['bounded_hold_pass'])

if __name__=='__main__':unittest.main()
