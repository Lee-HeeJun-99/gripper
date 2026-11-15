import sys,unittest,subprocess,hashlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import research_common as common
class AutonomousGuards(unittest.TestCase):
    def test_changed_source(self):
        with patch.object(common,'sources',return_value={}):
            with self.assertRaises(ValueError):common.identity()
    def test_changed_binary(self):
        original=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'changed'if p==common.PLUGIN else original(p)):
            with self.assertRaises(ValueError):common.identity()
    def test_changed_generated(self):
        original=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'changed'if p==common.BUILD/'MaterialPointGenerated.inc'else original(p)):
            with self.assertRaises(ValueError):common.identity()
    def test_historical_runner_preserved(self):
        old=subprocess.check_output(['git','show','63970172ad196e0add3ad42a67ccaee4c7a8975e:tools/research_trial.py'],cwd=common.ROOT)
        self.assertEqual(hashlib.sha256(old).hexdigest(),common.sha(common.ROOT/'tools/research_trial.py'))
if __name__=='__main__':unittest.main()
