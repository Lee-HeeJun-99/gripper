"""Native two-layer elastic/friction bending coupon,NOT calibrated vacuum jamming.
Pressure represented by explicit opposite outer-face nodal loads; no E change.
Material/friction/pressure are declared research assumptions,not measured PET.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def mesh():
 q=np.array([[x,y,z] for x in np.linspace(0,.04,9) for y in (-.005,.005) for z in (0,.0002)]);idx=lambda i,j,k:4*i+2*j+k;tet=[]
 for i in range(8):
  ids=[idx(i+a,b,c) for a,b,c in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
  for pattern in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
   t=[ids[j] for j in pattern]
   if np.linalg.det((q[t[1:]]-q[t[0]]).T)<0:t[1],t[2]=t[2],t[1]
   tet.append(t)
 faces={}
 for a,b,c,d in tet:
  for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(f)),[]).append(f)
 return q,np.array(tet),[v[0] for v in faces.values() if len(v)==1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--pressure',type=float,choices=[0,1000],default=1000);p.add_argument('--mu',type=float,choices=[0,.3],default=.3);p.add_argument('--steps',type=int,choices=[50,500],default=50);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);q0,tet,tri=mesh();root=ET.Element('Node',name='root',dt='.0002',gravity='0 0 0');add=lambda node,tag,**attrs:ET.SubElement(node,tag,{k:str(v) for k,v in attrs.items()});flat=lambda x:' '.join(format(float(v),'.17g') for v in np.array(x).ravel())
 for plugin in ('AnimationLoop','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant','MechanicalLoad','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 meta=json.loads((BASE/'results/default_control332/summary.json').read_text());binary=BASE.parent/meta['build']/'libReGripProductSequence.so';assert sha(binary)==meta['binary_sha256'];add(root,'RequiredPlugin',pluginName=str(binary));add(root,'FreeMotionAnimationLoop');add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=1);add(root,'CollisionPipeline',depth=6);add(root,'BruteForceBroadPhase');add(root,'BVHNarrowPhase',name='narrow');add(root,'MinProximityIntersection',alarmDistance=.00005,contactDistance=0);add(root,'CollisionResponse',response='FrictionContactConstraint',responseParams='mu='+str(a.mu));add(root,'EulerImplicitSolver',rayleighMass=1,rayleighStiffness=.0001);add(root,'SparseLDLSolver',name='globalLinear');add(root,'GenericConstraintCorrection',solverName='globalLinear');add(root,'NativeConstraintJournal',solver='@constraints',filename=str(out/'constraints.csv'));add(root,'NativeDetectionPairs',narrow='@narrow',filename=str(out/'layer_pairs.csv'))
 for layer in (0,1):
  q=q0.copy();q[:,2]+=layer*.000202;node=add(root,'Node',name='layer'+str(layer));add(node,'MeshTopology',name='topology',position=flat(q),tetrahedra=flat(tet),triangles=flat(tri));add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q));add(node,'UniformMass',totalMass=1400*.04*.01*.0002);add(node,'TetrahedronFEMForceField',name='FEM',method='large',youngModulus=2.5e9,poissonRatio=.3);add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(q0[:,0]==0))));forces=np.zeros_like(q)
  for i,(x,y,z) in enumerate(q0):
   if z==(0 if layer==0 else .0002):forces[i,2]+=(1 if layer==0 else -1)*a.pressure*.005*.005*(.5 if x in (0,.04) else 1)
   if x==.04:forces[i,2]-=1e-4/8
  add(node,'ConstantForceField',template='Vec3d',indices=' '.join(map(str,range(len(q)))),forces=flat(forces));add(node,'TriangleCollisionModel',group=layer+1);add(node,'LineCollisionModel',group=layer+1);add(node,'PointCollisionModel',group=layer+1);add(node,'NativePointJournal',body='@dofs',filename=str(out/f'layer{layer}.csv'))
 ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh.json').write_text(json.dumps(dict(q0=q0.tolist(),tetrahedra=tet.tolist(),triangles=tri)));cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',binary_sha256=sha(binary),command=cmd,pressure_Pa=a.pressure,friction=a.mu,E_Pa=2.5e9,density_kg_m3=1400,dimensions_m=[.04,.01,.0002],layers=2,initial_interface_gap_m=.000002,tip_bending_load_N=1e-4,dt_s=.0002,steps=a.steps,memory_GiB=4,child_limit_s=120,estimated_runtime_s=5 if a.steps==50 else 50,classification='ASSUMED_LAYER_CONTACT_COUPON_NOT_MEASURED_PET_OR_VACUUM',vacuum_chamber=None,material_calibration=None);(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[];quality=[]
 for layer in (0,1):
  file=out/f'layer{layer}.csv';rows=list(csv.DictReader(file.open())) if file.exists() else [];counts.append(len(rows));valid=[np.fromstring(r['q'],sep=' ') for r in rows];valid=[q.reshape(-1,3) for q in valid if len(q)==q0.size]
  if valid:
   q=np.array(valid);D=(q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2);D0=(q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1);quality.append(dict(minimum_volume_ratio=float((np.linalg.det(D)/np.linalg.det(D0)).min()),finite=bool(np.isfinite(q).all())))
 status='NATIVE_LAYER_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and counts==[a.steps]*2 and len(quality)==2 and all(x['finite'] and x['minimum_volume_ratio']>0 for x in quality) else 'FAIL_LAYER_EXECUTION_OR_QUALITY';d=dict(status=status,process=proc,outputs=counts,quality=quality,physical_validation='NOT QUALIFIED',layer_jamming='NOT VALIDATED_NO_VACUUM_OR_CALIBRATION',energy_work=None);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
