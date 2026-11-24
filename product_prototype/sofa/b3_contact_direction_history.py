"""Read-only active-response normal history;necessary bounds,not capacity."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def assess(name,out):
 src=BASE/'results'/name;rows=list(csv.DictReader((src/'object.csv').open()));times=[float(r['time_s']) for r in rows];index={t:i for i,t in enumerate(times)};active=[[] for _ in times];fz=np.zeros(len(times));seen=set()
 with (src/'response_rows.csv').open() as f:
  for r in csv.DictReader(f):
   models=r['model0']+r['model1']
   if '/object/'not in models or '/skinCollision/'not in models:continue
   t=float(r['time_s']);row=int(r['row_id']);assert (t,row)not in seen;seen.add((t,row));i=index[t];I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');fz[i]+=I[2]/.0025;lam=float(r['lambda_Ns'])
   if (row-int(r['first_row']))%3==0 and lam>0:
    n=I[:3]/lam;assert abs(np.linalg.norm(n)-1)<1e-8;active[i].append((lam/.0025,float(n[2]),float(n[2]+.3*np.linalg.norm(n[:2]))))
 records=[];barrier=[];deficit=[]
 for t,g,Fz,r in zip(times,active,fz,rows):
  coefficient=max((v[2] for v in g),default=None);bound=sum(v[0]*v[2] for v in g);state='NO_ACTIVE_NORMAL' if not g else 'ACTIVE_DIRECTION_BARRIER' if coefficient<=0 else 'MEASURED_ALLOCATION_DEFICIT' if bound<.981 else 'UPPER_BOUND_ONLY_NOT_HOLDING'
  if t>=1.2-1e-12:
   if state=='ACTIVE_DIRECTION_BARRIER':barrier.append(t)
   if state=='MEASURED_ALLOCATION_DEFICIT':deficit.append(t)
  records.append(dict(time_s=t,active_normals=len(g),min_nz=min((v[1] for v in g),default=None),max_nz=max((v[1] for v in g),default=None),normal_sum_N=sum(v[0] for v in g),measured_skin_Fz_N=float(Fz),optimistic_Fz_at_measured_normal_N=bound if g else None,max_vertical_force_per_unit_normal=coefficient,state=state,solver_iterations=int(r['solver_iterations'])))
 with (out/(name+'.csv')).open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 return dict(case=name,postwithdraw_first_active_direction_barrier_s=min(barrier) if barrier else None,postwithdraw_active_direction_barrier_samples=len(barrier),postwithdraw_measured_allocation_deficit_samples=len(deficit),samples=len(records),input_hashes={f:sha(src/f) for f in ('object.csv','response_rows.csv')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[assess(n,out) for n in ('b3_railback_grasp1001298','b3_railback_force_hold1306')];d=dict(status='ACTUAL_ACTIVE_NORMAL_HISTORY_ONLY',records=records,scope='Necessary force-direction upper bounds on actually active Skin normal rows only;not full contact-set infeasibility,causality,pressure,area or holding. Tangential redistribution uses assumedmu.3;no force increase suggested. Moment balance not solved by scalar bound.',physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
