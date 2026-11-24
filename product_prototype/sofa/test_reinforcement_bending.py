import json,unittest
from analyse import BASE
def result(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class BendingContractTests(unittest.TestCase):
 def test_template_failure_preserved(self):
  d=result('reinforcement_bending1379');self.assertEqual(d['status'],'FAIL_MATCHED_DIAGNOSTIC');self.assertTrue(all(r['process']['exit_code']!=0 for r in d['records']))
 def test_strict_reference_failure_not_relaxed(self):
  d=result('reinforcement_bending1380');self.assertEqual(d['status'],'FAIL_MATCHED_DIAGNOSTIC');self.assertTrue(all(r['native_velocity_error_m_s']>1e-12 for r in d['records']));self.assertTrue(all(r['native_position_error_m']<1e-12 for r in d['records']))
 def test_material_addition_and_static_ratio(self):
  d=result('reinforcement_bending1380');b,c=d['records'];self.assertGreater(c['mass_kg'],b['mass_kg']);self.assertAlmostEqual(d['static_effective_stiffness_ratio'],b['static_compliance_m_N']/c['static_compliance_m_N']);self.assertGreater(d['static_effective_stiffness_ratio'],1)
 def test_inventory_not_native_energy(self):
  d=result('reinforcement_bending_inventory1381');self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertTrue(all(r['reference_work_energy_absolute_error_J']<1e-18 for r in d['records']));self.assertEqual([r['first_strict_velocity_failure_s'] for r in d['records']],[.01,.0125])
 def test_origin_is_not_general_fix(self):
  d=result('reinforcement_origin1382');self.assertEqual(d['status'],'FAIL_MATCHED_DIAGNOSTIC');self.assertGreater(d['records'][0]['native_velocity_error_m_s'],1e-12)
 def test_mapped_native_completion_not_equilibrium(self):
  d=result('reinforcement_mapped1384');self.assertTrue(d['originalGuideGraphEqual']);self.assertEqual(d['status'],'COMPLETED_MATCHED_GUIDE_MAPPING_COUPONS');self.assertTrue(all(r['outputs']==20 and r['minimum_core_saved_volume_ratio']>0 for r in d['records']))
 def test_rigid_pullback_virtual_work(self):
  d=result('reinforcement_mapped_reference1385');self.assertTrue(all(r['guide_count']==12 and r['virtual_work_pullback_error_J']<1e-24 for r in d['records']));self.assertGreater(d['effective_static_compliance_ratio'],1);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_static_newton_fail_not_equilibrium_pass(self):
  d=result('reinforcement_static1386');self.assertEqual(d['status'],'FAIL_STATIC_DIAGNOSTIC');self.assertTrue(all(r['native_in_reference_free_residual_N']>1e-12 for r in d['records']))
if __name__=='__main__':unittest.main()
