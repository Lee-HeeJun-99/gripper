import unittest
from primitive_work_inventory import inventory
class TestWork(unittest.TestCase):
 def test_actual_discrete_identity(self):
  for case in ('primitive_offset_slip1230','primitive_offset_stick1231','primitive_offset_sliding1232'):
   r,_=inventory(case);self.assertEqual(r['status'],'PASS_TRANSLATIONAL_DISCRETE_IDENTITY_ONLY');self.assertLess(abs(r['cumulative_balance_J']),1e-16);self.assertIsNone(r['whole_system_energy']);self.assertIsNone(r['fixture_reaction_work'])
 def test_numerical_loss_not_physical_friction(self):
  r,_=inventory('primitive_offset_sliding1232');self.assertGreater(r['BE_numerical_loss_J'],0);self.assertLess(r['tangential_contact_work_J'],0);self.assertNotEqual(r['BE_numerical_loss_J'],-r['tangential_contact_work_J'])
if __name__=='__main__':unittest.main()
