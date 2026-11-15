import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import birth_common as common
class BirthGuards(unittest.TestCase):
    def test_source_mismatch(self):
        with patch.object(common,'sources',return_value={}):
            with self.assertRaises(ValueError):common.identity()
    def test_binary_mismatch(self):
        original=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'tampered' if p==common.PLUGIN else original(p)):
            with self.assertRaises(ValueError):common.identity()
    def test_generated_mismatch(self):
        original=common.sha
        with patch.object(common,'sha',side_effect=lambda p:'tampered' if p==common.BUILD/'BirthGenerated.inc' else original(p)):
            with self.assertRaises(ValueError):common.identity()
if __name__=='__main__':unittest.main()
