import unittest
from research_git_guard import forbidden
class TestGuard(unittest.TestCase):
 def test_limit_is_exact(self):
  self.assertFalse(forbidden('results/state.csv',99_999_999));self.assertTrue(forbidden('results/state.csv',100_000_000));self.assertTrue(forbidden('results/state.csv',128_561_058))
 def test_detector_always_forbidden(self):
  self.assertTrue(forbidden('product_prototype/results/a/detector.csv',1));self.assertFalse(forbidden('product_prototype/results/a/detection_pairs.csv',1))
 def test_layer_pairs_always_forbidden(self):
  self.assertTrue(forbidden('product_prototype/results/a/layer_pairs.csv',1))
if __name__=='__main__':unittest.main()
