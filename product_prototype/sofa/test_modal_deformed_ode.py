import json,unittest
from analyse import BASE

class ModalDeformedTests(unittest.TestCase):
    def test_independent_reference_scope(self):
        d=json.loads((BASE/'results/b3_modal_reference_audit1173/summary.json').read_text())
        self.assertEqual(d['status'],'PASS_LINEAR_REFERENCE_CROSSCHECK_ONLY')
        self.assertGreater(d['minimum_eigenvalue_s_minus2'],0)
        self.assertLess(max(x['relative'] for x in d['comparisons']),1e-6)
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
    def test_read_only_actual_path(self):
        d=json.loads((BASE/'results/b3_ode_deformed_step1174/summary.json').read_text())
        self.assertEqual(max(d['state_errors'].values()),0)
    def test_deformed_algebra_not_time_pass(self):
        d=json.loads((BASE/'results/b3_ode_deformed_rhs1175/summary.json').read_text())
        self.assertLess(d['matrix_error']['relative'],1e-14)
        self.assertLess(d['hypotheses']['no_convective_term']['free_velocity']['relative'],1e-8)
        self.assertEqual(d['time_convergence'],'FAIL_PRESERVED')
        self.assertIsNone(d['energy_work'])
    def test_force_candidate_scope(self):
        d=json.loads((BASE/'results/b3_ode_force_rhs1178/summary.json').read_text())
        self.assertEqual(d['command_impulse_error_Ns'],0)
        self.assertLess(d['impulse_velocity_correction']['relative'],2e-9)
        q=json.loads((BASE/'results/b3_ode_force_candidate1176/summary.json').read_text())
        self.assertEqual(q['quality']['inverted_samples'],0)
        pair=json.loads((BASE/'results/b3_ode_force_pair1180/summary.json').read_text())
        self.assertEqual(pair['status'],'FAIL_TIME_PAIR_GATE')
        self.assertEqual(pair['comparisons']['skin_displacement']['gate'],.001)
    def test_force_scene_change_is_explicit(self):
        import xml.etree.ElementTree as ET
        cases=['b3_rail_back_hold1129','b3_ode_force_candidate1176'];normalized=[]
        for name in cases:
            folder=BASE/'results'/name;root=ET.parse(folder/'scene.scn').getroot()
            for n in root.iter():
                for key,value in list(n.attrib.items()):
                    n.set(key,'DECLARED_DAMPING_CHANGE' if key in ('rayleighMass','rayleighStiffness') else value.replace(str(folder),'CASE'))
            normalized.append(ET.tostring(root))
        self.assertEqual(*normalized)

if __name__=='__main__':unittest.main()
