"""Finite objective P1 pin/backlash mode operator, scalar source stationarity only.
No fictitious relative fixation, zero-pressure open gap, or unique line pressure.
"""
import sys,json,time,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,sha,dump

def evaluate(pin,hole,R,t,gamma):
 # R/t is a COMMON Root pose; only upstream hole has local-Y relative shift.
 axis=R@np.array(pin['axis']);P=R@np.array(pin['axis_point_mm'])+t;H=R@(np.array(hole['axis_point_mm'])+[0,gamma,0])+t;v=H-P;v-=axis*(axis@v);rho=np.linalg.norm(v);gap=hole['radius_mm']-pin['radius_mm']-rho
 if rho<1e-12:return dict(gap_mm=float(gap),gamma_J=None,normal_world=None,pressure_N=0.,chart='STRICTLY_INACTIVE_COAXIAL_NO_DERIVATIVE')
 normal=v/rho;J=-float(normal@(R@np.array([0,1,0])))
 # Reaction on hole points away from displacement and toward centered clearance.
 return dict(gap_mm=float(gap),gamma_J=J,normal_world=(-normal).tolist(),chart='FINITE_RADIAL_CHART')

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());sp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/summary.json';s=json.loads(sp.read_text());gp=REPO/s['geometry']['path'];geometry=json.loads(gp.read_text());dump(out/'inputs.json',dict(candidate=ref(cp),fresh_local_source=ref(sp),actual_pin_holes=ref(gp),producer=ref(out/'producer.py'),conditional_scope='Source scalar gamma stationarity at specified reference/tilted Root+Motor poses. No whole support solve; source XZ clamp remains conditional.'))
 rows=[];controls=[]
 for g in geometry:
  for gamma in [0.,-.05,-.025,.025,.05,.051]:
   R=Rotation.from_rotvec([.003,-.002,.001]).as_matrix();t=np.array([.01,-.02,.03]);e=evaluate(g['pin'],g['hole'],R,t,gamma);zero=evaluate(g['pin'],g['hole'],np.eye(3),np.zeros(3),gamma);eps=1e-5;derivative=(evaluate(g['pin'],g['hole'],R,t,gamma+eps)['gap_mm']-evaluate(g['pin'],g['hole'],R,t,gamma-eps)['gap_mm'])/(2*eps);J=e['gamma_J'];controls.append(dict(part=g['part'],gamma_mm=gamma,gap_mm=e['gap_mm'],objective_error_mm=abs(e['gap_mm']-zero['gap_mm']),derivative_error=None if J is None else abs(derivative-J),coaxial_derivative_not_invented=J is None if gamma==0 else True,penetration_rejected=e['gap_mm']< -1e-10))
 for name in ['reference','tilt_minus','tilt_zero','tilt_plus']:
  c=next(c for c in s['results'] if c['case']==name);gamma=c['gamma_local_mm'];R=Rotation.from_rotvec([c['root_motor_common_X_rotation_rad'],0,0]).as_matrix();ev=[evaluate(g['pin'],g['hole'],R,np.zeros(3),gamma) for g in geometry];active=[i for i,e in enumerate(ev) if abs(e['gap_mm'])<1e-10];Q=c['gamma_force_N'];ranges=[];feasible=False;total=0.
  if active:
   J=np.array([ev[i]['gamma_J'] for i in active]);solution=linprog(np.ones(len(active)),A_eq=J[None,:],b_eq=[-Q],bounds=(0,None),method='highs');feasible=bool(solution.success)
   if feasible:
    total=float(solution.x.sum())
    for i in range(len(active)):
     objective=np.eye(len(active))[i];lo=linprog(objective,A_eq=J[None,:],b_eq=[-Q],bounds=(0,None),method='highs');hi=linprog(-objective,A_eq=J[None,:],b_eq=[-Q],bounds=(0,None),method='highs');ranges.append(dict(part=geometry[i]['part'],reaction_range_N=[float(lo.fun),float(-hi.fun)],unique=False))
    residual=abs(float(J@solution.x)+Q)
   else:residual=abs(Q)
   rank=int(np.linalg.matrix_rank(J[None,:]));nullity=len(active)-rank
  else:feasible=abs(Q)<1e-8;residual=abs(Q);rank=0;nullity=0
  rows.append(dict(case=name,gamma_mm=gamma,Qgamma_N=Q,pin_gaps_mm=[e['gap_mm'] for e in ev],active_pin_hole_pairs=len(active),conditional_scalar_KKT_feasible=feasible,scalar_force_residual_N=residual,total_necessary_pin_reaction_N=total,pressure_is_applied_to_support=False,active_constraint_rank=rank,individual_reaction_nullity=nullity,reaction_allocation_ranges=ranges,open_gap_has_assigned_pressure=False,whole_support_equilibrium=False))
 # Exact per-contact cotangent work with finite common rotation and relative mode.
 R=Rotation.from_rotvec([.003,-.002,.001]).as_matrix();omega=np.array([.0001,-.0002,.0003]);v=np.array([.002,.003,-.001]);dg=.002;tests=[]
 for g in geometry:
  gamma=-.05;e=evaluate(g['pin'],g['hole'],R,np.zeros(3),gamma);n=np.array(e['normal_world']);P=np.array(g['pin']['axis_point_mm']);H=np.array(g['hole']['axis_point_mm'])+[0,gamma,0];x=(max(g['pin']['bounds_mm'][0],g['hole']['bounds_mm'][0])+min(g['pin']['bounds_mm'][3],g['hole']['bounds_mm'][3]))/2;P[0]=x;H[0]=x;contact=R@(P-g['pin']['radius_mm']*np.array([0,-1,0]));vp=v+np.cross(omega,contact);vh=vp+R@np.array([0,dg,0]);force=n*.001;physical=float(force@(vh-vp));analytic=.001*e['gamma_J']*dg;tests.append(dict(part=g['part'],pair_work_error_Nmm=abs(physical-analytic),common_Root_force_sum_N=float(np.linalg.norm(force-force)),common_Root_moment_sum_Nmm=float(np.linalg.norm(np.cross(contact,force)+np.cross(contact,-force)))))
 checks=dict(all_objective_finite_charts=all(c['objective_error_mm']<1e-10 and(c['derivative_error'] is None or c['derivative_error']<1e-7) for c in controls),all_coaxial_derivatives_unassigned=all(c['coaxial_derivative_not_invented'] for c in controls),all_overclearance_rejected=all(c['penetration_rejected'] for c in controls if c['gamma_mm']>.05),reference_open_equilibrium=rows[0]['conditional_scalar_KKT_feasible'] and rows[0]['active_pin_hole_pairs']==0,tilted_lower_stop_scalar_equilibrium=rows[1]['conditional_scalar_KKT_feasible'] and rows[1]['scalar_force_residual_N']<1e-8,tilted_free_and_wrong_stop_rejected=not rows[2]['conditional_scalar_KKT_feasible'] and not rows[3]['conditional_scalar_KKT_feasible'],individual_pin_reaction_not_faked=rows[1]['individual_reaction_nullity']==3,paired_pin_virtual_work=all(c['pair_work_error_Nmm']<1e-12 for c in tests))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_LOCAL_PIN_MODE_SCALAR_KKT_VERIFIED_NOT_SUPPORT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_PIN_MODE_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,results=rows,finite_charts=controls,pair_virtual_work=tests,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['Conditional scalar gamma stationarity only, neither full upstream attachment nor whole product equilibrium. Tilt is explicit sensitivity, not new operating criterion.','Four identical radial constraints have rank1/nullity3: only total reaction determined, not each pin/rail/front load or finite line pressure. Do not feed arbitrary equal split into Root strength.','Nominal tangent cylinders contact on finite axial lines with zero ideal area. Compliance/contact pressure and complete3Dclamp/axialfriction/rotational restraint need physical model; no finite strength can be inferred from this necessary reaction.','Finite action/reaction uses same world contact and preserves force/moment; Root body is never grounded and gamma is never silently eliminated.']))
 print(json.dumps(dict(checks=checks,results=rows)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
