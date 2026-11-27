"""Independent actual field port resultants and free-Y closure controls.
No equilibrium solver, load distribution or active-set producer import.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
def W(q,f):return np.r_[f,np.cross(q,f)]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();rows=[]
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['field']['path']);old=json.loads((REPO/s['source']['path']).read_text());b=np.load(REPO/old['field']['path']);inp=json.loads((REPO/s['inputs']['path']).read_text());ls=json.loads((REPO/inp['loads']['path']).read_text());state=json.loads((REPO/s['state']['path']).read_text());pose=s['pose'];delta=a['applied_force_N']-b['applied_force_N'];mo=int(a['motor_offset'])
  def body(n,v):
   if n=='F0_MICRO_MOTOR':return np.r_[v[mo:mo+3],v[mo+3:mo+6]*.001+np.cross([0,0,.020],v[mo:mo+3])]
   p=a[n+'_points_mm'];off=int(a[n+'_offset']);f=v[off:off+3*len(p)].reshape(-1,3);return np.r_[f.sum(0),np.cross(p*.001,f).sum(0)]
  root=body('F0_ROOT_BACK',delta)+ls['Root_origin_wrench_N_Nm'];motor=body('F0_MICRO_MOTOR',delta)+ls['Motor_origin_wrench_N_Nm'];dr=root-state['Root_origin_wrench_N_Nm'];dm=motor-state['Motor_origin_wrench_N_Nm'];balance=sum((body(n,a['applied_force_N']) for n in s['elastic_bodies']+['F0_MICRO_MOTOR']),np.zeros(6));passive=max(np.linalg.norm(body(n,delta)) for n in ['OPEN_FRAME','MOTOR_CAP','GROUND_PLATE'])
  # Independently recover Root upstream wrench from actual common world points.
  c=state['string'];rw=W(np.array(c['E_m']),np.array(c['Fe_N']))+W(np.array(state['tip_world_m']),[state['normal_N'],0,0])
  for p in state['moving_mass_points']+state['fixed_mass_points']:rw+=W(np.array(p['position_m']),[0,0,-p['mass_kg']*9.80665])
  root_reconstruction=rw-np.array(state['Root_origin_wrench_N_Nm']);q=a['gauge_targets_mm'];labels=old['gauge_labels'];freeY=abs(c['root_free_Y_shift_mm']);port_force=max(np.linalg.norm(dr[:3]),np.linalg.norm(dm[:3]));port_moment=max(np.linalg.norm(dr[3:]),np.linalg.norm(dm[3:]));checks=dict(hashes=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ['candidate','field','inputs','producer','state','curves']),root_world_wrench=np.max(abs(root_reconstruction))<1e-12,port_force=port_force<1e-8,port_moment=port_moment<1e-10,absolute_freeY=freeY<1e-8,balanced_reference_force=np.linalg.norm(balance[:3])<1e-8,balanced_reference_moment=np.linalg.norm(balance[3:])<1e-10,unchanged_other_body_loads=passive<1e-12,motor_coordinate_retained=abs(q[labels.index('Motor_free_Y')]+.01)<1e-12)
  # A force-closed field can still have incompatible free-Y geometry.
  wrong_absolute_shift=abs(c['root_free_Y_shift_mm']+.0037634602017);checks['incompatible_shift_control_rejected']=wrong_absolute_shift>1e-8
  rows.append(dict(source=ref(src),checks={k:bool(v) for k,v in checks.items()},port_force_difference_N=float(port_force),port_moment_difference_Nm=float(port_moment),absolute_freeY_additional_mm=float(freeY),Root_reconstructed_error=root_reconstruction.tolist(),reference_applied_balance_N_Nm=balance.tolist(),other_body_delta_wrench_max=float(passive),root_coordinate_mm=float(q[labels.index('Root_free_Y')]),negative_control_shift_mm=float(wrong_absolute_shift)))
 ok=all(all(r['checks'].values()) for r in rows);dump(out/'summary.json',dict(status='ACTUAL_P1_RECLOSURE_PORT_VERIFY_PASS' if ok else 'ACTUAL_P1_RECLOSURE_PORT_VERIFY_FAIL',candidate=s['candidate'],verifier=ref(out/'verifier.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Unchanged reference-geometry elastic/hardware selfweights. Finite mathematical Base port balances actual reference loads; this is NOT physical anchorage or geometrically nonlinear global work closure.','Planar Finger constitutive law with spatial string; no lateral Finger equilibrium, stress convergence, source minima, physical retention or full3Finger release.']));print(json.dumps(rows));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
