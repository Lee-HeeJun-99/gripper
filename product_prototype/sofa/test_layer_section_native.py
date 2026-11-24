import unittest
import numpy as np
from layer_section_native import geometry
class NativeSectionTest(unittest.TestCase):
 def test_quality_load_mass(self):
  for n in (3,5):
   q,t,tri,F,d=geometry(n)
   self.assertEqual(len(q),9*2*n);self.assertTrue(all(type(i)==int for f in tri for i in f))
   self.assertAlmostEqual(d['volume_m3'],8e-8,places=18)
   self.assertGreater(d['minimum_tet_volume_m3'],0)
   np.testing.assert_allclose(F.sum(axis=0),[0,0,-5e-5],atol=1e-19)
   self.assertAlmostEqual(d['nodal_mass_kg']*len(q),.000112,places=18)
 def test_mass_quadrature_not_hidden(self):
  *_,a=geometry(3);*_,b=geometry(5)
  self.assertNotEqual(a['uniform_nodal_inertia_kg_m2'][0][0],b['uniform_nodal_inertia_kg_m2'][0][0])
if __name__=='__main__':unittest.main()
