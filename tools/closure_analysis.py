"""Small measured-data tables/figures; does not manufacture physics trial values."""
import csv,json,math,os
import numpy as np
from closure_common import ROOT,OUT,sha,write_json
def native(directory):
    result=json.loads((directory/'result.json').read_text());c=json.loads((directory/'config.json').read_text());obj=c['object_index'];before=None;maximum=0.;angle=0.;omega=0.;active=[];ratios=[];release=None
    with (directory/'native_states.jsonl').open() as f:
        for line in f:
            r=json.loads(line);t=r['time'];x=np.array(r['X'])[obj];v=np.array(r['V'])[obj];l=np.array(r['constraint_forces']);count=0
            if abs(t-6)<1e-7:before=x[:3]
            if before is not None and 6<=t<=14+1e-8:maximum=max(maximum,float(np.linalg.norm(x[:3]-before)))
            if 13.9-1e-7<=t<14-1e-7:
                angle=max(angle,float(2*np.arctan2(np.linalg.norm(x[3:6]),abs(x[6]))));omega=max(omega,float(abs(v[3:]).max()))
                if len(l)%3:raise ValueError('unexpected friction contact row count')
                for a,b,d in l.reshape(-1,3):
                    if a>1e-16:count+=1;ratios.append(float(math.hypot(b,d)/(c['mu']*a)))
                active.append(count)
            release=int(sum(np.linalg.norm(l.reshape(-1,3),axis=1)>1e-16)) if len(l)%3==0 else None
    checks=dict(force=result.get('object_force_relative',1)<1e-3,moment=result.get('object_moment_relative',1)<1e-3,speed=result.get('object_speed',1)<1e-5,angular_speed=omega<1e-5,translation=maximum<.05,angle=angle<.01,active_contact=bool(active) and min(active)>0,released=release==0)
    return dict(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',original_classifier_status=result['status'],audit_checks=checks,result_sha256=sha(directory/'result.json'),hold_subchecks=result.get('hold_subchecks'),force_relative=result.get('object_force_relative'),moment_relative=result.get('object_moment_relative'),speed=result.get('object_speed'),displacement_mm=maximum,angle_rad=angle,angular_speed=omega,min_active_hold_contacts=min(active) if active else None,max_friction_ratio=max(ratios) if ratios else None,final_active_contacts=release,numerical_buffer_mm=result.get('numerical_contact_buffer_mm'),scope='native triangle friction rows normal,tangent1,tangent2; candidate rows and active lambda contacts distinguished; impulse/dt physical wrench')
def main():
    evidence=ROOT/'reports/closure_evidence';evidence.mkdir(exist_ok=True);rows=[]
    for group,base in [('twofinger',OUT),('threefinger',OUT/'threefinger')]:
        for p in sorted((base/'trials').glob('*/metrics.json')):
            r=json.loads(p.read_text());c=r.get('config',{});rows.append(dict(group=group,trial=p.parent.name,status=r.get('status'),axis=c.get('axis'),load=c.get('load'),nodes=c.get('nodes'),samples=c.get('samples'),dt=c.get('dt'),duration=c.get('duration'),pressure=c.get('pressure'),tension=c.get('tension'),mu=c.get('mu'),displacement_mm=r.get('hold_displacement_mm'),max_angle_rad=r.get('max_object_angle'),force_residual=r.get('object_force_residual'),moment_residual=r.get('object_moment_residual'),holding_subgate=r.get('bounded_hold_pass'),runtime_s=r.get('process',{}).get('runtime_s'),failure_reason=r.get('failure_reason'),metrics_sha256=sha(p)))
    with (evidence/'trials.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    natives={}
    for name in ('native_gripper','native_gripper_scalar','native_gripper_buffer1','native_gripper_buffer_half'):
        if (OUT/name/'result.json').exists():natives[name]=native(OUT/name)
    if 'native_gripper_buffer_half' in natives:
        a,b=natives['native_gripper_buffer1']['displacement_mm'],natives['native_gripper_buffer_half']['displacement_mm'];difference=abs(a/b-1) if b else None
        natives['buffer_comparison']=dict(status='PASS' if difference is not None and difference<.01 else 'FAIL',relative_displacement_difference=difference,tolerance=.01,scope='two finite buffer offsets only; no dt/triangle continuum certificate')
    write_json(OUT/'native_audit.json',natives);write_json(evidence/'native_audit.json',natives)
    cache=ROOT/'.runtime/closure_matplotlib';cache.mkdir(parents=True,exist_ok=True);os.environ['MPLCONFIGDIR']=str(cache)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6,3.5))
    for n in (11,21,41):
        rr=sorted([r for r in rows if r['group']=='twofinger' and r['trial'] in [f'convergence_n{n}q{q}' for q in (8,16,32)]],key=lambda r:r['samples']);ax.plot([r['samples'] for r in rr],[r['displacement_mm'] for r in rr],'o-',label=f'{n} nodes')
    ax.set(xlabel='Active-interval Gauss order',ylabel='Object displacement (mm)',title='Measured SOFA: two-finger +Fx');ax.legend();fig.tight_layout();fig.savefig(evidence/'contact_convergence.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.5));rr=[r for r in rows if r['trial'].startswith('wrenches_')];labels=[r['group'][:1]+('2' if r['group']=='twofinger' else '3')+' '+r['trial'][9:] for r in rr];vals=[max(r['force_residual'] or 1e-16,r['moment_residual'] or 1e-16) for r in rr];ax.bar(range(len(rr)),vals,color=['tab:red' if r['status']=='FAIL' else 'tab:blue' for r in rr]);ax.axhline(.001,color='black',linestyle='--',label='unchanged residual limit');ax.set_yscale('log');ax.set_xticks(range(len(rr)),labels,rotation=90,fontsize=7);ax.set(ylabel='Max normalized force/moment residual',title='Actual same-condition wrench trials; geometry differs');ax.legend();fig.tight_layout();fig.savefig(evidence/'wrench_residuals.png',dpi=140);plt.close(fig)
    print('measured trials',len(rows),'native',list(natives))
if __name__=='__main__':main()
