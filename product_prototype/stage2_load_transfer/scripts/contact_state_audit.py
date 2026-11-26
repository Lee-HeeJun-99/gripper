"""Independent saved primal/dual verification using alternate quadrature and
Bernstein convex-hull bounds, plus deliberately corrupted in-memory controls.
"""
import argparse,copy,json,math
from pathlib import Path
import numpy as np
from scipy.linalg import block_diag
from finger_structure import ROOT,E_PET,E_RAIL,width,sha
LR=.088;LP=.0874
def basis(n,L,s,derivative=False):
    h=L/n;j=min(int(s/h),n-1);t=(s-j*h)/h;v=np.zeros(2*(n+1))
    values=[(-6*t+6*t*t)/h,1-4*t+3*t*t,(6*t-6*t*t)/h,-2*t+3*t*t] if derivative else [1-3*t*t+2*t**3,h*(t-2*t*t+t**3),3*t*t-2*t**3,h*(-t*t+t**3)]
    v[2*j:2*j+4]=values;return v
def stiffness(n,L,EI):
    h=L/n;K=np.zeros((2*(n+1),2*(n+1)))
    # Two-point integration exactly integrates cubic EI(s)*B''B''.
    for j in range(n):
        ke=np.zeros((4,4))
        for t in (.5-.5/math.sqrt(3),.5+.5/math.sqrt(3)):
            B=np.array([12*t-6,h*(6*t-4),6-12*t,h*(6*t-2)])/h**2
            ke+=h*.5*EI((j+t)*h)*np.outer(B,B)
        ids=np.arange(2*j,2*j+4);K[np.ix_(ids,ids)]+=ke
    return K
def constraint(n,kind,s,der=False):
    r=basis(n,LR,s,der);p=basis(n,LP,s,der)
    if kind=='interface':return np.r_[r,-p],0.
    line=np.zeros(len(r))
    if der:line[-1]=1
    else:line[-2]=1;line[-1]=s-LR
    a=np.r_[-line,p]
    return (a,0. if der else -.0001) if kind=='front' else (-a,0. if der else -.0002)
def verify(row):
    if 'constraint_duals_N' not in row:return dict(valid=False,reason='missing stored duals')
    n=row['n'];m=2*(n+1);u=np.r_[row['rail_q'],row['PET_q']];F=row['force_N']
    K=block_diag(stiffness(n,LR,lambda s:2*E_RAIL*.003*.0002**3/12),stiffness(n,LP,lambda s:E_PET*width(s)*.0003**3/12))
    f=np.zeros(2*m);f[m-2]=F
    A=[];b=[]
    for kind,s in row['constraint_locations']:
        a,lo=constraint(n,kind,s);A.append(a);b.append(lo)
    A=np.array(A);b=np.array(b);dual=np.array(row['constraint_duals_N']);res=K@u-f+A.T@dual
    free=np.array([j for j in range(2*m) if j not in (0,1,m,m+1)]);scaled=res[free].copy();scaled[free%2==1]/=LR
    residual=float(np.linalg.norm(scaled));force=abs(res[0]+res[m]+F);moment=abs(res[1]+res[m+1]+F*LR)
    bounds=[]
    for kind in ['interface']+(['front','back'] if row['guide'] else []):
        low=0. if kind=='interface' else .083
        knots=sorted(set([low,LP]+[s for s in np.r_[np.linspace(0,LR,n+1),np.linspace(0,LP,n+1)] if low<s<LP]))
        for a,bound in zip(knots,knots[1:]):
            v0,l0=constraint(n,kind,a);v1,l1=constraint(n,kind,bound)
            d0,_=constraint(n,kind,a,True);d1,_=constraint(n,kind,bound,True)
            g0=v0@u-l0;g1=v1@u-l1
            bounds.append(float(min(g0,g0+(bound-a)*(d0@u)/3,g1-(bound-a)*(d1@u)/3,g1)))
    complement=float(np.sum(abs(dual*(A@u-np.array([constraint(n,k,s)[1] for k,s in row['constraint_locations']]))))/1e-6)
    return dict(valid=bool(np.linalg.norm(u[[0,1,m,m+1]])<1e-15 and residual<1e-8 and force<1e-8 and moment<1e-10 and min(bounds)>=-1e-9 and dual.max()<=1e-12 and complement<1e-7),
        KKT_force_N=residual,force_balance_N=float(force),moment_balance_Nm=float(moment),minimum_Bernstein_gap_lower_bound_m=min(bounds),complementarity_relative=complement)
def main():
    p=argparse.ArgumentParser();p.add_argument('--input-tag',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    path=ROOT/'validation/finger'/a.input_tag/'summary.json';data=json.loads(path.read_text())
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False)
    positive=[verify(r) for r in data['rows']];r=copy.deepcopy(data['rows'][0]);r['PET_q'][-2]+=.001
    negative_gap=not verify(r)['valid'];r=copy.deepcopy(data['rows'][0]);r['constraint_duals_N']=[0.]*len(r['constraint_duals_N'])
    negative_force=not verify(r)['valid'];r=copy.deepcopy(data['rows'][0]);r['rail_q'][0]=1e-6
    negative_root=not verify(r)['valid']
    result=dict(status='PASS' if all(x['valid'] for x in positive) and negative_gap and negative_force and negative_root else 'FAIL',
        scope='SAVED LOCAL COUPON PRIMAL/DUAL CONSISTENCY ONLY',positive=positive,
        controls=dict(perturbed_skin_rejected=negative_gap,zero_contact_reaction_rejected=negative_force,moving_root_rejected=negative_root),
        source_SHA256=sha(Path(__file__)),input_SHA256=sha(path),hardware_executed=False,
        command='python scripts/contact_state_audit.py --input-tag '+a.input_tag+' --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
