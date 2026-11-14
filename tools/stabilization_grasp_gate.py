"""Independent bounded-hold gate; translation alone is never a grasp success."""
import csv
import json
import numpy as np
from stabilization_common import OUT,write_json,sha
from trial_validation import read_states

def evaluate(directory):
    r=json.loads((directory/'metrics.json').read_text());c=r['config']
    if (directory/'analysis_failure.json').exists():return dict(status='FAIL',reason='superseding invalid-physics audit',grasp_certified=False)
    if r['status']=='FAIL':return dict(status='FAIL',reason=r.get('failure_reason'),grasp_certified=False)
    if c['duration']<8:return dict(status='NOT RUN',reason='load phase not reached',grasp_certified=False)
    for file,h in r['artifacts'].items():
        if sha(directory/file)!=h:raise ValueError('damaged grasp artifact')
    end=c.get('hold_until',8);raw=read_states(directory/'state.txt');obj=c['object_index'];tail=[p for p in raw if end-.1-1e-8<=p['time']<end-1e-8]
    if not tail:raise ValueError('missing hold tail')
    v=np.array([p['V'] for p in tail]).reshape(len(tail),-1,6)[:,obj,:];res=np.array([p['R'] for p in tail]).reshape(len(tail),-1,6)[:,obj,:]
    with (directory/'contact.csv').open() as stream:contacts=[row for row in csv.DictReader(stream) if end-.1-1e-8<=float(row['time'])<end-1e-8]
    before=min(raw,key=lambda frame:abs(frame['time']-6));origin=np.array(before['X']).reshape(-1,7)[obj,:3]
    # Floating point times near an event must not select different physical
    # endpoints for half-dt versus base sampling. Raw historical metrics stay intact.
    displacement=max(float(np.linalg.norm(np.array(frame['X']).reshape(-1,7)[obj,:3]-origin)) for frame in raw if 6-1e-8<=frame['time']<=end+1e-8)
    scale=abs(c['load']) or 1e-6;force=float(abs(res[:,:3]).max()/scale);moment=float(abs(res[:,3:]).max()/(scale*5))
    checks=dict(translation=displacement<.05,rotation=r['peak_object_angle']<.01,velocity=float(abs(v[:,:3]).max())<1e-5,angular_velocity=float(abs(v[:,3:]).max())<1e-5,
                force_balance=force<1e-3,moment_balance=moment<1e-3,contact_sustained=bool(contacts) and min(float(row['contacts']) for row in contacts)>=2)
    return dict(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',bounded_hold_checks=checks,bounded_hold_pass=all(checks.values()),object_force_residual=force,object_moment_residual=moment,
                max_hold_velocity=float(abs(v[:,:3]).max()),max_hold_angular_velocity=float(abs(v[:,3:]).max()),displacement_mm=displacement,original_sample_window_displacement_mm=r['hold_displacement_mm'],grasp_certified=False,
                scope=f'bounded {end-6:g}s pose/velocity/force benchmark, not exact static friction or a full grasp certificate; convergence evaluated separately')

def main():
    rows={}
    for p in sorted((OUT/'grasp').glob('*/metrics.json')):
        try:rows[p.parent.name]=evaluate(p.parent)
        except (ValueError,OSError,KeyError) as e:rows[p.parent.name]=dict(status='FAIL',reason=str(e),grasp_certified=False)
    checks={};base=rows.get('sphere_x_valid')
    if base and 'displacement_mm' in base:
        for name,tol in [('sphere_repeat',1e-10),('sphere_halfdt',.001),('sphere_mesh',.01),('sphere_quadrature',.01)]:
            if name in rows and 'displacement_mm' in rows[name]:checks[name]=abs(rows[name]['displacement_mm']-base['displacement_mm'])<1e-10+tol*abs(base['displacement_mm'])
    write_json(OUT/'grasp/gate.json',dict(experiments=rows,convergence_checks=checks,full_grasp_certified=False,grasp_optimization='BLOCKED',reason='exact static stick, surface convergence and validated unconstrained 3D finger model not established'))
    print({name:r['status'] for name,r in rows.items()},checks)

if __name__=='__main__':main()
