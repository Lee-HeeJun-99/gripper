"""Actual finite rod boundary contrast; not an identification of assembly guides."""
import sys, shutil
from pathlib import Path
import numpy as np
from scipy.optimize import root
from scipy.integrate import solve_bvp
from extensible_rod_reference import section, continuous
from baseline_registry import ROOT, ref, dump, sha, REPO

def solve(body,L,F,n):
    h=L/n;s=(np.arange(n)+.5)*h;EA,EI=section(body,s)
    def fields(z):
        th=np.r_[0,z[:-1]];a=(th[:-1]+th[1:])/2;N=z[-1]
        p=N*np.cos(a)+F*np.sin(a);dp=-N*np.sin(a)+F*np.cos(a)
        e=p/EA;g=np.zeros(n+1);b=EI*np.diff(th)/h;c=-h*dp*(1+e)/2
        g[:-1]+=-b+c;g[1:]+=b+c
        r=np.cumsum(h*(1+e)[:,None]*np.column_stack((np.cos(a),np.sin(a))),axis=0)
        return th,e,g[1:],r
    def fun(z):
        th,e,g,r=fields(z)
        return np.r_[g/(abs(F)*L), (r[-1,0]-L)/L]
    sol=root(fun,np.zeros(n+1),tol=1e-9)
    th,e,g,r=fields(sol.x)
    U=float(np.sum(h*(EA*e**2+EI*(np.diff(th)/h)**2)/2))
    return dict(n=n,success=bool(sol.success),message=str(sol.message),axial_reaction_N=float(sol.x[-1]),tip_m=r[-1].tolist(),theta_rad=th.tolist(),strain=e.tolist(),r_m=r.tolist(),stored_energy_J=U,residual_Nm=float(max(abs(g))),axial_gap_m=float(r[-1,0]-L))

def bvp(body,L,F):
    def ode(s,z,p):
        EA,EI=section(body,s);t=z[2];e=(p[0]*np.cos(t)+F*np.sin(t))/EA
        return np.array([(1+e)*np.cos(t),(1+e)*np.sin(t),z[3]/EI,(1+e)*(p[0]*np.sin(t)-F*np.cos(t))])
    def bc(a,b,p):return np.array([a[0],a[1],a[2],b[3],b[0]-L])
    s=np.linspace(0,L,101);z=np.zeros((4,len(s)));z[0]=s
    v=solve_bvp(ode,bc,s,z,p=[0.],tol=1e-10,max_nodes=10000)
    return dict(success=bool(v.success),message=v.message,tip_m=v.y[:2,-1].tolist(),axial_reaction_N=float(v.p[0]),max_rms_residual=float(max(v.rms_residuals)))

def main():
    if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP')
    out=ROOT/'validation/finger'/sys.argv[1];out.mkdir(exist_ok=False,parents=True)
    shutil.copyfile(__file__,out/'producer.py')
    criteria=dict(tip_relative_max=.001,reaction_relative_max=.001,residual_Nm_max=1e-10,axial_gap_m_max=1e-10)
    inputs=[ref(Path(__file__)),ref(ROOT/'scripts/extensible_rod_reference.py'),ref(ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py'),ref(ROOT/'validation/finger/extensible_reference1/summary.json')]
    dump(out/'inputs.json',dict(inputs=inputs,criteria=criteria,contract='Root fixed; zero tip moment; spatial dead Fy; tip x=L enforced with unknown axial reaction. Free transverse tip. Counterfactual boundary contrast, NOT actual guide.',material='Unchanged conditional typical moduli and projected sections',predeclared='Compare 64-element midpoint with independent continuous BVP; retain all failures. No contact/system PASS.'))
    rows=[]
    for body,L in [('rail',.088),('PET',.0862)]:
        for F in (.001,.02):
            if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP')
            b=bvp(body,L,F);free=continuous(body,L,F);ds=[solve(body,L,F,n) for n in (16,32,64)]
            tip=abs(ds[-1]['tip_m'][1]/b['tip_m'][1]-1);reaction=abs(ds[-1]['axial_reaction_N']/b['axial_reaction_N']-1)
            ok=b['success'] and free['success'] and all(d['success'] and d['residual_Nm']<=criteria['residual_Nm_max'] and abs(d['axial_gap_m'])<=criteria['axial_gap_m_max'] for d in ds) and tip<=criteria['tip_relative_max'] and reaction<=criteria['reaction_relative_max']
            rows.append(dict(body=body,L_m=L,force_N=F,reference=b,free_reference=free,refinements=ds,tip_relative_error=tip,reaction_relative_error=reaction,constrained_vs_free_tip_relative=b['tip_m'][1]/free['tip_m'][1]-1,status='PASS' if ok else 'FAIL'))
    hashes=all(sha(REPO/i['path'])==i['SHA256'] for i in inputs)
    passed=hashes and all(r['status']=='PASS' for r in rows)
    dump(out/'summary.json',dict(status='BOUNDARY_REFERENCE_PASS' if passed else 'FAIL',scope='FINITE ROD AXIAL BOUNDARY CONTRAST ONLY',rows=rows,inputs=ref(out/'inputs.json'),input_hashes_verified=hashes,criteria=criteria,whole_system_release=False,limitations=['No actual guide boundary identification or contact','No actual deformed BRep, strength, friction or global assembly energy','RevAA remains adopted; old failures unchanged']))
    print([(r['body'],r['force_N'],r['status'],r['constrained_vs_free_tip_relative']) for r in rows]);raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
