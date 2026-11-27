"""Sparse minimum-L1 algorithmic phase-I seed on original P1 rows.
L1 is ONLY a feasibility initializer, never physical stiffness/energy.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_freeY_phase1/summary.json';s=json.loads(src.read_text());assert s['phase1_feasible'];p=np.load(REPO/s['problem']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);D=p['D'];E=p['E'];lo=p['lower'];hi=p['upper'];eq=np.isfinite(hi)&(lo==hi);ii=np.flatnonzero(~eq);ee=np.flatnonzero(eq);As=(sparse.diags(E*1e4)@A@sparse.diags(D)).tocsc();cols=np.flatnonzero(np.diff(As.indptr));Ar=As[:,cols];C=sparse.hstack([Ar,-Ar],format='csc');rhs=E*1e4*lo
 sol=linprog(np.ones(2*len(cols)),A_ub=-C[ii],b_ub=-rhs[ii],A_eq=C[ee],b_eq=rhs[ee],bounds=(0,None),method='highs-ds',options=dict(time_limit=90.,primal_feasibility_tolerance=1e-10,dual_feasibility_tolerance=1e-10,presolve=True));feasible=False;info=dict(solver_status=int(sol.status),solver_message=sol.message,iterations=int(sol.nit),solver_success=bool(sol.success))
 if sol.x is not None:
  z=np.zeros(len(D));z[cols]=sol.x[:len(cols)]-sol.x[len(cols):];x=D*z;sl=A@x-lo;primal=max(float(np.max(np.maximum(-sl[ii],0))),float(np.max(abs(sl[ee]))));feasible=primal<1e-10
  np.savez_compressed(out/'seed.npz',physical_x=x,scaled_z=z,physical_slack_mm=sl,LP_split_solution=sol.x,used_columns=cols,LP_inequality_dual=sol.ineqlin.marginals,LP_equality_dual=sol.eqlin.marginals,LP_lower_dual=sol.lower.marginals)
  info.update(output=ref(out/'seed.npz'),physical_primal_mm=primal,L1_scaled_initializer_objective=float(sol.fun),maximum_increment_mm_rad=float(np.max(abs(x))),gamma_mm=float(x[-1]),nonzero_coordinates=int(np.sum(x!=0)),active_contact_rows=int(np.sum(abs(sl[:2169])<1e-12)),minimum_contact_slack_mm=float(np.min(sl[:2169])),minimum_branch_slack_mm=float(np.min(sl[2180:])),equality_defect_mm=float(np.max(abs(sl[ee]))))
 result=dict(status='ACTUAL_P1_FREEY_SPARSE_FEASIBLE_SEED_NOT_EQUILIBRIUM' if feasible else 'ACTUAL_P1_FREEY_SPARSE_SEED_REJECTED',candidate=s['candidate'],source_field=s['source_field'],source=ref(src),producer=ref(out/'producer.py'),physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],phase1_feasible=bool(feasible),positive_row_numeric_factor=1e4,unused_A_columns_set_zero=len(D)-len(cols),physical_regularization=0.,all_original_inequalities_retained=True,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Minimum L1 is algorithmic feasibility selection only. No physical springs/energy or equilibrium claim; all physical objective P/q unchanged for subsequent KKT.','All2169contacts/14branches/11gauges retained; original RootY augmented with unpenalized physical gamma. No nonlinear increment applied.'],**info);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if feasible else 2)
if __name__=='__main__':main()
