"""Open parallel-crank guide alternative to an obstructing closed sleeve.
Stock geared articulation indices enforce the reduced1DOF kinematics. Actual
motor torque, mapped body masses and independently derived inertia are tested;
no imposed finger/object state and no custom force/ODE/contact solver.
"""
import argparse,copy,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--unique-coordinates',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=ET.parse(BASE/'results/captured_prismatic1746/scene.scn').getroot();root=ET.Element('Node',name='root',dt='.001',gravity='0 0 0')
 for n in source:
  if n.tag in ('RequiredPlugin','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):root.append(copy.deepcopy(n))
 ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad');L=.005;H=.003;m=.001;mc=.001;width=.0008;Izz=m*(L*L+width*width)/12;Ieff=2*(m*L*L/4+Izz)+mc*L*L;torque=1e-5;angles=ET.SubElement(root,'Node',name='angles');ET.SubElement(angles,'MechanicalObject',template='Vec1d',name='theta',position='0');ET.SubElement(angles,'ConstantForceField',template='Vec1d',indices='0',forces=str(torque));mapped=ET.SubElement(angles,'Node',name='mapped');positions=[[0,0,0,0,0,0,1],[L/2,0,0,0,0,0,1],[L,H/2,0,0,0,0,1],[L/2,H,0,0,0,0,1]];flat=lambda x:' '.join(format(float(y),'.17g') for y in np.asarray(x).ravel());ET.SubElement(mapped,'MechanicalObject',template='Rigid3d',name='frames',position=flat(positions));norm=np.diag([(2*width*width)/12,(L*L+width*width)/12,(L*L+width*width)/12]);ET.SubElement(mapped,'UniformMass',template='Rigid3d',name='links',indices='1 3',vertexMass=flat([m,L*width*width,*norm.ravel()]));ET.SubElement(mapped,'UniformMass',template='Rigid3d',name='coupler',indices='2',vertexMass=f'{mc} 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6');ET.SubElement(mapped,'ArticulatedSystemMapping',input1='@../theta',output='@frames');ET.SubElement(mapped,'NativeRigidJournal',body='@frames',solver='@../../constraints',filename=str(out/'body.csv'));ET.SubElement(angles,'ArticulatedHierarchyContainer');centres=ET.SubElement(angles,'Node',name='centres')
 for name,parent,child,pa,pc,axis in [('first',0,1,[0,0,0],[-L/2,0,0],[0,0,1]),('coupler',1,2,[L/2,0,0],[0,-H/2,0],[0,0,-1]),('parallel',0,3,[0,H,0],[-L/2,0,0],[0,0,1])]:
  node=ET.SubElement(centres,'Node',name=name);ET.SubElement(node,'ArticulationCenter',parentIndex=str(parent),childIndex=str(child),posOnParent=flat(pa),posOnChild=flat(pc),articulationProcess='0');arts=ET.SubElement(node,'Node',name='articulations');ET.SubElement(arts,'Articulation',translation='0',rotation='1',rotationAxis=flat(axis),articulationIndex='0')
 # Installed container requires at least one storage slot per centre even when
 # actual articulated indices are shared. Slots1/2 are UNUSED padding only;
 # fixing those removes zero-mass algebraic rows, NOT the driven theta0.
 angles.find('MechanicalObject').set('position','0 0 0');ET.SubElement(angles,'FixedProjectiveConstraint',indices='1 2')
 if a.unique_coordinates:
  # Installed ArticulationAxis/Pos caches are indexed by articulationIndex:
  # reused0 overwrites earlier joints although direct position apply closes.
  # Unique indices plus STOCK SubsetMapping preserve actual1DOF gearing and
  # sum reaction forces/masses; no prescribed active coordinate or SDK edit.
  root.remove(angles);driver=ET.SubElement(root,'Node',name='drive');ET.SubElement(driver,'MechanicalObject',template='Vec1d',name='theta',position='0');force=angles.find('ConstantForceField');angles.remove(force);driver.append(force);driver.append(angles);angles.find('MechanicalObject').set('name','values');angles.remove(angles.find('FixedProjectiveConstraint'));ET.SubElement(angles,'SubsetMapping',template='Vec1d,Vec1d',input='@../theta',output='@values',indices='0 0 0',mapMatrices='1');mapped.find('ArticulatedSystemMapping').set('input1','@../values');mapped.find('NativeRigidJournal').set('solver','@../../../constraints')
  for k,node in enumerate(centres.findall('Node')):node.find("Node[@name='articulations']/Articulation").set('articulationIndex',str(k))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),L_m=L,root_pivot_separation_m=H,link_mass_kg=m,coupler_mass_kg=mc,link_width_m=width,independent_generalized_inertia_kg_m2=Ieff,applied_motor_torque_Nm=torque,unique_articulation_coordinates=a.unique_coordinates,scope='Open parallel-crank kinematic alternative; ideal1:-1 counterrotation via opposite axes. Unique-coordinate mode uses actual stock SubsetMapping to copy ONE torque-driven theta into three UNIQUE articulation indices; shared-index mode is the preserved failed control. NOT a measured gear or pin joint. Original closed sleeve1761 is rejected, not resized. Native torque and actual mapped masses, no prescribed q/v. Fixed-base component coupon ONLY; actual finite joint/guide geometry, real closing force/wire route, moving FEM and nonlinear physical validation are NOT QUALIFIED.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','40','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));valid=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
 if valid:
  rows=list(csv.DictReader((out/'body.csv').open()));q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ').reshape(-1,6) for r in rows]);theta=np.unwrap(2*np.arctan2(q[:,1,5],q[:,1,6]));n=np.arange(1,len(q)+1);expected=torque/Ieff*.001**2*n*(n+1)/2;ae=float(abs(theta-expected).max());ve=float(abs(v[:,1,5]-torque/Ieff*.001*n).max());closure=0.;coupler_angle=0.;coupler_v=0.
  for k in range(len(q)):
   R=Rotation.from_quat(q[k,:,3:]);distal=q[k,3,:3]+R[3].apply([L/2,0,0]);upper=q[k,2,:3]+R[2].apply([0,H/2,0]);closure=max(closure,float(abs(distal-upper).max()));coupler_angle=max(coupler_angle,float(np.linalg.norm(R[2].as_rotvec())));expected_v=np.array([-L*np.sin(theta[k]),L*np.cos(theta[k]),0])*v[k,1,5];coupler_v=max(coupler_v,float(abs(v[k,2,:3]-expected_v).max()))
  finite=bool(np.isfinite(q).all() and np.isfinite(v).all());valid=finite and len(q)==40 and max(ae,ve,closure,coupler_angle,coupler_v)<=1e-12;metrics=dict(finite=finite,maximum_motor_angle_reference_error_rad=ae,maximum_motor_angular_velocity_reference_error_rad_s=ve,maximum_loop_closure_error_m=closure,maximum_coupler_orientation_rad=coupler_angle,maximum_coupler_velocity_kinematic_error_m_s=coupler_v,final_motor_angle_rad=float(theta[-1]))
 d=dict(status='PASS_OPEN_PARALLEL_GUIDE_COMPONENT_ONLY' if valid else 'FAIL_OPEN_PARALLEL_GUIDE_COMPONENT',process=process,measurements=metrics,sofa_error_lines=[x for x in logs.splitlines() if '[ERROR]'in x][:12],preflight_sha256=sha(out/'preflight.json'),scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
