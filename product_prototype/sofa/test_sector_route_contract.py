import unittest
import numpy as np
from sector_route_feasibility import outward_interval

class Sector(unittest.TestCase):
 def test_explicit_sector_plane(self):
  r=.02;h=.001;buffer=.0002
  _,upper=outward_interval(r,-.06,[0,0,-.06],h,buffer=buffer)
  self.assertAlmostEqual((-np.sqrt(3)*r+upper)/2+h,-buffer/2,places=15)
 def test_sphere_outward_boundary(self):
  lower,_=outward_interval(.02,-.06,[0,.001,-.06],.001)
  self.assertAlmostEqual(np.hypot(.02,lower-.001),.03025,places=15)
 def test_infeasible_and_below_pole(self):
  low,high=outward_interval(.005,0,[0,0,0],.001)
  self.assertGreater(low,high)
  low,_=outward_interval(.02,-.1,[0,0,-.06],.001)
  self.assertEqual(low,0.)
if __name__=='__main__':unittest.main()
