"""Immutable integrity ledger, NOT a physical qualification or old-manifest edit."""
import argparse,json,subprocess
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--verify',action='store_true');a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 target=ROOT/'reports'/('DESIGN_TEMPORAL_EVIDENCE_'+a.tag+'.json')
 if a.verify:
  data=json.loads(target.read_text());bad=[p for p,h in data['files'].items()if not(ROOT/p).is_file()or sha(ROOT/p)!=h]
  print(json.dumps(dict(integrity='FAIL'if bad else'PASS',files=len(data['files']),bad=bad)));raise SystemExit(bool(bad))
 if target.exists():raise FileExistsError('immutable manifest')
 roots=[ROOT/'designs',ROOT/'models/moving_sphere_benchmark',ROOT/'models/sphere_event_benchmark',ROOT/'diagnostics/temporal_event']
 for pattern in ['vector_history_moving_return_20261116_*','vector_history_moving_sphere_20261116_*','vector_history_moving_path_20261116_*','vector_history_sphere_event_20261116_*','sphere_event_prescribed_20261116_*','autonomous_design_20261116_*']:roots+=list((ROOT/'results').glob(pattern))
 files={}
 for base in roots:
  for f in base.rglob('*'):
   if f.is_file()and not f.is_symlink():files[str(f.relative_to(ROOT))]=sha(f)
 for pattern in ['models/general_vector_history/Moving*','models/general_vector_history/SphereEvent*','tests/test_moving*','tests/test_sphere_event*','tests/test_design_regrip.py','tools/moving_sphere_run.py','tools/sphere_event*.py','tools/design*.py','reports/REGRIP_*.md']:
  for f in ROOT.glob(pattern):
   if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
 write_json(target,dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='Artifact integrity only. Active-contact time PASS is not original CurvedContact/grasp qualification. Sphere birth time still FAIL; design meshes are concepts.',files=dict(sorted(files.items()))))
 print(json.dumps(dict(manifest=str(target),files=len(files))))
if __name__=='__main__':main()
