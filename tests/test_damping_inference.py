import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from curve_damping_assess import certificate


class ActualMatrixInference(unittest.TestCase):
    def test_negative_direction(self):
        M=np.diag([.2,.3]);J=np.diag([5.,-7.]);h=.00025;alpha=2.;beta=.1
        A=(1+h*alpha)*M-h*(h+beta)*J
        result=certificate(M,A,h,alpha,beta,[0,1],5)
        self.assertEqual(result['status'],'FAIL')
        self.assertAlmostEqual(result['candidate_velocity_quadratic_damping'],-.1,places=11)

    def test_nonsymmetric_jacobian_uses_symmetric_power(self):
        M=np.eye(2);J=np.array([[-2.,30.],[-30.,-4.]]);h=.000125;alpha=2.;beta=.1
        A=(1+h*alpha)*M-h*(h+beta)*J
        result=certificate(M,A,h,alpha,beta,[0,1],5)
        self.assertEqual(result['status'],'EXPERIMENTAL')
        self.assertAlmostEqual(result['candidate_velocity_quadratic_damping'],2.2,places=10)

    def test_unit_congruence_preserves_negative_sign(self):
        M=np.eye(6);J=np.diag([-1.,-1.,-1.,30.,-1.,-1.]);h=.00025;alpha=2.;beta=.1
        A=(1+h*alpha)*M-h*(h+beta)*J
        for length in(.1,5.,100.):
            result=certificate(M,A,h,alpha,beta,list(range(6)),length)
            self.assertEqual(result['status'],'FAIL')
            self.assertLess(result['candidate_velocity_quadratic_damping'],0)


if __name__=='__main__':unittest.main()
