import unittest
import numpy as np
from layer_section_reference import mesh,assess
from layer_mesh_reference import mesh as old_mesh

class SectionTest(unittest.TestCase):
 def test_original_mesh_identical(self):
  q,t=mesh(9,2,2);a,b,_=old_mesh(9)
  np.testing.assert_array_equal(q,a);np.testing.assert_array_equal(t,b)
 def test_width_independent_exact_field(self):
  a=assess(9,2,2);b=assess(9,5,2)
  self.assertAlmostEqual(a['total_energy_ratio'],b['total_energy_ratio'],places=9)
 def test_thickness_normal_and_longitudinal_shear(self):
  a=assess(9,2,2);b=assess(9,2,5);c=assess(17,2,5)
  self.assertAlmostEqual(b['normal_energy_ratio'],1.125,places=11)
  self.assertAlmostEqual(a['shear_energy_ratio'],b['shear_energy_ratio'],places=9)
  self.assertAlmostEqual(b['shear_energy_ratio']/c['shear_energy_ratio'],4,places=10)
  self.assertAlmostEqual(c['volume_m3'],8e-8,places=18)
if __name__=='__main__':unittest.main()
