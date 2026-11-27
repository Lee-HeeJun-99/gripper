"""Independent point-velocity/wrench reconstruction of six actual joint bodies.
Checks saved numerical states and negative controls;does not repair or re-solve them.
"""
import json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,sha,ref,dump

def main():
 out=ROOT/'validation/integrated/primaryP1_installed51_saved';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');sp=ROOT/'validation/integrated/primaryP1_installed51/summary.json';pp=ROOT/'validation/integrated/primaryP1_port51/summary.json';d=json.loads(sp.read_text());p=json.loads(pp.read_text());plan=json.loads((REPO/d['plan']['path']).read_text());names=list(plan['DOFs']);origin=np.array(plan['global_joint_origin_mm']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in [d['candidate'],d['plan'],d['bindings'],p['actual_installed_endpoint']]);cad=json.loads((REPO/d['candidate']['path']).read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);cols=[];rngx=np.random.default_rng(510);dq=rngx.normal(size=(6,6));workerrors=[];patches=0
 for c in d['contacts']:
  i=names.index(c['body_i']);j=names.index(c['body_j']);forces=np.zeros((6,3));moments=np.zeros((6,3));direct=0.
  if 'quadrature' in c:samples=c['quadrature'];patches+=1
  else:samples=[dict(point_mm=c['point_mm'],normal_force_on_bolt=c['force_on_i_per_multiplier_N'],area_mm2=1.)]
  for sm in samples:
   r=np.array(sm['point_mm'])-origin;f=np.array(sm['normal_force_on_bolt'])*sm['area_mm2'];forces[i]+=f;forces[j]-=f;moments[i]+=np.cross(r,f);moments[j]-=np.cross(r,f);vi=dq[i,:3]+np.cross(dq[i,3:],r);vj=dq[j,:3]+np.cross(dq[j,3:],r);direct+=float(np.dot(f,vi-vj))
  col=np.c_[forces,moments].reshape(36);cols.append(col);workerrors.append(abs(float(col@dq.reshape(36))-direct))
 A=np.array(cols).T;stored=np.array([c['column'] for c in d['contacts']]).T;lam=np.array(p['contact_reactions']);F=np.array(p['external_axial_load']);T=np.array(p['explicit_port_direction']);tau=p['required_opposing_port_torque_Nmm_per_N'];res=A@lam+F+T*tau;v=np.array(p['free_screw_certificate']['twist_36DOF']);bindings=[json.loads(s) for s in (REPO/d['bindings']['path']).read_text().splitlines()];negative=[]
 # Perturb each of six loadpath families independently in the actual saved state.
 for prefix in ['thread','headseat','nutseat','nutcage','socket','keycage']:
  bad=lam.copy()
  for j,c in enumerate(d['contacts']):
   if c['label'].startswith(prefix):bad[j]=0
  error=float(max(abs(A@bad+F+T*tau)));negative.append(dict(removed_family=prefix,force_moment_error=error,rejected=error>1e-6))
 wrong=T.copy();wrong[29]=1;wrong[35]=-1;negative.append(dict(control='reversed_required_port_torque',force_moment_error=float(max(abs(A@lam+F+wrong*tau))),rejected=float(max(abs(A@lam+F+wrong*tau)))>1e-6))
 # Constant/rigid chart rank leaves explicit free modes;never turn them into fixes.
 sv=np.linalg.svd(A,compute_uv=False);checks=dict(actual128CAD_assembly_BOM_hashes=True,independent_wrenches=float(max(abs(A-stored).flat))<1e-10,all36DOF_conditional_balance=float(max(abs(res)))<1e-8,reactions_nonnegative=float(min(lam))>=-1e-10,independent_spatial_virtualwork=max(workerrors)<1e-10,free_screw_zero_contact_work=float(max(abs(A.T@v)))<1e-7,positive_unbalanced_axial_work=abs(float(F@v)-.8/(2*math.pi))<1e-12,required_port_work_cancels=abs(float((F+T*tau)@v))<1e-8,all7_saved_state_negative_controls_reject=all(x['rejected'] for x in negative),finite_actual_face_binding=max(r['distance_mm'] for r in bindings)<1e-7 and max(r['normal_error'] or 0 for r in bindings)<1e-7,one_physical_loaded_flank=patches==48 and d['loaded_flank_side']==-1,original_pure_axial_FAIL_preserved=not d['solution']['feasible'])
 dump(out/'summary.json',dict(status='ACTUAL_P1_SAVED_CONDITIONAL_JOINT_AND_FREE_SCREW_RECONSTRUCTION_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_SAVED_JOINT_RECONSTRUCTION_FAIL',candidate=d['candidate'],verifier=ref(out/'verifier.py'),endpoint=ref(sp),conditional_port_solution=ref(pp),checks={k:bool(v) for k,v in checks.items()},independent_balance_residual=float(max(abs(res))),independent_column_error=float(max(abs(A-stored).flat)),independent_virtual_work_error=max(workerrors),free_screw_contact_work=float(max(abs(A.T@v))),free_screw_unbalanced_axial_work_Nmm=float(F@v),negative_controls=negative,normal_bindings=len(bindings),finite_thread_patches=patches,singular_values=sv.tolist(),body_balances=res.reshape(6,6).tolist(),accepted_physical_product_equilibria=0,required_port_torque_implemented=False,newly_qualified_system_gate_ids=[],whole_system_release=False))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},balance=float(max(abs(res))),work=max(workerrors),negative=negative)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
