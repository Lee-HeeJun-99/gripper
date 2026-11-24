"""Independent geometric checks; no constitutive/material qualification."""
import unittest
import numpy as np
from wire_bend_demand_inventory import curvature

class BendDemandTest(unittest.TestCase):
    def test_straight(self):
        np.testing.assert_array_equal(curvature(np.array([[0.,0,0],[1,0,0],[2,0,0]])),[0.])

    def test_circle_and_rigid_motion(self):
        a=np.linspace(-.6,.6,13);r=.008
        p=np.column_stack((r*np.cos(a),r*np.sin(a),np.zeros(len(a))))
        np.testing.assert_allclose(curvature(p),1/r,rtol=1e-12)
        rotated=p[:,[2,0,1]]+np.array([.02,-.03,.04])
        np.testing.assert_allclose(curvature(rotated),curvature(p),rtol=1e-11)

    def test_degenerate_rejected(self):
        with self.assertRaises(ValueError):
            curvature(np.zeros((3,3)))

if __name__=='__main__':unittest.main()
