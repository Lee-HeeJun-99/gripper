"""Read-only saved native cable Jacobian/transition audit. No state correction."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from cable_diagnostics import path_gradient
from analyse import cable_node
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('completed native run required')
 tree=ET.parse(src/'scene.scn');contact=read(src/'contact_rows.csv');times={float(x['time_s']) for x in contact if int(x['film_mask']) and abs(float(x['lambda_Ns']))>0};solver={float(x['time_s']):x for x in read(src/'constraints.csv')};records=[]
 for f in range(meta['fingers']):
  rows=read(src/f'finger{f}.csv')
  for j in (0,1):
   audits=read(src/f'cable_audit_{f}_{j}.csv');node=cable_node(tree,f,j);rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);pull=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ');L0=np.linalg.norm(np.diff(np.vstack([pull,rest]),axis=0),axis=1).sum();previous=rest
   for row,obs in zip(rows,audits):
    t=float(row['time_s']);q=np.fromstring(row[f'guide{j}_q_m'],sep=' ').reshape(-1,3);old=path_gradient(pull,previous);current=path_gradient(pull,q);J={}
    for col in obs['child_J'].split(';'):
     if col:
      r,k,v=col.split(':');J.setdefault(int(r),np.zeros_like(q))[int(k)]=np.fromstring(v,sep=' ')
    owner=min(J,key=lambda r:np.max(abs(J[r]-old))) if J else None;native=J.get(owner);length=np.linalg.norm(np.diff(np.vstack([pull,q]),axis=0),axis=1).sum();previous_length=np.linalg.norm(np.diff(np.vstack([pull,previous]),axis=0),axis=1).sum();linear_shortening=previous_length-length if native is None else float(np.sum(native*(q-previous)));actual=L0-length;command=float(row['command_m']);s=solver[t]
    records.append(dict(time_s=t,finger=f,cable=j,command_m=command,actual_shortening_m=actual,nonlinear_error_m=actual-command,internal_length_m=float(obs['L_internal_m']),geometric_length_m=length,previous_J_max_error=None if native is None else float(np.max(abs(native-old))),current_J_max_error=None if native is None else float(np.max(abs(native-current))),linearization_remainder_m=(previous_length-length)-linear_shortening,solver_error=float(s['error']),solver_iterations=int(s['iterations']),finger_contact=t in times,owner_row=owner))
    previous=q
 with (out/'transition.csv').open('w') as file:w=csv.DictWriter(file,fieldnames=records[0]);w.writeheader();w.writerows(records)
 worst=max(records,key=lambda x:abs(x['nonlinear_error_m']));result=dict(case=a.case,scope='actual geometric cable and native assembled Jacobian versus previous/current accepted state;no force/solver modification',status='DIAGNOSTIC_ONLY',first_nonzero_finger_impulse_s=min(times) if times else None,worst=worst,maximum_previous_J_error=max(x['previous_J_max_error'] for x in records if x['previous_J_max_error'] is not None),maximum_linearization_remainder_m=max(abs(x['linearization_remainder_m']) for x in records),source_sha256=sha(Path(__file__)),input_hashes={x.name:sha(x) for x in src.glob('*.csv')},native_constraint_violation=None,notes='length command residual is NOT native solver linear residual;row selected by previous-gradient match,not a persistent contact row identity')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
