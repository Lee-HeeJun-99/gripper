"""Deterministic algebra tests; never counted as Native grasp qualification."""
import unittest
import numpy as np
from cable_phase_coupon import jac,matrix

class WorkContracts(unittest.TestCase):
 def test_geometric_gradient_sign(self):
  rng=np.random.default_rng(1826);origin=np.array([-.1,0,0])
  for _ in range(20):
   q=rng.normal(size=(6,3));v=rng.normal(size=(6,3));eps=1e-6
   def length(x):return np.linalg.norm(np.diff(np.vstack([origin,x]),axis=0),axis=1).sum()
   fd=(length(q+eps*v)-length(q-eps*v))/(2*eps)
   self.assertLess(abs(fd+(jac(q,origin)*v).sum()),1e-8)
 def test_convex_length_work_gap(self):
  rng=np.random.default_rng(1827);origin=np.zeros(3)
  for _ in range(20):
   q=rng.normal(size=(6,3));qn=q+.1*rng.normal(size=(6,3))
   def length(x):return np.linalg.norm(np.diff(np.vstack([origin,x]),axis=0),axis=1).sum()
   gap=length(qn)-length(q)+(jac(q,origin)*(qn-q)).sum()
   self.assertGreaterEqual(gap,0)
 def test_impulse_midpoint_identity(self):
  rng=np.random.default_rng(1828);v=rng.normal(size=(6,3));imp=rng.normal(size=(6,3));m=.01;vn=v+imp/m
  kinetic=.5*m*((vn**2-v**2).sum());mid=(imp*(v+vn)/2).sum();loss=.5*m*((vn-v)**2).sum()
  self.assertLess(abs(kinetic-mid),1e-10)
  self.assertLess(abs((imp*vn).sum()-mid-loss),1e-10)
 def test_row_parser(self):
  np.testing.assert_array_equal(matrix('0:0:1 2 3;0:2:-1 0 2;',3),[[1,2,3],[0,0,0],[-1,0,2]])

if __name__=='__main__':unittest.main()
