"""Independent geometry/initial-mass algebra, not a grasp/Native substitute."""
import sys,unittest
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cad'))
from bellcrank_link_geometry import pose
from bellcrank_kkt_audit import skew
class BellcrankContracts(unittest.TestCase):
 def test_exact_rod_length(self):
  for angle in np.linspace(0,-.42,29):
   _,a,b,_=pose(angle);self.assertLess(abs(np.linalg.norm(b-a)-30),1e-12)
 def test_initial_jacobian(self):
  h=1e-5;_,a,b,p=pose(0);_,ap,bp,pp=pose(h);_,am,bm,pm=pose(-h)
  np.testing.assert_allclose((ap-am)/(2*h),[0,-10,0],atol=1e-8,rtol=0)
  np.testing.assert_allclose((bp-bm)/(2*h),[0,-10,0],atol=1e-8,rtol=0)
  self.assertLess(abs((pp-pm)/(2*h)),1e-12)
 def test_joint_null_velocity(self):
  H=np.zeros((6,8));H[:3,0]=[0,.01,0];H[:3,1:4]=np.eye(3);H[:3,4:7]=-skew([0,-.015,0]);H[3:,1:4]=-np.eye(3);H[3:,4:7]=skew([0,.015,0]);H[3:,7]=[0,1,0]
  v=np.array([1,0,-.01,0,0,0,0,-.01]);np.testing.assert_array_equal(H@v,np.zeros(6));self.assertEqual(np.linalg.matrix_rank(H),6)
 def test_curved_vs_tangent_residual(self):
  for t in (1e-4,.01,.2):
   R,_,_,_=pose(t);curved=(R@np.array([-.01,0,0]))[0]+.01;prediction=.02*np.sin(t/2)**2
   self.assertLess(abs(curved-prediction),1e-17)
if __name__=='__main__':unittest.main()
