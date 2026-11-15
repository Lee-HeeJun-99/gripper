"""Small-planar reference and immutable compiled-source guard contracts."""
import unittest,math
from models.conservative_beam.linear_reference import solve
from tools.beam_common import identity,material
class BeamContracts(unittest.TestCase):
    def test_reference_linear_limit(self):
        m=material();x=solve(EA=m['EA'],GA=m['GAz'],EI=m['EIy']);F=1e-6/2;expected=F*100**3/(3*m['EIy'])*(1-1/400)+F*100/m['GAz'];self.assertAlmostEqual(x['tip_deflection_mm']/expected,1.,places=7)
    def test_invalid_inputs(self):
        for kw in [dict(k=-1),dict(k=math.nan),dict(connectors=(1,1)),dict(connectors=(0,)),dict(nodes=2),dict(EA=0)]:
            with self.assertRaises(ValueError):solve(**kw)
    def test_coupling_trend(self):
        values=[solve(k=k,connectors=tuple(range(1,11))) for k in (0,.1,1,100)];self.assertTrue(all(a['tip_deflection_mm']>b['tip_deflection_mm'] for a,b in zip(values,values[1:])))
    def test_compiled_source_identity(self):
        r=identity();self.assertEqual(len(r['compiled_source_sha256']),4);self.assertEqual(r['plugin_sha256'],r['plugin_sha256'].lower())
    def test_dependency_guard(self):
        from unittest.mock import patch
        from tools import beam_common as b
        original=b.sha
        with patch.object(b,'sha',side_effect=lambda p:'bad' if str(p).endswith('finite_rotation/Kernel.h') else original(p)):
            with self.assertRaisesRegex(ValueError,'compiled dependency'):b.identity()
if __name__=='__main__':unittest.main()
