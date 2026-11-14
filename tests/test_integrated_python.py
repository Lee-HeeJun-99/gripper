import json
import math
from pathlib import Path
import tempfile
import unittest
from tools.integrated_trial import Config,interface_slips,force_reference
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
    def test_finite_slip_rigid_rotation(self):
        theta=.7;c=Config(mode=2,nodes=3)
        x=[v for layer in range(2) for i in range(3) for v in (i*50*math.cos(theta)+layer*.4*math.sin(theta)+2,1,-i*50*math.sin(theta)+layer*.4*math.cos(theta)+3,0,math.sin(theta/2),0,math.cos(theta/2))]
        self.assertLess(max(map(abs,interface_slips(x,c,.4))),1e-13)
    def test_nonzero_load_has_no_residual_floor(self):
        self.assertAlmostEqual(force_reference(Config(load=0,cable_tension=1e-6)),2e-9,places=18)
        self.assertEqual(force_reference(Config(load=0)),1e-6)
    @unittest.skipUnless(Path('build/integrated_20261115/plugin/libReGripIntegrated.so').exists(),'build integrated plugin first')
    def test_integrity_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'data.csv').write_text('corrupt\n');(p/'metrics.json').write_text(json.dumps(dict(binary_sha256=__import__('hashlib').sha256(Path('build/integrated_20261115/plugin/libReGripIntegrated.so').read_bytes()).hexdigest(),artifacts={'data.csv':'0'*64},status='PASS',equilibrium_validated=True)))
            with self.assertRaisesRegex(ValueError,'corrupt experiment'):verify_trial(p)
    @unittest.skipUnless(Path('results/integrated_20261115/strict_residual_retry/small_tension_18s/metrics.json').exists(),'actual strict-residual campaign required')
    def test_non_equilibrium_objective_rejected(self):
        p=Path('results/integrated_20261115/strict_residual_retry/small_tension_18s')
        with self.assertRaisesRegex(ValueError,'non-equilibrium'):verify_trial(p)
    @unittest.skipUnless(Path('results/integrated_20261115/multilayer/L8_mesh/metrics.json').exists(),'historical v1 campaign required')
    def test_historical_binary_mixing_rejected(self):
        p=Path('results/integrated_20261115/multilayer/L8_mesh')
        # Historical v1 output must be rejected after guard-hardening changes the binary,
        # even before its independently failed equilibrium gate is considered.
        with self.assertRaisesRegex(ValueError,'binary'):verify_trial(p)

if __name__=='__main__':unittest.main()
