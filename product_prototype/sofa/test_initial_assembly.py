import json,unittest
from analyse import BASE

class InitialAssembly(unittest.TestCase):
    def data(self,n):return json.loads((BASE/'results'/n/'summary.json').read_text())
    def test_first_material_probe_purity(self):
        d=self.data('b3_rail_back_initial_probe1136');self.assertEqual(d['status'],'PASS_BOUNDED_OBSERVER_PURITY');self.assertEqual(max(d['state_errors'].values()),0)
    def test_frozen_spectrum_scope(self):
        d=self.data('b3_rail_back_spectrum1137');self.assertFalse(d['native_assembled_mass_tangent_verified']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertEqual(d['free_dofs'],648)
    def test_actual_system_purity(self):
        for n in ('b3_rail_back_system1138','b3_rail_back_rest_system1139'):
            d=self.data(n);self.assertEqual(d['status'],'PASS_BOUNDED_ASSEMBLY_PATH_PURITY');self.assertEqual(max(d['state_errors'].values()),0);self.assertEqual(d['matrix_dimension'],720)
    def test_effective_system_not_mass_certification(self):
        d=self.data('b3_initial_system_assess1140');self.assertEqual(d['status'],'PASS_FIRST_EFFECTIVE_SYSTEM_IDENTITY_ONLY');self.assertFalse(d['mass_isolation_verified']);self.assertFalse(d['full_deformed_assembly_verified']);self.assertEqual(d['time_convergence'],'FAIL_PRESERVED')
        for v in d['blocks'].values():self.assertLess(v['relative_error'],.001)

if __name__=='__main__':unittest.main()
