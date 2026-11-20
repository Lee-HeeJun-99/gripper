"""Independent analytic intersection/union,rigid-objectivity and bore predicates."""
import json,unittest
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE
from finite_union_moments import raw,add,normalized,intersection,union
from finite_guide_coupon import eyelet
class UnionTest(unittest.TestCase):
 def test_analytic_overlap_and_union_boxes(self):
  a=trimesh.creation.box(extents=[2.,3.,4.]);b=a.copy();b.apply_translation([1,0,0]);overlap=intersection(a,b);V,c,I=normalized(overlap)
  self.assertAlmostEqual(V,12.,places=11);np.testing.assert_allclose(c,[.5,0,0],atol=1e-12);np.testing.assert_allclose(I,np.diag([25/12,17/12,10/12]),rtol=1e-12,atol=1e-12)
  V,c,I=normalized(add(raw(a),raw(b),tuple(-v for v in overlap)));self.assertAlmostEqual(V,36.,places=11);np.testing.assert_allclose(c,[.5,0,0],atol=1e-12);np.testing.assert_allclose(I,np.diag([25/12,25/12,18/12]),rtol=1e-12,atol=1e-12)
 def test_disjoint_and_boundary_rejection(self):
  a=trimesh.creation.box(extents=[2.,3.,4.]);b=a.copy();b.apply_translation([3.,0,0]);self.assertEqual(intersection(a,b)[0],0.)
  b.apply_translation([-1.,0,0])
  with self.assertRaises(ValueError):intersection(a,b)
 def test_intersection_objectivity(self):
  a=trimesh.creation.box(extents=[2.,3.,4.]);b=a.copy();b.apply_translation([1.,0,0]);V,c,I=normalized(intersection(a,b));Q=Rotation.from_rotvec([.3,-.7,.2]).as_matrix();shift=np.array([3.,-2.,7.])
  for m in (a,b):m.vertices=m.vertices@Q.T+shift
  Vt,ct,It=normalized(intersection(a,b));self.assertLess(abs(V-Vt),1e-10);np.testing.assert_allclose(ct,Q@c+shift,atol=1e-10);np.testing.assert_allclose(It,Q@I@Q.T,atol=1e-10)
 def test_annular_sector_decomposition_union(self):
  cfg=json.loads((BASE/'meshes/finite_eyelet_support_v11/config.json').read_text());ring,_=eyelet(cfg,32);bracket=trimesh.creation.box(extents=[2.,1.,1.]);bracket.apply_translation([0.,1.2,0.]);u,o,error=union(ring,bracket,32);self.assertLess(error,1e-11);self.assertGreater(o[0],0);self.assertLess(u[0],ring.volume+bracket.volume)
if __name__=='__main__':unittest.main()
