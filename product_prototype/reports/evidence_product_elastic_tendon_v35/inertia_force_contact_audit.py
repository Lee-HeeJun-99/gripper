"""Actual assembled nonsymmetric operator/contact rows;no sampled-input assumption."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_response_blocks import friction_blocks
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_inertia_contact_operator655');p.add_argument('--reference',default='b3_inertia_matrix_contact649');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((BASE/'results'/a.reference/'summary.json').read_text());steps=[];records=[]
 for variant in (0,1):
  d=src/str(variant);states=[read(d/f'guide{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];responses=read(d/'response0.csv');public=read(d/'matrix.csv')
  for k,s in enumerate(states[0]):
   t=float(s['time_s']);A=np.zeros((12,12));matrix_rows=[r for r in public if float(r['time_s'])==t]
   if len(matrix_rows)!=144:raise ValueError('incomplete actual Native operator')
   for r in matrix_rows:A[int(r['row']),int(r['column'])]=float(r['value'])
   rows=[{int(r['row_id']):r for r in x if float(r['time_s'])==t} for x in direct]
   if not rows[0]:continue
   free=np.r_[vec(next(iter(rows[0].values()))['free_v']),vec(next(iter(rows[1].values()))['free_v'])];after=np.r_[vec(states[0][k]['rigid_v']),vec(states[1][k]['rigid_v'])];imp=np.r_[vec(states[0][k]['object_impulse_Ns_Nms']),vec(states[1][k]['object_impulse_Ns_Nms'])];res=A@(after-free)-imp
   steps.append(dict(variant=variant,time_s=t,actual_operator_contact_linear_residual_Ns=float(max(np.linalg.norm(res[:3]),np.linalg.norm(res[6:9]))),actual_operator_contact_angular_residual_Nms=float(max(np.linalg.norm(res[3:6]),np.linalg.norm(res[9:]))),actual_operator_velocity_update_error=float(np.max(abs(after-free-np.linalg.solve(A,imp))))))
   q=[np.array(meta['initial'][i]['q']) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)]
   for b in friction_blocks(responses,t,rows[0]):
    J=[np.array([vec(rows[i][b+j]['J']) for j in range(3)]) for i in (0,1)];lever=[.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3)) for j in J];gap=float((q[0][:3]+lever[0]-q[1][:3]-lever[1])@J[0][0,:3]-.0002);post=float(np.r_[J[0][0],J[1][0]]@after);lam=float(rows[0][b]['lambda_Ns']);records.append(dict(variant=variant,time_s=t,first_row=b,normal_impulse_Ns=lam,previous_buffered_gap_m=gap,accepted_normal_velocity_m_s=post,gap_over_dt_target_m_s=-gap/meta['dt_s'],active_target_residual_m_s=post+gap/meta['dt_s'] if lam>0 else None))
 if not steps or not records:raise ValueError('no actual owned contact data')
 active=[r for r in records if r['normal_impulse_Ns']>0];result=dict(status='NATIVE_ACTUAL_OPERATOR_CONTACT_DIAGNOSTIC',scope='All owned actual3-row friction contacts;Native public global A maps impulse to velocity correction. Instantaneous impulse is not continuous force. No claimed physical energy/continuous-event/time convergence qualification.',source_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),reference_summary_sha256=sha(BASE/'results'/a.reference/'summary.json'),records=records,steps=steps,maximum_linear_residual_Ns=max(r['actual_operator_contact_linear_residual_Ns'] for r in steps),maximum_angular_residual_Nms=max(r['actual_operator_contact_angular_residual_Nms'] for r in steps),maximum_velocity_update_error=max(r['actual_operator_velocity_update_error'] for r in steps),maximum_active_gap_over_dt_residual_m_s=max(abs(r['active_target_residual_m_s']) for r in active))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('records','steps')},indent=2))
if __name__=='__main__':main()
