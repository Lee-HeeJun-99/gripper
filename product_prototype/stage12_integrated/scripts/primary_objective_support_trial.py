"""Actual P1 bounded load insertion eligibility, no fictitious Base correction.
Reuses recorded old stationarity only to compute residual at the EXACT saved u.
It is not a new FE equilibrium or an objective structural constitutive model.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_port import motor_pullback,skew

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_objective_port1/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['field']['path']);port=np.load(REPO/s['port']['path']);state=json.loads((REPO/s['state']['path']).read_text());oldsrc=ROOT/'validation/integrated/primaryP1_reclosure3/state.json';old=json.loads(oldsrc.read_text());n='F0_ROOT_BACK';p=a[n+'_points_mm'];tet=a[n+'_tetra'];off=int(a[n+'_offset']);mo=int(a['motor_offset']);um=a['u_mm'][mo:mo+6];oldf=a['applied_force_N'];f=oldf.copy();vol=abs(np.linalg.det(p[tet[:,1:]]-p[tet[:,0,None]]))/6;mass=np.zeros(len(p))
 for j in range(4):np.add.at(mass,tet[:,j],vol/4)
 gravity=np.zeros((len(p),3));gravity[:,2]=-mass*float(a[n+'_rho_kg_m3'])*1e-9*9.80665
 oldroot=oldf[off:off+3*len(p)].reshape(-1,3)-gravity;W=np.r_[oldroot.sum(0),np.cross(p*.001,oldroot).sum(0)];oldroot_error=W-old['Root_origin_wrench_N_Nm'];newroot=gravity.copy();newroot[port['root_nodes']]+=port['root_force_N'];f[off:off+3*len(p)]=newroot.ravel();f[mo:mo+6]=motor_pullback(um,np.array(state['Motor_origin_wrench_N_Nm']))
 delta=f-oldf;residual=a['stationarity_N']-delta
 def reference_wrench(v):
  W=np.r_[v[mo:mo+3],v[mo+3:mo+6]*.001+np.cross([0,0,.020],v[mo:mo+3])]
  oldsummary=json.loads((ROOT/'validation/integrated/primaryP1_reclosure3/summary.json').read_text())
  for name in oldsummary['elastic_bodies']:
   pp=a[name+'_points_mm'];o=int(a[name+'_offset']);ff=v[o:o+3*len(pp)].reshape(-1,3);W+=np.r_[ff.sum(0),np.cross(pp*.001,ff).sum(0)]
  return W
 reference_balance=reference_wrench(f);scaled=float(np.linalg.norm(residual)/max(np.linalg.norm(f),1));baseoff=int(a['TEST_BASE_offset']);baselen=3*len(a['TEST_BASE_points_mm']);base_unchanged=bool(np.array_equal(f[baseoff:baseoff+baselen],oldf[baseoff:baseoff+baselen]));checks=dict(old_root_verified=np.linalg.norm(oldroot_error)<1e-10,Base_no_arbitrary_cancellation=base_unchanged,unchanged_displacements=True,unchanged_original_contacts=bool(a['contact_C_shape'][0]==2169),unchanged14connectors=len(a['bolt_force_N'])==14,mixed_model_insertion_rejected=scaled>1e-8 and np.linalg.norm(reference_balance[3:])>1e-10)
 np.savez_compressed(out/'trial.npz',new_applied_force_N=f,delta_force_N=delta,unsolved_stationarity_N=residual)
 result=dict(status='ACTUAL_P1_OBJECTIVE_LOAD_INSERTION_REJECTED_MIXED_REFERENCE_MODEL' if all(checks.values()) else 'ACTUAL_P1_OBJECTIVE_LOAD_INSERTION_UNEXPECTED',candidate=s['candidate'],source=ref(src),old_state=ref(oldsrc),producer=ref(out/'producer.py'),implementation=ref(ROOT/'scripts/primary_finite_port.py'),trial=ref(out/'trial.npz'),checks={k:bool(v) for k,v in checks.items()},DOF=len(f),contact_rows=int(a['contact_C_shape'][0]),connectors=len(a['bolt_force_N']),old_Root_wrench_error_N_Nm=oldroot_error.tolist(),load_change_norm_N=float(np.linalg.norm(delta)),unsolved_stationarity_relative=scaled,unchanged_reference_Base_load_balance_N_Nm=reference_balance.tolist(),force_criterion_N=1e-8,moment_criterion_Nm=1e-10,artificial_Base_correction_applied=False,contact_solve_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Actual numerical trial at saved support field. Objective Root loads and Motor exponential cotangent replace old upstream loads, all other loads/contact/connectors remain exact. Mixed model violates unchanged reference rotational null balance; a new local contact solve would not certify current equilibrium. No solver success/stress update/global energy claim.')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
