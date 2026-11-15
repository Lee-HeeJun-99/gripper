"""Independent raw-state audits; successful execution never implies force closure."""
import csv,json,math
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
from grasp_common import ROOT,OUT,BUILD,sha,write_json
from trial_validation import read_states

def verify_record(directory):
    r=json.loads((directory/'metrics.json').read_text())
    for name,h in r.get('artifacts',{}).items():
        if sha(directory/name)!=h:raise ValueError('artifact mismatch: '+name)
    return r

def audit(directory):
    r=verify_record(directory);c=r['config'];result=dict(recorded_status=r['status'],metrics_sha256=sha(directory/'metrics.json'),execution_completed=r.get('execution_completed',False),bounded_hold_pass=r.get('bounded_hold_pass',False))
    if not r.get('execution_completed'):return dict(result,status='FAIL',reason=r.get('failure_reason'),physics_evaluated=False)
    raw=read_states(directory/'state.txt');obj=c['object_index'];time=np.array([p['time'] for p in raw]);x=np.array([p['X'] for p in raw]).reshape(len(raw),obj+1,7);v=np.array([p['V'] for p in raw]).reshape(len(raw),obj+1,6);end=c['hold_until'];tail=(time>=end-.1-1e-8)&(time<end-1e-8)
    tree=ET.parse(directory/'scene.scn').getroot();object_unconstrained=True
    for node in tree.iter():
        if 'Fixed' in node.tag and 'indices' in node.attrib and obj in map(int,node.get('indices').split()):object_unconstrained=False
    initial=x[0];free=[i for i in range(obj) if i not in (0,c['nodes'],2*c['nodes'],3*c['nodes'])]
    tail_positions=x[tail,obj,:3];delta=float(np.linalg.norm(tail_positions-tail_positions[0],axis=1).max());scale=r['hold_displacement_mm'];drift=delta/scale if scale>0 else (0 if delta==0 else None)
    points=[];endpoint_a=[];endpoint_b=[];coefficients=[]
    n=c['nodes']
    for layer in range(4):
        for i in range(n-1):
            for j in range(c['samples']+1):endpoint_a.append(layer*n+i);endpoint_b.append(layer*n+i+1);coefficients.append(j/c['samples'])
    a=np.array(endpoint_a);b=np.array(endpoint_b);s=np.array(coefficients)[:,None];max_vt=0.;min_rank=6
    def rotate(q,points):
        cross=np.cross(q[:3],points);return points+2*(q[3]*cross+np.cross(q[:3],cross))
    for frame in np.flatnonzero(tail):
        p=(1-s)*x[frame,a,:3]+s*x[frame,b,:3];vp=(1-s)*v[frame,a,:3]+s*v[frame,b,:3];object_pose=x[frame,obj];d=p-object_pose[:3];q=object_pose[3:7];local=rotate(np.array([-q[0],-q[1],-q[2],q[3]]),d);radius=c['object_radius'];normal=np.zeros_like(local)
        if c['shape']==0:
            norm=np.linalg.norm(local,axis=1);distance=norm-radius;normal=local/np.maximum(norm[:,None],1e-300)
        elif c['shape']==1:
            radial=np.linalg.norm(local[:,[0,2]],axis=1);d0=radial-radius;d1=abs(local[:,1])-radius;positive=np.stack([np.maximum(d0,0),np.maximum(d1,0)],axis=1);norm=np.linalg.norm(positive,axis=1);distance=norm+np.minimum(0,np.maximum(d0,d1));side=d0>=d1;normal[side,0]=local[side,0]/np.maximum(radial[side],1e-300);normal[side,2]=local[side,2]/np.maximum(radial[side],1e-300);normal[~side,1]=np.sign(local[~side,1]);outside=norm>0
            normal[outside,0]=positive[outside,0]/norm[outside]*local[outside,0]/np.maximum(radial[outside],1e-300);normal[outside,2]=positive[outside,0]/norm[outside]*local[outside,2]/np.maximum(radial[outside],1e-300);normal[outside,1]=positive[outside,1]/norm[outside]*np.sign(local[outside,1])
        else:
            gap=abs(local)-radius;positive=np.maximum(gap,0);norm=np.linalg.norm(positive,axis=1);distance=norm+np.minimum(0,gap.max(axis=1));nearest=gap.argmax(axis=1);normal[np.arange(len(local)),nearest]=np.sign(local[np.arange(len(local)),nearest]);outside=norm>0;normal[outside]=positive[outside]/norm[outside,None]*np.sign(local[outside])
        active=distance<.1
        if not active.any():min_rank=0;continue
        nw=rotate(q,normal[active]);relative=vp[active]-v[frame,obj,:3]-np.cross(v[frame,obj,3:],d[active]);vt=relative-nw*np.sum(relative*nw,axis=1)[:,None];max_vt=max(max_vt,float(np.linalg.norm(vt,axis=1).max()))
        blocks=[]
        for arm in d[active]/radius:
            rx,ry,rz=arm;blocks.append(np.vstack([np.eye(3),np.array([[0,-rz,ry],[rz,0,-rx],[-ry,rx,0]])]))
        singular=np.linalg.svd(np.hstack(blocks),compute_uv=False);rank=int(sum(singular>1e-10*singular[0]));min_rank=min(min_rank,rank)
    recovery=dict(finger_speed=float(abs(v[-1,free,:3]).max()),finger_angular_speed=float(abs(v[-1,free,3:]).max()),translation_error_mm=float(np.linalg.norm(x[-1,free,:3]-initial[free,:3],axis=1).max()),rotation_error_rad=float((2*np.arctan2(np.linalg.norm(x[-1,free,3:6],axis=1),abs(x[-1,free,6]))).max()),contacts=r['release_contacts'])
    recovery_checks=dict(contact_open=recovery['contacts']==0,finger_speed=recovery['finger_speed']<1e-5,finger_angular_speed=recovery['finger_angular_speed']<1e-5,translation_recovered=recovery['translation_error_mm']<1e-4,rotation_recovered=recovery['rotation_error_rad']<1e-5)
    with (directory/'contact.csv').open() as stream:contact=list(csv.DictReader(stream))
    held=[row for row in contact if end-.1-1e-8<=float(row['time'])<end-1e-8];slipping=max((float(row['slip']) for row in held),default=0)
    result.update(status='EXPERIMENTAL' if r.get('bounded_hold_pass') else 'FAIL',physics_evaluated=True,object_unconstrained=object_unconstrained,hold_displacement_mm=scale,hold_drift_ratio=drift,hold_drift_pass=drift is not None and drift<1e-4,max_relative_tangent_speed_mm_s=max_vt,stationary_elastic_stick=bool(r.get('bounded_hold_pass') and max_vt<1e-5 and slipping==0),min_unrestricted_point_wrench_rank=min_rank,wrench_rank_scope='rank<6 precludes full wrench closure; rank6 alone does NOT establish Coulomb force closure',recovery=recovery,recovery_checks=recovery_checks,full_release_recovery_pass=all(recovery_checks.values()),grasp_certified=False)
    return result

