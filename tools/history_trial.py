"""New history field, same conservative beam/loads/guards; immutable outputs."""
import argparse,json,math,csv,time,xml.etree.ElementTree as ET
import numpy as np
import beam_grasp_trial as base
from history_common import ROOT,OUT,BUILD,SDK,FRAME,BEAM,PLUGIN,identity,write_json,sha
from run_trial import execute_process
from trial_validation import read_states
from closure_frame_evaluate import relative_angles
def analyze(out,config,p):
    record=dict(status='FAIL',config=config,identity=json.loads((out/'identity.json').read_text()),analysis_source_sha256=sha(ROOT/'tools/history_trial.py'),process=p,full_grasp_certified=False)
    n=config['nodes'];obj=config['object_index'];duration=config['duration'];axis=config['axis'];load=config['load'];tension=config['tension'];angles=config['reference_angles']
    steps=round(duration/config['dt'])
    try:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        if p['exit_code'] or '[ERROR]' in log or f'{steps} iterations done' not in log:raise ValueError('SOFA error/timeout/incomplete')
        raw=read_states(out/'state.txt');x=np.array([r['X'] for r in raw]).reshape(-1,obj+1,7);v=np.array([r['V'] for r in raw]).reshape(-1,obj+1,6);R=np.array([r['R'] for r in raw]).reshape(-1,obj+1,6);t=np.array([r['time'] for r in raw]);tail=(t>=13.9-1e-8)&(t<14-1e-8);free=[i for i in range(obj) if i%n];before=np.argmin(abs(t-6));hold=(t>=6-1e-8)&(t<=14+1e-8)
        if len(raw)!=steps//20+1 or not all(np.isfinite(a).all() for a in (x,v,R,t)):raise ValueError('invalid frames')
        for finger,angle in enumerate(angles):
            local=relative_angles(np.broadcast_to(np.array([0,math.sin(angle/2),0,math.cos(angle/2)]),x[:,2*finger*n:2*(finger+1)*n,3:].shape),x[:,2*finger*n:2*(finger+1)*n,3:])
            if local.max()>=.005 or abs(x[:,:obj,[3,5]]).max()>1e-8:raise ValueError('unchanged small-planar layer domain exceeded')
        scale=abs(load)/(5 if axis>=3 else 1) if load else 1e-6;fr=float(abs(R[tail,obj,:3]).max()/scale);mr=float(abs(R[tail,obj,3:]).max()/(scale*5));disp=float(np.linalg.norm(x[hold,obj,:3]-x[before,obj,:3],axis=1).max());ang=float((2*np.arctan2(np.linalg.norm(x[:,obj,3:6],axis=1),abs(x[:,obj,6]))).max());rotincrement=float(relative_angles(np.broadcast_to(x[before,obj,3:],x[tail,obj,3:].shape),x[tail,obj,3:]).max());speed=float(abs(v[tail,obj,:3]).max());omega=float(abs(v[tail,obj,3:]).max());support=np.zeros_like(R[tail]);support[:,:obj: n,:]=-R[tail,:obj:n,:]
        for i in free:support[:,i,[1,3,5]]=-R[tail][:,i][:,[1,3,5]]
        arm=x[tail,:,:3]-x[tail,obj:obj+1,:3];resultF=support[:,:,:3].sum(axis=1);resultM=(support[:,:,3:]+np.cross(arm,support[:,:,:3])).sum(axis=1)
        if axis<3:resultF[:,axis]+=load
        else:resultM[:,axis-3]+=load
        globalforce=float(abs(resultF).max()/scale);globalmoment=float(abs(resultM).max()/(scale*5));ffscale=tension*.2/100 if tension else 1e-6;ff=float(abs(R[tail][:,free][:,:,[0,2]]).max()/ffscale);fm=float(abs(R[tail][:,free,4]).max()/(ffscale*100));drift=float(np.linalg.norm(x[tail,obj,:3]-x[tail,obj,:3][0],axis=1).max())/(disp or 1)
        with (out/'contact.csv').open() as f:ct=list(csv.DictReader(f))
        tailct=[r for r in ct if 13.9-1e-8<=float(r['time'])<14-1e-8];rest=float(np.linalg.norm(x[-1,free,:3]-x[0,free,:3],axis=1).max());restangle=float(relative_angles(x[0,free,3:],x[-1,free,3:]).max());release=int(float(ct[-1]['contacts']));D=[float(r['friction_dissipation'])+float(r['release_dissipation']) for r in ct]
        checks=dict(translation=disp<.05,rotation=ang<.01,object_force=fr<1e-3,object_moment=mr<1e-3,object_speed=speed<1e-5,object_omega=omega<1e-5,finger_force=ff<1e-3,finger_moment=fm<1e-3,finger_speed=float(abs(v[tail][:,free]).max())<1e-5,global_force=globalforce<1e-3,global_moment=globalmoment<1e-3,contact=bool(tailct) and min(float(r['contacts']) for r in tailct)>=2,capacity=max(float(r['max_ratio']) for r in ct)<=1+1e-10,dissipation=min(D)>=-1e-15 and all(b>=a-1e-15 for a,b in zip(D,D[1:])),drift=drift<1e-4);recovery=duration>=24 and release==0 and rest<1e-4 and restangle<1e-5 and abs(v[-1,free]).max()<1e-5
        record.update(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',execution_completed=True,checks=checks,bounded_hold_pass=all(checks.values()),hold_displacement_mm=disp,hold_rotation_increment_rad=rotincrement,max_object_angle=ang,object_force_residual=fr,object_moment_residual=mr,global_force_residual=globalforce,global_moment_residual=globalmoment,finger_force_residual=ff,finger_moment_residual=fm,object_speed=speed,object_angular_speed=omega,recovery_pass=bool(recovery),release_contacts=release,recovery_translation_mm=rest,recovery_angle_rad=restangle,friction_dissipation=D[-1])
    except (ValueError,OSError,KeyError,IndexError) as e:record['failure_reason']=str(e)
    return record
def run(name,nodes=11,samples=8,dt=.0005,duration=24.,history=.01,cell_order=2,profile=False,wall=480,prepare_only=False):
    identity();base.OUT=OUT;out=base.run(name,nodes=nodes,samples=samples,dt=dt,duration=24. if profile else duration,history=history,prepare_only=True)
    tree=ET.parse(out/'scene.scn');contact=tree.getroot().find('Node').find('ActiveIntervalContact');contact.tag='MaterialHistoryContact';contact.set('cellOrder',str(cell_order));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    c=json.loads((out/'config.json').read_text());c.update(duration=4. if profile else duration,contact_model='material_node_objective_transport_cell_split_v1',normal_quadrature=samples,tangent_cell_order=cell_order,profile_only=profile)
    write_json(out/'config.json',c);steps=round(c['duration']/dt);cmd=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(FRAME),str(BEAM),str(PLUGIN)]
    write_json(out/'command.json',cmd);write_json(out/'identity.json',identity())
    if prepare_only:return out
    p=execute_process(cmd,out,wall);write_json(out/'execution_result.json',p)
    if profile:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(status='EXPERIMENTAL' if p['exit_code']==0 and '[ERROR]' not in log and f'{steps} iterations done' in log else 'FAIL',config=c,process=p,scope='8000step profile, NOT hold/equilibrium qualification',predicted_18s_wall=p['runtime_s']*4.5,identity=identity())
    else:r=analyze(out,c,p)
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'metrics.json',r);print(name,r['status'],p['runtime_s'],r.get('hold_displacement_mm'),r.get('global_moment_residual'),flush=True);return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--profile',action='store_true');p.add_argument('--nodes',type=int,default=11);p.add_argument('--samples',type=int,default=8);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--history',type=float,default=.01);p.add_argument('--cell-order',type=int,default=2);p.add_argument('--duration',type=float,default=24);args=p.parse_args();run(args.name,nodes=args.nodes,samples=args.samples,dt=args.dt,duration=args.duration,history=args.history,cell_order=args.cell_order,profile=args.profile)
