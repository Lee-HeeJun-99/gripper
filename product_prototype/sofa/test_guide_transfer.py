import json,unittest
import xml.etree.ElementTree as ET
from analyse import BASE

class GuideTransfer(unittest.TestCase):
    def data(self,n):return json.loads((BASE/'results'/n/'summary.json').read_text())
    def test_native_force_and_couple(self):
        for n in ('b3_guide_translation1113','b3_guide_couple1114'):
            d=self.data(n);self.assertEqual(d['status'],'PASS_MAPPING_COUPON_ONLY')
            self.assertEqual(d['outputs'],4);self.assertLessEqual(d['mapped_position_max_error_m'],1e-12)
            self.assertLessEqual(d['first_step_velocity_relative_error'],.001)
            self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
    def test_joint_rank(self):
        d=self.data('b3_guide_couple1114');self.assertEqual(d['three_point_rank'],6);self.assertEqual(d['two_point_rank'],5)
    def test_failed_initialization_preserved(self):
        self.assertEqual(self.data('b3_reference_deadload1115')['status'],'FAIL_EXECUTION')
    def test_no_constraint_in_new_load_paths(self):
        for n in ('b3_reference_deadload1116','b3_recorded_load1117'):
            r=ET.parse(BASE/'results'/n/'scene.scn').getroot()
            self.assertEqual(len(list(r.iter('CableConstraint'))),0)
            self.assertEqual(len(list(r.iter('LinearForceField'))),36)
            self.assertEqual(len(list(r.iter('TetrahedronFEMForceField'))),1)
    def test_load_law_not_repaired_grasp(self):
        self.assertEqual(self.data('b3_reference_deadload1116')['status'],'NO_SAVED_INVERSION_DIFFERENT_LOAD_LAW')
        self.assertEqual(self.data('b3_recorded_load1117')['status'],'INVERSION_WITHOUT_CABLE_CONSTRAINT')
    def test_comparison_not_equivalence(self):
        d=self.data('b3_load_compare1118');self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
        for r in d['records']:self.assertLessEqual(r['first_step_max_position_error_m'],1e-12)

if __name__=='__main__':unittest.main()
