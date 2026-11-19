"""Check inherited immutable artifacts while explicitly excluding edited live source."""
import argparse,json,shutil
from pathlib import Path
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--ledger-name',default='20261119_tendon_v13');a=p.parse_args()
 if not a.ledger_name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in a.ledger_name):raise ValueError('ledger identifier required')
 ledger=ROOT/'reports'/('FILM_CONTACT_EVIDENCE_'+a.ledger_name+'.json');m=json.loads(ledger.read_text());out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');changed=[];checked=0;excluded=[]
 for name,digest in m['files'].items():
  if not (name.startswith(('results/','build/','designs/')) or Path(name).is_absolute()):excluded.append(name);continue
  path=Path(name) if Path(name).is_absolute() else ROOT/name;checked+=1
  if not path.is_file() or sha(path)!=digest:changed.append(name)
 r=dict(status='PASS' if not changed else 'FAIL',scope='inherited Raw/compiled-source archives/build/design/absolute-SDK artifact byte integrity ONLY;NOT live-source equivalence or physics certification',ledger_sha256=sha(ledger),ledger_source_commit=m['source_commit'],checked=checked,changed=changed,excluded_live_repository_files=excluded,exclusion_reason='Current source/reports intentionally developed;old archived compiled sources remain checked. Do not call the old live-root ledger unchanged.');write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='excluded_live_repository_files'}))
if __name__=='__main__':main()
