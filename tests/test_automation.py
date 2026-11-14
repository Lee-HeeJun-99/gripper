"""Real launcher tests and explicitly labelled corrupt-output classifier fixtures."""
import concurrent.futures
import csv
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verification_common import ROOT,RUN,SOFA,write_json
from run_trial import run_trial,execute_process
from trial_validation import TrialError,analyze,validate_config,verify_artifacts,read_states

OUT=Path(os.environ.get('REGRIP_AUTOMATION_OUT',str(RUN/'automation')))
SOURCE=Path(os.environ.get('REGRIP_PHYSICS_OUT',str(RUN/'physics_release')))/'free'


class Automation(unittest.TestCase):
    def folder(self,suffix=''):
        path=OUT/(self._testMethodName+suffix);path.mkdir(parents=True,exist_ok=False);return path

    def fixture(self,mutator=None):
        out=self.folder()
        for name in ('rigid.txt','interface.txt'):
            data=(SOURCE/name).read_text()
            if mutator and name=='rigid.txt':data=mutator(data)
            (out/name).write_text(data)
        write_json(out/'fixture_origin.json',dict(source=str(SOURCE),synthetic_fault=mutator is not None,
                                                scope='classifier replay, not a new physical simulation'))
        return out

    def classify(self,out,status,reason):
        source=json.loads((SOURCE/'metrics.json').read_text())
        with self.assertRaises(TrialError) as caught:
            analyze(out,source['config'],0,(SOURCE/'sofa.log').read_text())
        self.assertEqual(caught.exception.status,status)
        self.assertIn(reason,str(caught.exception))
        write_json(out/'classification.json',dict(status=status,reason=str(caught.exception)))

    def test_nan(self):
        self.classify(self.fixture(lambda s:s.replace('X= ','X= nan ',1)),'crash','initial mechanical state')
        # A well-shaped NaN is tested separately; malformed dimensions cannot pass either.

    def test_well_shaped_nan(self):
        self.classify(self.fixture(lambda s:s.replace('X= 0 ','X= nan ',1)),'diverged','nonfinite')

    def test_inf(self):
        self.classify(self.fixture(lambda s:s.replace('X= 0 ','X= inf ',1)),'diverged','nonfinite')

    def test_divergence(self):
        def mutate(s):
            lines=s.splitlines();index=[i for i,l in enumerate(lines) if l.startswith('X= ')][1]
            values=lines[index][3:].split();values[7]='1000';lines[index]='X= '+' '.join(values)
            return '\n'.join(lines)+'\n'
        self.classify(self.fixture(mutate),'diverged','displacement')

    def test_invalid_physics(self):
        def mutate(s):
            lines=s.splitlines();index=next(i for i,l in enumerate(lines) if l.startswith('X= '))
            values=lines[index][3:].split();values[11]=str(math.sin(.01/2));values[13]=str(math.cos(.01/2))
            lines[index]='X= '+' '.join(values);return '\n'.join(lines)+'\n'
        self.classify(self.fixture(mutate),'invalid_physics','planar domain')

    def test_interface_velocity_nan(self):
        out=self.fixture();path=out/'interface.txt'
        path.write_text(path.read_text().replace('V= 0 ','V= nan ',1))
        self.classify(out,'diverged','nonfinite')

    def test_nonmonotonic_middle_time(self):
        self.classify(self.fixture(lambda s:s.replace('T= 0.00050000000000000001','T= 0.002',1)),'crash','sample times')

    def test_partial_output(self):
        self.classify(self.fixture(lambda s:s[:s.rfind('T= ')]),'crash','incomplete')

    def test_duplicate_state_field(self):
        path=self.folder()/'bad.txt';path.write_text('T= 0\nX= 0\nX= 1\n')
        with self.assertRaises(TrialError):read_states(path)

    def test_invalid_arguments(self):
        for args in [dict(dt=float('nan')),dict(k=float('inf')),dict(dt=0),dict(n=1),dict(connectors=[1,1]),dict(connectors=[-1]),dict(timeout=-1)]:
            config=dict(k=1,connectors=None,dt=.0005,duration=3.,load=.0001,n=11,timeout=60);config.update(args)
            with self.assertRaises(ValueError):validate_config(**config)

    def test_corrupt_csv_manifest(self):
        out=self.folder()
        for path in SOURCE.iterdir():
            target=out/path.name
            if path.name=='timeseries.csv':shutil.copyfile(path,target)
            else:target.symlink_to(path)
        with (out/'timeseries.csv').open('a') as stream:stream.write('corrupt\n')
        with self.assertRaisesRegex(TrialError,'corrupted artifact'):verify_artifacts(out)

    def test_missing_artifact(self):
        out=self.folder()
        for path in SOURCE.iterdir():
            if path.name!='rigid.txt':(out/path.name).symlink_to(path)
        with self.assertRaisesRegex(TrialError,'missing or corrupted'):verify_artifacts(out)

    def test_partial_directory_refused(self):
        out=self.folder();(out/'metrics.json').write_text('{"status":"incomplete"}')
        with self.assertRaises(FileExistsError):run_trial(out,k=1,duration=.01)
        self.assertEqual((out/'metrics.json').read_text(),'{"status":"incomplete"}')

    def test_not_converged_live(self):
        out=OUT/self._testMethodName
        report=run_trial(out,k=1,duration=.01)
        self.assertEqual(report['status'],'not_converged');self.assertIsNone(report['effective_stiffness'])

    def test_timeout_live(self):
        report=run_trial(OUT/self._testMethodName,k=1,timeout=.001)
        self.assertEqual(report['status'],'timeout');self.assertIsNone(report['effective_stiffness'])
        self.assertEqual(report['exit_code'],-signal.SIGKILL)

    def test_interrupt_cleanup(self):
        timer=threading.Timer(.5,lambda:os.kill(os.getpid(),signal.SIGINT));timer.start()
        try:report=run_trial(OUT/self._testMethodName,k=1,duration=60)
        finally:timer.cancel();timer.join()
        self.assertEqual(report['process_status'],'interrupted');self.assertIsNone(report['effective_stiffness'])
        with self.assertRaises(ProcessLookupError):os.kill(report['pid'],0)

    def test_crash_process(self):
        out=self.folder()
        result=execute_process([sys.executable,'-c','import os,signal;os.kill(os.getpid(),signal.SIGSEGV)'],out,3)
        self.assertEqual(result['exit_code'],-signal.SIGSEGV)
        with self.assertRaisesRegex(TrialError,'abnormal exit'):analyze(out,dict(n=11,dt=.0005,load=.0001,k=None,duration=.001),result['exit_code'],'')

    def test_log_error_zero_exit_live(self):
        out=self.folder()
        command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','2',
                 '-l','NonexistentReGripFaultInjectionPlugin',str(ROOT/'scenes/environment_smoke.scn')]
        result=execute_process(command,out,10)
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        self.assertEqual(result['exit_code'],0);self.assertIn('[ERROR]',log)
        with self.assertRaisesRegex(TrialError,'error log'):analyze(out,dict(n=11,dt=.0005,load=.0001,k=None,duration=.001),0,log)

    def test_concurrent_duplicate_execution(self):
        target=OUT/self._testMethodName
        command=[sys.executable,str(ROOT/'tools/run_trial.py'),str(target),'--k','1','--duration','.01']
        a=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        b=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        aout=a.communicate(timeout=30)[0];bout=b.communicate(timeout=30)[0]
        self.assertEqual(sorted([a.returncode,b.returncode]),[1,2])
        self.assertEqual(json.loads((target/'metrics.json').read_text())['samples'],20)
        (target/'ownership_test.log').write_text(aout+'\n'+bout)

    def test_launcher_fd_and_process_leaks(self):
        before=len(list(Path('/proc/self/fd').iterdir()));root=self.folder()
        for i in range(24):
            path=root/str(i);path.mkdir();r=execute_process(['/bin/true'],path,2)
            self.assertEqual(r['exit_code'],0)
            with self.assertRaises(ProcessLookupError):os.kill(r['pid'],0)
        after=len(list(Path('/proc/self/fd').iterdir()))
        self.assertEqual(before,after)
        write_json(root/'fd_counts.json',dict(before=before,after=after,reaped_children=24))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=False)
    with (OUT/'unittest.log').open('x') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Automation))
    write_json(OUT/'result.json',dict(tests=result.testsRun,failures=[(str(t),v) for t,v in result.failures],
                                    errors=[(str(t),v) for t,v in result.errors],passed=result.wasSuccessful()))
    print('automation',result.testsRun,'passed=',result.wasSuccessful())
    raise SystemExit(0 if result.wasSuccessful() else 1)
