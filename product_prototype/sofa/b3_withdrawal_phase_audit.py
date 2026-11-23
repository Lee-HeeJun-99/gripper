"""Time ordering of actual object slip,normal direction and solver limits."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def first_time(t,mask):return float(t[np.flatnonzero(mask)[0]]) if mask.any() else None
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];hashes={}
 for case,wrench in [('b3_alarm_window485','b3_mass50_wrench1099'),('b3_mass100_explore1059','b3_mass100_wrench1067')]:
  src=BASE/'results'/case;wp=BASE/'results'/wrench/'wrenches.csv';obj=read(src/'object.csv');wr=read(wp);t=np.array([float(r['time_s']) for r in obj]);tw=np.array([float(r['time_s']) for r in wr]);
  if not np.array_equal(t,tw):raise ValueError('actual phase clocks disagree')
  z=np.array([np.fromstring(r['rigid_q'],sep=' ')[2] for r in obj]);ref=int(np.argmin(abs(t-1.)));drop=(z[ref]-z)*1000;n=np.array([float(r['normal_Fz_N']) for r in wr]);f=np.array([float(r['total_Fz_N']) for r in wr]);iters=np.array([int(r['solver_iterations']) for r in obj]);candidate=[]
  for k in range(len(t)-19):
   if 1<=t[k]<=2 and np.all(n[k:k+20]<0):candidate.append(float(t[k]));break
  phases=[]
  for start,stop in [(0.5,1.),(1.,1.2),(1.2,1.5),(1.6,2.)]:
   mask=(t>=start-1e-12)&(t<=stop+1e-12);phases.append(dict(window_s=[start,stop],mean_skin_normal_z_N=float(n[mask].mean()),mean_skin_total_z_N=float(f[mask].mean()),iteration_limited_outputs=int(sum(iters[mask]>=1000)),outputs=int(mask.sum()),maximum_downward_displacement_mm=float(drop[mask].max())))
  records.append(dict(case=case,first_2mm_downward_slip_after_support_withdrawal_s=first_time(t,(t>=1)&(t<=2)&(drop>2)),first_20_consecutive_negative_normal_z_start_s=candidate[0] if candidate else None,first_iteration_limit_after1s=first_time(t,(t>=1)&(t<=2)&(iters>=1000)),phases=phases))
  for path in [src/'object.csv',wp]:hashes[str(path.relative_to(BASE))]=sha(path)
 d=dict(status='TEMPORAL_ASSOCIATION_ONLY_NOT_UNIQUE_CAUSAL_PROOF',records=records,definition='20 consecutive negative normal-Z outputs is a sign-persistence diagnostic,not a force floor or acceptance Gate. First2mm slip uses existing functional limit;actual saved clock,not continuous event time.',scope='Direct response force split and actual object/solver traces. If normal reversal follows slip,it cannot alone explain initial loss of support;iteration limits remain confounding. No force/friction/stiffness change adopted.',physical_validation='NOT QUALIFIED',input_hashes=hashes,producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
