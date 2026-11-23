"""Current static assembly identity guards; not physical qualification."""
import json,unittest
from manufacturing_assembly import BASE
from incremental_wire_audit import changed_shapes

def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())

class IncrementalServiceTests(unittest.TestCase):
 def test_identical_geometry_not_new_study(self):
  p=dict(name='part',shape={'op':'box'})
  with self.assertRaises(ValueError):changed_shapes([p],[dict(p,group='metadata')])
 def test_missing_part_requires_full_audit(self):
  with self.assertRaises(ValueError):changed_shapes([dict(name='a',shape={})],[])
 def test_path_geometry_change_requires_new_paths(self):
  with self.assertRaises(ValueError):changed_shapes([dict(name='f0_eyelet',shape={'a':1})],[dict(name='f0_eyelet',shape={'a':2})])
 def test_all_hood_indexed_keys_retain_review(self):
  d=result('product_all_hood_drive1055');self.assertEqual(len(d['records']),6)
  self.assertEqual(d['status'],'CATALOG_ROOT_DRIVE_GEOMETRY_REVIEW')
  self.assertFalse(any(r['indexed_shank_vs_other_hardware'] for r in d['records']))
 def test_incremental_six_paths_and_two_changed_parts(self):
  d=result('product_all_hood_wire1056');self.assertEqual(len(d['changed_geometry_names']),2)
  self.assertEqual(d['unchanged_geometry_count'],298);self.assertEqual(len(d['records']),6)
  self.assertEqual(sum(r['probe_count'] for r in d['records']),4290)
  self.assertFalse(any(r['intersections'] for r in d['records']))
  self.assertFalse(d['physical_dynamic_clearance_qualified'])
 def test_current_bom_not_mass_or_fabrication_certificate(self):
  d=result('product_current_BOM1057');self.assertEqual(d['instances'],300)
  self.assertFalse(d['invalid_solids']);self.assertIsNone(d['actual_assembly_mass_g'])
  self.assertFalse(d['STEP_generated']);self.assertFalse(d['fabrication_ready'])
