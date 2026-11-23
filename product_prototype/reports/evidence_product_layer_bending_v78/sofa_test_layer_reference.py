import json,unittest
import numpy as np
from layer_bending_reference import BASE,element,elastic
class TestLayerReference(unittest.TestCase):
 def test_affine_patch(self):
  q=np.array([[0,0,0],[.005,0,0],[0,.01,0],[0,0,.0002]]);D=elastic(2.5e9,.3);V,B,K=element(q,D);A=np.array([[.2,.03,.02],[-.01,.1,.04],[.05,-.02,-.1]]);u=q@A.T+[.001,.002,.003];expected=[.2,.1,-.1,.02,.02,.07];np.testing.assert_allclose(B@u.ravel(),expected,atol=1e-13,rtol=1e-12);self.assertGreater(V,0);np.testing.assert_allclose(K,K.T,atol=1e-10,rtol=1e-12)
 def test_translation_kernel(self):
  q=np.array([[0,0,0],[.005,0,0],[0,.01,0],[0,0,.0002]]);V,B,K=element(q,elastic(2.5e9,.3));np.testing.assert_allclose(B@np.tile([1.,2.,3.],4),0,atol=1e-12)
 def test_actual_reference_does_not_qualify_equilibrium(self):
  d=json.loads((BASE/'results/layer_bending_reference1257/summary.json').read_text());self.assertLess(d['native_vs_CST_tip_relative_error'],1e-7);self.assertGreater(d['pure_bending_interpolant_energy_ratio'],500);self.assertGreater(d['native_in_linear_reference_residual_relative'],.1);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
