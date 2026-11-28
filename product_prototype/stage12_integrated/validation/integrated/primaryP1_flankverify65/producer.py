"""Independent saved actual finite-flank12row wrench/SE3virtualwork audit.
Axial force negative control preserves free axial DOF; no clamp/preload claim.
"""
import sys,json,shutil,numpy as np
from scipy.optimize import linprog
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_flank65c/summary.json';s=json.loads(src.read_text());assert all(s['checks'].values());cp=REPO/s['candidate']['path'];assert sha(cp)==s['candidate']['SHA256'];rows=[];worst=0.
for row in s['rows']:
 p=np.array([c['point_mm'] for c in row['contacts']]);n=np.array([c['normal_on_keeper'] for c in row['contacts']]);bolt=np.c_[-n,-np.cross(p,n)];keeper=-bolt;A=np.r_[bolt.T,keeper.T];f=np.array(row['contact_normal_forces_N']);T=row['reference_torque_Nmm'];W=np.r_[0.,0,0,0,0,T,0,0,0,0,0,-T];res=A@f+W;rank=int(np.linalg.matrix_rank(A));derrs=[]
 for q in [np.arange(12)/11.,np.cos(np.arange(12)),np.sin(np.arange(12)+.3)]:
  def g(h):
   pb=Rotation.from_rotvec(h*q[3:6]).apply(p)+h*q[:3];pk=Rotation.from_rotvec(h*q[9:12]).apply(p)+h*q[6:9];nb=Rotation.from_rotvec(h*q[3:6]).apply(n);return np.einsum('ij,ij->i',nb,pk-pb)
  exact=A.T@q
  for h in [1e-5,1e-6]:derrs.append(float(abs((g(h)-g(-h))/(2*h)-exact).max()))
 derivative=max(derrs);worst=max(worst,derivative);axial=W.copy();axial[2]+=.01;axial[8]-=.01;wrong=linprog(np.ones(len(f)),A_eq=A,b_eq=-axial,bounds=(0,None),method='highs');rows.append(dict(bolt=row['bolt'],sign=row['direction'],rank=rank,point_witnesses=len(f),maximum_original12row_error_N_Nmm=float(abs(res).max()),minimum_normal_force_N=float(f.min()),SE3_pointgap_virtualwork_derivative_error=derivative,axial001N_cannot_be_carried_by_frictionless_hex=not bool(wrong.success),axial_translation_column_exact_zero=bool(np.all(A[[2,8],:]==0)),torque_zero_reference=abs(T)<1e-14))
checks=dict(all12_actual_line_cases=len(rows)==12,all_original_resultants=all(r['maximum_original12row_error_N_Nmm']<1e-8 and r['minimum_normal_force_N']>=-1e-9 for r in rows),all_finite_line_rank5=all(r['rank']==5 and r['point_witnesses']==18 for r in rows),independent_SE3_work_derivatives=worst<1e-6,axial_negative_controls=all(r['axial001N_cannot_be_carried_by_frictionless_hex'] and r['axial_translation_column_exact_zero'] for r in rows))
dump(out/'summary.json',dict(status='ACTUAL_FINITE_FLANK12ROW_SE3_VIRTUALWORK_VERIFIED_AXIAL_REJECTED_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_FINITE_FLANK_INDEPENDENT_AUDIT_FAIL',candidate=s['candidate'],source=ref(src),producer=ref(out/'producer.py'),checks=checks,rows=rows,worst_SE3_derivative_error=worst,physical_fixed_DOF=0,axial_force_control_N=.01,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Linewitnesscone/Jacobians only,notelasticfinitecontactpressure orphysicalcapacity. Rank5isnotbilateralfixationorgrasp6DOFwrenchclosure.','Keepertongue/pin/nut/cage/installedsetting/preloadremainunsolved. Fourzeroactualtorquereferencecasesareexplicit;nonzerounittorquewerecontrols,notoperatingloads.']))
print(json.dumps(dict(checks=checks,worst=worst)));raise SystemExit(0 if all(checks.values()) else 2)
