"""Maintenance geometry and dependency guards;not physical service approval."""
import json,unittest
from manufacturing_assembly import BASE,union,cyl
from root_disconnect import bolt_envelopes
from root_service_plan import order_steps

def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())

class RootDisconnectTests(unittest.TestCase):
 def test_dependency_validation_rejects_cycles_unknowns_duplicates(self):
  for steps in ([dict(id='a',requires=['a'])],[dict(id='a',requires=['missing'])],[dict(id='a',requires=[]),dict(id='a',requires=[])]):
   with self.assertRaises(ValueError):order_steps(steps)
  self.assertEqual(order_steps([dict(id='b',requires=['a']),dict(id='a',requires=[])]),['a','b'])
 def test_bolt_envelope_requires_real_two_cylinder_description(self):
  _,_,d=bolt_envelopes(union(cyl(1.5,0,12),cyl(2.75,12,15)))
  self.assertEqual(d['axis_screen_radius_mm'],2.75)
  with self.assertRaises(ValueError):bolt_envelopes(cyl(1.5,0,12))
  with self.assertRaises(ValueError):bolt_envelopes(union(cyl(1.5,0,11),cyl(2.75,12,15)))
 def test_internal_bonds_not_cut_in_declared_cartridge_partition(self):
  d=result('product_root_disconnect1030');self.assertEqual(len(d['records']),6)
  self.assertTrue(all(not c['needs_internal_bond_cut_for_DECLARED_partition'] for c in d['cartridge_partitions']))
  self.assertFalse(any(r['axis_envelope_intersections'] for r in d['records']))
  self.assertTrue(all(r['actual_drive_geometry'] is None for r in d['records']))
 def test_valid_plan_is_not_executed_service(self):
  d=result('product_root_service_plan1031');self.assertEqual(d['physical_steps_executed'],0)
  self.assertTrue(all(r['status']=='BLOCKED_NOT_PHYSICALLY_EXECUTED' for r in d['records']))
  self.assertFalse(d['physical_service_qualified'])
 def test_integral_roof_retains_candidate_count_and_mating_review(self):
  d=result('product_root_nut_hood1032');self.assertEqual(d['candidate_part_count'],294)
  self.assertEqual(d['status'],'ROOT_NUT_HOOD_STATIC_REVIEW');self.assertEqual(len(d['solid_intersections']),3)
  d=result('product_root_hood_access1033');self.assertFalse(any(r['axis_envelope_intersections'] for r in d['records']))
 def test_actual_nut_axial_obstruction_not_retention_force(self):
  d=result('product_root_nut_capture1034');rows=d['records'];self.assertEqual(len(rows),16)
  self.assertFalse(any(r['intersections'] for r in rows if r['translation_root_Z_mm']==.025))
  self.assertTrue(all(any(h['part']=='f0_root_clamp' for h in r['intersections']) for r in rows if r['translation_root_Z_mm']==.1))
  self.assertIsNone(d['actual_nut_retention_N'])
 def test_static_clamp_can_still_fail_pad_service(self):
  self.assertEqual(result('product_drum_wire_clamp1035')['candidate_part_count'],297)
  self.assertFalse(result('product_drum_wire_clamp1035')['solid_intersections'])
  rows=result('product_drum_clamp_service1036')['service_records']
  self.assertTrue(any(r['intersections'] for r in rows if r['operation']=='ACTUAL_PAD_TRANSLATION_SAMPLED_ONLY'))
 def test_side_breakout_clear_only_unloaded_geometry(self):
  d=result('product_drum_pad_service1038');self.assertFalse(any(r['intersections'] for r in d['service_records']+d['free_end_wire_records']))
  self.assertIsNone(d['actual_pullout_N']);self.assertFalse(d['physical_service_qualified'])
  self.assertIn('results/product_supplier_first_recheck890/summary.json',d['input_hashes'])
 def test_changed_hood_and_drum_get_new_cartridge_samples(self):
  d=result('product_root_hood_cartridge1040');self.assertEqual(d['assembly_part_count'],297)
  self.assertEqual(len(d['records']),8);self.assertFalse(any(r['intersections'] for r in d['records']))
  self.assertFalse(d['physical_service_qualified'])
