"""Partial withdrawal evidence; never apply full hold-window verdict to1.2s."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;summary=json.loads((src/'summary.json').read_text());rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);index={x:i for i,x in enumerate(t)};q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);parts={k:np.zeros((len(rows),6)) for k in ('skin','rail','guide','support','other')}
 for r in read(src/'response_rows.csv'):
  names=(r['model0'],r['model1'])
  if not any('/object/'in x for x in names):continue
  other=names[1] if '/object/'in names[0] else names[0];kind='skin' if '/skinCollision/'in other else 'rail' if '/railCollision/'in other else 'guide' if '/guides'in other else 'support' if '/floor/'in other else 'other';parts[kind][index[float(r['time_s'])]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
 ref=int(np.argmin(abs(t-1.)));samples=[]
 for time in (.6,.8,1.,1.1,1.2):
  k=int(np.argmin(abs(t-time)));samples.append(dict(time_s=float(t[k]),object_z_mm=float(q[k,2]*1000),downward_from_1s_mm=float((q[ref,2]-q[k,2])*1000),speed_mm_s=float(np.linalg.norm(v[k,:3])*1000),vertical_velocity_mm_s=float(v[k,2]*1000),forces_N={n:(x[k,:3]/.0025).tolist() for n,x in parts.items()}))
 peaks=[];errors=[]
 for i in range(3):
  for r in read(src/f'latch{i}.csv'):
   if int(r['latched']):
    for j in range(2):peaks.append(abs(float(r[f'force{j}_Ns']))/.0025);errors.append(abs(float(r[f'target{j}_m'])-float(r[f'geometric{j}_m'])))
 d=dict(status='WITHDRAWAL_PILOT_INVENTORY_NOT_FULL_HOLD',case=a.case,samples=samples,maximum_emergent_tendon_force_N=max(peaks),maximum_geometric_command_error_m=max(errors),quality=summary['qualities'],full1_6_to2s_holding='NOT MEASURED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','summary.json','object.csv','response_rows.csv','latch0.csv')},scope='Actual partial states/response source/Nativeλ dividedbydt;not extrapolated finalHolding. PositiveFEMvolumes not allowable strain,convergence or materialPASS.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
