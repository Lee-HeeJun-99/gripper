"""Independent kernel sanity checks; not gripper performance tests."""
import unittest
import numpy as np
import trimesh
from finite_csg64 import boolean64

class FiniteCSG64Tests(unittest.TestCase):
    def boxes(self):
        a=trimesh.creation.box([.002]*3)
        b=a.copy();b.apply_translation([.001,0,0]);return a,b
    def test_analytic_intersection_and_difference(self):
        a,b=self.boxes()
        hit=boolean64([a,b],'intersection');remaining=boolean64([a,b],'difference')
        self.assertTrue(hit.is_volume and remaining.is_volume)
        self.assertLess(abs(hit.volume/4e-9-1),1e-12)
        self.assertLess(abs(remaining.volume/4e-9-1),1e-12)
    def test_translation_does_not_change_volume_or_inputs(self):
        a,b=self.boxes();a.apply_translation([.03,-.02,.1]);b.apply_translation([.03,-.02,.1])
        before=a.vertices.copy();hit=boolean64([a,b],'intersection')
        np.testing.assert_array_equal(a.vertices,before)
        self.assertLess(abs(hit.volume/4e-9-1),1e-12)
    def test_empty_intersection_is_empty_not_nan_volume(self):
        a,b=self.boxes();b.apply_translation([.01,0,0]);hit=boolean64([a,b],'intersection')
        self.assertEqual(len(hit.faces),0)
    def test_open_input_rejected(self):
        a,b=self.boxes();a.update_faces(np.arange(len(a.faces)-1))
        with self.assertRaises(ValueError):boolean64([a,b],'intersection')

if __name__=='__main__':unittest.main()
