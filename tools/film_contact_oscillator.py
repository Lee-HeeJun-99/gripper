"""Independent unilateral oscillator: separates event timing and stiff modes.

This is NOT reduced-order certification of the film. Oracle event alignment
uses continuous-reference events to test a hypothesis, not production CCD.
"""
import argparse,json,subprocess
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from curve_common import ROOT,sha,write_json

def reference(wc,tolerance):
    w0=2.;plane=.1;entry=1.408373
    # Exact no-contact ramp response fixes first entry independently of wc.
    matrix=np.array([[0,1,0,0],[-w0*w0,-2,1,0],[0,0,0,1],[0,0,0,0]],float)
    unit=expm(matrix*entry)@np.array([0,0,0,1.])
    ramp=plane/unit[0]
    def rhs(t,y):return [y[1],ramp*t-2*y[1]-w0*w0*y[0]-wc*wc*max(y[0]-plane,0.)]
    def event(t,y):return y[0]-plane
    sol=solve_ivp(rhs,(0,2),[0.,0.],rtol=tolerance,atol=tolerance*1e-3,
                  method='DOP853',max_step=.0005,dense_output=True,events=event)
    if not sol.success:raise RuntimeError(sol.message)
    return sol,ramp

def bdf(times,wc,ramp):
    x=v=xprev=vprev=0.;out=[[0.,0.,0.]];last_h=None
    for t,h in zip(times[1:],np.diff(times)):
        if last_h is None:a0,a1,a2=0.,-1.,1.
        else:
            ratio=h/last_h;a0=ratio*ratio/(1+ratio);a1=-(1+ratio);a2=(1+2*ratio)/(1+ratio)
        known=a1*x+a0*xprev
        coefficient=a2*a2/h**2+2*a2/h+4
        right=ramp*t-(a2/h**2+2/h)*known-(a1*v+a0*vprev)/h
        trial=right/coefficient
        if trial>.1:trial=(right+wc*wc*.1)/(coefficient+wc*wc)
        next_v=(a2*trial+known)/h
        xprev,vprev,x,v=x,v,trial,next_v;out.append([t,x,v]);last_h=h
    return np.array(out)

def metrics(rows,ref,wc):
    times=rows[:,0];exact=ref.sol(times);force=wc*wc*np.maximum(rows[:,1]-.1,0);ef=wc*wc*np.maximum(exact[0]-.1,0)
    result={}
    for key,value,target in (('position',rows[:,1],exact[0]),('velocity',rows[:,2],exact[1]),('contact_acceleration',force,ef)):
        absolute=float(max(abs(value-target)));scale=float(max(abs(target)))
        relative=absolute/scale if scale else (0. if absolute==0 else None)
        result[key]=dict(max_absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    report={}
    for wc in (0.,44.37059837324712,177.48239349298848):
        ref,ramp=reference(wc,1e-11);tight,_=reference(wc,2e-13)
        grid=np.linspace(0,2,4001)
        check=float(np.max(abs(ref.sol(grid)-tight.sol(grid))))
        cases={}
        for count in (200,400,800):
            uniform=np.linspace(0,2,count+1)
            for aligned in (False,True):
                events=tight.t_events[0]
                times=np.sort(np.concatenate([uniform,events])) if aligned and wc else uniform
                if min(np.diff(times))<=0:raise RuntimeError('degenerate event/grid intersection')
                rows=bdf(times,wc,ramp)
                np.savetxt(out/f'w{wc:g}_n{count}_aligned{int(aligned)}.csv',rows,delimiter=',',header='time,position,velocity',comments='')
                cases[f'{count}:{aligned}']=metrics(rows,tight,wc)
        report[str(wc)]=dict(w0=2.,damping=2.,ramp_acceleration_coefficient=ramp,
                             reference_max_state_difference=check,events=tight.t_events[0].tolist(),cases=cases)
    result=dict(source='independent mathematical oscillator; not actual SOFA or fitted film dynamics',
                commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__),
                physical_gate=.001,models=report,full_film_gate='UNCHANGED FAIL',
                limitation='Exact reference event times are an oracle diagnostic, not an implemented event detector. Different wc values are different physical controls.')
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
