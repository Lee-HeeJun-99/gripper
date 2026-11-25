"""Fixed-root principal-axis bellcrank, Native force/load inversion only."""
import argparse,csv,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat
sys.path.insert(0,str(BASE/'cad'))
from finite_csg64 import register

def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register()
 rotor=trimesh.creation.box([24.,2.,1.]);bore=trimesh.creation.cylinder(radius=.3,height=1.2,sections=32);rotor=trimesh.boolean.difference([rotor,bore],engine='manifold64');pin=trimesh.creation.cylinder(radius=.25,height=2.,sections=32);rotor.apply_scale(.001);pin.apply_scale(.001)
 assert rotor.is_watertight and rotor.volume>0;rotor.export(out/'rotor_m.stl');pin.export(out/'fixed_pin_m.stl')
 rho=1000.;mass=rotor.volume*rho;I=rotor.moment_inertia*rho;assert abs(rotor.center_mass).max()<1e-12 and np.linalg.eigvalsh(I).min()>0
 dt=.001;steps=10;initial_w=-.2;inputT=1e-4;outputF=5e-5;arms=np.array([[.01,0,0],[-.01,0,0]]);pull=np.array([.01,-.02,0])
 journal=BASE/'cad/build_default_control332/libReGripProductSequence.so';probe=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so';compiled=BASE/'results/b3_cable_typed1831';meta=json.loads((compiled/'phase_assessment.json').read_text());assert sha(probe)==meta['binary_sha256'] and sha(BASE/'sofa/native_cable_phase/Observer.cpp')==sha(compiled/'Observer.cpp')
 records=[]
 for name,loaded,observed in [('free_spin',False,False),('loaded_control',True,False),('loaded_observed',True,True)]:
  folder=out/name;folder.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
  for plugin in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer','Mapping.NonLinear','MechanicalLoad'):
   ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
  for plugin in (str(journal),'/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'):
   ET.SubElement(root,'RequiredPlugin',pluginName=plugin)
  if observed:ET.SubElement(root,'RequiredPlugin',pluginName=str(probe))
  ET.SubElement(root,'FreeMotionAnimationLoop');ET.SubElement(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-12',maxIterations='1000',computeConstraintForces='1');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(root,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');ET.SubElement(root,'GenericConstraintCorrection')
  body=ET.SubElement(root,'Node',name='lever');ET.SubElement(body,'MechanicalObject',template='Rigid3d',name='frames',position='0 0 0 0 0 0 1',velocity=flat([[0,0,0,0,0,initial_w]]));ET.SubElement(body,'UniformMass',template='Rigid3d',vertexMass=flat([[mass,rotor.volume,*(I/mass).ravel()]]));ET.SubElement(body,'PartialFixedProjectiveConstraint',template='Rigid3d',indices='0',fixedDirections='1 1 1 1 1 0');ET.SubElement(body,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(folder/'rigid.csv'))
  ports=ET.SubElement(body,'Node',name='ports');ET.SubElement(ports,'MechanicalObject',template='Vec3d',name='points',position=flat(arms));ET.SubElement(ports,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords='1',rigidIndexPerPoint='0 0',mapMatrices='1');ET.SubElement(ports,'CableConstraint',template='Vec3d',name='actuator',indices='0',pullPoint=flat(pull),valueType='force',value=str((inputT if loaded else 0)*dt),minForce='0');ET.SubElement(ports,'ConstantForceField',template='Vec3d',indices='1',forces=flat([[0,-outputF if loaded else 0,0]]));ET.SubElement(ports,'NativePointJournal',body='@points',filename=str(folder/'ports.csv'));ET.SubElement(root,'NativeConstraintJournal',solver='@constraints',filename=str(folder/'constraints.csv'))
  if observed:ET.SubElement(root,'NativeCablePhase',body='@lever/ports/points',rigidBody='@lever/frames',solver='@constraints',cable='@lever/ports/actuator',filename=str(folder/'phases.csv'))
  ET.ElementTree(root).write(folder/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));ok=process['exit_code']==0 and '[ERROR]'not in logs;metrics=[]
  if ok:
   rows=read(folder/'rigid.csv');points=read(folder/'ports.csv');constraints=read(folder/'constraints.csv');ok=len(rows)==len(points)==len(constraints)==steps;previous_q=np.array([0,0,0,0,0,0,1.]);previous_w=initial_w
   for k,row in enumerate(rows):
    q=np.fromstring(row['rigid_q'],sep=' ');v=np.fromstring(row['rigid_v'],sep=' ');r=Rotation.from_quat(previous_q[3:]).apply(arms);direction=(pull-r[0]);direction/=np.linalg.norm(direction);lam=float(np.fromstring(constraints[k]['impulses_Ns'],sep=' ')[0]);tau_c=np.cross(r[0],lam/dt*direction)[2];tau_l=np.cross(r[1],np.array([0,-outputF if loaded else 0,0]))[2];expected=previous_w+dt*(tau_c+tau_l)/I[2,2];x=np.fromstring(points[k]['q'],sep=' ').reshape(-1,3);pv=np.fromstring(points[k]['v'],sep=' ').reshape(-1,3)
    metrics.append(dict(step=k,angular_velocity_error_rad_s=abs(v[5]-expected),angular_impulse_residual_Nms=abs(I[2,2]*(v[5]-previous_w)-dt*(tau_c+tau_l)),force_impulse_error_Ns=abs(lam-(inputT if loaded else 0)*dt),fixed_component_velocity_error=float(abs(v[:5]).max()),input_torque_Nm=float(tau_c),resisting_output_torque_Nm=float(tau_l),output_displacement_y_m=float(x[1,1]),output_velocity_y_m_s=float(pv[1,1])));previous_q=q;previous_w=v[5]
   ok=ok and all(max(m['angular_velocity_error_rad_s'],m['angular_impulse_residual_Nms'],m['force_impulse_error_Ns'],m['fixed_component_velocity_error'])<=1e-12 for m in metrics)
  records.append(dict(case=name,status='PASS_FIXED_AXIS_PORT_SCOPE' if ok else 'FAIL_FIXED_AXIS_PORT',process=process,metrics=metrics,scene_sha256=sha(folder/'scene.scn'),errors=[s for s in logs.splitlines() if '[ERROR]'in s]))
 purity=None
 if all(r['status']=='PASS_FIXED_AXIS_PORT_SCOPE' for r in records):
  purity=max(float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()) for x,y in zip(read(out/'loaded_control/rigid.csv'),read(out/'loaded_observed/rigid.csv')) for k in ('rigid_q','rigid_v'))
 result=dict(status='PASS_FIXED_ROOT_BELLCRANK_PORT_ONLY' if purity==0 else 'FAIL_BELLCRANK_PORT',records=records,observer_purity_q_v=purity,rotor_volume_m3=float(rotor.volume),rotor_assumed_mass_kg=float(mass),rotor_inertia_kg_m2=I.tolist(),configuration=dict(density_assumption_kg_m3=rho,dt_s=dt,steps=steps,initial_omega_rad_s=initial_w,cable_tension_N=inputT,output_dead_load_N=outputF,wire_radius_requirement_m=.00025,ideal_joint='NativePartialFixed root at COM/principal z; reaction NOT MEASURED'),source_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256={str(f):sha(f) for f in (journal,probe,Path('/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'))},scope='New root force-inversion mechanism coupon. Constant fixed-axis inertia avoids only this coupon convective term; not a fix of1806moving-root dynamics. Finite rotor/bore/pin meshes, ideal projective pivot, no bearing contact. Output resisting dead-load port is NOT an assembled compression rod or actual Finger drive. No finite wire/sliding, FEM/contact/grasp/strength/mesh/time/hardware qualification. No physics solver or SDK changed.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'observer_compiled_source.cpp').write_bytes((compiled/'Observer.cpp').read_bytes());print(json.dumps({**result,'records':[{k:v for k,v in r.items() if k!='metrics'} for r in records]},indent=2))
if __name__=='__main__':main()
