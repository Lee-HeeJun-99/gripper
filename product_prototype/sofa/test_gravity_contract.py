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
    def test_ode_configuration_not_coefficient_tuning(self):
        import xml.etree.ElementTree as ET
        root=ET.parse(BASE/'results/b3_linear_gravity_ode1166/scene.scn').getroot()
        self.assertEqual(root.find('EulerImplicitSolver').get('rayleighMass'),'1')
        self.assertEqual(root.find('EulerImplicitSolver').get('rayleighStiffness'),'0.0001')
        self.assertEqual(root.find('Node/UniformMass').get('rayleighMass'),'0')
        self.assertEqual(root.find('Node/TetrahedronFEMForceField').get('rayleighStiffness'),'0')
        d=json.loads((BASE/'results/b3_linear_gravity_ode_assess1167/summary.json').read_text())
        self.assertEqual(d['status'],'PASS_LINEAR_COUPON_DISCRETE_REFERENCE_ONLY')
        self.assertGreater(d['maximum_relative_errors']['discrete_q_vs_continuous'],.9)

if __name__=='__main__':unittest.main()
