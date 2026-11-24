import csv,json,unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
def summary(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class NativeWireTests(unittest.TestCase):
    def test_old_factory_failure_preserved(self):
        d=summary('native_finite_wire1420');self.assertEqual(d['status'],'FAIL_NATIVE_FINITE_BEAM_PILOT');self.assertEqual(d['accepted_rows'],0)
    def test_loaded_and_zero_actual_states(self):
        for case in ('native_finite_wire1421','native_finite_wire_zero1422'):
            d=summary(case);self.assertEqual(d['accepted_rows'],20);self.assertEqual(d['sofa_errors'],0);self.assertEqual(d['maximum_fixed_root_error'],0);self.assertEqual(d['eyelet_contact'],'NOT IMPLEMENTED')
        self.assertGreater(summary('native_finite_wire1421')['endpoint_tip_y_m'],0)
        root=ET.parse(BASE/'results/native_finite_wire_zero1422/scene.scn').getroot();q=np.fromstring(root.find('./Node/MechanicalObject').get('position'),sep=' ').reshape(-1,7)
        for row in csv.DictReader((BASE/'results/native_finite_wire_zero1422/states.csv').open()):
            self.assertLess(float(np.abs(np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7)-q).max()),1e-12);self.assertLess(float(np.abs(np.fromstring(row['rigid_v'],sep=' ')).max()),1e-12)
    def test_only_load_and_log_path_changed(self):
        roots=[ET.parse(BASE/'results'/case/'scene.scn').getroot() for case in ('native_finite_wire1421','native_finite_wire_zero1422')]
        for root in roots:
            root.find('./Node/NativeRigidJournal').set('filename','LOG');root.find('./Node/ConstantForceField').set('forces','LOAD')
        self.assertEqual(ET.tostring(roots[0]),ET.tostring(roots[1]))
if __name__=='__main__':unittest.main()
