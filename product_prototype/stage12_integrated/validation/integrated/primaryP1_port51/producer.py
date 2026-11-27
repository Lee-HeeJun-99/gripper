"""Explicit required wrench ports and free-screw certificate for actual six-body joint.
No invented contact/hidden rotation restraint; pure axial FAIL remains immutable.
"""
import json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated/primaryP1_port51';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_installed51/summary.json';d=json.loads(sp.read_text());assert sha(REPO/d['candidate']['path'])==d['candidate']['SHA256'];A=np.array([c['column'] for c in d['contacts']]).T;F=np.array(d['external_load_vector_N_Nmm']);k=.8/(2*math.pi)
 # External port couple is explicitly solved,NOT represented as actual support.
 T=np.zeros(36);T[4*6+5]=-1;T[5*6+5]=1
 B=np.c_[A,T];s=linprog(np.r_[np.zeros(A.shape[1]),1.],A_eq=B,b_eq=-F,bounds=(0,None),method='highs');assert s.success
 lam=s.x[:-1];torque=s.x[-1];res=A@lam+F+T*torque
 # A physical infinitesimal free-screw motion: bolt/key/pin/receiver rotate
 # together and advance k per rad;nut/support stand still. All six body DOFs
 # kept; no gauge/body removed to make equilibrium appear feasible.
 v=np.zeros(36)
 for i in [0,2,3,4]:v[i*6+2]=k;v[i*6+5]=1
 certificate=dict(twist_36DOF=v.tolist(),maximum_active_contact_normal_velocity_mm_per_rad=float(max(abs(A.T@v))),external_axial_work_Nmm_per_rad=float(F@v),unit_port_work_Nmm_per_rad=float(T@v),meaning='Nonzero external positive work along zero-normal-work rigid screw mode rejects pure axial static support in isolated joint;port moment must oppose receiver yaw. This is NOT whole128part free mode.')
 # Balance after physically REQUIRED external torque is explicit; missing any
 # real internal contact path must fail even with this declared torque port.
 controls=[]
 for omitted in ['thread','headseat','nutseat','nutcage','socket','keycage']:
  ix=[j for j,c in enumerate(d['contacts']) if not c['label'].startswith(omitted)];r=linprog(np.zeros(len(ix)),A_eq=A[:,ix],b_eq=-F-T*torque,bounds=(0,None),method='highs');controls.append(dict(removed=omitted,feasible=bool(r.success),status=r.message))
 balances=[]
 for i,n in enumerate(json.loads((REPO/d['plan']['path']).read_text())['DOFs']):
  balances.append(dict(body=n,internal_wrench_N_Nmm=(A@lam).reshape(6,6)[i].tolist(),external_axial_wrench_N_Nmm=F.reshape(6,6)[i].tolist(),explicit_required_port_wrench_N_Nmm=(T*torque).reshape(6,6)[i].tolist(),balance_N_Nmm=res.reshape(6,6)[i].tolist()))
 checks=dict(original_pure_axial_failure_preserved=not d['solution']['feasible'],required_port_balances_all36DOFs=float(max(abs(res)))<1e-8,reactions_nonnegative=float(min(lam))>=-1e-10,required_torque_matches_lead=abs(torque-k)<1e-8,free_screw_contact_work_zero=certificate['maximum_active_contact_normal_velocity_mm_per_rad']<1e-7,free_screw_external_work_positive=abs(float(F@v)-k)<1e-12,port_closes_exact_missing_work=abs(float((F+T*torque)@v))<1e-8,all_six_internal_missing_path_controls_reject=all(not r['feasible'] for r in controls))
 dump(out/'summary.json',dict(status='ACTUAL_P1_CONDITIONAL_REQUIRED_WRENCH_PORT_BALANCE_AND_FREE_SCREW_CERTIFICATE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_REQUIRED_PORT_BALANCE_FAIL',candidate=d['candidate'],producer=ref(out/'producer.py'),actual_installed_endpoint=ref(sp),checks={k:bool(v) for k,v in checks.items()},required_opposing_port_torque_Nmm_per_N=torque,explicit_port_direction=T.tolist(),external_axial_load=F.tolist(),contact_reactions=lam.tolist(),contact_columns=ref(sp),body_balances=balances,maximum_balance_residual=float(max(abs(res))),minimum_reaction=float(min(lam)),free_screw_certificate=certificate,missing_internal_path_controls=controls,whole128part_pure_axial_equilibrium=None,accepted_physical_product_equilibria=0,normalized_conditional_wrench_joint_balance=1,port_torque_actual_source=None,installed_capacity_N=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Port torque is a computed required load,NOT an implemented restraint or fixed body','Receiver/support antiyaw source must come from actual other installedmounts/shankbore contacts;not assumed friction or benchkeys','Singlejoint free screw is NOT a demonstrated wholefourmount/128part mode','Rigid finitepatch/point normalreactions are conditional normalizedwrenches,not elasticcontact pressure/stiffness/capacity','No100g operatingload/sourceallowable/pinforming/ultimatehost/mesh/time/globalenergy qualification']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},torque=torque,residual=float(max(abs(res))),certificate=certificate,controls=controls)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
