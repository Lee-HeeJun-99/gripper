"""Stroke-controlled quasi-static load curve, finite cable compliance scenarios.
Independent KKT vs penalty-energy solution and input-work balance.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import root,minimize
from nonlinear_finger import model
from finger_structure import ROOT,L,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    for name in ('stroke_load.py','nonlinear_finger.py','finger_structure.py'):
        shutil.copyfile(Path(__file__).with_name(name),out/name)
    allrows=[];checks=[]
    for n in (16,32,64):
        for stiffness in (1000.,10000.,float('inf')):
            fn,H=model(n,True);l0=fn(np.zeros(n),0.)[3];previous=np.zeros(n+1);rows=[]
            for stroke in np.linspace(0,.01691,41):
                def residual(v):
                    energy,g,p,length,end=fn(v[:-1],v[-1])
                    constraint=l0-length+v[-1]/stiffness-stroke
                    return np.r_[g/L,1000*constraint]
                answer=root(residual,previous,tol=1e-10);previous=answer.x
                q=answer.x[:-1];t=float(answer.x[-1]);u,g,p,length,end=fn(q,t)
                eq=float(np.linalg.norm(g)/L);sr=abs(l0-length+t/stiffness-stroke)
                elastic=.5*float(q@H@q);cable_energy=.5*t*t/stiffness
                rows.append(dict(n=n,assumed_wire_stiffness_N_m=stiffness if np.isfinite(stiffness) else 'inextensible_limit',
                    drum_stroke_m=float(stroke),tendon_tension_N=t,tip_rotation_deg=float(np.degrees(q[-1])),pivot_m=p.tolist(),
                    beam_energy_J=elastic,wire_energy_J=cable_energy,equilibrium_residual_N=eq,stroke_residual_m=sr,
                    within_Stage1_0_60_deg=bool(-1e-10<=q[-1]<=np.pi/3),
                    status='PASS' if eq<1e-6 and sr<1e-9 and t>=-1e-10 else 'FAIL'))
            work=float(np.trapezoid([x['tendon_tension_N'] for x in rows],[x['drum_stroke_m'] for x in rows])) if hasattr(np,'trapezoid') else float(np.trapz([x['tendon_tension_N'] for x in rows],[x['drum_stroke_m'] for x in rows]))
            energy=rows[-1]['beam_energy_J']+rows[-1]['wire_energy_J']
            mismatch=abs(work-energy)/energy
            independent=None
            if np.isfinite(stiffness):
                stroke=.01691
                def potential(q):
                    _,g,p,length,end=fn(q,0.)
                    ext=stroke-l0+length;t=stiffness*ext
                    elastic=.5*q@H@q
                    dL=fn(q,1.)[1]-g
                    return float(elastic+.5*stiffness*ext**2),g+t*dL
                alt=minimize(potential,previous[:-1]+.0001,jac=True,method='BFGS',options={'gtol':1e-11,'maxiter':1000})
                independent=float(np.linalg.norm(alt.x-previous[:-1])/max(np.linalg.norm(previous[:-1]),1e-12))
            checks.append(dict(n=n,wire_stiffness_N_m=rows[-1]['assumed_wire_stiffness_N_m'],input_work_J=work,stored_energy_J=energy,
                work_energy_relative_error=mismatch,independent_energy_solution_relative_error=independent,
                status='PASS' if mismatch<.01 and (independent is None or independent<.01) else 'FAIL'))
            allrows.extend(rows)
    convergence=[]
    for stiffness in (1000.,10000.,'inextensible_limit'):
        rows=[r for r in allrows if r['assumed_wire_stiffness_N_m']==stiffness and r['drum_stroke_m']==.01691]
        lo,hi=rows[-2:];error=float(np.linalg.norm(np.array(lo['pivot_m'])-hi['pivot_m'])/np.linalg.norm(np.array(hi['pivot_m'])-np.array([.043,-.092])))
        convergence.append(dict(wire_stiffness_N_m=stiffness,pivot_refinement_relative_error=error,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in allrows+checks+convergence) else 'FAIL',
        scope='REDUCED QUASISTATIC STROKE/COMPLIANCE SENSITIVITY, NOT CERTIFIED CLOSING OR GRASP DEMAND',
        rows=allrows,checks=checks,convergence=convergence,
        required_wire_stiffness_for_0_25mm_extension_N_m=max(r['tendon_tension_N'] for r in allrows)/.00025,
        source_SHA256={name:sha(Path(__file__).with_name(name)) for name in ('stroke_load.py','nonlinear_finger.py','finger_structure.py')},
        criteria_SHA256=sha(ROOT/'models/analytical/stroke_criteria.json'),
        command='python scripts/stroke_load.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],final_rows=[r for r in allrows if r['n']==64 and r['drum_stroke_m']==.01691],checks=checks,convergence=convergence),indent=2))
if __name__=='__main__':main()
