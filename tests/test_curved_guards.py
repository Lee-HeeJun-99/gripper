import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import curve_common as common
import curve_trial
class CurvedArtifactGuards(unittest.TestCase):
    def test_current_compiled_identity(self):
        self.assertEqual(common.identity()['model'],'director_hermite_fixed_material_midpoints_normal_and_tangent_v1')
    def test_source_change(self):
        with patch.object(common,'sources',return_value={}):
            with self.assertRaises(ValueError):common.identity()
    def test_binary_change(self):
        old=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'bad'if p==common.PLUGIN else old(p)):
            with self.assertRaises(ValueError):common.identity()
    def test_generated_change(self):
        old=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'bad'if p==common.BUILD/'CurvedGenerated.inc'else old(p)):
            with self.assertRaises(ValueError):common.identity()
    def test_existing_raw_refused_before_execution(self):
        with patch.object(curve_trial,'execute_process',side_effect=AssertionError('must not execute')):
            with self.assertRaises(FileExistsError):curve_trial.run('profile_n11',profile=True)
if __name__=='__main__':unittest.main()
