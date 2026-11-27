"""Actual primary RootY attachment contrast; no support update accepted."""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from baseline_registry import ROOT,REPO,ref,dump
from primary_finite_contact_support import FiniteContactSupport
from primary_attached_current_loads import CurrentLoads
from primary_finite_current_loads import CurrentLoads as SlipLoads

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_finite_increment2/summary.json';s=json.loads(src.read_text());local=json.loads((REPO/s['source']['path']).read_text());a=dict(np.load(REPO/s['source_field']['path']));model=FiniteContactSupport(a,local['elastic_bodies']);loads=CurrentLoads(model);slip=SlipLoads(model);trial=np.load(REPO/s['trial_field_npz']['path'])['u_mm'];u=a['u_mm'];direction=np.zeros(len(u));b=model.bodies['F0_ROOT_BACK'];o=b['offset'];direction[o+1:o+3*len(b['X']):3]=1;gauge=float(np.max(abs(a['gauge_Q']@direction)));states=[];saved={}
 for name,z in [('initial',u),('trial',trial),('rootY_minus',u-.0001*direction),('rootY_plus',u+.0001*direction)]:
  f,d=loads(z);W=model.wrench(z,f);st=d['upstream'];checks=dict(upstream=all(st['checks'].values()),zero_auxiliary_slip=abs(d['root_freeY_increment_mm'])<1e-8,physical_force=np.linalg.norm(W[:3])<1e-8,physical_moment=np.linalg.norm(W[3:])<1e-10,all_fivebody_gravity=len(d['elastic_gravity'])==5,no_Base_residual_cancellation=not d['Base_residual_cancellation'])
  states.append(dict(state=name,checks={k:bool(v) for k,v in checks.items()},normal_N=st['normal_N'],root_Y_load_N=st['Root_origin_wrench_N_Nm'][1],cable_Y_force_N=st['string']['Fe_N'][1],auxiliary_slip_mm=d['root_freeY_increment_mm'],applied_current_wrench_N_Nm=W.tolist(),Root_wrench_N_Nm=st['Root_origin_wrench_N_Nm']));saved[name]=(f,d)
  dump(out/(name+'_loads.json'),d)
  if name=='trial':np.savez_compressed(out/'trial_field.npz',u_mm=z)
 oldf,oldd=slip(trial);newf,newd=saved['trial'];expected=np.cross([0,oldd['root_freeY_increment_mm']*.001,0],oldd['upstream']['Root_origin_wrench_N_Nm'][:3]);observed=model.wrench(trial,oldf)[3:];control_error=float(np.linalg.norm(expected+observed));stiffness=(states[-1]['root_Y_load_N']-states[-2]['root_Y_load_N'])/.0002
 checks=dict(all_physical_states=all(all(z['checks'].values()) for z in states),original_RootY_fixed_target_gauge_detected=abs(gauge-1)<1e-12,missing_slip_moment_control=control_error<1e-10 and np.linalg.norm(observed)>1e-10,Y_force_transmitted=abs(states[1]['cable_Y_force_N'])>1e-10,restoring_Y_load=stiffness<0)
 np.savez_compressed(out/'attached_forces.npz',initial_force_N=saved['initial'][0],trial_force_N=newf,original_RootY_direction=direction)
 result=dict(status='ACTUAL_P1_ORIGINAL_FREEY_ATTACHMENT_PARTIAL_PASS' if all(checks.values()) else 'ACTUAL_P1_ORIGINAL_FREEY_ATTACHMENT_FAIL',candidate=s['candidate'],source=s['source'],rejected_predictor=ref(src),source_field=s['source_field'],producer=ref(out/'producer.py'),output=ref(out/'attached_forces.npz'),states=states,checks={k:bool(v) for k,v in checks.items()},original_RootY_gauge_response=gauge,measured_rootY_load_derivative_N_per_mm=stiffness,old_unapplied_slip_moment_Nm=observed.tolist(),old_slip_control_error_Nm=control_error,changed_trial_force_norm_N=float(np.linalg.norm(newf-oldf)),actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Auxiliary shooting slip is zero; original physical RootY remains in FE and transmits nonzero cableY force. No added physical fixation. RootY plus/minus are load evaluations only, NOT feasible contact states or equilibrium.','Same spatial string and planar Finger constitutive model, finite wire bending/full3D Finger/freeY retention not certified. All original contact constraints/current quasiNewton KKT must qualify before ONE corrected coupled update.','Sourcepoint-derived Base only; fullsystem energy/mesh/material/physical anchorage/strength/full3Finger remain unqualified.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
