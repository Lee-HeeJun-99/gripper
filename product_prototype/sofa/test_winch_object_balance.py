"""Analytic algebra checks, never substitutes for an actual Native experiment."""
import unittest
import numpy as np
from winch_object_balance import residuals,window_mask

class ObjectBalance(unittest.TestCase):
 def test_original_holding_endpoint_roundoff(self):
  self.assertEqual(window_mask(np.array([1.5,1.6-2e-14,2.-3e-14,2.01]),1.6,2.).tolist(),[False,True,True,False])
 def test_free_fall(self):
  g=np.array([0,0,-9.81]);dt=.0025;v=np.zeros((4,6));v[:,:3]=np.arange(1,5)[:,None]*g*dt
  a,b=residuals(v,np.zeros(6),np.zeros((4,6)),.1,.03,g,dt)
  self.assertLess(abs(a).max(),1e-17);self.assertEqual(abs(b).max(),0.)
 def test_static_weight_support(self):
  imp=np.zeros((4,6));imp[:,2]=.1*9.81*.0025
  a,b=residuals(np.zeros((4,6)),np.zeros(6),imp,.1,.03,[0,0,-9.81],.0025)
  self.assertEqual(abs(a).max(),0.);self.assertEqual(abs(b).max(),0.)
 def test_angular_and_initial_velocity(self):
  v0=np.arange(6)*.01;v=np.stack([v0+.001,v0+.002]);dv=np.diff(np.vstack([v0,v]),axis=0);imp=dv*np.array([.1]*3+[.4*.1*.03**2]*3)
  a,b=residuals(v,v0,imp,.1,.03,[0,0,0],.0025)
  self.assertEqual(abs(a).max(),0.);self.assertEqual(abs(b).max(),0.)
 def test_missing_support_detected(self):
  a,b=residuals(np.zeros((1,6)),np.zeros(6),np.zeros((1,6)),.1,.03,[0,0,-9.81],.0025)
  self.assertGreater(abs(a).max(),1e-10)
if __name__=='__main__':unittest.main()
