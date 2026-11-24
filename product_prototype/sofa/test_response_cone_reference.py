import unittest
import numpy as np
from b3_response_cone_reference import cone_lp
class ConeReferenceTest(unittest.TestCase):
 def test_symmetric_side_contacts(self):
  cols=[]
  for a in np.arange(3)*2*np.pi/3:
   r=.03*np.array([np.cos(a),np.sin(a),0]);n=-r/.03;t=np.array([0,0,1.]);s=np.cross(n,t);F=np.column_stack([n,t,s]);cols.append(np.vstack([F,np.cross(r,F.T).T]))
  d=cone_lp(cols,.981);self.assertEqual(d['status'],'CONDITIONAL_STATIC_SUBSET_FEASIBLE');self.assertAlmostEqual(d['minimum_normal_sum_N'],.981/.3,places=8);self.assertLess(d['moment_residual_Nm'],1e-12)
 def test_downward_normals_cannot_support(self):
  F=np.array([[0,1,0],[0,0,1],[-1,0,0.]])
  d=cone_lp([np.vstack([F,np.zeros((3,3))])],.981);self.assertIsNone(d['minimum_normal_sum_N'])
 def test_no_columns_not_measured(self):
  self.assertEqual(cone_lp([],.981)['status'],'NOT MEASURED_NO_COMPLETE_COLUMNS')
if __name__=='__main__':unittest.main()
