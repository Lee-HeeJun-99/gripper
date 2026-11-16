"""Immutable v2 ledger; historical raw drift is an error, source evolution is audited."""
import argparse,hashlib,json,subprocess
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--verify',action='store_true');p.add_argument('--audit-old',action='store_true');a=p.parse_args();target=ROOT/'reports/FILM_CONTACT_EVIDENCE_20261116_v2.json'
 if a.verify:
  ledger=json.loads(target.read_text());bad=[key for key,value in ledger['files'].items() if not (ROOT/key).is_file() or sha(ROOT/key)!=value];print(json.dumps(dict(status='FAIL' if bad else 'PASS',files=len(ledger['files']),mismatches=bad)));raise SystemExit(bool(bad))
 if target.exists():raise RuntimeError('immutable evidence ledger already exists')
 old=json.loads((ROOT/'reports/FILM_NEWTON_EVIDENCE_20261116_v1.json').read_text());unchanged=0;evolved={};bad=[]
 for rel,digest in old['files'].items():
  file=ROOT/rel
  if file.is_file() and sha(file)==digest:unchanged+=1;continue
  if rel.startswith(('results/','build/','designs/')):bad.append(rel);continue
  historical=False
  for commit in ('04637d3b7bddf7d4aba3c58fe8d220ce2679becb',old['source_commit']):
   result=subprocess.run(['git','show',commit+':'+rel],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
   if result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==digest:historical=True;break
  if historical:evolved[rel]=dict(old=digest,current=sha(file) if file.is_file() else None,historical_commit=commit)
  else:bad.append(rel)
 if bad:raise RuntimeError('historical data drift:'+str(bad))
 if a.audit_old:
  print(json.dumps(dict(status='PASS',unchanged=unchanged,source_evolution=len(evolved),unexpected=bad)));return
 paths=set()
 for directory in (ROOT/'results').glob('autonomous_film_20261116_*'):
  paths.update(f for f in directory.rglob('*') if f.is_file() and '__pycache__' not in str(f))
 for pattern in ('models/film_shell/*','models/film_rail_tendon/*','models/film_native_contact/*','diagnostics/film_shell/*','diagnostics/film_rail_tendon/*','tests/test_film*','tools/film_*.py','reports/AUTONOMOUS_RESEARCH_*.md','reports/FILM_CONTACT_DYNAMICS_20261116.md','reports/FILM_SHELL_PHYSICS.md','reports/REGRIP_*.md','build/film_shell_20261116_*/libReGripFilmShell.so','build/film_rail_20261116_*/libReGripFilmRailTendon.so','build/film_native_20261116_*/libReGripFilmNativeObserver.so','build/film_native_installed_20261116_*/*/*.so'):
  paths.update(f for f in ROOT.glob(pattern) if f.is_file())
 for directory in ('contact_dynamics_20261116_actual56','film_rail_20261116_actual94','film_native_20261116_actual120','film_native_20261116_actual133'):
  paths.update(f for f in (ROOT/'designs/visualizations'/directory).glob('*') if f.is_file())
 statuses={}
 for directory in sorted((ROOT/'results').glob('autonomous_film_20261116_*')):
  file=directory/'summary.json'
  if file.exists():
   summary=json.loads(file.read_text());statuses[directory.name]={key:summary[key] for key in ('status','process_status','time_status','assembly_time_status','scope') if key in summary}
  else:statuses[directory.name]=dict(status='NOT QUALIFIED',reason='No final summary;not inferred PASS')
 ledger=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='actual contact dynamics and prototype evidence;NOT final grasp certification',historical_unchanged=unchanged,historical_source_evolution=evolved,unexpected_historical_changes=bad,campaign_statuses=statuses,notes=['107 launcher ET path exception occurred after build;no final summary,not a completed physics trial','Native fixed sphere projected zero Jacobian is not physical zero reaction','Partial discrete energy does not certify full ReGrip energy','No automatically restarted/background physics is claimed'],files={str(f.relative_to(ROOT)):sha(f) for f in sorted(paths)})
 write_json(target,ledger);print(json.dumps(dict(files=len(ledger['files']),old_unchanged=unchanged,old_source_evolution=len(evolved),unexpected=bad)))
if __name__=='__main__':main()
