"""Analytic reference/protocol regressions, not physical joint approval."""
import unittest
import numpy as np
from guide_joint_load_reference import point_wrench
from joint_bench_protocol import plans,validate_joint_record
from prototype_protocol import measurement_unit

class JointReferenceTests(unittest.TestCase):
 def test_antiparallel_equal_tension(self):
  F,M,_,_=point_wrench([0,0,0],[1,0,0],[-1,0,0],[0,20,0],1.5,1.5)
  np.testing.assert_array_equal(F,[0,0,0]);np.testing.assert_array_equal(M,[0,0,0])
 def test_unequal_tension_millimetre_moment(self):
  F,M,_,_=point_wrench([0,0,0],[1,0,0],[-1,0,0],[0,20,0],3,.5)
  np.testing.assert_allclose(F,[2.5,0,0]);np.testing.assert_allclose(M,[0,0,.05])
 def test_rigid_motion_objectivity(self):
  args=np.array([[1,2,3],[4,2,3],[1,5,3],[0,0,0]],float)
  Q=np.array([[0,-1,0],[1,0,0],[0,0,1]])
  F,M,_,_=point_wrench(*args,2,3)
  f,m,_,_=point_wrench(*(args@Q.T+[7,8,9]),2,3)
  np.testing.assert_allclose(f,Q@F);np.testing.assert_allclose(m,Q@M)
 def test_invalid_load_or_leg(self):
  for T in (-1,float('nan'),float('inf')):
   with self.assertRaises(ValueError):point_wrench([0,0,0],[1,0,0],[-1,0,0],[0,0,0],T,1)
  with self.assertRaises(ValueError):point_wrench([0,0,0],[0,0,0],[-1,0,0],[0,0,0],1,1)
 def test_protocol_does_not_fabricate_results(self):
  p=plans();self.assertEqual(len(p),6)
  for test in p:
   self.assertEqual(test['status'],'NOT RUN');self.assertFalse(test['physical_qualified_pass'])
   self.assertTrue(all(v is None for v in test['physical_measurements'].values()))
 def test_unmeasured_unit_guard(self):
  r=dict(status='NOT MEASURED',value=None,metric='preload_N',units=measurement_unit('preload_N'))
  validate_joint_record(r)
  with self.assertRaises(ValueError):validate_joint_record(dict(r,units='mm'))
