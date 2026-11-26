import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import release_gate_current as g
class FailClosedTests(unittest.TestCase):
 def check(self,j,status,case):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'p.json').write_text(json.dumps(j))
   with patch.object(g,'ROOT',p):return g.proof('p.json',status,case)
 def test_explicit_case_status(self):self.assertEqual(self.check({'status':'PASS','case':'A'},'PASS','A')[0]['case'],'A')
 def test_fail_status_rejected(self):
  with self.assertRaises(ValueError):self.check({'status':'FAIL','case':'A'},'PASS','A')
 def test_wrong_case_rejected(self):
  with self.assertRaises(ValueError):self.check({'status':'PASS','case':'B'},'PASS','A')
 def test_missing_status_rejected(self):
  with self.assertRaises(ValueError):self.check({'case':'A'},'PASS','A')
 def test_missing_hashed_input_rejected(self):
  with self.assertRaises(ValueError):self.check({'case':'A','status':'PASS','input_sha256':{'missing.json':'not-a-hash'}},'PASS','A')
if __name__=='__main__':unittest.main()
