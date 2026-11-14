"""Dependency-free guard/objective tests using freshly measured SOFA results.

These tests do not emulate Optuna and do not count as optimization trials.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verification_common import ROOT,RUN,PHYSICS,write_json
from optimize import validate_gate,objective_values
import verification_common

PHY=PHYSICS
OUT=RUN/'optimization_guards_release'


class Guards(unittest.TestCase):
    def setUp(self):
        self.gate=json.loads((PHY/'gate.json').read_text())
        self.off=json.loads((PHY/'free/metrics.json').read_text())
        self.on=json.loads((PHY/'k1/metrics.json').read_text())

    def reject(self,mutate):
        gate=copy.deepcopy(self.gate);mutate(gate)
        path=OUT/(self._testMethodName+'.json');write_json(path,gate)
        with self.assertRaises((RuntimeError,FileNotFoundError)):validate_gate(path)

    def test_real_gate_and_real_objective(self):
        validate_gate(PHY/'gate.json')
        ratio,slip=objective_values(self.off,self.on)
        self.assertAlmostEqual(ratio,self.off['tip_deflection_mm']/self.on['tip_deflection_mm'],places=14)
        self.assertGreater(ratio,1);self.assertLess(slip,1)

    def test_failed_gate(self):self.reject(lambda g:g.update(passed=False))
    def test_partial_gate(self):self.reject(lambda g:g.update(checks={}))
    def test_missing_hashes(self):self.reject(lambda g:g.update(source_sha256={}))
    def test_source_mismatch(self):self.reject(lambda g:g['source_sha256'].update({'tools/run_trial.py':'0'*64}))
    def test_binary_mismatch(self):self.reject(lambda g:g.update(plugin_sha256='0'*64))

    def test_build_manifest_source_mismatch(self):
        directory=OUT/self._testMethodName;directory.mkdir()
        write_json(directory/'build_manifest.json',dict(source_sha256={},binary_sha256={}))
        with mock.patch.object(verification_common,'BUILD',directory):
            with self.assertRaisesRegex(RuntimeError,'sources do not match'):verification_common.assert_build_current()

    def test_build_manifest_binary_mismatch(self):
        directory=OUT/self._testMethodName;directory.mkdir();(directory/'marker').write_bytes(b'changed')
        write_json(directory/'build_manifest.json',dict(source_sha256=verification_common.compiled_sources(),binary_sha256={'marker':'0'*64}))
        with mock.patch.object(verification_common,'BUILD',directory):
            with self.assertRaisesRegex(RuntimeError,'changed build artifact'):verification_common.assert_build_current()

    def test_failed_trials_have_no_values(self):
        for status in ('timeout','crash','diverged','not_converged','invalid_physics'):
            changed=copy.deepcopy(self.on);changed['status']=status
            with self.assertRaises(ValueError):objective_values(self.off,changed)

    def test_nonfinite_values_rejected(self):
        for bad in (float('nan'),float('inf'),-1.):
            changed=copy.deepcopy(self.on);changed['tip_deflection_mm']=bad
            with self.assertRaises(ValueError):objective_values(self.off,changed)

    def test_different_load_rejected(self):
        changed=copy.deepcopy(self.on);changed['config']['load']*=2
        with self.assertRaises(ValueError):objective_values(self.off,changed)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=False)
    with (OUT/'unittest.log').open('x') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Guards))
    write_json(OUT/'result.json',dict(tests=result.testsRun,passed=result.wasSuccessful(),
                                    failures=[(str(t),v) for t,v in result.failures],errors=[(str(t),v) for t,v in result.errors]))
    print('optimization guards',result.testsRun,'passed=',result.wasSuccessful())
    raise SystemExit(0 if result.wasSuccessful() else 1)
