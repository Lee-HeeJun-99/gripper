import json
import math
from pathlib import Path
import tempfile
import unittest
from tools.integrated_trial import Config
from tools.integrated_slip import interior_slip
from tools.integrated_integrity import verify_trial

class IntegratedPython(unittest.TestCase):
    def test_configuration_bounds(self):
        self.assertEqual(Config().validate(),24000)
        for values in [dict(layers=3),dict(nodes=2),dict(k=-1),dict(pressure=-1),dict(dt=float('nan')),dict(duration=.0007),dict(stride=0),dict(connectors=(1,1)),dict(pressure_times=(1,0),pressure_values=(0,1)),dict(mode=True),dict(k='1'),dict(object_fixed=1),dict(mode=2,normal_k=.1)]:
            with self.assertRaises(ValueError):Config(**values).validate()
    def test_hermite_interior_not_nodal(self):
        x=[]
        for l in range(2):
            for i in range(3):x.extend([10*i,0,l*.4-(.01 if i else 0),0,0,0,1])
        r=interior_slip(x,2,3,20,.4)
        self.assertAlmostEqual(r['max_reconstructed_slip_mm'],.4*1.5*.01/10,places=14)
        self.assertAlmostEqual(r['location']['x'],5.,places=12)
    def test_hermite_zero_rigid_translation(self):
        x=[v for l in range(2) for i in range(3) for v in (i*10+3,2,l*.4-7,0,0,0,1)]
        self.assertEqual(interior_slip(x,2,3,20,.4)['max_reconstructed_slip_mm'],0)
    def test_integrity_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'data.csv').write_text('corrupt\n');(p/'metrics.json').write_text(json.dumps(dict(binary_sha256=__import__('hashlib').sha256(Path('build/integrated_20261115/plugin/libReGripIntegrated.so').read_bytes()).hexdigest(),artifacts={'data.csv':'0'*64},status='PASS',equilibrium_validated=True)))
            with self.assertRaisesRegex(ValueError,'corrupt experiment'):verify_trial(p)
    def test_non_equilibrium_objective_rejected(self):
        p=Path('results/integrated_20261115/multilayer/L8_mesh')
        # Historical v1 output must be rejected after guard-hardening changes the binary,
        # even before its independently failed equilibrium gate is considered.
        with self.assertRaisesRegex(ValueError,'non-equilibrium|binary'):verify_trial(p)

if __name__=='__main__':unittest.main()
