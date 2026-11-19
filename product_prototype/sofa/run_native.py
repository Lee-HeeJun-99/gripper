"""Native SOFA FEM/CableConstraint trial,all outputs unique;NO custom solver."""
import argparse,csv,json,math,subprocess,sys,hashlib,shutil
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(BASE/'cad'))
from film_guarded_process import guarded
from generate import world,width
SDK=Path('/home/ubuntu/SOFA/v26.06.00')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(n,tag,**kw):return ET.SubElement(n,tag,{k:str(v) for k,v in kw.items()})
def flat(x):return ' '.join(format(float(a),'.17g') for row in x for a in row)
def main():
 extra=argparse.ArgumentParser(add_help=False);extra.add_argument('--guide-normal-mm',type=float);extra.add_argument('--cable-audit',action='store_true');extra.add_argument('--split-contact-surfaces',action='store_true');variant,remaining=extra.parse_known_args();sys.argv=[sys.argv[0],*remaining]
 if variant.guide_normal_mm is not None and not -6<=variant.guide_normal_mm<=6:raise ValueError('bounded physical guide offset study')
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fingers',type=int,choices=(1,3),default=1);p.add_argument('--steps',type=int);p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);p.add_argument('--object',choices=('none','fixed','free'),default='none');p.add_argument('--radius',type=float,choices=(20,30),default=30);p.add_argument('--stroke',type=float,default=5);p.add_argument('--reuse-build');p.add_argument('--gravity',action='store_true');p.add_argument('--floor',action='store_true');p.add_argument('--outboard',type=float,choices=(4.,10.,14.),default=4.);p.add_argument('--intersection',choices=('MinProximityIntersection','LocalMinDistance'),default='MinProximityIntersection');p.add_argument('--lift',action='store_true');p.add_argument('--center-z',type=float,choices=(-65.,-75.,-80.),default=-65.);p.add_argument('--shape',choices=('sphere','cylinder','box'),default='sphere');p.add_argument('--support-gap',type=float,choices=(0.,.4),default=0.);p.add_argument('--support-radius',type=float,choices=(5.,35.),default=5.);p.add_argument('--slow-cycle',action='store_true');p.add_argument('--support-shape',choices=('mesh','sphere'),default='mesh');p.add_argument('--dense-guides',action='store_true');p.add_argument('--withdraw-support',action='store_true');p.add_argument('--constraint-solver',choices=('BlockGaussSeidelConstraintSolver','GenericConstraintSolver'),default='BlockGaussSeidelConstraintSolver')
 p.add_argument('--guide-location',choices=('outboard','surface','rail-back'),default='outboard');p.add_argument('--rail-back-offset',type=float,default=.5);p.add_argument('--root-angle',type=float,choices=(0,10,12,14,15),default=0);p.add_argument('--cables',type=int,choices=(1,2),default=2);p.add_argument('--constraint-journal',action='store_true');p.add_argument('--rigid-guides',action='store_true');p.add_argument('--nncg',action='store_true');p.add_argument('--global-native-ode',action='store_true');p.add_argument('--mapped-guide-joints',action='store_true');p.add_argument('--object-depth',type=float,choices=(50.,65.,75.,80.));p.add_argument('--object-mass',type=float,choices=(.02,.05,.1),default=.1);p.add_argument('--component-film-damping',action='store_true');p.add_argument('--smooth-support',action='store_true');p.add_argument('--end-clock-motion',action='store_true');p.add_argument('--guide-bridges',action='store_true');a=p.parse_args()
 if a.guide_bridges and not a.mapped_guide_joints:raise ValueError('cross-bridge study requires disjoint mapped guide attachments')
 if a.guide_bridges and (a.steps is None or a.steps>4):raise ValueError('Cross-bridge DiagonalMass scene137/138 currently fails initialization;only bounded4-step API diagnostics allowed,NOT grasp trials')
 if a.lift and a.mapped_guide_joints:raise ValueError('BLOCKED:mapped-root lift must drive the free subset fixture,not the mapped full FEM;qualify this path and holding/time gates first')
 if a.lift and not(a.gravity and a.object=='free'):raise ValueError('Lift experiments require explicit gravity and a free object')
 if a.end_clock_motion and not(a.withdraw_support or a.lift):raise ValueError('explicit moving native fixture/root required')
 if a.smooth_support and not a.withdraw_support:raise ValueError('smooth support is an explicit withdrawal input variant')
 if a.component_film_damping and not a.global_native_ode:raise ValueError('explicit global zero-Rayleigh solver required to avoid double counting')
 if a.object_depth is not None:a.center_z=-a.object_depth
 if a.mapped_guide_joints and not(a.rigid_guides and a.global_native_ode):raise ValueError('mapped rigidification requires explicit rigid-guides and global-native-ode')
 if a.nncg:a.constraint_solver='NNCGConstraintSolver'
 if a.lift and a.slow_cycle:raise ValueError('separate explicit lift and slow profiles;do not mix timings')
 if a.constraint_solver=='GenericConstraintSolver':raise ValueError('Installed v26.06 factory removed GenericConstraintSolver;045 preserves actual rejection. Use BlockGaussSeidelConstraintSolver.')
 if a.withdraw_support and (a.slow_cycle or not a.floor or a.support_shape!='sphere'):raise ValueError('explicit rounded support/ordinary cycle required for withdrawal')
 if a.steps is None:a.steps=round((4 if a.slow_cycle else 3 if a.lift or a.withdraw_support else 2)/a.dt)
 if not 0<a.steps<=4000 or not 0<=a.stroke<=10:raise ValueError('bounded exploratory prototype only')
 out=BASE/'results'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copy2(__file__,out/'runner.py');meshdir=BASE/'meshes/product_v1b';c=json.loads((meshdir/'config.json').read_text());m=json.loads((meshdir/'mesh.json').read_text());c['tendon']['outboard']=a.outboard;c['tendon']['maximum_stroke']=a.stroke;c['simulation']['dt_s']=a.dt;c['simulation']['sphere_radius_mm']=a.radius;c['simulation']['closing_end_s']=1 if a.slow_cycle else .5;c['simulation']['hold_end_s']=2 if a.slow_cycle or a.lift or a.withdraw_support else 1;c['simulation']['release_end_s']=3 if a.slow_cycle else 2.5 if a.lift or a.withdraw_support else 1.5;c['simulation']['sphere_center_mm'][2]=a.center_z;c['tendon']['guide_stations']=[10,20,30,40,50,60,70,80,90,98] if a.dense_guides else c['tendon']['guide_stations'];(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_text(json.dumps(m));source=out/'source';shutil.copytree(BASE/'sofa',source,ignore=shutil.ignore_patterns('__pycache__'))
 c['palm']['root_angle_deg']=a.root_angle;c['simulation']['sphere_mass_kg']=a.object_mass
 if a.guide_location=='surface':c['tendon'].update(outboard=-1,normal_offset=c['finger']['skin_thickness']);(out/'config.json').write_text(json.dumps(c,indent=2))
 if a.guide_location=='rail-back':
  if not .5<=a.rail_back_offset<=3:raise ValueError('explicit bounded rail-back guide offset')
  c['tendon'].update(outboard=-1,normal_offset=-a.rail_back_offset);(out/'config.json').write_text(json.dumps(c,indent=2))
 if variant.guide_normal_mm is not None:c['tendon']['normal_offset']=variant.guide_normal_mm
 c['study']=dict(guide_normal_override_mm=variant.guide_normal_mm,cable_audit=variant.cable_audit,skin_load_bearing_minimum_fraction=.8,qualification='Skin-only rows required;whole FEM surface is NOT Skin-only;no qualification from surface_mask alone')
 (out/'config.json').write_text(json.dumps(c,indent=2))
 r=dict(status='FAIL',scope='experimental native SOFA product prototype;NOT numerical/material/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={f.name:sha(f) for f in source.iterdir() if f.is_file()},config_sha256=sha(out/'config.json'),mesh_sha256=sha(meshdir/'mesh.json'),sdk=str(SDK),runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),fingers=a.fingers,object=a.object,steps=a.steps,dt_s=c['simulation']['dt_s'],stroke_mm=a.stroke,units='SI',contact_force=None,root_reaction=None,lift='NOT RUN',cables_per_finger=a.cables,guide_location=a.guide_location)
 build=BASE/'cad'/('build_'+a.tag) if not a.reuse_build else BASE/'cad'/('build_'+a.reuse_build)
 if a.reuse_build:
  old=json.loads((BASE/'results'/a.reuse_build/'summary.json').read_text());build=ROOT/old['build'];binary=build/'libReGripProductSequence.so'
  if any(old['source_hashes'][k]!=r['source_hashes'][k] for k in ('Controller.cpp','CMakeLists.txt')) or sha(binary)!=old['binary_sha256']:raise ValueError('exact compiled controller source/binary required;Python runners have separate snapshots')
 else:
  r['configure']=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
  if r['configure']['exit_code']!=0:(out/'summary.json').write_text(json.dumps(r,indent=2));return
  r['compile']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180)
  if r['compile']['exit_code']!=0:(out/'summary.json').write_text(json.dumps(r,indent=2));return
 binary=build/'libReGripProductSequence.so';r['binary_sha256']=sha(binary);r['build']=str(build.relative_to(ROOT));(out/'ldd.txt').write_text(subprocess.check_output(['ldd',binary],text=True));s=c['simulation'];dt=a.dt;r.update(dt_s=dt,gravity_m_s2=[0,0,-9.81] if a.gravity else [0,0,0],floor=a.floor,frame='proper right-handed;longitudinal down,width minus-tangent,normal inward');root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 -9.81' if a.gravity else '0 0 0')
 plugins=['AnimationLoop','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant','Mapping.Linear','Mapping.NonLinear','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact']
 for plugin in plugins:add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 add(root,'RequiredPlugin',pluginName=str(SDK/'plugins/SoftRobots/lib/libSoftRobots.so'));add(root,'RequiredPlugin',pluginName=str(binary));add(root,'FreeMotionAnimationLoop');add(root,a.constraint_solver,name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=1)
 if a.object!='none':
  add(root,'CollisionPipeline',depth=6);add(root,'BruteForceBroadPhase');add(root,'BVHNarrowPhase');add(root,a.intersection,alarmDistance=s['alarm_distance_mm']*.001,contactDistance=s['contact_distance_mm']*.001,**({'useSphereTriangle':1} if a.intersection=='MinProximityIntersection' else {}));add(root,'CollisionResponse',response='FrictionContactConstraint',responseParams='mu='+str(s['friction']))
 for f in range(a.fingers):
  angle=c['palm']['angles_deg'][f];points=np.array([world(c,x,angle) for x in m['local_positions_mm']])*.001;node=add(root,'Node',name='finger'+str(f));add(node,'EulerImplicitSolver',rayleighMass=s['rayleigh_mass_per_s'],rayleighStiffness=s['rayleigh_stiffness_s']);add(node,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixMat3x3d');add(node,'MeshTopology',name='topology',position=flat(points),tetrahedra=flat(m['tetrahedra']),triangles=flat(m['triangles']));add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(points));add(node,'UniformMass',totalMass=s['mass_per_finger_kg']);add(node,'TetrahedronFEMForceField',name='nativeFEM',method='large',youngModulus=s['young_modulus_Pa'],poissonRatio=s['poisson_ratio']);fixed=[i for i,p in enumerate(m['local_positions_mm']) if p[0]<=c['finger']['clamp_length']];add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,fixed)));add(node,'GenericConstraintCorrection',solverName='linear')
  for j,side in enumerate((-1,1)[:a.cables]):
   cable=add(node,'Node',name='cable'+str(j));local=[[x,side*(width(c,x)/2+c['tendon']['outboard']),c['tendon']['normal_offset']] for x in c['tendon']['guide_stations']];route=[np.array(world(c,x,angle))*.001 for x in local];pull=np.array(world(c,[0,side*(width(c,0)/2+c['tendon']['outboard']),c['tendon']['normal_offset']],angle))*.001;add(cable,'MechanicalObject',name='points',template='Vec3d',position=flat(route));add(cable,'CableConstraint',name='actuator',indices=' '.join(map(str,range(len(route)))),pullPoint=flat([pull]),value=0,valueType='displacement',minForce=0);add(cable,'BarycentricMapping',input='@../dofs',output='@points')
  add(node,'NativeCableSequence',body='@dofs',cable0='@cable0/actuator',cable1='@cable1/actuator' if a.cables==2 else '@cable0/actuator',filename=str(out/('finger'+str(f)+'.csv')),stroke=a.stroke*.001)
  if a.object!='none':
   surface=add(node,'Node',name='collision');add(surface,'MeshTopology',name='surfaceTopology',position=flat(points),triangles=flat(m['triangles']));add(surface,'MechanicalObject',name='surface',template='Vec3d',position=flat(points));add(surface,'TriangleCollisionModel',group=f+1);add(surface,'LineCollisionModel',group=f+1);add(surface,'PointCollisionModel',group=f+1);add(surface,'IdentityMapping',input='@../dofs',output='@surface')
 if a.object!='none':
  body=add(root,'Node',name='object');center=s['sphere_center_mm'];add(body,'EulerImplicitSolver');add(body,'SparseLDLSolver',name='linear');add(body,'MechanicalObject',name='rigid',template='Rigid3d',position=flat([[x*.001 for x in center]+[0,0,0,1]]));R=a.radius*.001;I=.4*R*R;add(body,'UniformMass',template='Rigid3d',vertexMass=f'{s["sphere_mass_kg"]} {4*math.pi*R**3/3} {I} 0 0 0 {I} 0 0 0 {I}');add(body,'GenericConstraintCorrection',solverName='linear')
  if a.object=='fixed':add(body,'FixedProjectiveConstraint',indices=0)
  coll=add(body,'Node',name='collision')
  if a.shape=='sphere':
   add(coll,'MechanicalObject',template='Vec3d',name='center',position='0 0 0');add(coll,'SphereCollisionModel',radius=R,group=10);add(coll,'RigidMapping',input='@../rigid',output='@center',globalToLocalCoords=0,initialPoints='0 0 0');add(body,'NativeRigidJournal',body='@rigid',solver='@../constraints',center='@collision/center',filename=str(out/'object.csv'))
  else:
   import trimesh
   primitive=trimesh.creation.cylinder(radius=R,height=2*R,sections=24) if a.shape=='cylinder' else trimesh.creation.box(extents=[2*R]*3)
   add(coll,'MeshTopology',position=flat(primitive.vertices),triangles=flat(primitive.faces));add(coll,'MechanicalObject',template='Vec3d',name='surface',position=flat(primitive.vertices));add(coll,'TriangleCollisionModel',group=10);add(coll,'LineCollisionModel',group=10);add(coll,'PointCollisionModel',group=10);add(coll,'RigidMapping',input='@../rigid',output='@surface',globalToLocalCoords=0,initialPoints=flat(primitive.vertices));add(body,'NativeRigidJournal',body='@rigid',solver='@../constraints',filename=str(out/'object.csv'))
   inertia=[(3*R*R+4*R*R)/12]*2+[R*R/2] if a.shape=='cylinder' else [2*R*R/3]*3
   volume=math.pi*R*R*(2*R) if a.shape=='cylinder' else (2*R)**3
   body.find('UniformMass').set('vertexMass',f'{s["sphere_mass_kg"]} {volume} {inertia[0]} 0 0 0 {inertia[1]} 0 0 0 {inertia[2]}')
  r.update(object_shape=a.shape,object_radius_or_halfwidth_mm=a.radius,object_inertia_assumption='solid homogeneous primitive;normalized inertia supplied to RigidMass,not measured')
  if a.floor:
   z=center[2]*.001-R-a.support_gap*.001;r['initial_support_gap_mm']=a.support_gap;r['support_radius_mm']=a.support_radius;floor=add(root,'Node',name='floor')
   if a.support_radius==5:corners=[[-.005,-.005,z],[.005,-.005,z],[.005,.005,z],[-.005,.005,z]];faces=[[0,1,2],[0,2,3]]
   else:
    corners=[[0,0,z]]+[[.035*math.cos(2*math.pi*k/32),.035*math.sin(2*math.pi*k/32),z] for k in range(32)];faces=[[0,k+1,(k+1)%32+1] for k in range(32)]
   add(floor,'MeshTopology',position=flat(corners),triangles=flat(faces));add(floor,'MechanicalObject',template='Vec3d',position=flat(corners));add(floor,'TriangleCollisionModel',simulated=0,moving=0,group=20);add(floor,'LineCollisionModel',simulated=0,moving=0,group=20);add(floor,'PointCollisionModel',simulated=0,moving=0,group=20)
 if a.lift:
  for node in root.findall("./Node"):
   fixed=node.find('FixedProjectiveConstraint')
   if node.get('name','').startswith('finger') and fixed is not None:
    indices=fixed.get('indices');node.remove(fixed);add(node,'LinearMovementProjectiveConstraint',indices=indices,keyTimes='0 1 1.5 3',movements='0 0 0 0 0 0 0 0 .02 0 0 .02')
    control=node.find('NativeCableSequence');control.set('hold','2');control.set('release','2.5');control.set('liftHeight','.02')
  r['lift']='EXPERIMENTAL ATTEMPT:palm/root and cable origins +20mm,1-1.5s;object free,gravity included if requested'
 if a.floor and a.support_shape=='sphere':
  oldfloor=root.find("./Node[@name='floor']");root.remove(oldfloor);floor=add(root,'Node',name='floor');z=s['sphere_center_mm'][2]*.001-a.radius*.001-a.support_gap*.001-.035;add(floor,'MechanicalObject',template='Vec3d',position=f'0 0 {z}');add(floor,'SphereCollisionModel',radius=.035,simulated=0,moving=0,group=20);r['support_shape']='fixed R35 rounded pedestal;NEW physical fixture,NOT flat-table repair'
 for corr in root.iter('GenericConstraintCorrection'):corr.attrib.pop('solverName',None)
 if variant.split_contact_surfaces and a.object!='none':
  local=np.array(m['local_positions_mm']);tri=np.array(m['triangles']);rail=np.any(local[tri,2]<0,axis=1)
  c['surface_partition']=dict(rule='Skin:all reference vertices z>=0;Rail:any z<0;native generated exterior faces',skin_triangles=int((~rail).sum()),rail_triangles=int(rail.sum()),contact_area=None,pressure=None)
  for f in range(a.fingers):
   node=root.find(f"./Node[@name='finger{f}']");old=node.find("./Node[@name='collision']");points=old.find('MechanicalObject').get('position');node.remove(old)
   for label,selection in (('skin',~rail),('rail',rail)):
    faces=tri[selection];ids=sorted(set(faces.reshape(-1).tolist()));lookup={v:k for k,v in enumerate(ids)};compact=np.array([[lookup[int(v)] for v in face] for face in faces]);positions=flat(np.fromstring(points,sep=' ').reshape(-1,3)[ids]);edges=sorted({tuple(sorted((int(t[k]),int(t[(k+1)%3])))) for t in compact for k in range(3)});surface=add(node,'Node',name=label+'Collision');add(surface,'MeshTopology',name='surfaceTopology',position=positions,triangles=flat(compact),edges=flat(edges));add(surface,'MechanicalObject',name='surface',template='Vec3d',position=positions);add(surface,'TriangleCollisionModel',group=f+1);add(surface,'LineCollisionModel',group=f+1);add(surface,'PointCollisionModel',group=f+1);add(surface,'SubsetMapping',input='@../dofs',output='@surface',indices=' '.join(map(str,ids)))
  if a.object=='free' and a.constraint_journal:
   for label in ('skin','rail'):add(root,'NativeContactRows',solver='@constraints',body='@object/rigid',filename=str(out/f'{label}_rows.csv'),**{'film'+str(f):f'@finger{f}/{label}Collision/surface' for f in range(a.fingers)})
  (out/'config.json').write_text(json.dumps(c,indent=2));r['config_sha256']=sha(out/'config.json')
 if a.withdraw_support:
  floor=root.find("./Node[@name='floor']");floor.find('MechanicalObject').set('name','support');floor.find('SphereCollisionModel').set('moving','1');add(floor,'EulerImplicitSolver');add(floor,'SparseLDLSolver');add(floor,'UniformMass',totalMass=1);add(floor,'LinearMovementProjectiveConstraint',indices=0,keyTimes='0 1 1.5 3',movements='0 0 0 0 0 0 0 0 -.04 0 0 -.04');add(floor,'NativePointJournal',body='@support',filename=str(out/'support.csv'))
  for node in root.iter('NativeCableSequence'):node.set('hold','2');node.set('release','2.5')
  r['support_withdrawal']='native kinematic support down40mm1-1.5s;object/finger shapes NOT prescribed;fixture work NOT measured'
  if a.smooth_support:
   knots=np.r_[0.,np.linspace(1.,1.5,101),3.];u=np.clip((knots-1)/.5,0,1);distance=-.04*u**3*(10+u*(-15+6*u));movement=floor.find('LinearMovementProjectiveConstraint');movement.set('keyTimes',' '.join(format(x,'.17g') for x in knots));movement.set('movements',flat([[0,0,z] for z in distance]));r['support_withdrawal']='fixed101-knot piecewise-linear approximation to quintic40mm withdrawal1-1.5s;NOT exact C2;different physical input,not old-model gate repair'
 if a.slow_cycle:
  for node in root.iter('NativeCableSequence'):node.set('closing','1');node.set('hold','2');node.set('release','3')
  r['control_profile']='C2 closing0-1/hold1-2/release2-3/recovery3-4s;changed physical input,not a numerical fix'
 if a.constraint_journal:
  add(root,'NativeConstraintJournal',solver='@constraints',filename=str(out/'constraints.csv'))
  if a.object=='free':add(root,'NativeContactRows',solver='@constraints',body='@object/rigid',filename=str(out/'contact_rows.csv'),**{'film'+str(f):'@finger'+str(f)+'/dofs' for f in range(a.fingers)})
 if a.rigid_guides:
  if a.cables!=2:raise ValueError('explicit rigid bracket prototype currently requires two cables')
  from rigid_guides import install
  r['rigid_guides']=[install(root,root.find(f"./Node[@name='finger{f}']"),c,m,c['palm']['angles_deg'][f],f,add,out,mapped=a.mapped_guide_joints,bridges=a.guide_bridges) for f in range(a.fingers)]
  c['guide_mechanics']=r['rigid_guides'];(out/'config.json').write_text(json.dumps(c,indent=2));r['config_sha256']=sha(out/'config.json')
  observer=root.find('NativeContactRows')
  if observer is not None:
   for f in range(a.fingers):observer.set('guide'+str(f),'@guides'+str(f)+'/frames')
 if a.withdraw_support:
  protocol=dict(scope='experimental native holding,NOT whole physical certification',mass_kg=s['sphere_mass_kg'],radius_mm=a.radius,gravity_m_s2=[0,0,-9.81] if a.gravity else [0,0,0],window_s=[1.6,2.0],reference_s=1.,max_vertical_slip_mm=2.,max_speed_mm_s=5.,minimum_support_surface_gap_mm=5.,maximum_support_resultant_N=1e-5,friction_assumed=s['friction'],contact_rows_required=True)
  (out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));r['holding_protocol_sha256']=sha(out/'holding_protocol.json')
 if variant.cable_audit:
  for f in range(a.fingers):
   for j in range(a.cables):add(root,'NativeCableAudit',body=f'@finger{f}/dofs',cable=f'@guides{f}/cable{j}/actuator' if a.rigid_guides else f'@finger{f}/cable{j}/actuator',filename=str(out/f'cable_audit_{f}_{j}.csv'))
 if a.global_native_ode:
  for node in root.iter('Node'):
   for child in list(node):
    if child.tag in ('EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):node.remove(child)
  add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0);add(root,'SparseLDLSolver',name='globalLinear',template='CompressedRowSparseMatrixd');add(root,'GenericConstraintCorrection');r['global_native_ode']='one stock EulerImplicit/SparseLDL scalar mixed system;Rayleigh=0 explicitly CHANGED physical damping,not old-model gate repair'
 if a.component_film_damping:
  for node in root.findall("./Node"):
   if node.get('name','').startswith('finger'):
    node.find('UniformMass').set('rayleighMass',str(s['rayleigh_mass_per_s']));node.find('TetrahedronFEMForceField').set('rayleighStiffness',str(s['rayleigh_stiffness_s']))
  r['component_film_damping']=dict(mass_per_s=s['rayleigh_mass_per_s'],stiffness_s=s['rayleigh_stiffness_s'],scope='explicit original Film coefficient assumptions via native Mass/ForceField;object and hardware undamped;NOT measured material or old-model convergence repair')
 if a.end_clock_motion:
  commands=[]
  for node in root.iter('Node'):
   for movement in node.findall('LinearMovementProjectiveConstraint'):
    times=np.fromstring(movement.get('keyTimes'),sep=' ');commands.append(dict(node=node.get('name'),keyTimes_s=times.tolist(),movements_m=np.fromstring(movement.get('movements'),sep=' ').reshape(-1,3).tolist()));movement.set('keyTimes',' '.join(format(x-dt,'.17g') for x in times))
  (out/'motion_commands.json').write_text(json.dumps(dict(clock='declared accepted-end physical time;native component evaluates begin clock,serialized keyTimes shifted by-dt',commands=commands),indent=2));r['motion_commands_sha256']=sha(out/'motion_commands.json');r['native_motion_clock']='end-clock-via-keyshift;NEW explicit command interpretation,not rewriting historical begin-clock trials'
 shutil.copy2(BASE/'cad/generate.py',out/'geometry_generator.py');r['geometry_generator_sha256']=sha(out/'geometry_generator.py')
 for f in range(a.fingers):
  points=np.array([world(c,x,c['palm']['angles_deg'][f]) for x in m['local_positions_mm']])*.001
  if min(np.linalg.det((points[np.array(tet)[1:]]-points[tet[0]]).T) for tet in m['tetrahedra'])<=0:raise ValueError('world tetra orientation must be positive')
  if a.object!='none' and a.shape=='sphere':
   import trimesh
   centre=np.array(s['sphere_center_mm'])*.001;tri=np.array(m['triangles']);closest=trimesh.triangles.closest_point(points[tri],np.repeat(centre[None,:],len(tri),axis=0));gap=float(np.linalg.norm(closest-centre,axis=1).min()-a.radius*.001);r.setdefault('initial_surface_gap_mm',[]).append(gap*1000)
   if gap<0:
    r.update(status='REJECTED_INITIAL_PENETRATION',process=None);(out/'summary.json').write_text(json.dumps(r,indent=2));raise ValueError('initial penetration:reject before physics run')
 ET.ElementTree(root).write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');r['process']=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',a.steps,'--hideProgressBar',out/'scene.scn'],out/'process',480)
 r['sofa_errors']=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'))
 if r['process']['exit_code']==0 and not r['sofa_errors']:
  metrics=[]
  for f in range(a.fingers):
   rows=list(csv.DictReader((out/('finger'+str(f)+'.csv')).open()));q=np.array([np.fromstring(x['q_m'],sep=' ') for x in rows]).reshape(-1,len(m['local_positions_mm']),3);rest=np.array([world(c,x,c['palm']['angles_deg'][f]) for x in m['local_positions_mm']])*.001;tip=np.array([i for i,p in enumerate(m['local_positions_mm']) if p[0]==100]);motion=np.linalg.norm(q[:,tip].mean(axis=1)-rest[tip].mean(axis=0),axis=1);metrics.append(dict(rows=len(rows),peak_tip_displacement_m=float(motion.max()),final_tip_displacement_m=float(motion[-1]),finite=bool(np.isfinite(q).all()),last_time_s=float(rows[-1]['time_s']),max_cable_raw_force=max(float(x[k]) for x in rows for k in ('cable0_force_raw','cable1_force_raw'))))
  r.update(status='RUN_COMPLETED_NOT_QUALIFIED' if all(x['rows']==a.steps and x['finite'] for x in metrics) else 'FAIL',metrics=metrics)
 r['raw_hashes']={p.name:sha(p) for p in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes')}))
if __name__=='__main__':main()
