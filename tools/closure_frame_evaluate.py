"""Independent three-finger gates; fixed-reference rotations, no global certificate."""
import json
import numpy as np
from closure_frame_common import OUT,sha,write_json
from trial_validation import read_states

def relative_angles(q0,q):
    v0,w0=q0[...,:3],q0[...,3:4];v,w=q[...,:3],q[...,3:4]
    vec=w0*v-w*v0-np.cross(v0,v)
    scalar=w0*w+np.sum(v0*v,axis=-1,keepdims=True)
    return 2*np.arctan2(np.linalg.norm(vec,axis=-1),abs(scalar[...,0]))

def trial(directory):
    r=json.loads((directory/'metrics.json').read_text())
    for name,digest in r.get('artifacts',{}).items():
        if sha(directory/name)!=digest:raise ValueError('corrupt '+name)
    result={k:r.get(k) for k in ('status','execution_completed','bounded_hold_pass','hold_displacement_mm','max_object_angle','object_force_residual','object_moment_residual','object_speed','object_angular_speed','finger_force_residual','finger_moment_residual','failure_reason')}
    result.update(config=r['config'],metrics_sha256=sha(directory/'metrics.json'),grasp_certified=False)
    if not r.get('execution_completed'):return result
    raw=read_states(directory/'state.txt');c=r['config'];n=c['nodes'];obj=c['object_index'];x0=np.array(raw[0]['X']).reshape(-1,7);x=np.array(raw[-1]['X']).reshape(-1,7);v=np.array(raw[-1]['V']).reshape(-1,6);free=[i for i in range(obj) if i%n]
    rest=float(np.linalg.norm(x[free,:3]-x0[free,:3],axis=1).max());angle=float(relative_angles(x0[free,3:],x[free,3:]).max());speed=float(abs(v[free,:3]).max());omega=float(abs(v[free,3:]).max())
    tail=[s for s in raw if c['hold_until']-.1-1e-8<=s['time']<c['hold_until']-1e-8]
    positions=np.array([s['X'][7*obj:7*obj+3] for s in tail]);drift=float(np.linalg.norm(positions-positions[0],axis=1).max());drift_ratio=drift/r['hold_displacement_mm'] if r['hold_displacement_mm'] else float('inf')
    before=min(raw,key=lambda s:abs(s['time']-6.));q0=np.array(before['X']).reshape(-1,7)[obj,3:];qt=np.array([s['X'][7*obj+3:7*obj+7] for s in tail]);increment=float(relative_angles(np.broadcast_to(q0,qt.shape),qt).max())
    result.update(hold_rotation_increment_rad=increment,recovery=dict(translation_mm=rest,angle_rad=angle,speed_mm_s=speed,omega_rad_s=omega,contacts=r['release_contacts'],time=raw[-1]['time']),recovery_pass=bool(c['duration']>=24 and rest<1e-4 and angle<1e-5 and speed<1e-5 and omega<1e-5 and r['release_contacts']==0),hold_drift_ratio=drift_ratio,hold_drift_pass=drift_ratio<1e-4)
    return result

def main():
    trials={}
    for p in (OUT/'trials').glob('*/metrics.json'):
        try:trials[p.parent.name]=trial(p.parent)
        except (ValueError,OSError,KeyError,IndexError) as e:trials[p.parent.name]=dict(status='FAIL',failure_reason=str(e),grasp_certified=False)
    comparisons={}
    def compare(label,a,b,tol):
        if a not in trials or b not in trials:return
        values={}
        for metric in ('hold_displacement_mm','hold_rotation_increment_rad'):
            aa,bb=trials[a].get(metric),trials[b].get(metric)
            values[metric]=abs(aa/bb-1) if aa is not None and bb else None
        comparisons[label]=dict(status='PASS' if all(v is not None and v<=tol for v in values.values()) else 'FAIL',relative_differences=values,tolerance=tol,trial=a,reference=b)
    for n in (11,21,41):
        for q in (8,16):compare(f'q{q}_to32_n{n}',f'convergence_n{n}q{q}',f'convergence_n{n}q32',.01)
    for n in (11,21):compare(f'mesh_n{n}_to41',f'convergence_n{n}q32','convergence_n41q32',.01)
    compare('dt_half','convergence_halfdt','convergence_n11q8',.001);compare('repeat','convergence_repeat','convergence_n11q8',1e-6);compare('history_half','convergence_history_half','convergence_n11q8',.01)
    names=['wrenches_'+a+s for a in ('Fx','Fy','Fz','Tx','Ty','Tz') for s in ('plus','minus')]
    qualified=len(comparisons)==11 and all(v['status']=='PASS' for v in comparisons.values())
    all12=all(n in trials and trials[n].get('bounded_hold_pass') and trials[n].get('hold_drift_pass') and trials[n].get('recovery_pass') for n in names)
    write_json(OUT/'gate.json',dict(trials=trials,comparisons=comparisons,spatial_temporal_history_convergence='PASS' if qualified else 'FAIL',same_condition_12_wrenches_with_recovery='PASS' if all12 else 'FAIL',full_grasp_certified=False,grasp_optimization='BLOCKED',reason='guided research geometry; inherited Beam force has nonzero closed-loop work, global energy gate fails; native surface qualification remains separate'))
    print('convergence',qualified,'all12',all12,'trials',len(trials))
if __name__=='__main__':main()
