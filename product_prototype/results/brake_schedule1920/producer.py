"""Actual public Data schedule versus applied Native M/C/K operator."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from brake_schedule_common import attach

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/winch_brake1916';ref=json.loads((src/'preflight.json').read_text());root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'))
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 schedule=attach(root,out,['shaft'],ref['coefficient_Nms_per_rad'],2*dt,5*dt);ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),reference_sha256=sha(src/'preflight.json'),schedule=schedule);(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','50','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ['stdout.log','stderr.log']);ok=proc['exit_code']==0 and '[ERROR]'not in logs;metrics=[]
 if ok:
  read=lambda f:list(csv.DictReader((out/f).open()));states=read('states.csv');constraints=read('constraints.csv');coeff=read('shaft_brake_schedule.csv');assert len(states)==len(constraints)==len(coeff)==50;M=np.array(ref['M']);K=np.array(ref['K']);theta=np.zeros(2);omega=np.array([-.1,-.2]);ports=root.find("Node[@name='shaft']/Node[@name='ports']");base=np.array([.003,0,0]);arms=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)-base;pull=np.fromstring(ports.find('CableConstraint').get('pullPoint'),sep=' ')
  for row,con,crow in zip(states,constraints,coeff):
   c=float(crow['coefficient']);t=float(crow['applied_end_clock_s']);u=np.clip((t-2*dt)/(3*dt),0,1);wanted=ref['coefficient_Nms_per_rad']*u**3*(10+u*(-15+6*u));assert abs(c-wanted)<=1e-15;C=np.diag([0,c]);q=np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7);v=np.fromstring(row['rigid_v'],sep=' ').reshape(-1,6);nxt=Rotation.from_quat(q[1:,3:]).as_rotvec()[:,0];w=v[1:,3];imp=np.fromstring(con['impulses_Ns'],sep=' ');assert len(imp)==1;r=Rotation.from_rotvec([theta[-1],0,0]).apply(arms);direction=pull-base-r[0];direction/=np.linalg.norm(direction);external=np.array([0,imp[0]*np.cross(r[0],direction)[0]+dt*np.cross(r[1],[0,0,-.9000000000000008])[0]]);expected=np.linalg.solve(M+dt*C+dt*dt*K,M@omega-dt*K@theta+external);dx=nxt-theta;dv=w-omega;closure=.5*(w@M@w+nxt@K@nxt-omega@M@omega-theta@K@theta)-external@dx/dt+dt*w@C@w+.5*(dv@M@dv+dx@K@dx);metrics.append(dict(time_s=float(row['time_s']),actual_coefficient=c,maximum_velocity_error=float(abs(w-expected).max()),relative_velocity_error=float(np.linalg.norm(w-expected)/np.linalg.norm(expected)),physical_dissipation_J=float(dt*w@C@w),reference_energy_identity_residual_J=float(closure)));theta=nxt;omega=w
  ok=all(m['maximum_velocity_error']<=1e-12 and m['relative_velocity_error']<=1e-9 and m['physical_dissipation_J']>=0 and abs(m['reference_energy_identity_residual_J'])<=1e-12 for m in metrics)
 d=dict(status='PASS_PUBLIC_BRAKE_DATA_NATIVE_OPERATOR_ONLY' if ok else 'FAIL_PUBLIC_BRAKE_DATA_CONTRACT',process=proc,metrics=metrics,source_sha256=sha(Path(__file__)),preflight_sha256=sha(out/'preflight.json'),scope='Actual installed stock damping force/matrix with externally scheduled nonnegative data. Controller writes only dampingCoefficient; no q/v/row/force solver edits. Variable ideal viscous loss passivity does not certify real electrical switching, hardware brake, closing or Holding.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='metrics'},indent=2))
if __name__=='__main__':main()
