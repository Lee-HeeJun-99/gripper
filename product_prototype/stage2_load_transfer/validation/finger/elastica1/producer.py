"""Independent finite-rotation projected elastica under terminal cable tension.
Quasi-static reduced research model, NOT SOFA, full 3D FE or material approval.
"""
import argparse, json, math, shutil
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.optimize._numdiff import approx_derivative
from finger_structure import ROOT,L,definition,sha

def cable(p,r=.01118):
    c=np.array([.044,.025]);d=p-c
    if np.linalg.norm(d)<=r:raise ValueError('terminal inside idler')
    b=-(math.atan2(-d[1],-d[0])-math.acos(r/np.linalg.norm(d)))
    q=c-r*np.array([math.cos(b),-math.sin(b)])
    cd=np.array([-.036,.005]);normal=np.array([-cd[1],cd[0]])/np.linalg.norm(cd)
    if normal[1]<0:normal=-normal
    phi=math.atan2(normal[1],normal[0]);end=math.atan2(-(q-c)[1],-(q-c)[0])
    # q-c is the radial vector; arc endpoint must be its angle.
    end=math.atan2((q-c)[1],(q-c)[0])
    while end<phi:end+=2*math.pi
    return np.linalg.norm(cd)+r*(end-phi)+np.linalg.norm(p-q)-.020,(p-q)/np.linalg.norm(p-q)
def model(n,locked):
    EI,kr,k,d,neutral=definition(.00030,.00020)
    if not locked:kr=0.
    h=L/n;H=np.zeros((n,n))
    for i in range(n):
        b=np.zeros(n);b[i]=1
        if i:b[i-1]=-1
        H+=EI((i+.5)*h)/h*np.outer(b,b)
    H[-1,-1]+=kr
    offset=np.array([.043-(.050+neutral),.003])
    def compute(q,tension):
        full=np.r_[0.,q];a=(full[:-1]+full[1:])/2
        step=h*np.column_stack((-np.sin(a),-np.cos(a)))
        end=np.array([.050+neutral,-.007])+step.sum(axis=0)
        t=q[-1];ct,st=np.cos(t),np.sin(t)
        p=end+np.array([[ct,st],[-st,ct]])@offset
        dp=np.zeros((2,n))
        for i in range(n):
            ds=h/2*np.array([-np.cos(a[i]),np.sin(a[i])])
            dp[:,i]+=ds
            if i:dp[:,i-1]+=ds
        dp[:,-1]+=np.array([-st*offset[0]+ct*offset[1],-ct*offset[0]-st*offset[1]])
        length,g=cable(p)
        energy=.5*q@H@q+tension*length
        grad=H@q+tension*dp.T@g
        return float(energy),grad,p,length,end
    return compute,H
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=ROOT/'validation/finger'/args.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py');shutil.copyfile(Path(__file__).with_name('finger_structure.py'),out/'finger_structure.py')
    allrows=[];gradtests=[]
    for locked in (False,True):
        for n in (8,16,32,64):
            fn,H=model(n,locked);q=np.zeros(n)
            # Validation point is a nonzero rotation/force, not only REST.
            test=np.linspace(.001,.2,n)
            numeric=approx_derivative(lambda v:np.array([fn(v,.5)[0]]),test,method='3-point').ravel()
            analytic=fn(test,.5)[1]
            err=np.linalg.norm(numeric-analytic)/np.linalg.norm(analytic)
            assert err<1e-6,err
            gradtests.append(dict(locked=locked,n=n,error=float(err)))
            for tension in (.05,.25,.5,1.,1.5):
                result=minimize(lambda v:fn(v,tension)[:2],q,jac=True,method='BFGS',options=dict(gtol=1e-11,maxiter=1000))
                q=result.x;u,g,p,length,end=fn(q,tension)
                hes=approx_derivative(lambda v:fn(v,tension)[1],q,method='3-point')
                mineig=float(np.linalg.eigvalsh((hes+hes.T)/2).min())
                residual=float(np.linalg.norm(g)/L)
                allrows.append(dict(locked=locked,n=n,tension_N=tension,tip_rotation_deg=float(np.degrees(q[-1])),
                    pivot_m=p.tolist(),end_m=end.tolist(),free_cable_length_m=float(length),
                    equilibrium_force_residual_N=residual,min_tangent_eigenvalue_Nm=mineig,
                    within_Stage1_0_60_deg=bool(0<=q[-1]<=math.pi/3),stable_local_minimum=mineig>0,
                    model_equilibrium_status='PASS' if residual<1e-6 and mineig>0 else 'FAIL',
                    optimizer_message=str(result.message),elastic_energy_J=float(.5*q@H@q),
                    angles_rad=q.tolist()))
    convergence=[]
    for locked in (False,True):
        for t in (.05,.25,.5,1.,1.5):
            rows=[x for x in allrows if x['locked']==locked and x['tension_N']==t]
            a,b=rows[-2:];err=float(np.linalg.norm(np.array(a['pivot_m'])-b['pivot_m'])/max(1e-12,np.linalg.norm(np.array(b['pivot_m'])-np.array([.043,-.092]))))
            convergence.append(dict(locked=locked,tension_N=t,pivot_displacement_relative_error=err,status='PASS' if err<.01 else 'FAIL'))
    result=dict(status='PASS' if all(x['model_equilibrium_status']=='PASS' for x in allrows) and all(x['status']=='PASS' for x in convergence) else 'FAIL',
        scope='CONDITIONAL PROJECTED QUASISTATIC ELASTICA; NOT 3D CAD DYNAMICS OR STRENGTH',
        case='revAA_heel_relief2',rows=allrows,gradient_tests=gradtests,convergence=convergence,
        source_SHA256=sha(Path(__file__)),beam_source_SHA256=sha(Path(__file__).with_name('finger_structure.py')),
        criteria_SHA256=sha(ROOT/'models/analytical/criteria.json'),
        exclusions=['actual clamp slip','local terminal stress','contact with other solids','axial centreline extension','out-of-plane rail taper mechanics','material certification','dynamic inertia'],
        command='python scripts/nonlinear_finger.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],fine_rows=[{k:v for k,v in r.items() if k!='angles_rad'} for r in allrows if r['n']==64],convergence=convergence),indent=2))
if __name__=='__main__':main()
