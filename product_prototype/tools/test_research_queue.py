import unittest
from research_queue import select
def task(i,status='READY',deps=None):return dict(id=i,status=status,scope='Component only',priority=1,prerequisites=deps or [])
class QueueTest(unittest.TestCase):
 def test_failed_dependency_blocks(self):
  r=select(dict(tasks=[task('a','FAIL'),task('b',deps=['a'])]));self.assertIsNone(r['next']);self.assertTrue(r['requires_project_reevaluation'])
 def test_pass_dependency_selects(self):
  r=select(dict(tasks=[task('a','PASS'),task('b',deps=['a'])]));self.assertEqual(r['next']['id'],'b');self.assertIn('successors',r['next']);self.assertFalse(r['qualified_product'])
 def test_rejected_allowed_and_missing_dependency_fails(self):
  self.assertIsNone(select(dict(tasks=[task('a','REJECTED')]))['next'])
  with self.assertRaises(AssertionError):select(dict(tasks=[task('b',deps=['missing'])]))
 def test_running_is_not_empty_project(self):
  r=select(dict(tasks=[task('a','RUNNING')]));self.assertEqual(r['running'],['a']);self.assertFalse(r['requires_project_reevaluation'])
 def test_explicit_failure_diagnosis_not_physics_pass(self):
  b=task('b',deps=['a']);b['prerequisite_states']={'a':['PASS','FAIL']}
  r=select(dict(tasks=[task('a','FAIL'),b]));self.assertEqual(r['next']['id'],'b');self.assertFalse(r['qualified_product'])
if __name__=='__main__':unittest.main()
