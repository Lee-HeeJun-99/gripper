import json,unittest
from analyse import BASE

class GravityContractTests(unittest.TestCase):
    def test_failed_assumption_preserved(self):
        d=json.loads((BASE/'results/b3_linear_gravity_assess1163/summary.json').read_text())
        self.assertEqual(d['status'],'FAIL_LINEAR_COUPON_DISCRETE_REFERENCE')
        self.assertGreater(d['maximum_relative_errors']['native_v_vs_discrete'],.18)
    def test_actual_contrast(self):
        d=json.loads((BASE/'results/b3_linear_damping_contract1165/summary.json').read_text())
        self.assertEqual(d['observer_q_v_max_error'],0)
        self.assertLess(d['variants']['both_A_only']['max_v_relative'],1e-6)
        self.assertGreater(d['variants']['physical_velocity_damping']['max_v_relative'],.18)
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
        self.assertIsNone(d['energy_work'])

if __name__=='__main__':unittest.main()
