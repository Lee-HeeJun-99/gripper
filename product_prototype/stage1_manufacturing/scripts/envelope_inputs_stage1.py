"""Typed offline envelope loader; never silently substitute operating CAD."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(case,tag):
 if tag is None:return {}
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 j=json.loads((ROOT/'validation'/tag/'summary.json').read_text());assert j['case']==case and j['case_SHA256']==sha(ROOT/'cad/exports'/case/'summary.json');assert j['manufacturing_parts'] is False and j['status']=='STOCK_MAX_EXTERIOR_ENVELOPES_CLEAR'
 idx=json.loads((ROOT/'cad/exports'/case/'summary.json').read_text())
 for n,v in j['variants'].items():
  assert v['actual_manufacturing_part_SHA256']==idx['parts'][n]['sha256'];assert sha(ROOT/v['path'])==v['sha256'];assert sha((ROOT/v['path']).with_suffix('.stl'))==v['STL_sha256']
 return {n:(ROOT/v['path']).with_suffix('.stl') for n,v in j['variants'].items()}
