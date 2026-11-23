import json,unittest
from analyse import BASE

class GravityRhsTests(unittest.TestCase):
    def test_purity(self):
        d=json.loads((BASE/'results/b3_first_free_step1159/summary.json').read_text())
        self.assertEqual(max(d['state_errors'].values()),0)
    def test_scoped_identity(self):
        d=json.loads((BASE/'results/b3_gravity_rhs1160/summary.json').read_text())
        self.assertEqual(d['status'],'PASS_FIRST_STEP_GRAVITY_DISCRETE_IDENTITY_ONLY')
        self.assertLess(max(v['relative_error'] for v in d['blocks'].values()),2e-9)
        self.assertEqual(d['time_convergence'],'FAIL_PRESERVED')
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
        self.assertIsNone(d['energy_work'])

if __name__=='__main__':unittest.main()
