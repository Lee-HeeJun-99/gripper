"""Finite BeamAdapter tube against eccentric finite eyelet; bounded Native coupon."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded,add,flat
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--slide',action='store_true');p.add_argument('--audit',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/native_finite_wire1421';root=ET.parse(src/'scene.scn').getroot();root.remove(root.find('DefaultAnimationLoop'));add(root,'FreeMotionAnimationLoop');solver=root.find('BlockGaussSeidelConstraintSolver');solver.set('tolerance','1e-12');solver.set('maxIterations','1000');solver.set('computeConstraintForces','1')
 for plugin in ('Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact','Constraint.Lagrangian.Correction','Mapping.NonLinear'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 add(root,'CollisionPipeline');add(root,'BruteForceBroadPhase');add(root,'BVHNarrowPhase');add(root,'LocalMinDistance',alarmDistance=.0001,contactDistance=.000002);add(root,'CollisionResponse',response='FrictionContactConstraint',responseParams='mu=0.0');add(root,'NativeConstraintJournal',solver='@unusedJournalSolver',filename=str(out/'solver.csv'))
 n=root.find('Node');n.find('ConstantForceField').set('forces','.0001 -.0004 0 0 0 0' if a.slide else '0 -.0004 0 0 0 0');add(n,'LinearSolverConstraintCorrection',wire_optimization='true');n.find('NativeRigidJournal').set('filename',str(out/'states.csv'))
 if a.slide:
  n.remove(n.find('FixedProjectiveConstraint'));add(n,'PartialFixedProjectiveConstraint',indices=0,fixedDirections='0 1 1 1 1 1')
 # Faceted finite tube radius .25mm, not a zero-radius line collision.
 points=[];tri=[];nr=16;nx=41
 for x in np.linspace(0,.02,nx):
  for t in np.arange(nr)*2*np.pi/nr:points.append([x,.00025*np.cos(t),.00025*np.sin(t)])
 for i in range(nx-1):
  for j in range(nr):
   k=i*nr+j;l=i*nr+(j+1)%nr;tri.extend([[k,k+nr,l+nr],[k,l+nr,l]])
 tri=[face[::-1] for face in tri]
 indexed=np.array(points);indexed[:,0]=np.minimum(indexed[:,0]/.002,np.nextafter(10.,0.))
 c=add(n,'Node',name='wireSurface');add(c,'MeshTopology',position=flat(points),triangles=flat(tri));add(c,'MechanicalObject',name='surface',position=flat(points));add(c,'TriangleCollisionModel',group=1);add(c,'LineCollisionModel',group=1);add(c,'PointCollisionModel',group=1);add(c,'AdaptiveBeamMapping',input='@../dofs',output='@surface',interpolation='@../interpolation',points=flat(indexed),useCurvAbs=0,mapForces=1,mapMasses=0);add(c,'NativePointJournal',body='@surface',filename=str(out/'surface.csv'))
 source=BASE/'results/eccentric_eyelet_mesh1416/route0_guide4.stl';mesh=trimesh.load(source,force='mesh');q=mesh.vertices*.001;world=np.column_stack([q[:,2]+.01,q[:,0],q[:,1]])
 e=add(root,'Node',name='finiteEyelet');add(e,'MeshTopology',position=flat(world),triangles=flat(mesh.faces));add(e,'MechanicalObject',position=flat(world));add(e,'TriangleCollisionModel',moving=0,simulated=0,group=2);add(e,'LineCollisionModel',moving=0,simulated=0,group=2);add(e,'PointCollisionModel',moving=0,simulated=0,group=2)
 if a.audit:
  root.find('BVHNarrowPhase').set('name','narrow');root.find('CollisionResponse').set('name','response');add(root,'NativeDetectionPairs',narrow='@narrow',filename=str(out/'detector.csv'));add(root,'NativeResponseRows',manager='@response',body='@wire/dofs',solver='@unusedJournalSolver',filename=str(out/'response_rows.csv'))
 plugins=[x for x in root if x.tag=='RequiredPlugin']
 for x in plugins:root.remove(x)
 for i,x in enumerate(plugins):root.insert(i,x)
 ET.ElementTree(root).write(out/'scene.scn');command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','200','--hideProgressBar',str(out/'scene.scn')];process=guarded(command,out/'process',60);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];sr=list(csv.DictReader((out/'solver.csv').open())) if (out/'solver.csv').exists() else [];imp=[np.fromstring(r['impulses_Ns'],sep=' ') for r in sr];active=sum(bool(len(x) and np.max(np.abs(x))>0) for x in imp)
 result=dict(status='NATIVE_COUPON_COMPLETED_CONTACT_NOT_YET_QUALIFIED' if process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==200 else 'FAIL_NATIVE_WIRE_EYELET',process=process,rows=len(rows),active_constraint_outputs=active,slide=a.slide,command=command,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),eyelet_sha256=sha(source),binary_sha256=json.loads((src/'summary.json').read_text())['binary_sha256'],scope='Finite16-sided tube via stock AdaptiveBeamMapping against actual eccentric solid. E/rho inherited assumed2GPa/1000;zero-friction contact separates sliding availability from unmeasured friction. Initial mesh mapping/gap/contact impulse still need independent assessment. No grasp or constrained-loop/time/mesh/material PASS.',physical_validation='NOT QUALIFIED',load_basis='0.4mN transverse load gives approximate Euler midpoint54um versus ~42um nominal radial entry clearance;20ms observation,not gripper tension tuning',corrections='Explicit beam-index coordinate mapping;outer-facing tube normals;old malformed/no-contact runs preserved. End coordinate nextafter10 implements last beam endpoint without invalid beam10.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
