"""Strict parent-hashed CAD delta resolver;never repairs missing/duplicate parts."""
import json
from pathlib import Path
from manufacturing_assembly import BASE,sha

def resolve_recipe(path,root=BASE,seen=None):
 root=Path(root).resolve();path=Path(path).resolve();seen=set() if seen is None else set(seen)
 if not path.is_relative_to(root) or path in seen:raise ValueError('external or cyclic recipe')
 seen.add(path);d=json.loads(path.read_text());inputs={str(path.relative_to(root)):sha(path)}
 if d.get('units')!='mm':raise ValueError('explicit mm recipe required')
 if 'parts' in d:parts=d['parts']
 else:
  parent=(root/d['parent_recipe']).resolve()
  if not parent.is_relative_to(root) or sha(parent)!=d['parent_SHA256']:raise ValueError('parent identity mismatch')
  parts,prior=resolve_recipe(parent,root,seen);inputs.update(prior);names=[p['name'] for p in parts];removed=d['remove_names'];add=d['add_parts']
  if len(removed)!=len(set(removed)) or not set(removed)<=set(names):raise ValueError('missing or duplicate removal')
  parts=[p for p in parts if p['name'] not in removed]+add
 names=[p['name'] for p in parts]
 if len(names)!=len(set(names)):raise ValueError('duplicate final part identity')
 return parts,inputs
