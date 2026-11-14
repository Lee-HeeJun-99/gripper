"""Independent bounded-hold gate; translation alone is never a grasp success."""
import csv
import json
import numpy as np
import xml.etree.ElementTree as ET
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
    velocities=np.array([p['V'] for p in tail]).reshape(len(tail),-1,6);residuals=np.array([p['R'] for p in tail]).reshape(len(tail),-1,6);v=velocities[:,obj,:];res=residuals[:,obj,:]
    roots={0,c['nodes'],2*c['nodes'],3*c['nodes']};free=[i for i in range(obj) if i not in roots]
    scene=ET.parse(directory/'scene.scn').getroot();offset=abs(float(scene.find('.//RoutedCable').get('offsetZ')));radius=float(scene.find('.//DistributedContact').get('radius'))
    finger_force_scale=c['tension_per_layer']*offset/c['length'];finger_torque_scale=c['tension_per_layer']*offset
    finger_force=float(abs(residuals[:,free][:,:,[0,2]]).max()/finger_force_scale);finger_moment=float(abs(residuals[:,free,4]).max()/finger_torque_scale)
    with (directory/'contact.csv').open() as stream:contacts=[row for row in csv.DictReader(stream) if end-.1-1e-8<=float(row['time'])<end-1e-8]
    before=min(raw,key=lambda frame:abs(frame['time']-6));origin=np.array(before['X']).reshape(-1,7)[obj,:3]
    # Floating point times near an event must not select different physical
    # endpoints for half-dt versus base sampling. Raw historical metrics stay intact.
    displacement=max(float(np.linalg.norm(np.array(frame['X']).reshape(-1,7)[obj,:3]-origin)) for frame in raw if 6-1e-8<=frame['time']<=end+1e-8)
    scale=abs(c['load']) or 1e-6;force=float(abs(res[:,:3]).max()/scale);moment=float(abs(res[:,3:]).max()/(scale*radius))
    checks=dict(translation=displacement<c['hold_limit_mm'],rotation=r['peak_object_angle']<.01,velocity=float(abs(v[:,:3]).max())<1e-5,angular_velocity=float(abs(v[:,3:]).max())<1e-5,
                force_balance=force<1e-3,moment_balance=moment<1e-3,contact_sustained=bool(contacts) and min(float(row['contacts']) for row in contacts)>=2,
                finger_force_balance=finger_force<1e-3,finger_moment_balance=finger_moment<1e-3,
                finger_velocity=float(abs(velocities[:,free][:,:,[0,2]]).max())<1e-5,finger_angular_velocity=float(abs(velocities[:,free,4]).max())<1e-5)
    return dict(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',bounded_hold_checks=checks,bounded_hold_pass=all(checks.values()),object_force_residual=force,object_moment_residual=moment,
                max_hold_velocity=float(abs(v[:,:3]).max()),max_hold_angular_velocity=float(abs(v[:,3:]).max()),displacement_mm=displacement,original_sample_window_displacement_mm=r['hold_displacement_mm'],grasp_certified=False,
                finger_force_residual=finger_force,finger_moment_residual=finger_moment,finger_projected_free_dofs=[0,2,4],fixed_roots=sorted(roots),
                normalization=dict(object_force=scale,object_moment=scale*radius,finger_force=finger_force_scale,finger_moment=finger_torque_scale),
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
    for label,a,b in [('fine_quadrature','sphere_mesh21_q16','sphere_mesh21_q32_holdonly'),('fine_beam_mesh','sphere_mesh21_q32_holdonly','sphere_mesh41_q16_holdonly'),
                      ('fast_full_vs_holdonly','sphere_mesh21_q32_holdonly','sphere_fast_mesh21_full'),('fast_fine_beam_mesh','sphere_fast_mesh21_full','sphere_fast_mesh41_holdonly')]:
        if a in rows and b in rows and 'displacement_mm' in rows[a] and 'displacement_mm' in rows[b]:checks[label]=abs(rows[b]['displacement_mm']-rows[a]['displacement_mm'])<1e-10+.01*abs(rows[a]['displacement_mm'])
    write_json(OUT/'grasp/gate.json',dict(experiments=rows,convergence_checks=checks,full_grasp_certified=False,grasp_optimization='BLOCKED',reason='exact static stick, surface convergence and validated unconstrained 3D finger model not established'))
    print({name:r['status'] for name,r in rows.items()},checks)

if __name__=='__main__':main()
