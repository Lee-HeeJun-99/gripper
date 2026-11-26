"""Finite-rotation PET against a prescribed circular RIGID rail test fixture.

Independent PET angles, inextensible segments and unilateral normal contact.
Rail fixture is NOT a solved flexible rail or actual whole Finger. Frictionless
limit only. This isolates geometry/axial migration before coupled friction FE.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,nnls
from baseline_registry import ROOT,S2,ref,dump
L=.0874;LR=.088;offset=.00025;gapmax=.00010
def curve(q,n):
    angles=np.r_[0.,q];delta=np.diff(angles);average=(angles[1:]+angles[:-1])/2
    # Exact constant-curvature integration, not chord lengths.
    steps=L/n*np.sinc(delta/(2*np.pi))[:,None]*np.column_stack((np.cos(average),np.sin(average))) if False else None
    factor=(L/n)*np.sinc(delta/(2*np.pi))
    step=factor[:,None]*np.column_stack((np.cos(average),np.sin(average)))
    return np.vstack(([0.,offset],np.array([0.,offset])+np.cumsum(step,axis=0)))
def solve(n,theta):
    R=LR/theta;h=L/n
    # Actual taper approximated from24mm at material z=0 to12mm at z=-100.
    s=(np.arange(n)+.5)*h;width=.024-(.024-.012)*(.007+s)/.100
    E=507000*6894.757293168 # manufacturer typical, NOT allowable
    EI=E*width*.0003**3/12
    energy_scale=float(np.mean(EI)*theta*theta/LR)
    def energy(q):return float(np.sum(EI*np.diff(np.r_[0.,q])**2/(2*h))/energy_scale)
    def constraints(q):
        p=curve(q,n);rad=np.linalg.norm(p[1:]-[0.,R],axis=1)
        gap=R-offset-rad
        # Channel lip is a finite rear bound only in last4.4mm of rail.
        arc=R*np.arctan2(p[-1,0],R-p[-1,1])
        return np.r_[gap/1e-4,(gapmax-gap[-1])/1e-4,(arc-.083)/.001,(LR-arc)/.001]
    initial=np.arange(1,n+1)*h/(R-offset)
    result=minimize(energy,initial,method='SLSQP',constraints=[dict(type='ineq',fun=constraints)],options=dict(ftol=1e-12,maxiter=600))
    q=result.x;p=curve(q,n);c=constraints(q)
    # Finite-difference stationarity + nonnegative unilateral multipliers.
    eps=1e-6
    grad=np.array([(energy(q+np.eye(n)[i]*eps)-energy(q-np.eye(n)[i]*eps))/(2*eps) for i in range(n)])
    jac=np.column_stack([(constraints(q+np.eye(n)[i]*eps)-constraints(q-np.eye(n)[i]*eps))/(2*eps) for i in range(n)])
    active=np.flatnonzero(c<1e-5)
    multip,res=nnls(jac[active].T,grad,maxiter=20*n) if len(active) else (np.zeros(0),np.linalg.norm(grad))
    # Independent dense witness only; explicitly NOT continuous contact proof.
    dense=[]
    full=np.r_[0.,q]
    for i in range(n):
        for t in np.linspace(0,1,21):
            d=(full[i+1]-full[i])*t;a=full[i]+d/2
            pt=p[i]+h*t*np.sinc(d/(2*np.pi))*np.array([np.cos(a),np.sin(a)])
            dense.append(R-offset-np.linalg.norm(pt-[0.,R]))
    arc=R*math.atan2(p[-1,0],R-p[-1,1]);expected_arc=L*R/(R-offset)
    return dict(n=n,fixture_angle_deg=math.degrees(theta),solver_success=bool(result.success),message=result.message,
        energy_J=energy(q)*energy_scale,minimum_node_constraint=float(c.min()),sampled_min_gap_m=float(min(dense)),
        stationarity_scaled=float(res),PET_end_projection_m=arc,axial_migration_m=arc-L,
        circular_contact_reference_projection_m=expected_arc,projection_reference_relative=abs(arc-expected_arc)/expected_arc,
        PET_end_angle_rad=float(q[-1]),state_angles_rad=q.tolist(),PET_nodes_m=p.tolist(),
        active_constraints=active.tolist(),scaled_multipliers=multip.tolist(),
        status='PASS' if result.success and c.min()>-1e-5 and min(dense)>-1e-9 and res<1e-5 else 'FAIL')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    rows=[solve(n,math.radians(angle)) for angle in (15.,30.,60.) for n in (8,16,32)]
    conv=[]
    for angle in (15.,30.,60.):
        values=[r for r in rows if abs(r['fixture_angle_deg']-angle)<1e-8];a,b=values[-2:]
        error=abs(a['energy_J']-b['energy_J'])/b['energy_J'];conv.append(dict(angle_deg=angle,energy_refinement_relative=error,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows+conv) else 'FAIL',scope='FRICTIONLESS FINITE-ROTATION PET / RIGID CIRCULAR RAIL FIXTURE COUPON ONLY',
        rows=rows,convergence=conv,producer=ref(Path(__file__)),candidate=ref(S2/'revised_cad/revAB_sliding_pet1/summary.json'),
        typical_modulus_not_allowable=True,friction=0,rail_is_prescribed_fixture=True,
        coupled_finger_validated=False,limitations=['No flexible-rail coupling, friction, PET extension, shell wrinkling or material certification','Contact between nodes checked by dense witnesses only; not continuous proof','Actual 3D finite guide geometry replaced by declared projected channel inequalities'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','fixture_angle_deg','status','sampled_min_gap_m','stationarity_scaled','axial_migration_m')} for r in rows],convergence=conv),indent=2))
if __name__=='__main__':main()
