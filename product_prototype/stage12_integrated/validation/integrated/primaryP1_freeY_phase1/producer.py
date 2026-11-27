"""Actual P1 original-row phase I, free RootY; no physical support update.
HiGHS solves a linear feasibility problem, not a structural equilibrium.
The finite scaled box is a SEARCH region only and never a physical support.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,dump,sha
from primary_rootY_coordinate import augment_rootY

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'validation/integrated/primaryP1_matrixfree1/summary.json';s=json.loads(src.read_text());p=np.load(REPO/s['problem']['path']);P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);q=p['q'];lo=p['lower'];hi=p['upper'];labels=['unused']*11;labels[6]='Root_free_Y';labels[7]='Motor_free_Y'
 P,q,A,lo,hi,coord=augment_rootY(P,q,A,lo,hi,labels);assert coord['original_RootY_row']==2175 and coord['original_MotorY_row']==2176
 D=np.r_[p['D'],1.];E=p['E'];As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();eq=np.isfinite(hi)&(lo==hi);ii=np.flatnonzero(~eq);ee=np.flatnonzero(eq);n=len(D);gap_unit_mm=1e-4
 # min t >= 0, with As*z + E*gap_unit*t >= E*lo.
 # All eleven original equality rows exact. RootY gamma has zero P/q.
 C=sparse.hstack([-As[ii],sparse.csr_matrix((-E[ii]*gap_unit_mm)[:,None])],format='csc');be=-E[ii]*lo[ii];Ce=sparse.hstack([As[ee],sparse.csr_matrix((len(ee),1))],format='csc');he=E[ee]*lo[ee];c=np.r_[np.zeros(n),1.]
 bounds=np.vstack([-np.ones(n+1),np.ones(n+1)]).T;bounds[-1]=[0,np.inf]
 for name,mat in [('physical_P',P),('physical_A',A)]:sparse.save_npz(out/(name+'.npz'),mat)
 np.savez_compressed(out/'problem.npz',q=q,lower=lo,upper=hi,D=D,E=E,inequality_rows=ii,equality_rows=ee,phase_gap_unit_mm=gap_unit_mm,search_bounds=bounds)
 dump(out/'preexecution.json',dict(source=ref(src),candidate=s['candidate'],source_field=s['source_field'],producer=ref(out/'producer.py'),coordinate=coord,physical_rows=A.shape[0],physical_coordinates=n,phase1_objective='minimum uniform physical inequality violation / 1e-4mm; equalities exact',search_box='scaled coordinate [-1,1], purely algorithmic, not physical restraint',time_limit_s=90,all_original_rows_retained=True))
 sol=linprog(c,A_ub=C,b_ub=be,A_eq=Ce,b_eq=he,bounds=bounds,method='highs-ds',options=dict(time_limit=90.,primal_feasibility_tolerance=1e-10,dual_feasibility_tolerance=1e-10,presolve=True))
 info=dict(solver_status=int(sol.status),solver_message=sol.message,iterations=int(sol.nit),solver_success=bool(sol.success));feasible=False
 if sol.x is not None:
  z=sol.x[:-1];x=D*z;t=float(sol.x[-1]);sl=A@x-lo;physical=max(float(np.max(np.maximum(-sl[ii],0))),float(np.max(abs(sl[ee]))));feasible=physical<1e-8 and t*gap_unit_mm<1e-8
  # LP multipliers explicitly include the search bounds; never structural duals.
  lpgrad=c+C.T@sol.ineqlin.marginals+Ce.T@sol.eqlin.marginals if False else c-C.T@sol.ineqlin.marginals-Ce.T@sol.eqlin.marginals-sol.lower.marginals-sol.upper.marginals
  np.savez_compressed(out/'phase1.npz',physical_x=x,scaled_z=z,phase_t=t,physical_slack_mm=sl,LP_inequality_dual=sol.ineqlin.marginals,LP_equality_dual=sol.eqlin.marginals,LP_lower_dual=sol.lower.marginals,LP_upper_dual=sol.upper.marginals,LP_stationarity=lpgrad)
  info.update(output=ref(out/'phase1.npz'),phase_violation_mm=t*gap_unit_mm,physical_primal_mm=physical,maximum_increment_mm_rad=float(np.max(abs(x[:-15]))),gamma_mm=float(x[-1]),max_scaled_coordinate=float(np.max(abs(z))),search_box_active_coordinates=int(np.sum(abs(z)>1-1e-8)),LP_stationarity=float(np.max(abs(lpgrad))),minimum_contact_gap_mm=float(np.min(sl[:2169])),minimum_branch_slack_mm=float(np.min(sl[2180:])),equality_defect_mm=float(np.max(abs(sl[ee]))))
 result=dict(status='ACTUAL_P1_FREEY_PHASE1_FEASIBLE_NOT_EQUILIBRIUM' if feasible else 'ACTUAL_P1_FREEY_PHASE1_REJECTED',candidate=s['candidate'],source_field=s['source_field'],source=ref(src),producer=ref(out/'producer.py'),physical_P=ref(out/'physical_P.npz'),physical_A=ref(out/'physical_A.npz'),problem=ref(out/'problem.npz'),coordinate=coord,phase1_feasible=bool(feasible),physical_regularization=0.,all_original_inequalities_retained=True,original_contacts=2169,original_branches=14,original_equalities=11,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Phase I is only feasibility of original-source linear constraints. No equilibrium, physical multipliers, nonlinear acceptance, new stress, strength or mesh/energy qualification.','Search box has algorithmic bound multipliers; it is not a fixation and cannot be included in product force equilibrium. Free RootY gamma has zero metric/force; MotorY and all original rows unchanged.'],**info)
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if feasible else 2)
if __name__=='__main__':main()
