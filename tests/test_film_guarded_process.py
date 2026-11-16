import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_guarded_process import guarded
class Guard(unittest.TestCase):
    def test_success(self):
        with tempfile.TemporaryDirectory() as root:
            result=guarded([sys.executable,'-c','print("ok")'],Path(root)/'case',2)
            self.assertEqual(result['exit_code'],0);self.assertEqual(result['process_status'],'exited')
    def test_newton_failure_stops_and_reaps(self):
        with tempfile.TemporaryDirectory() as root:
            result=guarded([sys.executable,'-u','-c','import time;print("Newton-Raphson method failed to converge");time.sleep(60)'],Path(root)/'case',2)
            self.assertEqual(result['process_status'],'nonlinear_failure');self.assertNotEqual(result['exit_code'],0);self.assertLess(result['runtime_s'],2)
    def test_timeout(self):
        with tempfile.TemporaryDirectory() as root:
            result=guarded([sys.executable,'-c','import time;time.sleep(60)'],Path(root)/'case',.2)
            self.assertEqual(result['process_status'],'timeout');self.assertNotEqual(result['exit_code'],0)
if __name__=='__main__':unittest.main()
