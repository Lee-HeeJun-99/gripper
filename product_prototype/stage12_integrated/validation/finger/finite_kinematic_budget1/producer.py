"""Actual distributed-state axial-kinematic budget; no new equilibrium or CAD certificate."""
import hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from baseline_registry import ROOT,dump,ref
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from finger_structure import E_RAIL,E_PET,width
SOURCE=ROOT/'validation/finger/flexible_distributed2/summary.json'
CRITERIA={'quadrature_relative_max':1e-9,'quadrature_absolute_max':1e-18,
          'existing_contact_gap_budget_m':1e-9}
def quantities(q,L,EA,EI,adaptive=False):
    n=len(q)//2-1;h=L/n;total=np.zeros(6);gx,gw=np.polynomial.legendre.leggauss(16)
    for j in range(n):
        y0,d0,y1,d1=q[2*j:2*j+4]
        c=np.array([y0,h*d0,3*(y1-y0)-h*(2*d0+d1),2*(y0-y1)+h*(d0+d1)])
        def values(t):
            s=(j+t)*h
            v=(c[1]+2*c[2]*t+3*c[3]*t*t)/h
            a=(2*c[2]+6*c[3]*t)/h**2
            stretch=np.sqrt(1+v*v)
            # Stable sqrt(1+v²)-1 and 1-1/sqrt(1+v²).
            e=v*v/(stretch+1);short=e/stretch
            return np.array([e,short,v*(1/stretch-1),.5*EA(s)*e*e,
                             .5*EI(s)*a*a,.5*EI(s)*a*a/stretch**5])*h
        if adaptive:
            total+=np.array([quad(lambda t:values(t)[k],0,1,epsabs=1e-20,epsrel=1e-11)[0] for k in range(6)])
        else:
            total+=sum(w*values((x+1)/2)/2 for x,w in zip(gx,gw))
    return total

def main():
    out=ROOT/'validation/finger'/sys.argv[1]
    if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
    out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    deps=[SOURCE,Path(__file__),ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',ROOT/'cad/exports/revAD_funnel1/summary.json']
    dump(out/'inputs.json',{'criteria':CRITERIA,'inputs':[ref(p) for p in deps],
        'hypothesis':'Keeping material x fixed introduces axial stretch; inextensible tangent integration instead moves x and y, invalidating reuse of projected contact coordinates.',
        'definitions':['graph x=s,y=y_h(s); engineering axial energy integral EA*(sqrt(1+y_prime^2)-1)^2/2 ds',
        'inextensible lift integrates (cos(atan(y_prime)),sin(atan(y_prime))) in material s; NOT a solved state',
        'graph geometric bending comparator integral EI*y_second^2/(1+y_prime^2)^(5/2)/2 dx; NOT total rod energy'],
        'material_basis':'unchanged conditional supplier typical moduli and projected sections; no actual lot certification'})
    rows=[];verification=[]
    for r in json.loads(SOURCE.read_text())['rows']:
        if r['n'] not in (16,32):continue
        for body,L,EA,EI in [('rail',.088,lambda s:2*E_RAIL*.003*.0002,lambda s:2*E_RAIL*.003*.0002**3/12),('PET',.0862,lambda s:E_PET*width(s)*.0003,lambda s:E_PET*width(s)*.0003**3/12)]:
            if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
            q=r[body+'_q'];a=quantities(q,L,EA,EI);b=quantities(q,L,EA,EI,True)
            checks=np.abs(a-b)<=CRITERIA['quadrature_absolute_max']+CRITERIA['quadrature_relative_max']*np.abs(b)
            verification.append({'n':r['n'],'force_N':r['force_N'],'body':body,'max_absolute_difference':float(max(abs(a-b))),'checks':checks.tolist()})
            rows.append(dict(n=r['n'],force_N=r['force_N'],body=body,graph_extension_m=float(a[0]),inextensible_tip_x_shortening_m=float(a[1]),inextensible_tip_y_change_m=float(a[2]),fixed_x_axial_energy_J=float(a[3]),linear_bending_energy_J=float(a[4]),graph_geometric_bending_energy_J=float(a[5]),axial_to_linear_bending_ratio=float(a[3]/a[4]) if a[4]>0 else None,projected_coordinates_reusable_within_existing_gap_budget=bool(max(abs(a[1]),abs(a[2]))<=CRITERIA['existing_contact_gap_budget_m'])))
    # Independent exact constant-slope lift validates signs, scale and integration.
    slope=.2;L=.0862;q=[0,slope,L*slope,slope];a=quantities(q,L,lambda s:2.,lambda s:3.)
    e=np.sqrt(1+slope*slope)-1
    expected=np.array([L*e,L*(1-1/np.sqrt(1+slope*slope)),L*slope*(1/np.sqrt(1+slope*slope)-1),L*e*e,0,0])
    control=bool(np.allclose(a,expected,atol=1e-16,rtol=1e-12))
    verified=control and all(all(v['checks']) for v in verification)
    dump(out/'verification.json',dict(status='PASS' if verified else 'FAIL',independent_adaptive_quadrature=verification,analytic_constant_slope_control=control))
    reuse=all(r['projected_coordinates_reusable_within_existing_gap_budget'] for r in rows)
    result=dict(status='ANALYSIS_COMPLETE' if verified else 'VERIFICATION_FAIL',scope='ACTUAL SAVED DISTRIBUTED STATES KINEMATIC CONTRAST ONLY',rows=rows,criteria=CRITERIA,projected_to_finite_state_reuse='PASS' if reuse else 'FAIL',verification=ref(out/'verification.json'),inputs=ref(out/'inputs.json'),whole_system_release=False,decision='Use separate axial and rotational DOFs with contact re-evaluation; neither lift is a finite equilibrium.',limitations=['No finite-contact solve or deformed BRep','No axial boundary condition selected by this diagnostic','No physical membrane-energy claim for the free-sliding assembly','No strength, friction or global energy qualification; old coarse Green FAIL preserved'])
    dump(out/'summary.json',result)
    print(json.dumps(dict(status=result['status'],projected_to_finite_state_reuse=result['projected_to_finite_state_reuse'],rows=rows),indent=2))
    raise SystemExit(0 if verified else 2)
if __name__=='__main__':main()
