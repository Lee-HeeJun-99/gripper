"""All cross-finger response sources, including hidden hardware/foreign Skin.
Native scalar impulse is not a body force or contact area.
"""
import argparse,csv,json,re
from pathlib import Path
from analyse import BASE,sha

def identify(path):
 m=re.match(r'/(guides|finger)(\d+)/',path)
 if not m:return None
 return int(m[2]),('hardware' if m[1]=='guides' else 'skin' if '/skinCollision/'in path else 'rail' if '/railCollision/'in path else 'other_finger')

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);groups={};active=hold=0
 for r in csv.DictReader((src/'response_rows.csv').open()):
  paths=[r[k] for k in ('model0','model1')];ids=[identify(x) for x in paths]
  if any(x is None for x in ids) or ids[0][0]==ids[1][0] or float(r['lambda_Ns'])==0:continue
  t=float(r['time_s']);key=' | '.join(sorted(paths));d=groups.setdefault(key,dict(kind='-'.join(sorted(x[1] for x in ids)),first_s=t,last_s=t,nonzero_rows=0,hold_nonzero_rows=0,maximum_abs_multiplier_Ns=0.));d['last_s']=t;d['nonzero_rows']+=1;d['maximum_abs_multiplier_Ns']=max(d['maximum_abs_multiplier_Ns'],abs(float(r['lambda_Ns'])));d['hold_nonzero_rows']+=int(1.6-1e-12<=t<=2+1e-12);active+=1;hold+=int(1.6-1e-12<=t<=2+1e-12)
 d=dict(status='NO_NONZERO_CROSS_FINGER_RESPONSE' if active==0 else 'CROSS_FINGER_INTERNAL_RESPONSE_PRESENT',case=a.case,nonzero_rows=active,hold_nonzero_rows=hold,source_pairs=groups,scope='All actual response rows between DIFFERENT fingers (Skin/Rail/hardware),not just GuideGuide. Same-finger bonds/groups intentionally outside this test. No time/swept/energy/finite-wire/material qualification; scalar lambda NOT full wrench.',input_sha256=sha(src/'response_rows.csv'),source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
