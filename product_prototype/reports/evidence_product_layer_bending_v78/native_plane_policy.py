"""Native sphere/plane policy coupon vs explicit perfectly-inelastic reference.
No FEM,cable,gyro,custom ODE/contact solver. Reference is NOT Native output.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_pair_rows
def vec(s):return np.fromstring(s,sep=' ')
def read(p):return list(csv.DictReader(p.open()))
def add(parent,tag,**attrs):return ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);physical=BASE/'cad/build_default_control332/libReGripProductSequence.so';direct,_=compiled_pair_rows()
 if sha(physical)!='3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0':raise ValueError('physical journal binary changed')
 records=[];mass=.001;radius=.001;buffer=.0002;gap=.0015;z0=radius+buffer+gap;speed=-1.;duration=.01;event=gap/-speed
 for velocity_first in (False,True):
  for dt in (.0025,.00125,.000625):
   name=('velocity' if velocity_first else 'position')+'_'+format(dt,'.6f');d=out/name;d.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
   plugins=['AnimationLoop','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Model','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer','Topology.Container.Constant','Mapping.NonLinear','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact']
   for plugin in plugins:add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
   for binary in (physical,direct):add(root,'RequiredPlugin',pluginName=binary)
   add(root,'FreeMotionAnimationLoop',solveVelocityConstraintFirst=int(velocity_first));add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-10',maxIterations=1000,computeConstraintForces=1);add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0);add(root,'EigenSparseLU',name='linear');add(root,'GenericConstraintCorrection');add(root,'CollisionPipeline',depth=6);add(root,'BruteForceBroadPhase');add(root,'BVHNarrowPhase',name='narrow');add(root,'LocalMinDistance',alarmDistance=.005,contactDistance=buffer,useSphereTriangle=1);add(root,'CollisionResponse',name='responses',response='FrictionContactConstraint',responseParams='mu=0')
   sphere=add(root,'Node',name='sphere');add(sphere,'MechanicalObject',name='frames',template='Rigid3d',position=f'.001 .002 {z0:.17g} 0 0 0 1',velocity='0 0 -1 0 0 0');add(sphere,'UniformMass',template='Rigid3d',vertexMass='.001 1 4e-7 0 0 0 4e-7 0 0 0 4e-7');add(sphere,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=d/'rigid.csv',auditMass=1);col=add(sphere,'Node',name='collision');add(col,'MechanicalObject',name='points',template='Vec3d',position='0 0 0');add(col,'SphereCollisionModel',radius=radius,group=1);add(col,'RigidMapping',input='@../frames',output='@points')
   plane=add(root,'Node',name='plane');points='-.01 -.01 0 .01 -.01 0 .01 .01 0 -.01 .01 0';add(plane,'MeshTopology',position=points,triangles='0 1 2 0 2 3');add(plane,'MechanicalObject',name='points',template='Vec3d',position=points);add(plane,'FixedConstraint',indices='0 1 2 3');add(plane,'TriangleCollisionModel',moving=0,simulated=0,group=2)
   add(root,'NativePairRows',body='@sphere/frames',solver='@constraints',filename=d/'direct.csv');add(root,'NativeResponseRows',manager='@responses',body='@sphere/frames',solver='@constraints',filename=d/'response.csv');add(root,'NativeDetectionPairs',narrow='@narrow',filename=d/'detector.csv');ET.ElementTree(root).write(d/'scene.scn');steps=round(duration/dt);proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(mode='velocity_first' if velocity_first else 'position_first',dt_s=dt,process=proc,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_RUN',frames=[])
   if proc['exit_code']==0 and '[ERROR]' not in logs:
    states=read(d/'rigid.csv');oldv=speed
    if len(states)!=steps:raise ValueError('partial Native result')
    for row in states:
     t=float(row['time_s']);q=vec(row['rigid_q']);v=vec(row['rigid_v']);imp=vec(row['object_impulse_Ns_Nms']);refz=z0+speed*min(t,event);refv=speed if t<event else 0.;r['frames'].append(dict(time_s=t,actual_z_m=float(q[2]),actual_vz_m_s=float(v[2]),actual_normal_impulse_Ns=float(imp[2]),actual_buffered_gap_m=float(q[2]-radius-buffer),reference_z_m=refz,reference_vz_m_s=refv,reference_law='e=0 instantaneous impact at buffered plane (NEW reference assumption,not inferred Native law)',linear_momentum_residual_Ns=float(mass*(v[2]-oldv)-imp[2]),position_reference_error_m=float(q[2]-refz),velocity_reference_error_m_s=float(v[2]-refv)));oldv=v[2]
    r.update(status='NATIVE_RUN_COMPLETED_NOT_IMPACT_QUALIFIED',maximum_momentum_residual_Ns=max(abs(x['linear_momentum_residual_Ns']) for x in r['frames']),maximum_position_reference_error_m=max(abs(x['position_reference_error_m']) for x in r['frames']),maximum_velocity_reference_error_m_s=max(abs(x['velocity_reference_error_m_s']) for x in r['frames']))
   records.append(r)
 result=dict(status='NATIVE_PLANE_POLICY_COMPARISON_ONLY' if all(r['status']!='FAIL_NATIVE_RUN' for r in records) else 'FAIL_NATIVE_COUPON',scope='Actual installed Native contact policies;analytical e=0 buffered-plane reference is separately specified,not Native solver output or a new contact solver. No B3/holding/time/energy qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),physical_binary_sha256=sha(physical),direct_binary_sha256=sha(direct),SDK='/home/ubuntu/SOFA/v26.06.00',mass_kg=mass,sphere_radius_m=radius,contact_buffer_m=buffer,initial_buffered_gap_m=gap,initial_velocity_m_s=speed,analytic_reference_event_s=event,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**{k:v for k,v in result.items() if k!='records'},'runs':[{k:v for k,v in r.items() if k!='frames'} for r in records]},indent=2))
if __name__=='__main__':main()
