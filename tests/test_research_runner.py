import tempfile
from pathlib import Path
import unittest
from tools.research_trial import run

class Runner(unittest.TestCase):
    def test_invalid_settings_rejected_before_output(self):
        for kw in (dict(duration=.0007),dict(k=float('nan')),dict(n=True),dict(connectors=[0]),dict(length=151),dict(duration=61),dict(dt=.00001,duration=10)):
            with tempfile.TemporaryDirectory() as tmp:
                out=Path(tmp)/'out'
                with self.assertRaises(ValueError):run(out,**kw)
                self.assertFalse(out.exists())

if __name__=='__main__':unittest.main()
