"""Finite extensible planar rod reference, free axial tip; no assembly contact claim.
Independent e,theta with r'=(1+e)t. Stationary e=(F.t)/EA is
condensed exactly. Midpoint energy is compared with continuous BVP, not fitted.
"""
import os,sys,shutil,json
from pathlib import Path
import numpy as np
from scipy.optimize import root
from scipy.integrate import solve_bvp,quad
from baseline_registry import ROOT,REPO,ref,dump
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from finger_structure import E_RAIL,E_PET,width
CRITERIA={'finest_tip_relative_max':.001,'finest_rotation_relative_max':.001,
          'gradient_residual_Nm_max':1e-10,'virtual_work_relative_max':1e-7,
          'objectivity_absolute_J_max':1e-13,'small_load_linear_relative_max':1e-5}
def section(body,s):
    if body=='rail':return 2*E_RAIL*.003*.0002,2*E_RAIL*.003*.0002**3/12
    return E_PET*width(s)*.0003,E_PET*width(s)*.0003**3/12

def discrete(body,L,F,n):
    h=L/n;s=(np.arange(n)+.5)*h;EA,EI=section(body,s)
    def calc(z):
        th=np.r_[0,z];a=(th[:-1]+th[1:])/2;d=np.diff(th)/h
        # F=(0,Fy), dead load in fixed spatial frame.
        p=F*np.sin(a);dp=F*np.cos(a)
        g=np.zeros(n+1);b=EI*d;c=-h*dp*(1+p/EA)/2
        g[:-1]+=-b+c;g[1:]+=b+c
        return g[1:]
    sol=root(calc,np.zeros(n),tol=1e-10)
    th=np.r_[0,sol.x];a=(th[:-1]+th[1:])/2;e=F*np.sin(a)/EA
    dr=h*np.column_stack(((1+e)*np.cos(a),(1+e)*np.sin(a)))
    r=np.vstack((np.zeros(2),np.cumsum(dr,axis=0)))
    U=float(np.sum(h*(EA*e**2+EI*(np.diff(th)/h)**2)/2))
    return dict(n=n,solver_success=bool(sol.success),solver_message=str(sol.message),
        residual_Nm=float(max(abs(calc(sol.x)))),tip_m=r[-1].tolist(),rotation_rad=float(th[-1]),
        r_m=r.tolist(),theta_rad=th.tolist(),strain=e.tolist(),stored_energy_J=U,
        potential_J=U-F*r[-1,1])

def continuous(body,L,F):
    def ode(s,z):
        EA,EI=section(body,s);e=F*np.sin(z[2])/EA
        return np.array([(1+e)*np.cos(z[2]),(1+e)*np.sin(z[2]),z[3]/EI,-F*(1+e)*np.cos(z[2])])
    def bc(a,b):return np.array([a[0],a[1],a[2],b[3]])
    s=np.linspace(0,L,101);z=np.zeros((4,len(s)));z[0]=s
    sol=solve_bvp(ode,bc,s,z,tol=1e-10,max_nodes=10000)
    return dict(success=bool(sol.success),message=sol.message,nodes=len(sol.x),
        tip_m=sol.y[:2,-1].tolist(),rotation_rad=float(sol.y[2,-1]),max_rms_residual=float(max(sol.rms_residuals)))

