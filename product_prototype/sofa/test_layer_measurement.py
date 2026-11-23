import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from layer_measurement_log import validate,FIELDS
class LayerMeasurementTests(unittest.TestCase):
 def test_no_fake_measurement(self):self.assertEqual(validate([],{})['status'],'NOT MEASURED')
 def test_synthetic_format_not_hardware(self):
  r=dict(zip(FIELDS,['0','-1000','1','.0001','.00001','load']));d=validate([r],dict(source_kind='SYNTHETIC_TEST_FIXTURE'));self.assertEqual(d['status'],'BLOCKED_UNCALIBRATED_OR_NONLAB');self.assertIsNone(d['stiffness'])
 def test_bad_clock(self):
  r=dict(zip(FIELDS,['0','0','0','0','0','unloaded']))
  with self.assertRaises(ValueError):validate([r,r],{})
if __name__=='__main__':unittest.main()
