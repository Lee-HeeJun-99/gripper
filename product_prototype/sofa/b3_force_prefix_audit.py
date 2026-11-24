"""Strict recorded-state prefix equivalence;not time convergence."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);short=BASE/'results/b3_railback_force_contact1303';full=BASE/'results/b3_railback_force_hold1306';records=[]
 for name in ('object.csv','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv','constraints.csv','support.csv'):
  count=0;error=0.;text_equal=True
  with (short/name).open() as f,(full/name).open() as g:
   rr=csv.DictReader(f);ss=csv.DictReader(g);assert rr.fieldnames==ss.fieldnames
   for r in rr:
    b=next(ss);count+=1
    for key in r:
     try:x=np.array([float(v) for v in r[key].split()]);y=np.array([float(v) for v in b[key].split()])
     except ValueError:
      text_equal &= r[key]==b[key]
      continue
     assert x.shape==y.shape and np.isfinite(x).all() and np.isfinite(y).all()
     if len(x):error=max(error,float(abs(x-y).max()))
     else:text_equal &= r[key]==b[key]
  assert count==480;records.append(dict(file=name,compared_outputs=count,max_numeric_error=error,text_fields_equal=text_equal,short_sha256=sha(short/name),full_sha256=sha(full/name)))
 d=dict(status='PASS_STRICT_PREFIX_ONLY' if all(r['max_numeric_error']<=1e-12 and r['text_fields_equal'] for r in records) else 'FAIL_PREFIX',records=records,tolerance=1e-12,physical_validation='NOT QUALIFIED',scope='Actual recorded q/v/commands/impulses/solver fields on identical dt/force prefix;not interpolation or state correction,not time-step convergence or grasp success.');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
