"""Independent closure runner adapted from immutable grasp_trial at20249c9."""
import argparse,csv,json,math
from dataclasses import dataclass,asdict
import xml.etree.ElementTree as ET
import numpy as np
from integrated_trial import Config as BaseConfig,scene,sequence
from trial_validation import read_states
from run_trial import execute_process
from closure_frame_common import ROOT,SOFA,OUT,PLUGIN,identity,write_json,sha,provenance,SDK

@dataclass(frozen=True)
class Config:
    shape:int=0
    axis:int=0
    load:float=1e-6
    nodes:int=11
    samples:int=8
    dt:float=.0005
    duration:float=18.
    hold_until:float=14.
    rayleigh_mass:float=2.
    mu:float=.3
    normal_k:float=.001
    tangent_k:float=.001
    tension:float=.001
    pressure:float=.001
    base_z:float=5.305
    object_x:float=95.
    object_radius:float=5.
    stride:int=20
    history_spacing:float=.01

    def validate(self):
        if type(self.shape) is not int or type(self.axis) is not int or self.shape not in (0,1,2) or self.axis not in (0,1,2,3,4,5) or type(self.nodes) is not int or not 3<=self.nodes<=41 or type(self.samples) is not int or not 2<=self.samples<=32 or type(self.stride) is not int:raise ValueError('shape/axis/mesh/sample type or bound')
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in asdict(self).values()):raise ValueError('invalid numeric value')
        if not .001<=self.history_spacing<=1:raise ValueError('history spacing')
        if min(self.dt,self.normal_k,self.tangent_k,self.base_z,self.object_radius)<=0 or min(self.mu,self.tension,self.pressure)<0 or not 8<=self.duration<=24 or not 8<=self.hold_until<=self.duration-4 or not 0<=self.rayleigh_mass<=5:raise ValueError('physical/schedule bound')
        steps=round(self.duration/self.dt)
        if steps>120000 or self.stride<1 or steps%self.stride or abs(steps*self.dt-self.duration)>1e-10:raise ValueError('step/sample bound')
        return steps

