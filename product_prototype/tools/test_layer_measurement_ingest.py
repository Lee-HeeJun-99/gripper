import copy,unittest
from layer_measurement_ingest import analyze
def fixture():
 meta=dict(data_origin='synthetic_fixture',units=dict(force='N',displacement='m',pressure='Pa',time='s'),specimen_id='SYNTHETIC_NOT_HARDWARE',fixture_id='parser_fixture',operator='unittest',test_date='synthetic',calibration_files={x:{'path':'NOT_REAL','sha256':'NOT_REAL'} for x in ('force','displacement','pressure')})
 rows=[dict(time_s=str(i),specimen_id=meta['specimen_id'],condition='flex' if i<3 else 'pressure',cycle='1',branch='loading',steady='1',force_N=str(i%3),displacement_m=str((i%3)*(.001 if i<3 else .0005)),pressure_Pa='0' if i<3 else '10000') for i in range(6)];return rows,meta
class MeasurementTests(unittest.TestCase):
 def test_synthetic_never_hardware_pass(self):
  r,m=fixture();d=analyze(r,m);self.assertEqual(d['status'],'SYNTHETIC_PARSER_FIXTURE_ONLY');self.assertEqual(d['hardware_test'],'NOT MEASURED');self.assertEqual(d['jamming_validation'],'NOT QUALIFIED')
 def test_missing_calibration(self):
  r,m=fixture();m['calibration_files'].pop('pressure')
  with self.assertRaises(ValueError):analyze(r,m)
 def test_mixed_units(self):
  r,m=fixture();m['units']['displacement']='mm'
  with self.assertRaises(ValueError):analyze(r,m)
 def test_nan(self):
  r,m=fixture();r[2]['force_N']='nan'
  with self.assertRaises(ValueError):analyze(r,m)
 def test_unpaired_cycles(self):
  r,m=fixture()
  for row in r[3:]:row['cycle']='2'
  with self.assertRaises(ValueError):analyze(r,m)
 def test_no_declared_origin(self):
  r,m=fixture();m.pop('data_origin')
  with self.assertRaises(ValueError):analyze(r,m)
 def test_not_enough_steady(self):
  r,m=fixture();r[0]['steady']='0'
  with self.assertRaises(ValueError):analyze(r,m)
 def test_pressure_not_changed(self):
  r,m=fixture()
  for row in r:row['pressure_Pa']='0'
  with self.assertRaises(ValueError):analyze(r,m)
if __name__=='__main__':unittest.main()