def variational_checks(body,L):
    n=19;h=L/n;s=(np.arange(n)+.5)*h;EA,EI=section(body,s)
    th=.4*np.sin(np.linspace(0,1,n+1));e=np.linspace(-.0002,.0003,n)
    dt=np.cos(np.arange(n+1))*.2;dt[0]=0;de=np.sin(np.arange(n))*.001
    F=np.array([.012,-.009])
    def energy(e,t,F):
        a=(t[:-1]+t[1:])/2;v=np.column_stack((np.cos(a),np.sin(a)))
        return float(np.sum(h*(EA*e*e+EI*(np.diff(t)/h)**2)/2)-F@np.sum(h*(1+e)[:,None]*v,axis=0))
    a=(th[:-1]+th[1:])/2;t=np.column_stack((np.cos(a),np.sin(a)));normal=np.column_stack((-np.sin(a),np.cos(a)))
    analytic=float(np.sum(h*EA*e*de+EI*np.diff(th)*np.diff(dt)/h-h*(de*(t@F)+(1+e)*(normal@F)*(dt[:-1]+dt[1:])/2)))
    eps=1e-4;numeric=(energy(e+eps*de,th+eps*dt,F)-energy(e-eps*de,th-eps*dt,F))/(2*eps)
    angle=1.1;Q=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    obj=abs(energy(e,th,F)-energy(e,th+angle,Q@F))
    rel=abs(analytic-numeric)/max(abs(analytic),1e-16)
    return dict(analytic_virtual_work_J=analytic,finite_difference_J=numeric,relative_error=rel,
        objectivity_absolute_J=obj,passed=bool(rel<=CRITERIA['virtual_work_relative_max'] and obj<=CRITERIA['objectivity_absolute_J_max']))

def main():
    if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
    out=ROOT/'validation/finger'/sys.argv[1];out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    dump(out/'inputs.json',dict(criteria=CRITERIA,inputs=[ref(Path(__file__)),ref(ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py'),ref(ROOT/'validation/finger/finite_kinematic_budget1/summary.json'),ref(ROOT/'cad/exports/revAD_funnel1/summary.json')],
        contract='Each separate body: root x=y=theta=0, free axial/transverse tip with dead Fy; Mtip=0. NOT actual guide boundary conditions. Strain e independent before exact static condensation.',
        energy='Integral [EA e^2/2+EI theta_prime^2/2] ds - F.r(L); r_prime=(1+e)(cos(theta),sin(theta)). Engineering strain, unshearable planar rod.',
        material='Unchanged conditional typical moduli/projected sections; no certified lot or actual BRep.',
        acceptance='Predeclared reference-only thresholds; old contact and release thresholds untouched.'))
    rows=[];checks=[]
    for body,L in [('rail',.088),('PET',.0862)]:
        checks.append(dict(body=body,**variational_checks(body,L)))
        for F in (1e-7,.001,.02):
            if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
            b=continuous(body,L,F);ds=[discrete(body,L,F,n) for n in (16,32,64)]
            tiperr=abs(ds[-1]['tip_m'][1]/b['tip_m'][1]-1);roterr=abs(ds[-1]['rotation_rad']/b['rotation_rad']-1)
            lin=F*quad(lambda s:(L-s)**2/section(body,s)[1],0,L,epsabs=1e-16)[0]
            linearerr=abs(b['tip_m'][1]/lin-1)
            passed=b['success'] and all(d['residual_Nm']<=CRITERIA['gradient_residual_Nm_max'] for d in ds) and tiperr<=CRITERIA['finest_tip_relative_max'] and roterr<=CRITERIA['finest_rotation_relative_max'] and (F!=1e-7 or linearerr<=CRITERIA['small_load_linear_relative_max'])
            rows.append(dict(body=body,L_m=L,force_N=F,reference=b,refinements=ds,finest_tip_relative_error=tiperr,finest_rotation_relative_error=roterr,continuous_vs_linear_relative=linearerr,status='PASS' if passed else 'FAIL'))
    passed=all(c['passed'] for c in checks) and all(r['status']=='PASS' for r in rows)
    dump(out/'summary.json',dict(status='REFERENCE_PASS' if passed else 'FAIL',scope='SEPARATE FREE-TIP FINITE EXTENSIBLE ROD REFERENCE ONLY',rows=rows,variational_checks=checks,criteria=CRITERIA,inputs=ref(out/'inputs.json'),whole_system_release=False,limitations=['No coupled contact, actual guide or deformed BRep','No friction, strength, dynamics or global assembly energy','No adoption of candidate RevAD; RevAA unchanged','Original linear coarse Green FAIL and coordinate reuse FAIL preserved']))
    print(json.dumps(dict(status='REFERENCE_PASS' if passed else 'FAIL',cases=[{k:r[k] for k in ('body','force_N','status','finest_tip_relative_error','continuous_vs_linear_relative')} for r in rows],checks=checks),indent=2))
    raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
