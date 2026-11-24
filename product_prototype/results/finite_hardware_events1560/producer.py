"""Actual nonzero Guide-Guide response chronology, not inferred contact area."""
import argparse,csv,json,re
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);events={}
 for r in csv.DictReader((src/'response_rows.csv').open()):
  paths=[r['model0'],r['model1']];m=[re.match(r'/guides(\d+)/cable(\d+)/',s) for s in paths]
  if not all(m) or m[0][1]==m[1][1] or float(r['lambda_Ns'])==0:continue
  t=float(r['time_s']);key=' | '.join(sorted(paths));e=events.setdefault(key,dict(first_s=t,last_s=t,rows=0,hold_rows=0,maximum_abs_multiplier_Ns=0.));e['last_s']=t;e['rows']+=1;e['hold_rows']+=int(1.6-1e-12<=t<=2+1e-12);e['maximum_abs_multiplier_Ns']=max(e['maximum_abs_multiplier_Ns'],abs(float(r['lambda_Ns'])))
 d=dict(case=a.case,status='INDIRECT_BRACING_NOT_EXCLUDED' if events else 'NO_NONZERO_GUIDE_PAIR_ROWS_IN_OBSERVED_WINDOW',events=events,scope='Actual Native response chronology only. Absence before1.6s does not qualifyHolding. Presence can brace fingers even withzeroGuideObjectload. Notfullbodywrench,CCD orphysicalPASS.',source_sha256=sha(Path(__file__)),input_sha256=sha(src/'response_rows.csv'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
