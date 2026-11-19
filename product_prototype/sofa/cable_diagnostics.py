"""Independent path gradient/mapping/alternating-state audit, no simulation edits."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path_gradient(pull,q):
 d=np.diff(np.vstack([pull,q]),axis=0);length=np.linalg.norm(d,axis=1)
 if np.any(length==0):raise ValueError('undefined zero segment')
 g=-d/length[:,None];g[:-1]+=d[1:]/length[1:,None];return g
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='cable_B_audit_055');a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');rows=read(src/'finger0.csv');audit=read(src/'cable_audit.csv');m=json.loads((src/'mesh.json').read_text());rest=np.fromstring(tree.find('./Node/MechanicalObject').get('position'),sep=' ').reshape(-1,3);tet=np.array(m['tetrahedra']);points=rest[tet];inverse=np.linalg.inv((points[:,1:]-points[:,0,None,:]).transpose(0,2,1));centre=points.mean(axis=1);initial=np.fromstring(tree.find('./Node/Node/MechanicalObject').get('position'),sep=' ').reshape(-1,3);pull=np.fromstring(tree.find('./Node/Node/CableConstraint').get('pullPoint'),sep=' ');weights=np.zeros((len(initial),len(rest)))
 for i,point in enumerate(initial):
  b=np.einsum('ijk,ik->ij',inverse,point-points[:,0]);violation=np.maximum.reduce([-b[:,0],-b[:,1],-b[:,2],b.sum(axis=1)-1]);distance=np.where(violation>0,np.sum((point-centre)**2,axis=1),violation);index=int(np.argmin(distance));weights[i,tet[index]]=np.r_[1-b[index].sum(),b[index]]
 q=np.array([np.fromstring(row['q_m'],sep=' ').reshape(-1,3) for row in rows]);guides=np.array([np.fromstring(row['guide0_q_m'],sep=' ').reshape(-1,3) for row in rows]);mapped=np.einsum('ij,tjk->tik',weights,q);mapping_error=float(np.max(np.abs(mapped-guides)));dt=json.loads((src/'summary.json').read_text())['dt_s'];records=[]
 for i in range(1,len(rows)):
  j=np.zeros_like(initial)
  for col in audit[i]['child_J'].split(';'):
   if col:j[int(col.split(':')[1])]=np.fromstring(col.split(':')[2],sep=' ')
  old=path_gradient(pull,guides[i-1]);now=path_gradient(pull,guides[i]);parent=np.zeros_like(rest)
  for col in audit[i]['parent_J'].split(';'):
   if col:parent[int(col.split(':')[1])]=np.fromstring(col.split(':')[2],sep=' ')
  pullback=weights.T@j;fixed=np.array(m['local_positions_mm'])[:,0]<=5;pullback[fixed]=0
  records.append(dict(time_s=float(rows[i]['time_s']),J_previous_error=float(np.max(np.abs(j-old))),J_current_error=float(np.max(np.abs(j-now))),parent_pullback_error=float(np.max(np.abs(parent-pullback))),one_step_motion_m=float(np.linalg.norm(q[i]-q[i-1])),two_step_motion_m=float(np.linalg.norm(q[i]-q[max(0,i-2)]))))
 selected=[r for r in records if r['time_s']>.8];result=dict(scope='independent saved-state diagnostics NOT whole physical certification',source_sha256=sha(Path(__file__)),case=a.case,input_hashes={f.name:sha(f) for f in (src/'finger0.csv',src/'cable_audit.csv',src/'scene.scn')},mapping_max_error_m=mapping_error,mapping_min_weight=float(weights.min()),mapping_max_weight=float(weights.max()),mapping_max_row_l1=float(np.abs(weights).sum(axis=1).max()),maximum_J_previous_error=max(x['J_previous_error'] for x in records),hold_max_J_current_error=max(x['J_current_error'] for x in selected),hold_one_step_motion_range_m=[min(x['one_step_motion_m'] for x in selected),max(x['one_step_motion_m'] for x in selected)],hold_max_two_step_motion_m=max(x['two_step_motion_m'] for x in selected),interpretation='Check mapping reconstruction before attributing mechanism. Small linear residual is NOT nonlinear path clearance.')
 # Compare read-only audit enabled vs earlier identical physical inputs.
 prior=BASE/'results/cable_B_single_out_051/finger0.csv'
 if a.case=='cable_B_audit_055' and prior.exists():
  old=read(prior);err=max(float(np.max(np.abs(np.fromstring(row[k],sep=' ')-np.fromstring(old[i][k],sep=' ')))) for i,row in enumerate(rows) for k in ('q_m','v_m_s','guide0_q_m'));result['query_purity']=dict(max_state_difference=err,gate=1e-12,status='PASS' if err<=1e-12 else 'FAIL')
 result['maximum_parent_pullback_error']=max(r['parent_pullback_error'] for r in records)
 point=guides[-1].copy();g=path_gradient(pull,point);fd=np.zeros_like(g);eps=1e-8
 for index in np.ndindex(point.shape):
  plus=point.copy();minus=point.copy();plus[index]+=eps;minus[index]-=eps;fd[index]=-(np.linalg.norm(np.diff(np.vstack([pull,plus]),axis=0),axis=1).sum()-np.linalg.norm(np.diff(np.vstack([pull,minus]),axis=0),axis=1).sum())/(2*eps)
 result['independent_length_gradient_FD_max_error']=float(np.max(np.abs(fd-g)))
 with (out/'diagnostics.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
