"""Verify inherited immutable RAW/build/SDK bytes, separately from evolving sources."""
import argparse,json,shutil
from pathlib import Path
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ledger=ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_recovery_v12.json';data=json.loads(ledger.read_text());selected={k:v for k,v in data['files'].items() if k.startswith(('results/','build/','/'))};changed=[]
 for name,digest in selected.items():
  path=Path(name) if Path(name).is_absolute() else ROOT/name
  if not path.is_file() or sha(path)!=digest:changed.append(name)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if not changed else 'FAIL',scope='inherited immutable RAW/build/SDK byte preservation ONLY;NOT physics or unchanged live-source certification',ledger_sha256=sha(ledger),checked=len(selected),changed=changed,excluded_evolving_source_and_reports=len(data['files'])-len(selected));write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
