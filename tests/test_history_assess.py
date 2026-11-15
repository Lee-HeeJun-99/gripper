import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from history_assess import comparison
class HistoryConvergenceTests(unittest.TestCase):
    def test_no_small_denominator_mask(self):
        a=dict(hold_displacement_mm=1e-12,hold_rotation_increment_rad=1e-4);b=dict(hold_displacement_mm=1.01e-12,hold_rotation_increment_rad=1e-4)
        self.assertEqual(comparison(a,b,.001)['status'],'FAIL')
    def test_rotation_not_ignored(self):
        a=dict(hold_displacement_mm=1e-6,hold_rotation_increment_rad=1e-4);b=dict(hold_displacement_mm=1e-6,hold_rotation_increment_rad=1.1e-4)
        self.assertEqual(comparison(a,b,.01)['status'],'FAIL')
    def test_repetition(self):
        a=dict(hold_displacement_mm=1e-6,hold_rotation_increment_rad=1e-4)
        self.assertEqual(comparison(a,a,1e-6)['status'],'PASS')
if __name__=='__main__':unittest.main()
