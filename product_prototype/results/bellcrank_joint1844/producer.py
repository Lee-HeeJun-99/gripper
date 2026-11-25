"""Three finite-body mass/ideal joint coupon; preserve nonlinear closure failure."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat

def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/bellcrank_link1843';geo=json.loads((src/'summary.json').read_text());assert geo['status']=='PASS_SAMPLED_FINITE_LINK_GEOMETRY_ONLY';rho=1000.;mass={};tensor={}
 for name in ('rotor','rod','slider'):
  c=geo['components'][name];mass[name]=c['volume_mm3']*1e-9*rho;tensor[name]=np.array(c['unit_density_inertia_mm5'])*1e-15*rho
 dt=.001;T=1e-4;load=5e-5;r=.01;effective=tensor['rotor'][2,2]+(mass['rod']+mass['slider'])*r*r;expected_accel=(-r*T+r*load)/effective
 binary=BASE/'cad/build_default_control332/libReGripProductSequence.so';probe=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so';meta=json.loads((BASE/'results/b3_cable_typed1831/phase_assessment.json').read_text());assert sha(probe)==meta['binary_sha256'];records=[]
 for name,omega,steps in [('initial_mass',0.,1),('finite_velocity',-.2,10)]:
  folder=out/name;folder.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
  for plugin in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Model','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer','Mapping.NonLinear','MechanicalLoad'):
   ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
  for plugin in (str(binary),str(probe),'/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'):
   ET.SubElement(root,'RequiredPlugin',pluginName=plugin)
  ET.SubElement(root,'FreeMotionAnimationLoop');ET.SubElement(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-12',maxIterations='1000',computeConstraintForces='1');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(root,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');ET.SubElement(root,'GenericConstraintCorrection')
  for component,label,centre,velocity in [('rotor','lever',[0,0,0],[0,0,0,0,0,omega]),('rod','rod',[-r,.015,.002],[0,-r*omega,0,0,0,0]),('slider','slider',[-r,.03,.004],[0,-r*omega,0,0,0,0])]:
   n=ET.SubElement(root,'Node',name=label);ET.SubElement(n,'MechanicalObject',name='frames',template='Rigid3d',position=flat([[*centre,0,0,0,1]]),velocity=flat([velocity]));ET.SubElement(n,'UniformMass',template='Rigid3d',vertexMass=flat([[mass[component],mass[component]/rho,*(tensor[component]/mass[component]).ravel()]]));ET.SubElement(n,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(folder/f'{label}.csv'))
   if label=='lever':ET.SubElement(n,'PartialFixedProjectiveConstraint',template='Rigid3d',indices='0',fixedDirections='1 1 1 1 1 0')
   if label=='slider':ET.SubElement(n,'PartialFixedProjectiveConstraint',template='Rigid3d',indices='0',fixedDirections='1 0 1 1 1 1');ET.SubElement(n,'ConstantForceField',template='Rigid3d',indices='0',forces=flat([[0,-load,0,0,0,0]]))
   ends=ET.SubElement(n,'Node',name='ends');points={'lever':[[r,0,-.0015],[-r,0,.002]],'rod':[[-r,0,.002],[-r,.03,.002]],'slider':[[-r,.03,.002]]}[label];ET.SubElement(ends,'MechanicalObject',template='Vec3d',name='points',position=flat(points));ET.SubElement(ends,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords='1',rigidIndexPerPoint=' '.join('0' for _ in points),mapMatrices='1');ET.SubElement(ends,'NativePointJournal',body='@points',filename=str(folder/f'{label}_ends.csv'))
   if label=='lever':ET.SubElement(ends,'CableConstraint',template='Vec3d',name='actuator',indices='0',pullPoint=flat([r,-.02,-.0015]),valueType='force',value=str(T*dt),minForce='0')
  ET.SubElement(root,'BilateralLagrangianConstraint',name='joint0',template='Vec3d',object1='@lever/ends/points',object2='@rod/ends/points',first_point='1',second_point='0');ET.SubElement(root,'BilateralLagrangianConstraint',name='joint1',template='Vec3d',object1='@rod/ends/points',object2='@slider/ends/points',first_point='1',second_point='0');ET.SubElement(root,'NativeConstraintJournal',solver='@constraints',filename=str(folder/'constraints.csv'));ET.SubElement(root,'NativeCablePhase',body='@rod/ends/points',rigidBody='@rod/frames',solver='@constraints',cable='@joint0',filename=str(folder/'joint_phases.csv'))
  ET.ElementTree(root).write(folder/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));ok=process['exit_code']==0 and '[ERROR]'not in logs;measure={}
  if ok:
   q={k:read(folder/f'{k}_ends.csv') for k in ('lever','rod','slider')};body={k:read(folder/f'{k}.csv') for k in ('lever','rod','slider')};assert all(len(rows)==steps for rows in q.values());closure=[]
   for k in range(steps):
    l,rd,s=(np.fromstring(q[n][k]['q'],sep=' ').reshape(-1,3) for n in ('lever','rod','slider'));closure.append(float(max(abs(l[1]-rd[0]).max(),abs(rd[1]-s[0]).max())))
   first_w=np.fromstring(body['lever'][0]['rigid_v'],sep=' ')[5];error=abs(first_w-(omega+dt*expected_accel));measure=dict(initial_frozen_generalized_mass_kg_m2=effective,initial_reference_acceleration_rad_s2=expected_accel,first_omega_actual_rad_s=float(first_w),first_omega_reference_rad_s=float(omega+dt*expected_accel),first_angular_velocity_reference_error=error,joint_closure_maximum_m=max(closure),joint_closure_by_step_m=closure,first_joint_closure_fail_step=next((k for k,x in enumerate(closure) if x>1e-12),None),last_output_stroke_m=float(np.fromstring(q['slider'][-1]['q'],sep=' ')[1]-.03),initial_mass_response_gate=bool(error<=1e-12),finite_joint_closure_gate=bool(max(closure)<=1e-12));ok=error<=1e-12 and max(closure)<=1e-12
  records.append(dict(case=name,status='PASS_IDEAL_LINK_COUPON_SCOPE' if ok else 'FAIL_NATIVE_LINK_RESPONSE_OR_CLOSURE',process=process,measurements=measure,scene_sha256=sha(folder/'scene.scn'),errors=[line for line in logs.splitlines() if '[ERROR]'in line]))
 d=dict(status='PASS_NATIVE_IDEAL_OUTPUT_LINK_ONLY' if all(x['status']=='PASS_IDEAL_LINK_COUPON_SCOPE' for x in records) else 'FAIL_NATIVE_IDEAL_OUTPUT_LINK',records=records,body_mass_kg=mass,body_inertia_kg_m2={k:v.tolist() for k,v in tensor.items()},source_sha256=sha(Path(__file__)),geometry_sha256=sha(src/'summary.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256={str(f):sha(f) for f in (binary,probe,Path('/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'))},scope='Only three finite rotor/rod/slider bodies at assumedrho1000; ideal massless pins and Bilateral point joints, physical pin mass/reaction/retention NOT qualified. Not the full seven-part dynamic assembly. Initial reduced1DOF reference at theta0 has Mprime0; does not validate general convective dynamics. Joint closure1e-12 unchanged, no projected q/v repair. No Finger, FEM, contact, finite wire, time/mesh or grasp qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
