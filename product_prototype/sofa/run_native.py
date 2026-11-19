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
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fingers',type=int,choices=(1,3),default=1);p.add_argument('--steps',type=int);p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);p.add_argument('--object',choices=('none','fixed','free'),default='none');p.add_argument('--radius',type=float,choices=(20,30),default=30);p.add_argument('--stroke',type=float,default=5);p.add_argument('--reuse-build');p.add_argument('--gravity',action='store_true');p.add_argument('--floor',action='store_true');a=p.parse_args()
 if a.steps is None:a.steps=round(2/a.dt)
 if not 0<a.steps<=4000 or not 0<=a.stroke<=10:raise ValueError('bounded exploratory prototype only')
 out=BASE/'results'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copy2(__file__,out/'runner.py');meshdir=BASE/'meshes/product_v1b';c=json.loads((meshdir/'config.json').read_text());m=json.loads((meshdir/'mesh.json').read_text());(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_text(json.dumps(m));source=out/'source';shutil.copytree(BASE/'sofa',source,ignore=shutil.ignore_patterns('__pycache__'))
 r=dict(status='FAIL',scope='experimental native SOFA product prototype;NOT numerical/material/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={f.name:sha(f) for f in source.iterdir() if f.is_file()},config_sha256=sha(meshdir/'config.json'),mesh_sha256=sha(meshdir/'mesh.json'),sdk=str(SDK),runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),fingers=a.fingers,object=a.object,steps=a.steps,dt_s=c['simulation']['dt_s'],stroke_mm=a.stroke,units='SI',contact_force=None,root_reaction=None,lift='NOT RUN')
 build=BASE/'cad'/('build_'+a.tag) if not a.reuse_build else BASE/'cad'/('build_'+a.reuse_build)
 if a.reuse_build:
  old=json.loads((BASE/'results'/a.reuse_build/'summary.json').read_text());binary=build/'libReGripProductSequence.so'
  if old['source_hashes']!=r['source_hashes'] or sha(binary)!=old['binary_sha256']:raise ValueError('exact controller binary required')
 else:
  r['configure']=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
  if r['configure']['exit_code']!=0:(out/'summary.json').write_text(json.dumps(r,indent=2));return
  r['compile']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180)
  if r['compile']['exit_code']!=0:(out/'summary.json').write_text(json.dumps(r,indent=2));return
 binary=build/'libReGripProductSequence.so';r['binary_sha256']=sha(binary);r['build']=str(build.relative_to(ROOT));(out/'ldd.txt').write_text(subprocess.check_output(['ldd',binary],text=True));s=c['simulation'];dt=a.dt;r.update(dt_s=dt,gravity_m_s2=[0,0,-9.81] if a.gravity else [0,0,0],floor=a.floor,frame='proper right-handed;longitudinal down,width minus-tangent,normal inward');root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 -9.81' if a.gravity else '0 0 0')
 plugins=['AnimationLoop','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant','Mapping.Linear','Mapping.NonLinear','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact']
 for plugin in plugins:add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 add(root,'RequiredPlugin',pluginName=str(SDK/'plugins/SoftRobots/lib/libSoftRobots.so'));add(root,'RequiredPlugin',pluginName=str(binary));add(root,'FreeMotionAnimationLoop');add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=1)
 if a.object!='none':
  add(root,'CollisionPipeline',depth=6);add(root,'BruteForceBroadPhase');add(root,'BVHNarrowPhase');add(root,'MinProximityIntersection',alarmDistance=s['alarm_distance_mm']*.001,contactDistance=s['contact_distance_mm']*.001,useSphereTriangle=1);add(root,'CollisionResponse',response='FrictionContactConstraint',responseParams='mu='+str(s['friction']))
 for f in range(a.fingers):
  angle=c['palm']['angles_deg'][f];points=np.array([world(c,x,angle) for x in m['local_positions_mm']])*.001;node=add(root,'Node',name='finger'+str(f));add(node,'EulerImplicitSolver',rayleighMass=s['rayleigh_mass_per_s'],rayleighStiffness=s['rayleigh_stiffness_s']);add(node,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixMat3x3d');add(node,'MeshTopology',name='topology',position=flat(points),tetrahedra=flat(m['tetrahedra']),triangles=flat(m['triangles']));add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(points));add(node,'UniformMass',totalMass=s['mass_per_finger_kg']);add(node,'TetrahedronFEMForceField',name='nativeFEM',method='large',youngModulus=s['young_modulus_Pa'],poissonRatio=s['poisson_ratio']);fixed=[i for i,p in enumerate(m['local_positions_mm']) if p[0]<=c['finger']['clamp_length']];add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,fixed)));add(node,'GenericConstraintCorrection',solverName='linear')
  for j,side in enumerate((-1,1)):
   cable=add(node,'Node',name='cable'+str(j));local=[[x,side*(width(c,x)/2+c['tendon']['outboard']),c['tendon']['normal_offset']] for x in c['tendon']['guide_stations']];route=[np.array(world(c,x,angle))*.001 for x in local];pull=np.array(world(c,[0,side*(width(c,0)/2+c['tendon']['outboard']),c['tendon']['normal_offset']],angle))*.001;add(cable,'MechanicalObject',name='points',template='Vec3d',position=flat(route));add(cable,'CableConstraint',name='actuator',indices=' '.join(map(str,range(len(route)))),pullPoint=flat([pull]),value=0,valueType='displacement',minForce=0);add(cable,'BarycentricMapping',input='@../dofs',output='@points')
  add(node,'NativeCableSequence',body='@dofs',cable0='@cable0/actuator',cable1='@cable1/actuator',filename=str(out/('finger'+str(f)+'.csv')),stroke=a.stroke*.001)
  if a.object!='none':add(node,'TriangleCollisionModel',group=f+1);add(node,'LineCollisionModel',group=f+1);add(node,'PointCollisionModel',group=f+1)
 if a.object!='none':
  body=add(root,'Node',name='object');center=s['sphere_center_mm'];add(body,'EulerImplicitSolver');add(body,'SparseLDLSolver',name='linear');add(body,'MechanicalObject',name='rigid',template='Rigid3d',position=flat([[x*.001 for x in center]+[0,0,0,1]]));R=a.radius*.001;I=.4*R*R;add(body,'UniformMass',template='Rigid3d',vertexMass=f'{s["sphere_mass_kg"]} {4*math.pi*R**3/3} {I} 0 0 0 {I} 0 0 0 {I}');add(body,'GenericConstraintCorrection',solverName='linear')
  if a.object=='fixed':add(body,'FixedProjectiveConstraint',indices=0)
  coll=add(body,'Node',name='collision');add(coll,'MechanicalObject',template='Vec3d',name='center',position='0 0 0');add(coll,'SphereCollisionModel',radius=R,group=10);add(coll,'RigidMapping',input='@../rigid',output='@center',globalToLocalCoords=0,initialPoints='0 0 0');add(body,'NativeRigidJournal',body='@rigid',solver='@../constraints',center='@collision/center',filename=str(out/'object.csv'))
  if a.floor:
   z=center[2]*.001-R;floor=add(root,'Node',name='floor');corners=[[-.005,-.005,z],[.005,-.005,z],[.005,.005,z],[-.005,.005,z]];add(floor,'MeshTopology',position=flat(corners),triangles='0 1 2 0 2 3');add(floor,'MechanicalObject',template='Vec3d',position=flat(corners));add(floor,'TriangleCollisionModel',simulated=0,moving=0,group=20);add(floor,'LineCollisionModel',simulated=0,moving=0,group=20);add(floor,'PointCollisionModel',simulated=0,moving=0,group=20)
 for corr in root.iter('GenericConstraintCorrection'):corr.attrib.pop('solverName',None)
 shutil.copy2(BASE/'cad/generate.py',out/'geometry_generator.py');r['geometry_generator_sha256']=sha(out/'geometry_generator.py')
 for f in range(a.fingers):
  points=np.array([world(c,x,c['palm']['angles_deg'][f]) for x in m['local_positions_mm']])*.001
  if min(np.linalg.det((points[np.array(tet)[1:]]-points[tet[0]]).T) for tet in m['tetrahedra'])<=0:raise ValueError('world tetra orientation must be positive')
 ET.ElementTree(root).write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');r['process']=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',a.steps,'--hideProgressBar',out/'scene.scn'],out/'process',480)
 r['sofa_errors']=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'))
 if r['process']['exit_code']==0 and not r['sofa_errors']:
  metrics=[]
  for f in range(a.fingers):
   rows=list(csv.DictReader((out/('finger'+str(f)+'.csv')).open()));q=np.array([np.fromstring(x['q_m'],sep=' ') for x in rows]).reshape(-1,len(m['local_positions_mm']),3);rest=np.array([world(c,x,c['palm']['angles_deg'][f]) for x in m['local_positions_mm']])*.001;tip=np.array([i for i,p in enumerate(m['local_positions_mm']) if p[0]==100]);motion=np.linalg.norm(q[:,tip].mean(axis=1)-rest[tip].mean(axis=0),axis=1);metrics.append(dict(rows=len(rows),peak_tip_displacement_m=float(motion.max()),final_tip_displacement_m=float(motion[-1]),finite=bool(np.isfinite(q).all()),last_time_s=float(rows[-1]['time_s']),max_cable_raw_force=max(float(x[k]) for x in rows for k in ('cable0_force_raw','cable1_force_raw'))))
  r.update(status='RUN_COMPLETED_NOT_QUALIFIED' if all(x['rows']==a.steps and x['finite'] for x in metrics) else 'FAIL',metrics=metrics)
 r['raw_hashes']={p.name:sha(p) for p in out.glob('*.csv')};(out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes')}))
if __name__=='__main__':main()
