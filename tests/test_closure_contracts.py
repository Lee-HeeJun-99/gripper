import unittest
from dataclasses import replace
from closure_trial import Config
from closure_wrench import analyze
class ClosureContracts(unittest.TestCase):
    def test_config_numeric_history_and_wrench(self):
        self.assertEqual(Config(axis=5,load=5e-6).validate(),36000)
        for change in [dict(samples=1),dict(axis=6),dict(history_spacing=.0001),dict(history_spacing=float('nan')),dict(stride=20.)]:
            with self.subTest(change=change),self.assertRaises(ValueError):replace(Config(),**change).validate()
    def test_rank5_control(self):
        r=analyze([[0,0,5],[0,0,-5]],[[0,0,1],[0,0,-1]],[5e-6]*2,.3,5)
        self.assertEqual(r['rank'],5);self.assertFalse(r['cone_origin_strict_interior']);self.assertFalse(r['bounded_feasibility']['Tzplus']['feasible'])
    def test_rank6_not_sufficient_without_friction(self):
        p=[[5,0,0],[-2.5,4.330127,0],[-2.5,-4.330127,0]];n=[[a/5 for a in point] for point in p]
        r=analyze(p,n,[5e-6]*3,0,5);self.assertEqual(r['rank'],6);self.assertLess(r['cone_rank'],6);self.assertFalse(r['cone_origin_strict_interior'])
    def test_single_contact_left_nullspace_complete(self):
        r=analyze([[0,0,5]],[[0,0,1]],[5e-6],.3,5);self.assertEqual(r['rank'],3);self.assertEqual(len(r['left_nullspace']),3)
    def test_zero_capacity_not_approved_by_unbounded_cone(self):
        p=[[5,0,0],[-2.5,4.330127,0],[-2.5,-4.330127,0]];n=[[a/5 for a in point] for point in p];r=analyze(p,n,[0]*3,.3,5)
        self.assertTrue(r['cone_origin_strict_interior']);self.assertFalse(any(v['feasible'] for v in r['bounded_feasibility'].values()))
if __name__=='__main__':unittest.main()
