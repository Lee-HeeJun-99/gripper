"""Read-only acceptance of an explicitly hash-bound same-input reassessment.

Never modifies original FAIL or admits runtime/clearance failures.
"""
import json
from curve_common import ROOT,sha
def require_completed(src,qualification=None):
 summary=json.loads((src/'summary.json').read_text())
 if summary['status']=='PASS':return None
 if not qualification:raise ValueError('actual original FAIL requires explicit matching-mass reassessment')
 path=ROOT/'results'/('autonomous_film_'+qualification);q=json.loads((path/'summary.json').read_text());case=src.name.removeprefix('autonomous_film_')
 if q['status']!='PASS' or q.get('actual')!=case or q.get('absolute_api_gate')!=1e-12 or max(q.get('errors',{'missing':1}).values())>1e-12 or not q.get('prior_fail_is_preserved'):raise ValueError('unsupported reassessment')
 if summary['process']['exit_code']!=0 or summary['sofa_error_count'] or summary['minimum_gap']< -1e-10:raise ValueError('runtime/physical failure cannot be bypassed')
 for name,digest in q['raw_hashes'][case].items():
  if sha(src/name)!=digest:raise ValueError('reassessed actual Raw changed:'+name)
 return dict(name=qualification,sha256=sha(path/'summary.json'),original_status=summary['status'],note='original FAIL preserved;reference input corrected,not new actual run')
