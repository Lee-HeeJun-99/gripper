"""Evidence scope regressions, not physical certification."""
import json,unittest
import xml.etree.ElementTree as ET
from analyse import BASE

class Contrasts(unittest.TestCase):
    def data(self,name):return json.loads((BASE/'results'/name/'summary.json').read_text())
    def test_zero_input_bounded(self):
        d=self.data('b3_zero_input1107');self.assertEqual(d['outputs'],240)
        self.assertEqual(d['quality']['inverted_element_samples'],0)
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
    def test_polar_not_repair(self):
        self.assertEqual(self.data('b3_polar_contrast1108')['status'],'INVERSION_OBSERVED')
    def test_joint_rejected_even_without_actuation(self):
        for n in ('b3_two_point_joint1109','b3_two_point_zero1111'):
            d=self.data(n);self.assertEqual(d['status'],'INVERSION_OBSERVED')
            self.assertLess(d['quality']['first_inversion_time_s'],.04)
    def test_only_declared_changes(self):
        for case,parent,tag,attribute,value in [
            ('b3_zero_input1107','b3_high_force_isolation1105','NativeCableSequence','maximumForceN','0'),
            ('b3_polar_contrast1108','b3_high_force_isolation1105','TetrahedronFEMForceField','method','polar'),
            ('b3_two_point_zero1111','b3_two_point_joint1109','NativeCableSequence','maximumForceN','0')]:
            a=ET.parse(BASE/'results'/parent/'scene.scn').getroot()
            b=ET.parse(BASE/'results'/case/'scene.scn').getroot()
            a.find('.//'+tag).set(attribute,value)
            for n in a.iter():
                for k,v in list(n.attrib.items()):n.set(k,v.replace(parent,case))
            self.assertEqual(ET.tostring(a),ET.tostring(b))
    def test_valid_prefix_only(self):
        d=self.data('b3_inversion_compare1110')
        self.assertEqual(d['status'],'DIAGNOSTIC_ONLY_NOT_CAUSAL_CERTIFICATION')
        self.assertEqual(d['records'][0]['first_element_rigid_owned_nodes'],[172,175])
    def test_unloaded_rest_not_forced_state(self):
        d=self.data('b3_joint_rest1112')
        self.assertEqual(d['quality']['maximum_node_motion_mm'],0)
        self.assertEqual(d['quality']['minimum_determinant_ratio'],1)
        a=ET.parse(BASE/'results/b3_two_point_zero1111/scene.scn').getroot()
        b=ET.parse(BASE/'results/b3_joint_rest1112/scene.scn').getroot()
        a.set('gravity','0 0 0')
        for n in a.iter():
            for k,v in list(n.attrib.items()):n.set(k,v.replace('b3_two_point_zero1111','b3_joint_rest1112'))
        self.assertEqual(ET.tostring(a),ET.tostring(b))

if __name__=='__main__':unittest.main()
