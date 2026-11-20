"""Separate sampled inertia,actual mass response and Native discrete gap/dt law."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
from native_response_blocks import friction_blocks
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def matrix(points,c,m):
 r=points-c;I=m/len(r)*sum(((x@x)*np.eye(3)-np.outer(x,x) for x in r),np.zeros((3,3)));M=np.zeros((6,6));M[:3,:3]=m*np.eye(3);M[3:,3:]=I;return M
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];steps=[]
 for case in ('b3_inertia_input_contact600','b3_inertia_input_contact_half601','b3_inertia_input_contact_quarter602'):
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text());dt=meta['dt_s'];m=meta['assumed_mass_kg'];d=src/'0';root=ET.parse(d/'scene.scn').getroot();states=[read(d/f'guide{i}.csv') for i in (0,1)];mass=[read(d/f'mass{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];inputs=[read(d/f'inertia_input{i}.csv') for i in (0,1)];responses=read(d/'response0.csv');oldpoints=[vec(root.find(f"./Node[@name='guide{i}']/Node[@name='massQuadrature']/MechanicalObject").get('position')).reshape(-1,3) for i in (0,1)]
  for k,s in enumerate(states[0]):
   t=float(s['time_s']);q=[np.array(meta['initial'][i]['q']) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)];before=[np.array(meta['initial'][i]['v']) if k==0 else vec(states[i][k-1]['rigid_v']) for i in (0,1)];after=[vec(states[i][k]['rigid_v']) for i in (0,1)];rows=[{int(r['row_id']):r for r in data if float(r['time_s'])==t} for data in direct];M=[matrix(oldpoints[i],q[i][:3],m) for i in (0,1)]
   for i in (0,1):
    actual=vec(inputs[i][k]['applied_torque_Nm']);expected=-np.cross(before[i][3:],M[i][3:,3:]@before[i][3:]);imp=vec(states[i][k]['object_impulse_Ns_Nms']);full=M[i]@(after[i]-before[i])-np.r_[np.zeros(3),actual*dt]-imp;free=None
    if rows[i]:free=vec(next(iter(rows[i].values()))['free_v'])
    steps.append(dict(case=case,body=i,time_s=t,input_time_s=float(inputs[i][k]['input_time_s']),inertial_torque_law_error_Nm=float(np.linalg.norm(actual-expected)),linear_step_residual_Ns=float(np.linalg.norm(full[:3])),angular_step_residual_Nms=float(np.linalg.norm(full[3:])),free_predictor_error= None if free is None else float(np.max(abs(free-before[i]-np.linalg.solve(M[i],np.r_[np.zeros(3),actual*dt]))))))
   for b in friction_blocks(responses,t,rows[0]):
    J=[np.array([vec(rows[i][b+j]['J']) for j in range(3)]) for i in (0,1)];lever=[.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3)) for j in J];gap=float((q[0][:3]+lever[0]-q[1][:3]-lever[1])@J[0][0,:3]-.0002);post=sum(j@v for j,v in zip(J,after));pre=sum(j@v for j,v in zip(J,before));normal=float(rows[0][b]['lambda_Ns']);records.append(dict(case=case,time_s=t,step_start_s=t-dt,first_row=b,normal_impulse_Ns=normal,previous_buffered_gap_m=gap,previous_normal_velocity_m_s=float(pre[0]),accepted_normal_velocity_m_s=float(post[0]),gap_over_dt_target_m_s=-gap/dt,active_target_residual_m_s=float(post[0]+gap/dt) if normal>0 else None))
   oldpoints=[vec(mass[i][k]['q']).reshape(-1,3) for i in (0,1)]
 result=dict(status='NATIVE_INPUT_CONTACT_DIAGNOSTIC_ONLY',scope='Actual mapped mass and Native rows. Inertial coordinate torque is NOT external applied mechanical work. No energy heat labels,impulse interpolation or contact convergence PASS.',producer_sha256=sha(Path(__file__)),steps=steps,records=records,maximum_linear_step_residual_Ns=max(r['linear_step_residual_Ns'] for r in steps),maximum_angular_step_residual_Nms=max(r['angular_step_residual_Nms'] for r in steps),maximum_torque_law_error_Nm=max(r['inertial_torque_law_error_Nm'] for r in steps),maximum_free_predictor_error=max(r['free_predictor_error'] for r in steps if r['free_predictor_error'] is not None),maximum_active_gap_over_dt_residual_m_s=max(abs(r['active_target_residual_m_s']) for r in records if r['active_target_residual_m_s'] is not None),first_active_rows=[next(r for r in records if r['case']==c and r['normal_impulse_Ns']>0) for c in dict.fromkeys(r['case'] for r in records)])
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('steps','records')},indent=2))
if __name__=='__main__':main()
