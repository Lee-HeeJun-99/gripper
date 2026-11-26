"""Minimal independent contact-owner Jacobian counterexample.
Same feasible intersection, different numerical representation. Not proof that
this is the ONLY cause of the actual PET failure; no PET state is modified.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,nnls
from baseline_registry import ROOT,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/contact'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    A=np.array([[1.,1.,0.],[1.,0.,1.]]);target=-np.ones(3)
    lam=np.linalg.solve(A@A.T,-A@target);exact=target+A.T@lam
    def energy(x):return .5*float((x-target)@(x-target))
    def gradient(x):return x-target
    # Identically zero root-contact row is satisfied, but carries no free-DOF force.
    def aggregated(x):return min(0.,float(np.min(A@x)))
    step=1e-6;g=np.array([(aggregated(exact+step*np.eye(3)[j])-aggregated(exact-step*np.eye(3)[j]))/(2*step) for j in range(3)])
    _,cone_error=nnls(A.T,g)
    explicit=minimize(energy,np.zeros(3),jac=gradient,method='SLSQP',constraints=[dict(type='ineq',fun=lambda x:A@x,jac=lambda x:A)],options=dict(ftol=1e-12,maxiter=200))
    combined=minimize(energy,np.zeros(3),jac=gradient,method='SLSQP',constraints=[dict(type='ineq',fun=aggregated)],options=dict(ftol=1e-12,maxiter=200))
    result=dict(status='PASS' if np.linalg.norm(explicit.x-exact)<1e-8 and cone_error>.01 and np.linalg.norm(gradient(exact)-A.T@lam)<1e-10 else 'FAIL',
        scope='INDEPENDENT MINIMUM-OWNER DIFFERENTIATION COUNTEREXAMPLE ONLY',
        exact_solution=exact.tolist(),explicit_result=explicit.x.tolist(),explicit_solver_success=bool(explicit.success),
        aggregated_result=combined.x.tolist(),aggregated_solver_success=bool(combined.success),aggregated_message=combined.message,
        aggregated_solution_error=float(np.linalg.norm(combined.x-exact)),
        central_difference_of_minimum=g.tolist(),distance_to_physical_normal_cone=float(cone_error),
        true_contact_rows=A.tolist(),true_multipliers=lam.tolist(),
        criterion='Explicit force/KKT error<1e-10 and solution<1e-8; min-Jacobian outside physical normal cone by>0.01',
        significance='Finite differences of a minimum over changing owners can produce a vector outside the admissible contact normal cone; preserve material feature Jacobians explicitly.',
        actual_PET_cause_confirmed=False,actual_PET_state_changed=False,
        next='Feature-owned material contact rows / witness exchange, analytic point Jacobians; independently recertify real PET force, gap and1% migration convergence',producer=ref(out/'producer.py'))
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
