"""Moving root + transported carriage mass + Native cable + actual stop.
Independent2x2 discrete reference never writes Native state. It checks this
installed contract, not a general physical impact law or ReGrip grasp.
"""
import argparse,copy,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def reference(steps=40):
 M=np.array([[.006,.001],[.001,.001]]);W=np.linalg.inv(M);q=np.zeros(2);v=np.zeros(2);result=[]
 for n in range(steps):
  v=v+.001*(W@np.array([.01,.01]));trial=q+.001*v;lam=0.
  if trial[1]>.002:lam=(.002-trial[1])/(.001*W[1,1])
  if trial[1]<0:lam=-trial[1]/(.001*W[1,1])
  v=v+W[:,1]*lam;q=trial+.001*W[:,1]*lam;result.append((q.copy(),v.copy(),lam))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/captured_root_mass1752';fixed=BASE/'results/captured_prismatic1746';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);assert json.loads((src/'summary.json').read_text())['status']=='PASS_MOVING_ROOT_MAPPED_PRISMATIC_MASS_ONLY';root=ET.parse(src/'scene.scn').getroot();joint=root.find("Node[@name='carriage']");mapped=joint.find("Node[@name='rigid']");mapped.remove(mapped.find('ConstantForceField'));mapped.append(copy.deepcopy(ET.parse(fixed/'scene.scn').getroot().find("Node[@name='carriage']/Node[@name='rigid']/Node[@name='cable']")));joint.append(copy.deepcopy(ET.parse(fixed/'scene.scn').getroot().find("Node[@name='carriage']/StopperLagrangianConstraint")))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)).replace(str(fixed),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),moving_root_contract_sha256=sha(src/'summary.json'),fixed_cable_contract_sha256=sha(fixed/'summary.json'),scope='Original moving-root1752 mass transport, but mapped CableConstraint drives the carriage into an actual Native1DOF stopper. No duplicated scalar mass or state overrides. Fourty1mssteps; reference is2x2 mass/compliance projection ONLY, not a new simulator/solver used by Native. Real friction, FEM root, finite carriage geometry and impact/energy accuracy unqualified.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','40','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));valid=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
 if valid:
  b=list(csv.DictReader((out/'base.csv').open()));c=list(csv.DictReader((out/'body.csv').open()));assert len(b)==len(c)==40;qb=np.array([np.fromstring(x['rigid_q'],sep=' ') for x in b]);vb=np.array([np.fromstring(x['rigid_v'],sep=' ') for x in b]);qc=np.array([np.fromstring(x['rigid_q'],sep=' ').reshape(-1,7)[1] for x in c]);vc=np.array([np.fromstring(x['rigid_v'],sep=' ').reshape(-1,6)[1] for x in c]);q=np.column_stack([qb[:,0],qc[:,0]-qb[:,0]-.01]);v=np.column_stack([vb[:,0],vc[:,0]-vb[:,0]]);ref=reference();rq=np.array([r[0] for r in ref]);rv=np.array([r[1] for r in ref]);qe=float(abs(q-rq).max());ve=float(abs(v-rv).max());pe=float(abs(.005*vb[:,0]+.001*vc[:,0]-.01*.001*np.arange(1,41)).max());finite=bool(np.isfinite(q).all() and np.isfinite(v).all());valid=finite and max(qe,ve,pe)<=1e-12
  metrics=dict(finite=finite,maximum_discrete_position_error_m=qe,maximum_discrete_velocity_error_m_s=ve,total_linear_momentum_error_Ns=pe,maximum_joint_travel_m=float(q[:,1].max()),final_joint_travel_m=float(q[-1,1]),final_root_position_m=float(q[-1,0]),final_root_velocity_m_s=float(v[-1,0]),final_child_velocity_m_s=float(vc[-1,0]))
 d=dict(status='PASS_MOVING_ROOT_CABLE_STOPPER_CONTRACT_ONLY' if valid else 'FAIL_MOVING_ROOT_CABLE_STOPPER_CONTRACT',process=process,measurements=metrics,sofa_error_lines=[x for x in logs.splitlines() if '[ERROR]'in x][:12],preflight_sha256=sha(out/'preflight.json'),scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
