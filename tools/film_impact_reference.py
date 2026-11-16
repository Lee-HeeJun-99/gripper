"""Independent scalar hard-stop reference, NOT a 3D contact/friction certificate.

Demonstrates why an ideal impact atom and a finite sampled contact force must
be distinguished. It does NOT waive existing SOFA pointwise-force FAIL gates.
"""
import argparse
import csv
import json
import math
import subprocess
import sys
from curve_common import ROOT,sha,write_json

def solve(steps,duration=.2,mass=.1,load=.01,x0=.1,v0=-1.):
    h=duration/steps;x=x0;v=v0;rows=[];total=0.;maximum_residual=0.
    for i in range(steps):
        free_v=v-h*load/mass;free_x=x+h*free_v
        if free_x>=0:next_x,next_v,impulse=free_x,free_v,0.
        else:next_x,next_v=0.,-x/h;impulse=mass*(next_v-v)+h*load
        residual=mass*(next_v-v)+h*load-impulse
        maximum_residual=max(maximum_residual,abs(residual));total+=impulse
        if next_x<0 or impulse<0:raise RuntimeError('unilateral conditions')
        rows.append(dict(time=(i+1)*h,position=next_x,velocity=next_v,impulse=impulse,step_mean_force=impulse/h,total_impulse=total))
        x,v=next_x,next_v
    return rows,maximum_residual

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    m,f,x0,v0,T=.1,.01,.1,-1.,.2
    tau=2*x0/(math.sqrt(v0*v0+2*f*x0/m)-v0)
    impact_speed=v0-f*tau/m;atom=-m*impact_speed;exact_impulse=atom+f*(T-tau)
    data={};cases={}
    for n in (32,64,128,256,512):
        rows,residual=solve(n);data[n]=rows
        with (out/f'steps_{n}.csv').open('x') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        cases[n]=dict(dt=T/n,maximum_step_momentum_residual=residual,peak_step_mean_force=max(row['step_mean_force'] for row in rows),endpoint_impulse_error=abs(rows[-1]['total_impulse']-exact_impulse),first_load_time=next(row['time'] for row in rows if row['impulse']>0))
    pairs={}
    for n in (32,64,128,256):
        old=data[n];fine=data[2*n]
        error=max(abs(row['step_mean_force']-fine[2*i+1]['step_mean_force']) for i,row in enumerate(old));scale=max(row['step_mean_force'] for row in fine)
        pairs[f'{n}:{2*n}']=dict(absolute_force_difference=error,relative_force_difference=error/scale,status='PASS' if error/scale<=.001 else 'FAIL')
    verified=max(case['endpoint_impulse_error'] for case in cases.values())<1e-12 and max(case['maximum_step_momentum_residual'] for case in cases.values())<1e-13
    write_json(out/'summary.json',dict(status='PASS' if verified else 'FAIL',scope='independent scalar diagnostic ONLY;does not certify or excuse SOFA time failures',
        parameters=dict(mass=m,downward_force=f,initial_gap=x0,initial_speed=v0,duration=T),
        exact=dict(impact_time=tau,incoming_velocity=impact_speed,impact_impulse_atom=atom,postimpact_continuous_reaction=f,endpoint_contact_impulse=exact_impulse,pointwise_force_at_ideal_impact=None),
        cases=cases,pointwise_force_pairs=pairs,existing_sofa_time_gate='UNCHANGED:FAIL',
        interpretation='ideal hard-stop force is a measure at impact;finite incoming speed/impulse alone do not prove this dominates coupled SOFA error,especially precontact dynamics',
        script_sha256=sha(__file__),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),python_version=sys.version))
    print(json.dumps(dict(reference_verified=verified,impact_time=tau,peak_forces={n:case['peak_step_mean_force'] for n,case in cases.items()},force_pairs=pairs)))

if __name__=='__main__':main()
