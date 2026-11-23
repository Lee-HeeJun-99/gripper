import json,unittest
from analyse import BASE

class StepMatrix(unittest.TestCase):
    def data(self,n):return json.loads((BASE/'results'/n/'summary.json').read_text())
    def test_observer_purity(self):
        for n in ('b3_step_base1143','b3_step_deformed1144','b3_step_half1147'):
            d=self.data(n);self.assertEqual(d['status'],'PASS_BOUNDED_STEP_OBSERVER_PURITY');self.assertEqual(max(d['state_errors'].values()),0)
    def test_same_step_clocks(self):
        for n,dt in [('b3_step_base1143',.0025),('b3_step_deformed1144',.0025),('b3_step_half1147',.00125)]:
            d=self.data(n);self.assertEqual(d['phases'],['begin','build_end','solve_end','accepted_end']);self.assertAlmostEqual(d['phase_clocks_s'][-1]-d['phase_clocks_s'][0],dt,places=12)
    def test_matrix_and_correction(self):
        for n in ('b3_step_assess1145','b3_step_assess1146','b3_step_half_assess1149'):
            d=self.data(n);self.assertEqual(d['status'],'PASS_SAMPLED_EFFECTIVE_MATRIX_ONLY');self.assertEqual(d['impulse_correction_status'],'PASS_DISCRETE_CORRECTION_IDENTITY_ONLY');self.assertEqual(d['command_impulse_error_Ns'],0)
    def test_not_physical_time_pass(self):
        d=self.data('b3_step_assess1146');self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertEqual(d['time_convergence'],'FAIL_PRESERVED');self.assertIsNone(d['energy_work'])
    def test_one_step_input_not_state_reset(self):
        d=self.data('b3_pause_assess1151');self.assertEqual(d['status'],'PASS_ONE_STEP_PHASE_SEPARATION_ONLY');self.assertEqual(d['paused_lambda_Ns'],[0,0]);self.assertTrue(all(d['matrix_hash_identity'].values()));self.assertEqual(len(d['changed_command_times_s']),1);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')

if __name__=='__main__':unittest.main()
