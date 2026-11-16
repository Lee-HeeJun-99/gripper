import itertools
import math
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_contact_metrics import circular_span_radians

class TestContactMetrics(unittest.TestCase):
    def test_order_and_branch_cut(self):
        for values,target in (([179,-179,180],2),([0,90,180,270],270),([30,30],0),([7],0)):
            for order in itertools.permutations(values):
                self.assertAlmostEqual(math.degrees(circular_span_radians(map(math.radians,order))),target,places=11)
        self.assertIsNone(circular_span_radians([]))
    def test_bad_angle(self):
        with self.assertRaises(ValueError):circular_span_radians([float('nan')])

if __name__=='__main__':unittest.main()
