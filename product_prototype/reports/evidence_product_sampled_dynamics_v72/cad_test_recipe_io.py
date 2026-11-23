import csv,json,tempfile,unittest
from pathlib import Path
from assembly_recipe_io import resolve_recipe
from manufacturing_assembly import sha

class RecipeIOTests(unittest.TestCase):
 def test_completed_c1_chain_and_wire(self):
  from manufacturing_assembly import BASE
  parts,hashes=resolve_recipe(BASE/'results/product_remaining_f2lead975/assembly_delta_recipe.json')
  self.assertEqual(len(parts),283);self.assertEqual(len(hashes),5)
  d=json.loads((BASE/'results/product_remaining_f2wire976/summary.json').read_text())
  self.assertFalse(any(r['classification']=='UNRESOLVED_OBSTACLE' for r in d['intersections']))
 def test_service_does_not_become_motion_qualification(self):
  from manufacturing_assembly import BASE
  for n,finger in [('product_remaining_f1service977',1),('product_remaining_f2service978',2),('product_completed_f0service979',0)]:
   d=json.loads((BASE/'results'/n/'summary.json').read_text());self.assertEqual(d['target_finger'],finger)
   self.assertFalse(any(r['intersections'] for r in d['records']));self.assertFalse(d['actual_locking_or_preload_qualified'])
   self.assertTrue(any(r['type']=='SAMPLED_DIAGONAL_ASSEMBLY_REMOVAL' for r in d['records']))
 def test_BOM_does_not_invent_material_mass(self):
  from manufacturing_assembly import BASE
  with (BASE/'results/product_resolved_BOM980/assembly_instance_BOM.csv').open() as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),283);self.assertEqual(len({r['instance'] for r in rows}),283)
  self.assertTrue(all(r['actual_mass_g']=='NULL' and r['actual_material']=='NULL' for r in rows))
 def test_actual_chain_has_unique_ids(self):
  from manufacturing_assembly import BASE
  parts,hashes=resolve_recipe(BASE/'results/product_remaining_c1lead971/assembly_delta_recipe.json')
  self.assertEqual(len(parts),281);self.assertEqual(len({p['name'] for p in parts}),281);self.assertEqual(len(hashes),3)
 def test_bad_parent_and_duplicate_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);p=root/'parent.json';p.write_text(json.dumps(dict(units='mm',parts=[dict(name='a')])))
   d=dict(units='mm',parent_recipe='parent.json',parent_SHA256=sha(p),remove_names=[],add_parts=[dict(name='a')]);q=root/'delta.json';q.write_text(json.dumps(d))
   with self.assertRaisesRegex(ValueError,'duplicate'):resolve_recipe(q,root)
   d['add_parts']=[];d['remove_names']=['absent'];q.write_text(json.dumps(d))
   with self.assertRaisesRegex(ValueError,'missing'):resolve_recipe(q,root)
   d['remove_names']=[];d['parent_SHA256']='0'*64;q.write_text(json.dumps(d))
   with self.assertRaisesRegex(ValueError,'identity'):resolve_recipe(q,root)
 def test_external_and_duplicate_full_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);p=root/'x.json';p.write_text(json.dumps(dict(units='mm',parts=[dict(name='a'),dict(name='a')])))
   with self.assertRaisesRegex(ValueError,'duplicate'):resolve_recipe(p,root)
   with self.assertRaisesRegex(ValueError,'external'):resolve_recipe(root.parent/'outside.json',root)
