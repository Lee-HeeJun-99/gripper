"""Strict contact-observable comparison, not motion/full-grasp qualification."""
import argparse,csv,json,math
from pathlib import Path
from curve_common import ROOT,write_json,sha

def difference(a,b):
 absolute=abs(a-b)
 return dict(absolute=absolute,relative=(absolute/abs(b)if b else (0 if not a else None)),undefined_nonzero_reference=(b==0 and a!=0))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--kind',choices=['time','integration'],required=True);p.add_argument('cases',nargs='+');a=p.parse_args()
 if not a.tag.replace('_','').isalnum()or len(a.cases)<2:raise ValueError('fresh tag and cases')
 out=ROOT/'results'/('vector_history_compare_'+a.tag);out.mkdir(exist_ok=False)
 paths=[ROOT/'results'/('vector_history_moving_'+s)for s in a.cases]
 identities=[json.loads((q/'identity.json').read_text())for q in paths]
 rows=[list(csv.DictReader((q/'contact.csv').open()))for q in paths]
 for d,r,q in zip(identities,rows,paths):
  if json.loads((q/'summary.json').read_text())['status']!='PASS':raise ValueError('failed source case')
  if len(r)!=d['steps']:raise ValueError('incomplete trace')
  if d['binary_sha256']!=identities[0]['binary_sha256']or d['speed']!=identities[0]['speed']:raise ValueError('different model/load')
  if not math.isclose(d['dt']*d['steps'],identities[0]['dt']*identities[0]['steps'],rel_tol=1e-12):raise ValueError('different duration')
  for key in (['spacing']if a.kind=='time'else['dt','steps']):
   if d[key]!=identities[0][key]:raise ValueError('mixed experimental factors')
 limit=.001 if a.kind=='time'else .01
 contrasts=[]
 for i in range(len(rows)-1):
  for j in range(i+1,len(rows)):
   metrics={k:difference(float(rows[i][-1][k]),float(rows[j][-1][k]))for k in ('normal_force','friction_dissipation','elastic_energy','Fz','Mx')}
   # Phase increments cannot be hidden by final accumulated loss.
   phases=[];fine={round(float(r['time']),12):r for r in rows[j]};prior0=prior1=0
   for r in rows[i]:
    t=round(float(r['time']),12)
    if t not in fine:continue
    u=fine[t];d0=float(r['friction_dissipation']);d1=float(u['friction_dissipation'])
    phases.append(dict(time=t,**difference(d0-prior0,d1-prior1)));prior0=d0;prior1=d1
   check=list(metrics.values())+phases
   passed=all(v['relative']is not None and v['relative']<=limit for v in check)
   contrasts.append(dict(cases=[a.cases[i],a.cases[j]],status='PASS'if passed else'FAIL',final=metrics,phase_loss=phases))
 result=dict(status='PASS'if all(c['status']=='PASS'for c in contrasts)else'FAIL',scope='short sphere/Hermite contact observables;NOT mesh or full gripper/motion/energy qualification',threshold=limit,contrasts=contrasts,inputs={str(q.relative_to(ROOT)):sha(q/'contact.csv')for q in paths})
 write_json(out/'assessment.json',result);print(json.dumps(dict(out=str(out),status=result['status'])))
if __name__=='__main__':main()
