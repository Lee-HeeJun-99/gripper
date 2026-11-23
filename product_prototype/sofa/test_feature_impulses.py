import unittest
from primitive_feature_impulses import assess
class TestFeatureImpulse(unittest.TestCase):
 def test_actual_feature_impulse_join(self):
  for c in ('primitive_center_impulses1247','primitive_offset_impulses1248'):
   r=assess(c);self.assertEqual(r['maximum_impulse_join_error_Ns'],0.)
 def test_nearly_parallel_rows_are_scoped_not_native_W(self):
  r=assess('primitive_center_impulses1247');self.assertTrue(any(x['normal_gram_condition']>1e8 and x['solver_iterations']>=1000 for x in r['records']));self.assertIn('NOT direct Native W',r['scope'])
if __name__=='__main__':unittest.main()
