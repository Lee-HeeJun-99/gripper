"""Independent diagnosis of Native elastic tendon taut/slack transition.

Separately test the continuous physical reference and old-state tangent discrete
reference. Correct linearized algebra is NOT nonlinear or physical convergence.
"""
import argparse
import itertools
import json
import subprocess
from pathlib import Path

import numpy as np

from analyse import BASE, sha
from native_elastic_tendon import MASS, STIFFNESS, STRETCH, exact


def old_tangent_reference(h, count):
    z, v, acc = 0., 0., STIFFNESS*STRETCH/MASS
    result=[]
    for _ in range(count):
        f=STIFFNESS*max(STRETCH-z,0.)
        tangent=-STIFFNESS if z<STRETCH else 0.
        anew=(f+tangent*(h*v+h*h*acc/4))/(MASS-h*h*tangent/4)
        z, v = z+h*v+h*h*(acc+anew)/4, v+h*(acc+anew)/2
        acc=anew
        result.append((z,v,acc))
    return np.asarray(result)


def nonlinear_be_reference(h, count):
    z,v=0.,0.
    result=[]
    for _ in range(count):
        # Exact piecewise solution of BE, NOT a production force/ODE solver.
        free=z+h*v
        znew=free if free>=STRETCH else (MASS*free+h*h*STIFFNESS*STRETCH)/(MASS+h*h*STIFFNESS)
        vnew=(znew-z)/h
        result.append((znew,vnew,STIFFNESS*max(STRETCH-znew,0.)/MASS))
        z,v=znew,vnew
    return np.asarray(result)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--tag',required=True)
    p.add_argument('--case',default='b3_native_elastic_tendon693')
    a=p.parse_args()
    out=BASE/'results'/a.tag
    out.mkdir(exist_ok=False)
    source=BASE/'results'/a.case/'summary.json'
    data=json.loads(source.read_text())
    records=[]
    for r in data['records']:
        if not r['frames'] or r['sofa_errors'] or r['process']['exit_code']:
            raise ValueError('partial Native input')
        actual=np.asarray([[f['q'][1][2], f['v'][1][2]] for f in r['frames']])
        if r['mode']=='initial_slack':
            records.append(dict(mode=r['mode'],dt_s=r['dt_s'],strict_zero_motion=bool(np.max(abs(actual))==0.)))
            continue
        h=r['dt_s']
        nonlinear=data.get('ode')=='bdf1'
        discrete=(nonlinear_be_reference if nonlinear else old_tangent_reference)(h,len(actual))
        error=np.max(abs(actual-discrete[:,:2]),axis=0)
        crossing=next(i for i,f in enumerate(r['frames']) if f['q'][1][2]>=STRETCH)
        f=r['frames'][crossing]
        prev=0. if crossing==0 else r['frames'][crossing-1]['q'][1][2]
        records.append(dict(mode=r['mode'],dt_s=h,maximum_discrete_position_error_m=float(error[0]),maximum_discrete_velocity_error_m_s=float(error[1]),
                            discrete_reference='exact_nonlinear_BE' if nonlinear else 'old_state_tangent_Newmark',
                            strict_discrete_reference_pass=bool(max(error)<=1e-12),
                            first_sampled_slack_time_s=f['time_s'],continuous_analytic_release_s=data['analytic_release_s'],
                            first_sampled_slack_position_m=f['q'][1][2],previous_sampled_position_m=prev,
                            discrete_acceleration_at_slack_m_s2=float(discrete[crossing,2]),
                            physical_acceleration_at_slack_m_s2=0.,
                            scope='sampled release bracket,NOT continuous Native event time;negative extrapolated acceleration is not physical string compression force'))
    pairs=[]
    runs=[r for r in data['records'] if r['mode']=='taut_release']
    for x,y in itertools.combinations(runs,2):
        ratio=round(x['dt_s']/y['dt_s']);measurements=[]
        for i,fx in enumerate(x['frames']):
            fy=y['frames'][(i+1)*ratio-1]
            # Explicit moving-point quantities only:fixed anchor/absolute position
            # cannot dilute displacement/velocity relative errors.
            values=lambda f:dict(moving_point_displacement_m=f['q'][1][2],moving_point_velocity_m_s=f['v'][1][2],
                                  elastic_tension_N=f['inferred_elastic_tension_N'],reconstructed_energy_J=f['reconstructed_energy_J'])
            for key,u in values(fx).items():
                w=values(fy)[key];absolute=abs(u-w);denom=max(abs(u),abs(w))
                measurements.append(dict(time_s=fx['time_s'],observable=key,absolute=absolute,relative=absolute/denom if denom else 0.))
        pairs.append(dict(dt_s=[x['dt_s'],y['dt_s']],pass_time_gate=all(m['relative']<=.001 for m in measurements),worst=max(measurements,key=lambda m:m['relative']),measurements=measurements))
    result=dict(status='ELASTIC_DISCRETE_DIAGNOSIS_NOT_PHYSICAL_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),
                producer_sha256=sha(Path(__file__)),input_summary_sha256=sha(source),input_case=a.case,strict_gate=1e-12,time_gate=.001,
                records=records,pairs=pairs,scope='Native elastic physical model differs from force-controlled Cable. Correct discrete old-tangent algebra does not qualify slack-event consistency. All common times/all pairs,moving-point displacement,NO relative floor. No B3 modification.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({**{k:v for k,v in result.items() if k!='pairs'},'pair_worst':[p['worst'] for p in pairs]},indent=2))


if __name__=='__main__':
    main()
