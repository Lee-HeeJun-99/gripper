import json,unittest
from analyse import BASE

class OdeDampingScopeTests(unittest.TestCase):
    def test_time_failure_not_hidden(self):
        d=json.loads((BASE/'results/b3_ode_gravity_assess1170/summary.json').read_text())
        self.assertEqual(d['status'],'FAIL_TIME_PAIR_GATE')
        self.assertEqual(d['comparisons']['skin_displacement']['gate'],.001)
        self.assertGreater(d['comparisons']['skin_displacement']['maximum_relative_error'],.3)
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
    def test_reference_energy_not_heat(self):
        d=json.loads((BASE/'results/b3_linear_energy_contract1171/summary.json').read_text())
        self.assertIsNone(d['Native_potential_energy_API']);self.assertIsNone(d['global_B3_energy_work'])
        for r in d['records'].values():self.assertLess(r['maximum_residual_relative'],1e-8)
        e=d['records']['b3_linear_gravity_ode1166']['final']
        self.assertGreater(e['backward_Euler_numerical_loss_J'],10*e['reference_velocity_damping_work_J'])

if __name__=='__main__':unittest.main()
