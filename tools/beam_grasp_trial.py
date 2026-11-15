"""Same explicit guided3finger geometry with ONLY beam constitutive replacement.

Prior immutable XML is a configuration template, never a performance result.
All evaluated states come from a new matched-SDK child process.
"""
import json,csv,math,argparse
import xml.etree.ElementTree as ET
import numpy as np
from beam_common import ROOT,OUT,SDK,PLUGIN,FRAME,identity,material,sha,write_json
from run_trial import execute_process
from trial_validation import read_states
from closure_frame_evaluate import relative_angles
TEMPLATE=ROOT/'models/conservative_beam/templates'
def run(name,nodes=11,samples=8,dt=.0005,duration=24.,axis=5,load=5e-6,history=.01,pressure=.001,tension=.001,mu=.3,shape=0,prepare_only=False,wall=480):
    if not name.replace('_','').isalnum() or nodes not in (11,21,41) or samples not in (8,16,32) or axis not in range(6) or shape not in (0,1,2) or not .001<=history<=.02 or not .000125<=dt<=.001 or duration not in (18.,24.):raise ValueError('bounded grasp configuration')
    if not all(math.isfinite(v) for v in (load,pressure,tension,mu)) or min(pressure,tension,mu)<0:raise ValueError('physical inputs')
    if wall!=480 and not (wall==900 and nodes==41 and samples==32 and duration==18.):raise ValueError('only one profile-justified900s high-resolution exception; otherwise480s')
    out=OUT/'grasp'/name;out.mkdir(parents=True,exist_ok=False);tree=ET.parse(TEMPLATE/'scene.scn');root=tree.getroot();root.set('dt',str(dt));body=root.find('Node');config=json.loads((TEMPLATE/'config.json').read_text());seq=lambda v:' '.join(map(str,v));n=nodes;obj=6*n;angles=(0,2*math.pi/3,-2*math.pi/3);poses=[]
    for angle in angles:
        ex=np.array([math.cos(angle),0,-math.sin(angle)]);ez=np.array([math.sin(angle),0,math.cos(angle)]);origin=np.array([95,0,0])-95*ex+5.305*ez
        for layer in (0,1):
            for i in range(n):poses.append([*(origin+100*i/(n-1)*ex+(layer-.5)*.4*ez),0,math.sin(angle/2),0,math.cos(angle/2)])
    poses.append([95,0,0,0,0,0,1]);edges=[j for layer in range(6) for i in range(n-1) for j in (layer*n+i,layer*n+i+1)];body.find('MechanicalObject').set('position',seq(v for p in poses for v in p));body.find('MeshTopology').set('lines',seq(edges));inertia=[10,10,10] if shape==0 else ([25/4+100/12,12.5,25/4+100/12] if shape==1 else [50/3]*3);masses=[[.00006/obj,1,1,0,0,0,1,0,0,0,1] for _ in range(obj)]+[[.0001,1,inertia[0],0,0,0,inertia[1],0,0,0,inertia[2]]];body.find('DiagonalMass').set('vertexMass',seq(v for row in masses for v in row));old=body.find('BeamFEMForceField');body.remove(old);ET.SubElement(body,'ConservativeBeam',name='new_beam',edges=seq(edges),**{k:str(v) for k,v in material().items()});body.find('FixedProjectiveConstraint').set('indices',seq(i*n for i in range(6)));body.find('PartialFixedProjectiveConstraint').set('indices',seq(range(obj)))
    # Recorder.init queries all fields. Put the beam BEFORE observers so its
    # reference edges exist at the first observer query; initial failure retained.
    newbeam=body.find('ConservativeBeam');body.remove(newbeam);body.insert(3,newbeam)
    for f,e in enumerate(body.findall('FrameLayerNetwork')):e.set('nodesPerLayer',str(n));e.set('startIndex',str(2*f*n));e.set('pressureValues',seq([0,pressure,0]));e.set('filename',str(out/f'layer{f}.csv'))
    for layer,e in enumerate(body.findall('RoutedCable')):e.set('route',seq(range(layer*n,(layer+1)*n)));e.set('commandValues',seq([0,tension,0]))
    contact=body.find('ActiveIntervalContact')
    for k,v in dict(segments=seq(edges),objectIndex=obj,samples=samples,historySpacing=history,mu=mu,shape=shape,filename=out/'contact.csv').items():contact.set(k,str(v))
    e=body.find('SpatialLoad');e.set('index',str(obj));e.set('axis',str(axis));e.set('values',seq([0,load,0]));body.find('IntegratedRecorder').set('filename',str(out/'state.txt'));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    config.update(nodes=n,samples=samples,dt=dt,duration=duration,axis=axis,load=load,history_spacing=history,pressure=pressure,tension=tension,mu=mu,shape=shape,object_index=obj,object_inertia_per_mass=inertia,model_version='conservative_midpoint_rod_guided3finger_v1',beam_material=material(),template_config_sha256=sha(TEMPLATE/'config.json'),template_scene_sha256=sha(TEMPLATE/'scene.scn'));write_json(out/'config.json',config);steps=round(duration/dt);command=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(FRAME),str(PLUGIN)];write_json(out/'command.json',command);record=dict(status='FAIL',config=config,identity=identity(),full_grasp_certified=False)
    if prepare_only:
        write_json(out/'prepared_only.json',dict(status='NOT RUN',config=config,identity=identity(),scope='configuration only, not an executed or successful physics trial'));return out
    p=execute_process(command,out,wall);record['process']=p
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
    record['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'metrics.json',record);print(name,record['status'],record.get('global_moment_residual'),record.get('hold_displacement_mm'),record.get('failure_reason'),p['runtime_s'],flush=True);return record
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--duration',type=float,default=24.);a=p.parse_args();run(a.name,duration=a.duration)