def main():
    trials={}
    for p in sorted((OUT/'trials').glob('*/metrics.json')):
        try:trials[p.parent.name]=audit(p.parent)
        except (ValueError,OSError,KeyError) as e:trials[p.parent.name]=dict(status='FAIL',reason=str(e),grasp_certified=False)
    comparisons={};base=trials['settled_sphere_xplus']['hold_displacement_mm']
    for name,tol in [('sphere_halfdt',.001),('sphere_q16',.01),('sphere_q32',.01),('sphere_n21q16',.01),('sphere_n21q32',.01),('sphere_n41q16',.01),('fast_repeat',1e-6)]:
        if name in trials and trials[name].get('hold_displacement_mm') is not None:
            val=trials[name]['hold_displacement_mm'];comparisons[name]=dict(reference=base,value=val,relative_difference=abs(val/base-1),tolerance=tol,pass_check=abs(val-base)<=1e-10+tol*abs(base))
    for label,an,bn,tol in [('matched_quadrature_beam_mesh','sphere_q32','sphere_n21q16',.01),('fine_quadrature','sphere_n21q16','fast_n21q32',.01),('fine_beam_mesh','fast_n21q32','fast_n41q16',.01),('finer_quadrature','fast_n41q16','fast_n41q32',.01)]:
        if an in trials and bn in trials and trials[an].get('hold_displacement_mm') and trials[bn].get('hold_displacement_mm'):
            a,b=trials[an]['hold_displacement_mm'],trials[bn]['hold_displacement_mm'];comparisons[label]=dict(reference=a,value=b,relative_difference=abs(b/a-1),tolerance=tol,pass_check=abs(b-a)<=1e-10+tol*abs(a))
    final_names=['final_sphere_'+axis+sign for axis in 'xyz' for sign in ('plus','minus')]
    groups={}
    for prefix in ('sphere_','settled_sphere_','final_sphere_'):
        names=[prefix+axis+sign for axis in 'xyz' for sign in ('plus','minus')];present=[n for n in names if n in trials];groups[prefix]=dict(complete=len(present)==6,all_bounded_hold=len(present)==6 and all(trials[n].get('bounded_hold_pass') for n in names),all_stationary_stick=len(present)==6 and all(trials[n].get('stationary_elastic_stick') for n in names),all_release_recovered=len(present)==6 and all(trials[n].get('full_release_recovery_pass') for n in names))
    write_json(OUT/'gate.json',dict(trials=trials,comparisons=comparisons,direction_groups=groups,full_grasp_certified=False,grasp_optimization='BLOCKED',reason='surface/dt/space/full-wrench and global-energy certification remain distinct from bounded guided-finger holding; old45gates not combined'))
    print(groups,comparisons)

if __name__=='__main__':main()
