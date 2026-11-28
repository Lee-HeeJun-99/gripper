"""Independent force, couple and physical virtual-work audit for screw-aware P1 bounds."""
import sys,json,shutil,math
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_screw59full';d=json.loads((src/'summary.json').read_text());loads=json.loads((ROOT/'validation/integrated/primaryP1_contacts59c/load_ledger.json').read_text());names=loads['body_names'];ext=np.array(loads['external_wrench_N_Nm']);cases=json.loads((src/'torque_cases.json').read_text());tw=np.sin(np.arange(30)*.41+.13).reshape(5,6);h=1e-5;reports=[]
for case in cases:
 if not case['feasible']:continue
 internal=np.zeros((5,6));wrong=np.zeros((5,6));analytic=0.;finite=0.;limit=[];torques=[]
 for q in case['all_reactions']:
  i,j=names.index(q['body_i']),names.index(q['body_j']);f=np.array(q['direction'])*q['coefficient_N'];p=np.array(q['point_mm'])*.001;m=np.array(q['couple_Nm_per_N'])*q['coefficient_N'];w=np.r_[f,np.cross(p,f)+m];internal[i]+=w;internal[j]-=w;analytic+=w@(tw[i]-tw[j]);bad=np.r_[f,np.cross(p,f)-m];wrong[i]+=bad;wrong[j]-=bad
  def motion(step):
   return f@(Rotation.from_rotvec(step*tw[i,3:]).apply(p)-Rotation.from_rotvec(step*tw[j,3:]).apply(p)+step*(tw[i,:3]-tw[j,:3]))+step*m@(tw[i,3:]-tw[j,3:])
  finite+=(motion(-2*h)-8*motion(-h)+8*motion(h)-motion(2*h))/(12*h)
  if q['kind']=='screw_axial_plus_helix_torque':
   F=q['coefficient_N'];torques.append(abs(m[2]-.5/(2*np.pi)*.001*F));limit.append(abs(m[2])-.001*case['head_mu_ASSUMED']*2.75*F)
 host=np.zeros((5,6));host[-1]=case['required_unknown_host_wrench_N_Nm'];res=internal+ext+host;bad=wrong+ext+host;reports.append(dict(contact_mu_ASSUMED=case['contact_mu_ASSUMED'],head_mu_ASSUMED=case['head_mu_ASSUMED'],all30_force_residual_N=float(np.linalg.norm(res[:,:3],axis=1).max()),all30_moment_residual_Nm=float(np.linalg.norm(res[:,3:],axis=1).max()),SE3_virtualwork_error_Nm=abs(analytic-finite),helix_torque_error_Nm=max(torques),head_friction_bound_violation_Nm=max(limit),wrong_helix_sign_moment_residual_Nm=float(np.linalg.norm(bad[:,3:],axis=1).max())))
actual=json.loads((src/'actual_connectors.json').read_text());v=np.array(d['screw_free_mode']['null_mode']);K=np.array(d['screw_free_mode']['tangent_N_mm_mixed']);energy=float(.5*v@K@v);ratio=.5/(2*np.pi);spin_error=abs(v[0]-ratio*v[1]);rod=[]
for q in actual:
 # Independent exact integration of piecewise linear internalforce, same actual engagement.
 L=q['free_shank_mm'];g=q['actual_overlap_mm'];Ac=np.pi*q['basic_minor_core_d_mm']**2/4;C=(L+g/3)/(q['conditional_E_MPa']*Ac);rod.append(abs(C-q['conditional_axial_compliance_mm_N']))
checks=dict(producer_local_checks=all(d['checks'].values()),two_explicit_assumed_friction_cases=len(reports)==2,all30_original_force=all(q['all30_force_residual_N']<1e-8 for q in reports),all30_original_moment=all(q['all30_moment_residual_Nm']<1e-10 for q in reports),independent_physical_SE3_work=all(q['SE3_virtualwork_error_Nm']<1e-9 for q in reports),physical_helix_torque=all(q['helix_torque_error_Nm']<1e-12 for q in reports),head_necessary_friction_bound=all(q['head_friction_bound_violation_Nm']<1e-12 for q in reports),wrong_helix_sign_rejected=all(q['wrong_helix_sign_moment_residual_Nm']>1e-6 for q in reports),actual_free_screw_spin_mode=abs(energy)<1e-10 and spin_error<1e-14,conditional_rod_integral=max(rod)<1e-15,zero_head_friction_rejects=all(not q['feasible'] for q in cases if q['head_mu_ASSUMED']==0),unqualified_full_product=d['accepted_physical_product_equilibria']==0 and not d['whole_system_release'])
dump(out/'summary.json',dict(status='ACTUAL77_SCREW_TORQUE_FORCE_VIRTUALWORK_INDEPENDENT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL77_SCREW_TORQUE_FORCE_AUDIT_FAIL',candidate=d['candidate'],source=ref(src/'summary.json'),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},reports=reports,free_screw_mode_energy_Nmm=energy,free_screw_lead_error_mm=spin_error,maximum_conditional_rod_integral_error_mm_N=max(rod),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independent necessary screw-aware cut statics/conditionalrod work, NOT friction/preload/actualthread elastic/cage capacity/ultimatehost/globalenergy certificate.'))
print((out/'summary.json').read_text());raise SystemExit(0 if all(checks.values()) else 2)
