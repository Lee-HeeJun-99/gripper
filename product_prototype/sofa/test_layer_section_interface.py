import unittest
from layer_section_interface import solve
class InterfaceSectionTest(unittest.TestCase):
 def test_symmetric_normal_constraint_not_stick(self):
  n=solve(9,3,(2,));s=solve(9,3,(0,1,2))
  self.assertLess(abs(n['free_to_tied_displacement_ratio']-1),1e-7)
  self.assertGreater(s['free_to_tied_displacement_ratio'],1.005)
  self.assertEqual(n['interface_constrained_displacement_error_m'],0)
  self.assertEqual(s['interface_constrained_displacement_error_m'],0)
if __name__=='__main__':unittest.main()
