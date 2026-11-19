"""Finite CAD actual-row gap/dt diagnosis; not swept CCD or an impact solver."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());records=[]
 if meta.get('mapped_mass'):raise ValueError('requires public parent mass;do not silently substitute mass under mapping')
 for variant in (0,1):
  d=src/str(variant);states=[read(d/f'guide{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];responses=read(d/'response0.csv');M=[np.array(json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['matrix']) for i in (0,1)]
  for k,state in enumerate(states[0]):
   t=float(state['time_s']);rows=[{int(r['row_id']):r for r in x if float(r['time_s'])==t} for x in direct];q=[np.array(meta['initial'][i]['q']) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)];v=[np.array(meta['initial'][i]['v']) if k==0 else vec(states[i][k-1]['rigid_v']) for i in (0,1)];after=[vec(states[i][k]['rigid_v']) for i in (0,1)]
   for b in sorted({int(r['first_row']) for r in responses if float(r['time_s'])==t}):
    J=[np.array([vec(x[b+j]['J']) for j in range(3)]) for x in rows];lever=[.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3)) for j in J];points=[q[i][:3]+lever[i] for i in (0,1)];gap=float((points[0]-points[1])@J[0][0,:3]-.0002);post=sum(j@u for j,u in zip(J,after));pre=sum(j@u for j,u in zip(J,v));lam=np.array([float(rows[0][b+j]['lambda_Ns']) for j in range(3)])
    # A body can have several simultaneous blocks: include every cross-block impulse.
    total=[sum((vec(r['J'])*float(r['lambda_Ns']) for r in body.values()),np.zeros(6)) for body in rows]
    prediction=sum(j@np.linalg.solve(m,f) for j,m,f in zip(J,M,total))
    records.append(dict(variant=variant,time_s=t,step_start_s=t-meta['dt_s'],first_row=b,normal_impulse_Ns=float(lam[0]),previous_surface_buffered_gap_m=gap,previous_normal_velocity_m_s=float(pre[0]),accepted_normal_velocity_m_s=float(post[0]),gap_over_dt_target_m_s=-gap/meta['dt_s'],target_residual_m_s=float(post[0]+gap/meta['dt_s']),row_velocity_update_error_m_s=float(np.max(abs(post-pre-prediction))),continuous_event_time=None))
 active=[r for r in records if r['normal_impulse_Ns']>0];result=dict(status='FINITE_COM_DISCRETE_EVENT_DIAGNOSTIC',scope='Actual finite-surface J lever points,public full anisotropic constant-world M. Confirms installed discrete gap/dt target;does not locate continuous first impact or certify time convergence. Contact distance unchanged0.2mm.',producer_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),records=records,maximum_active_target_residual_m_s=max(abs(r['target_residual_m_s']) for r in active),maximum_row_velocity_update_error_m_s=max(r['row_velocity_update_error_m_s'] for r in records))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
