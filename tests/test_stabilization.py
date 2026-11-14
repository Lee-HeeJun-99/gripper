import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from stabilization_common import OUT
from stabilization_grasp_gate import evaluate

class StabilizationContracts(unittest.TestCase):
    @unittest.skipUnless((OUT/'grasp/sphere_x_valid/metrics.json').exists(),'actual SOFA campaign required')
    def test_object_is_not_fixed(self):
        directory=OUT/'grasp/sphere_x_valid';c=json.loads((directory/'config.json').read_text());root=ET.parse(directory/'scene.scn').getroot()
        for element in root.iter():
            if 'Constraint' in element.tag:self.assertNotIn(c['object_index'],list(map(int,element.get('indices','').split())))
        self.assertEqual(len(list(root.iter('DiagonalMass'))),1)
        self.assertEqual(len(list(root.iter('UniformMass'))),0)
    @unittest.skipUnless((OUT/'grasp/sphere_mu_zero/metrics.json').exists(),'actual negative control required')
    def test_free_friction_control_fails(self):
        result=evaluate(OUT/'grasp/sphere_mu_zero');self.assertEqual(result['status'],'FAIL');self.assertFalse(result['bounded_hold_checks']['velocity']);self.assertFalse(result['grasp_certified'])
    @unittest.skipUnless((OUT/'grasp/sphere_halfdt/metrics.json').exists(),'actual convergence campaign required')
    def test_matched_event_time_metric(self):
        a=evaluate(OUT/'grasp/sphere_x_valid');b=evaluate(OUT/'grasp/sphere_halfdt')
        self.assertLess(abs(a['displacement_mm']-b['displacement_mm']),1e-10+.001*a['displacement_mm'])
    def test_damaged_result_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'metrics.json').write_text(json.dumps(dict(status='EXPERIMENTAL',config=dict(duration=12),artifacts={'state.txt':'0'*64})))
            with self.assertRaises((ValueError,OSError)):evaluate(p)
    @unittest.skipUnless((OUT/'grasp/sphere_x/analysis_failure.json').exists(),'invalid-mass experiment required')
    def test_undefined_mass_never_accepted(self):self.assertEqual(evaluate(OUT/'grasp/sphere_x')['status'],'FAIL')

if __name__=='__main__':unittest.main()
