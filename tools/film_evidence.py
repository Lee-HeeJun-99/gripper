"""Immutable film campaign integrity ledger,not physical approval."""
import argparse,hashlib,json,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--verify',action='store_true');a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 manifest=ROOT/'reports'/('FILM_RESEARCH_EVIDENCE_'+a.tag+'.json')
 if a.verify:
  d=json.loads(manifest.read_text());bad=[f for f,h in d['files'].items()if not(ROOT/f).is_file()or sha(ROOT/f)!=h];print(json.dumps(dict(integrity='FAIL'if bad else'PASS',count=len(d['files']),bad=bad)));raise SystemExit(bool(bad))
 if manifest.exists():raise FileExistsError('immutable manifest')
 out=ROOT/'results'/('autonomous_film_evidence_'+a.tag);out.mkdir(exist_ok=False)
 tests={}
 for name,cmd in [('new_design',['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s','tests','-p','test_film_design.py','-v']),('old_design',['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s','tests','-p','test_design_regrip.py','-v']),('ldd',['ldd',ROOT/'build/film_shell_20261116_matrix_probe/libReGripFilmShell.so'])]:tests[name]=logged(cmd,out/name,120)
 old=json.loads((ROOT/'reports/DESIGN_TEMPORAL_EVIDENCE_20261116_v1.json').read_text());drift=[];unexpected=[]
 for f,h in old['files'].items():
  if (ROOT/f).is_file()and sha(ROOT/f)==h:continue
  if f.startswith('reports/REGRIP_'):
   historical=subprocess.check_output(['git','show','099847b:'+f],cwd=ROOT)
   if hashlib.sha256(historical).hexdigest()==h:drift.append(f);continue
  unexpected.append(f)
 write_json(out/'previous_ledger.json',dict(historical_commit='099847b',historical_docs_verified=drift,unexpected_changes=unexpected,current_full_old_ledger='FAIL for intentionally updated reports;old manifest is not edited',raw_source_binary_unchanged='PASS'if not unexpected else'FAIL'))
 roots=[ROOT/'models/film_shell',ROOT/'diagnostics/film_shell',ROOT/'designs/film_contact/equal_volume_v1',ROOT/'designs/film_contact/equal_volume_v2',ROOT/'designs/visualizations/film_actual_v1']
 roots+=list((ROOT/'results').glob('autonomous_film_*'))+list((ROOT/'results').glob('autonomous_temporal_exact_*'))
 files={}
 for root in roots:
  for f in root.rglob('*'):
   if f.is_file()and not f.is_symlink():files[str(f.relative_to(ROOT))]=sha(f)
 for pattern in ['tools/film_*.py','tools/sphere_temporal_reference.py','tests/test_film*.cpp','tests/test_film*.py','reports/FILM_SHELL_PHYSICS.md','reports/REGRIP*.md']:
  for f in ROOT.glob(pattern):files[str(f.relative_to(ROOT))]=sha(f)
 write_json(manifest,dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='New artifact integrity only. Physical dynamics/mesh/global energy/grasp still FAIL/BLOCKED. Immutable snapshots identify actual compiled dirty source.',test_exit_codes={k:v['exit_code']for k,v in tests.items()},historical_raw_status='PASS'if not unexpected else'FAIL',files=dict(sorted(files.items()))))
 print(json.dumps(dict(manifest=str(manifest),files=len(files),unexpected_old_changes=unexpected)))
if __name__=='__main__':main()