def run(name,c=Config(),wall=240):
    if not isinstance(name,str) or not name or name in ('.','..') or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in name):raise ValueError('trial name must be one safe path component')
    if type(wall) not in (int,float) or not math.isfinite(wall) or not 0<wall<=480:raise ValueError('wall cap must be in (0,480] seconds')
    steps=c.validate();out=OUT/'trials'/name;out.mkdir(parents=True,exist_ok=False)
    scene(out,BaseConfig(nodes=c.nodes,load=0,duration=c.duration,dt=c.dt,stride=c.stride));tree=ET.parse(out/'scene.scn');root=tree.getroot();root.find('EulerImplicitSolver').set('rayleighMass',str(c.rayleigh_mass));body=root.find('Node')
    for element in list(body):body.remove(element)
    n=c.nodes;obj=6*n;poses=[]
    angles=(0.,2*math.pi/3,-2*math.pi/3)
    for finger,angle in enumerate(angles):
        ex=np.array([math.cos(angle),0,-math.sin(angle)]);ez=np.array([math.sin(angle),0,math.cos(angle)]);origin=np.array([95.,0,0])-95*ex+c.base_z*ez
        for layer in (0,1):
            for i in range(n):poses.append([*(origin+100*i/(n-1)*ex+(layer-.5)*.4*ez),0,math.sin(angle/2),0,math.cos(angle/2)])
    poses.append([c.object_x,0,0,0,0,0,1]);edges=[(f*2*n+l*n+i,f*2*n+l*n+i+1) for f in range(3) for l in (0,1) for i in range(n-1)]
    ET.SubElement(body,'MechanicalObject',name='dofs',template='Rigid3d',position=sequence(v for p in poses for v in p))
    ET.SubElement(body,'MeshTopology',name='edges',lines=sequence(v for e in edges for v in e))
    # Actual inertia per mass: sphere2r²/5; finite cylinder axis y vs transverse;
    # cube side2r. No isotropic-cylinder approximation in the new model.
    r=c.object_radius;inertia=[2*r*r/5]*3 if c.shape==0 else ([r*r/4+(2*r)**2/12,r*r/2,r*r/4+(2*r)**2/12] if c.shape==1 else [2*r*r/3]*3)
    masses=[[.00006/obj,1,1,0,0,0,1,0,0,0,1] for _ in range(obj)]+[[.0001,1,inertia[0],0,0,0,inertia[1],0,0,0,inertia[2]]]
    ET.SubElement(body,'DiagonalMass',name='all_masses',template='Rigid3d,Rigid3d',mstate='@dofs',geometryState='@dofs',topology='@edges',vertexMass=sequence(v for row in masses for v in row))
    ET.SubElement(body,'BeamFEMForceField',radius=str((4*(8*.4**3/12)/math.pi)**.25),youngModulus='250',poissonRatio='.32')
    ET.SubElement(body,'FixedProjectiveConstraint',indices=sequence([i*n for i in range(6)]))
    ET.SubElement(body,'PartialFixedProjectiveConstraint',indices=sequence(range(obj)),fixedDirections='0 1 0 1 0 1')
    for finger,angle in enumerate(angles):
        ET.SubElement(body,'FrameLayerNetwork',name=f'layer{finger}',referenceOrientation=sequence([0,math.sin(angle/2),0,math.cos(angle/2)]),filename=str(out/f'layer{finger}.csv'),stride=str(c.stride),startIndex=str(finger*2*n),nodesPerLayer=str(n),layers='2',mode='1',stiffness='1',height='.4',normalStiffness='.001',width='8',length='100',pressure='0',mu='.3',pressureTimes=sequence([0,3,c.hold_until+1]),pressureValues=sequence([0,c.pressure,0]))
        for layer in (0,1):ET.SubElement(body,'RoutedCable',name=f'cable{finger}_{layer}',route=sequence(range(finger*2*n+layer*n,finger*2*n+(layer+1)*n)),offsetZ='-.2',commandTimes=sequence([0,.5,c.hold_until+2]),commandValues=sequence([0,c.tension,0]))
    ET.SubElement(body,'ActiveIntervalContact',name='contact',historySpacing=str(c.history_spacing),segments=sequence(v for e in edges for v in e),objectIndex=str(obj),shape=str(c.shape),radius=str(r),halfHeight=str(r),pointRadius='.1',lineStiffness=str(c.normal_k),tangentLineStiffness=str(c.tangent_k),mu=str(c.mu),samples=str(c.samples),stride=str(c.stride),filename=str(out/'contact.csv'))
    ET.SubElement(body,'SpatialLoad',name='disturbance',index=str(obj),axis=str(c.axis),times=sequence([0,6,c.hold_until]),values=sequence([0,c.load,0]))
    ET.SubElement(body,'IntegratedRecorder',filename=str(out/'state.txt'),stride=str(c.stride));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    config=dict(**asdict(c),object_index=obj,object_constraints=[],fingers=3,layers=2,reference_angles=list(angles),finger_total_mass=.00006,wire_offsets=[-.2]*6,layer_dissipation_source='layer0/1/2.csv; original recorder does not identify new frame class',object_mass=.0001,object_inertia_per_mass=inertia,model_version='three-guided-planar-fingers/fixed-reference-layer/v1',friction='unchanged elastic stick/equal-mu law; independent material-history interpolation',guided_planar_fingers=True,hold_limit_mm=.05)
    command=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar','-l',str(PLUGIN),str(out/'scene.scn')]
    if SDK:command=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(PLUGIN)]
    write_json(out/'config.json',config);write_json(out/'command.json',command);record=dict(config=config,identity=identity(),provenance=provenance(),status='FAIL',grasp_certified=False)
    process=execute_process(command,out,wall);record['process']=process
    try:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        if process['exit_code'] or '[ERROR]' in log or 'behavior is undefined' in log or f'{steps} iterations done' not in log:raise ValueError('SOFA error/exit/timeout/incomplete run')
        raw=read_states(out/'state.txt')
        if len(raw)!=steps//c.stride+1:raise ValueError('missing frames')
        xs=np.array([p['X'] for p in raw]).reshape(len(raw),obj+1,7);vs=np.array([p['V'] for p in raw]).reshape(len(raw),obj+1,6);res=np.array([p['R'] for p in raw]).reshape(len(raw),obj+1,6);time=np.array([p['time'] for p in raw])
        if not all(np.isfinite(v).all() for v in (xs,vs,res,time)):raise ValueError('nonfinite state')
        local_y=np.empty_like(xs[:,:obj,4]);local_w=np.empty_like(xs[:,:obj,6])
        for finger,angle in enumerate(angles):
            rows=slice(2*n*finger,2*n*(finger+1));local_y[:,rows]=math.cos(angle/2)*xs[:,rows,4]-math.sin(angle/2)*xs[:,rows,6];local_w[:,rows]=math.cos(angle/2)*xs[:,rows,6]+math.sin(angle/2)*xs[:,rows,4]
        if abs(xs[:,:obj,[3,5]]).max()>1e-8 or (2*np.arctan2(abs(local_y),abs(local_w))).max()>=.005:raise ValueError('relative reference-frame small-planar domain exceeded')
        with (out/'contact.csv').open() as stream:contact=list(csv.DictReader(stream))
        if not contact:raise ValueError('missing contact history')
        diss=[float(r['friction_dissipation'])+float(r['release_dissipation']) for r in contact]
        if min(diss)<-1e-15 or any(b<a-1e-15 for a,b in zip(diss,diss[1:])):raise ValueError('negative dissipation')
        before=np.argmin(abs(time-6));mask=(time>=6-1e-8)&(time<=c.hold_until+1e-8);tail=(time>=c.hold_until-.1-1e-8)&(time<c.hold_until-1e-8);free=[i for i in range(obj) if i%n!=0]
        displacement=float(np.linalg.norm(xs[mask,obj,:3]-xs[before,obj,:3],axis=1).max());scale=(abs(c.load)/(r if c.axis>=3 else 1)) or 1e-6
        force=float(abs(res[tail,obj,:3]).max()/scale);moment=float(abs(res[tail,obj,3:]).max()/(scale*r));speed=float(abs(vs[tail,obj,:3]).max());omega=float(abs(vs[tail,obj,3:]).max())
        ffscale=c.tension*.2/100 if c.tension else 1e-6;mfscale=ffscale*100
        fforce=float(abs(res[tail][:,free][:,:,[0,2]]).max()/ffscale);fmoment=float(abs(res[tail][:,free,4]).max()/mfscale)
        ct=[r for r in contact if c.hold_until-.1-1e-8<=float(r['time'])<c.hold_until-1e-8]
        angle=float((2*np.arctan2(np.linalg.norm(xs[:,obj,3:6],axis=1),abs(xs[:,obj,6]))).max())
        checks=dict(translation=displacement<.05,rotation=angle<.01,object_velocity=speed<1e-5,object_angular_velocity=omega<1e-5,object_force=force<1e-3,object_moment=moment<1e-3,finger_force=fforce<1e-3,finger_moment=fmoment<1e-3,finger_velocity=float(abs(vs[tail][:,free][:,:,[0,2]]).max())<1e-5,finger_angular_velocity=float(abs(vs[tail][:,free,4]).max())<1e-5,contact=bool(ct) and min(float(r['contacts']) for r in ct)>=2,friction_capacity=max(float(r['max_ratio']) for r in contact)<=1+1e-10)
        release_contacts=float(contact[-1]['contacts']);release_motion=float(np.linalg.norm(xs[-1,:obj,:3]-np.array(poses)[:obj,:3],axis=1).max())
        record.update(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',execution_completed=True,hold_checks=checks,bounded_hold_pass=all(checks.values()),hold_displacement_mm=displacement,object_force_residual=force,object_moment_residual=moment,object_speed=speed,object_angular_speed=omega,finger_force_residual=fforce,finger_moment_residual=fmoment,max_object_angle=angle,release_contacts=release_contacts,release_finger_max_displacement_mm=release_motion,release_contact_open=release_contacts==0,friction_dissipation=diss[-1],final_stick=float(contact[-1]['stick']),final_slip=float(contact[-1]['slip']),max_friction_ratio=max(float(r['max_ratio']) for r in contact),limitation='adaptive line skin with interpolated material history; not full surface or certified force closure')
    except (ValueError,OSError,KeyError) as exc:record['failure_reason']=str(exc)
    record['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'};write_json(out/'metrics.json',record);print(name,record['status'],record.get('hold_displacement_mm'),record.get('object_force_residual'),record.get('failure_reason'),flush=True);return record

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--duration',type=float,default=18);p.add_argument('--axis',type=int,default=0);p.add_argument('--load',type=float,default=1e-6);p.add_argument('--shape',type=int,default=0);args=p.parse_args();run(args.name,Config(duration=args.duration,axis=args.axis,load=args.load,shape=args.shape))
