"""Separate normal beam DOFs + finite channel unilateral coupon for RevAB.
Static convex QP only. No shared PET curvature or hidden distal bond imposed.
Continuous piecewise-cubic gaps checked independently of constraint samples.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy.linalg import block_diag,null_space
from scipy.optimize import lsq_linear
from scipy.sparse import csc_matrix
import osqp
import osqp.ext_builtin
from finger_structure import ROOT,E_PET,E_RAIL,width,sha
LR=.088;LP=.0874
def beam(n,length,EI):
    K=np.zeros((2*(n+1),2*(n+1)));h=length/n;x,w=np.polynomial.legendre.leggauss(3)
    for j in range(n):
        ke=np.zeros((4,4))
        for t,v in zip((x+1)/2,w/2):
            B=np.array([(-6+12*t)/h**2,(-4+6*t)/h,(6-12*t)/h**2,(-2+6*t)/h])
            ke+=v*h*EI((j+t)*h)*np.outer(B,B)
        ids=np.arange(2*j,2*j+4);K[np.ix_(ids,ids)]+=ke
    return K
def shape(n,length,s):
    h=length/n;j=min(int(s/h),n-1);t=(s-j*h)/h;v=np.zeros(2*(n+1))
    v[2*j:2*j+4]=[1-3*t*t+2*t**3,h*(t-2*t*t+t**3),3*t*t-2*t**3,h*(-t*t+t**3)]
    return v
def gap_row(n,kind,s):
    r=shape(n,LR,s);p=shape(n,LP,s)
    if kind=='interface':return np.r_[r,-p],0.
    line=np.zeros(len(r));line[-2]=1;line[-1]=s-LR
    a=np.r_[-line,p]
    return (a,-.0001) if kind=='front' else (-a,-.0002)
def exact_min(n,u,kind):
    lo=0 if kind=='interface' else .083
    knots=sorted(set([lo,LP]+[x for x in np.r_[np.linspace(0,LR,n+1),np.linspace(0,LP,n+1)] if lo<x<LP]))
    best=(float('inf'),None)
    for a,b in zip(knots,knots[1:]):
        xs=np.array([0.,1/3,2/3,1.]);values=[]
        for x in xs:
            row,bound=gap_row(n,kind,a+(b-a)*x);values.append(float(row@u-bound))
        co=np.polynomial.polynomial.polyfit(xs,values,3)
        critical=np.roots([3*co[3],2*co[2],co[1]])
        candidates=[0.,1.]+[float(v.real) for v in critical if abs(v.imag)<1e-8 and 0<v.real<1]
        for t in candidates:
            value=float(np.polynomial.polynomial.polyval(t,co))
            if value<best[0]:best=(value,a+(b-a)*t)
    return best
def trial(n,force,guide):
    m=2*(n+1);K=block_diag(beam(n,LR,lambda s:2*E_RAIL*.003*.0002**3/12),beam(n,LP,lambda s:E_PET*width(s)*.0003**3/12))
    f=np.zeros(2*m);f[m-2]=force;fixed={0,1,m,m+1};free=np.array([i for i in range(2*m) if i not in fixed])
    scale=np.tile([.001,.001/LR],2*(n+1));D=scale[free];unit=1e-6
    P=K[np.ix_(free,free)]*np.outer(D,D)/unit;q=-f[free]*D/unit
    kinds=['interface']+(['front','back'] if guide else [])
    points={kind:sorted(set(np.linspace(0,LP,2*n+1)[1:] if kind=='interface' else np.linspace(.083,LP,9))) for kind in kinds}
    u=np.zeros(2*m);result=None
    for loop in range(12):
        rows=[];lower=[];labels=[]
        for kind in kinds:
            for s in points[kind]:
                row,bound=gap_row(n,kind,s);rows.append(row);lower.append(bound);labels.append((kind,s))
        A=np.array(rows);lower=np.array(lower);An=A[:,free]*D/.001
        qp=osqp.OSQP();qp.setup(P=csc_matrix(P),q=q,A=csc_matrix(An),l=lower/.001,u=np.full(len(lower),np.inf),
            eps_abs=1e-10,eps_rel=1e-10,max_iter=100000,polishing=True,verbose=False,time_limit=60.)
        result=qp.solve();
        if result.x is None:raise RuntimeError(result.info.status)
        # OSQP polishing can return an inaccurate x on redundant channel
        # rows. Solve the SAME convex energy on its guessed active subspace,
        # then independently require nonpositive duals, global feasibility,
        # stationarity and complementarity. This is a STATIC equilibrium
        # solve, never correction of a Native q/v trajectory.
        seed=result.x.copy();seed_slack=An@seed-lower/.001
        # Near-zero geometric gap alone is NOT proof of a load-bearing
        # equality. Including unloaded near-contact rows overconstrains the
        # beam. Use supporting duals, then certify ALL original inequalities.
        active=np.flatnonzero(result.y < -1e-9)
        if len(active):
            aa=An[active];bb=lower[active]/.001
            xp=np.linalg.lstsq(aa,bb,rcond=None)[0];Z=null_space(aa)
            exact=xp+Z@np.linalg.solve(Z.T@P@Z,-Z.T@(P@xp+q))
            dual=lsq_linear(aa.T,-P@exact-q,bounds=(-np.inf,0),tol=1e-14,lsq_solver='exact',max_iter=1000)
            y=np.zeros(len(lower));y[active]=dual.x
        else:
            exact=np.linalg.solve(P,-q);y=np.zeros(len(lower))
        u[free]=D*exact
        minima={kind:exact_min(n,u,kind) for kind in kinds}
        new=False
        for kind,(value,s) in minima.items():
            if value < -1e-9 and all(abs(s-p)>1e-12 for p in points[kind]):points[kind].append(s);points[kind].sort();new=True
        if not new:break
    multiplier=y*.001;res=K@u-f+A.T@multiplier
    scaled=res[free].copy();scaled[free%2==1]/=LR
    residual=float(np.linalg.norm(scaled));slack=A@u-lower
    complement=float(np.sum(abs(multiplier*slack))/unit)
    root_force=float(res[0]+res[m]);balance=abs(root_force+force)
    minimum=min(v[0] for v in minima.values())
    guide_force=sum(abs(multiplier[i]) for i,(kind,s) in enumerate(labels) if kind!='interface')
    return dict(n=n,force_N=force,guide=guide,rail_tip_m=float(u[m-2]),PET_tip_m=float(u[-2]),
        minimum_continuous_cubic_gap_m=minimum,KKT_force_equivalent_N=residual,root_force_balance_N=balance,
        complementarity_relative=complement,guide_normal_multiplier_sum_N=float(guide_force),
        energy_J=float(.5*u@K@u),qp_status=result.info.status,cutting_plane_rounds=loop+1,
        final_method='active-subspace exact equilibrium plus nonpositive-dual feasibility',
        active_rank=int(np.linalg.matrix_rank(An[active])) if len(active) else 0,
        constraint_locations=labels,constraint_duals_N=multiplier.tolist(),
        rail_q=u[:m].tolist(),PET_q=u[m:].tolist(),
        status='PASS' if result.info.status=='solved' and minimum>=-1e-9 and residual<1e-8 and balance<1e-8 and complement<1e-7 else 'FAIL')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=ROOT/'validation/finger'/args.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py');rows=[]
    for force in (-.001,.001):
        for n in (8,16,32):rows.append(trial(n,force,True))
    rows.append(trial(32,.001,False));convergence=[]
    for force in (-.001,.001):
        c=[r for r in rows if r['force_N']==force and r['guide']];lo,hi=c[-2:]
        error=max(abs(lo[key]/hi[key]-1) for key in ('rail_tip_m','PET_tip_m'))
        convergence.append(dict(force_N=force,error_relative=error,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows+convergence) else 'FAIL',
        scope='SMALL-DEFLECTION SEPARATE-LAYER FRICTIONLESS CHANNEL COUPON ONLY',
        candidate='RevAB sliding PET, no adoption',rows=rows,convergence=convergence,osqp_version=osqp.__version__,
        source_SHA256=sha(Path(__file__)),beam_source_SHA256=sha(Path(__file__).with_name('finger_structure.py')),
        OSQP_binary_SHA256=sha(Path(osqp.ext_builtin.__file__)),
        candidate_geometry_SHA256=sha(ROOT/'revised_cad/revAB_sliding_pet1/summary.json'),
        criteria_SHA256=sha(ROOT/'models/analytical/contact_coupon_criteria.json'),
        exclusions=['finite rotation','axial friction and strain coupling','3D shell wrinkling','actual strength','dynamic response','grasp'],
        command='PYTHONPATH=/tmp/regrip_stage2_fem OPENBLAS_NUM_THREADS=1 python scripts/sliding_pet_contact.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({**result,'rows':[{k:v for k,v in r.items() if k not in ('rail_q','PET_q')} for r in rows]},indent=2))
if __name__=='__main__':main()
