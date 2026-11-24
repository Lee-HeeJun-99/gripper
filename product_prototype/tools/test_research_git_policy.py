import unittest
from research_git_guard import forbidden

class Policy(unittest.TestCase):
 def test_new_50MB_limit(self):
  self.assertFalse(forbidden('results/surface.csv',49_999_999))
  self.assertTrue(forbidden('results/surface.csv',50_000_000))
 def test_excluded_journals_any_size(self):
  for name in ('detector.csv','layer_pairs.csv'):self.assertTrue(forbidden('results/'+name,0))
if __name__=='__main__':unittest.main()
