import json,unittest
import xml.etree.ElementTree as ET
from analyse import BASE

class DeformedJoint(unittest.TestCase):
    def data(self,n):return json.loads((BASE/'results'/n/'summary.json').read_text())
    def test_observer_purity(self):
        for tag in (1121,1122,1123):
            d=self.data(f'b3_deformed_probe{tag}');self.assertEqual(d['status'],'PASS_BOUNDED_OBSERVER_PURITY');self.assertEqual(max(d['state_errors'].values()),0)
    def test_tangent_failure_not_hidden(self):
        self.assertEqual(self.data('b3_deformed_probe1121')['tangent_status'],'PASS_SINGLE_DIRECTION_ONLY')
        for tag in (1122,1123):self.assertEqual(self.data(f'b3_deformed_probe{tag}')['tangent_status'],'FAIL_SINGLE_DIRECTION_TANGENT')
    def test_neo_patch_not_grasp(self):
        d=self.data('native_material_patch1124');self.assertEqual(d['status'],'PASS_SMALL_SHEAR_COMPARISON_ONLY');self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
    def test_neo_rejected_despite_tangent(self):
        self.assertEqual(self.data('b3_native_neo1125')['status'],'INVERSION_OBSERVED')
        self.assertNotEqual(self.data('b3_native_neo1125')['process']['exit_code'],0)
        self.assertEqual(self.data('b3_native_neo_probe1126')['tangent_status'],'PASS_SINGLE_DIRECTION_ONLY')
    def test_joint_no_stiffness_or_control_change(self):
        src=ET.parse(BASE/'results/b3_high_force_isolation1105/scene.scn').getroot();new=ET.parse(BASE/'results/b3_rail_back_force1128/scene.scn').getroot()
        for tag in ('TetrahedronFEMForceField','UniformMass','CableConstraint','FixedProjectiveConstraint'):
            self.assertEqual([n.attrib for n in src.iter(tag)],[n.attrib for n in new.iter(tag)])
        self.assertEqual(len(list(new.iter('RigidMapping'))),len(list(src.iter('RigidMapping'))))
    def test_bounded_quality_not_time_pass(self):
        for n in ('b3_rail_back_zero1127','b3_rail_back_force1128','b3_rail_back_hold1129','b3_rail_back_half1130'):
            d=self.data(n);self.assertEqual(d['quality']['inverted_element_samples'],0);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
        d=self.data('b3_rail_back_assess1131');self.assertEqual(d['status'],'FAIL_TIME_PAIR_GATE');self.assertEqual(d['short_to_long_prefix_q_error_m'],0)
    def test_actual_control_identity(self):
        self.assertEqual(self.data('b3_rail_back_input1132')['status'],'PASS_INPUT_SCENE_IDENTITY_ONLY')
    def test_mapping_stabilization_rejected(self):
        for n in ('b3_mapping_nsd_base1133','b3_mapping_nsd_half1134'):
            d=self.data(n);self.assertEqual(d['status'],'INVERSION_OBSERVED');self.assertNotEqual(d['process']['exit_code'],0);self.assertFalse(d['exact_tangent'])

if __name__=='__main__':unittest.main()
