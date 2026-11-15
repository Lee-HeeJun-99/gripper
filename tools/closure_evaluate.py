"""Read actual artifacts, enforce old tolerances, and keep global optimization shut."""
import csv,json
import numpy as np
from closure_common import ROOT,OUT,sha,write_json
from trial_validation import read_states
def trial(directory):
    r=json.loads((directory/'metrics.json').read_text())
    for name,digest in r.get('artifacts',{}).items():
        if sha(directory/name)!=digest:raise ValueError('corrupt '+name)
    result={k:r.get(k) for k in ('status','execution_completed','bounded_hold_pass','hold_displacement_mm','max_object_angle','object_force_residual','object_moment_residual','object_speed','object_angular_speed','finger_force_residual','finger_moment_residual','failure_reason')}
    result['config']=r['config'];result['metrics_sha256']=sha(directory/'metrics.json');result['grasp_certified']=False
    if not r.get('execution_completed'):return result
    raw=read_states(directory/'state.txt');c=r['config'];n=c['nodes'];obj=c['object_index'];x0=np.array(raw[0]['X']).reshape(-1,7);x=np.array(raw[-1]['X']).reshape(-1,7);v=np.array(raw[-1]['V']).reshape(-1,6);free=[i for i in range(obj) if i not in (0,n,2*n,3*n)]
    rest=float(np.linalg.norm(x[free,:3]-x0[free,:3],axis=1).max());angle=float((2*np.arctan2(np.linalg.norm(x[free,3:6],axis=1),abs(x[free,6]))).max());speed=float(abs(v[free,:3]).max());omega=float(abs(v[free,3:]).max());last=raw[-1]['time'];tail=[s for s in raw if c['hold_until']-.1-1e-8<=s['time']<c['hold_until']-1e-8];positions=np.array([s['X'][7*obj:7*obj+3] for s in tail]);drift=float(np.linalg.norm(positions-positions[0],axis=1).max());drift_ratio=drift/r['hold_displacement_mm'] if r['hold_displacement_mm'] else float('inf')
    result.update(recovery=dict(translation_mm=rest,angle_rad=angle,speed_mm_s=speed,omega_rad_s=omega,contacts=r['release_contacts'],time=last),recovery_pass=bool(rest<1e-4 and angle<1e-5 and speed<1e-5 and omega<1e-5 and r['release_contacts']==0),hold_drift_ratio=drift_ratio,hold_drift_pass=drift_ratio<1e-4)
    return result
def main():
    trials={}
    for p in (OUT/'trials').glob('*/metrics.json'):
        try:trials[p.parent.name]=trial(p.parent)
        except (ValueError,OSError,KeyError) as e:trials[p.parent.name]=dict(status='FAIL',reason=str(e),grasp_certified=False)
    comparisons={}
    def compare(label,a,b,tol):
        if a not in trials or b not in trials:return
        aa,bb=trials[a].get('hold_displacement_mm'),trials[b].get('hold_displacement_mm')
        if aa is None or bb is None:comparisons[label]=dict(status='FAIL',reason='no valid metrics');return
        difference=abs(aa/bb-1);comparisons[label]=dict(status='PASS' if difference<=tol else 'FAIL',reference=b,trial=a,relative_difference=difference,tolerance=tol)
    for n in (11,21,41):
        for q in (8,16):compare(f'q{q}_to32_n{n}',f'convergence_n{n}q{q}',f'convergence_n{n}q32',.01)
    for n in (11,21):compare(f'mesh_n{n}_to41',f'convergence_n{n}q32','convergence_n41q32',.01)
    compare('dt_half','convergence_halfdt','convergence_n11q8',.001);compare('repeat','convergence_repeat','convergence_n11q8',1e-6);compare('history_spacing_half','convergence_history_half','convergence_n11q8',.01)
    complete=len(comparisons)==11;spatial=complete and all(v['status']=='PASS' for v in comparisons.values())
    wrench_names=['wrenches_'+a+s for a in ('Fx','Fy','Fz','Tx','Ty','Tz') for s in ('plus','minus')];all_wrench=len([n for n in wrench_names if n in trials])==12 and all(trials[n].get('bounded_hold_pass') and trials[n].get('hold_drift_pass') and trials[n].get('recovery_pass') for n in wrench_names)
    write_json(OUT/'gate.json',dict(trials=trials,comparisons=comparisons,spatial_temporal_history_convergence='PASS' if spatial else 'FAIL',baseline_all12_wrenches='PASS' if all_wrench else 'FAIL',full_grasp_certified=False,grasp_optimization='BLOCKED',reason='full12wrench and conservative integrated beam/global energy remain unverified or failed; native calibration does not certify gripper'))
    print('convergence',spatial,[(k,v['relative_difference']) for k,v in comparisons.items() if 'relative_difference' in v],'all12',all_wrench)
if __name__=='__main__':main()
