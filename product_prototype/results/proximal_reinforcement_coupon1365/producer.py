"""Independent small-strain Native layer+subset-bond contract coupon.

No contact,cable or moving parent. Same finite pad reference,material and mapped
mass. Independent CST/Backward-Euler recurrence is a reference,not a new solver.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.linalg import cho_factor,cho_solve
from analyse import BASE,sha
from native_bending_coupon import guarded
from b3_contact_layer_native import flat,add
from layer_bending_reference import element,elastic

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reinforcement',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);geom=BASE/'results'/('proximal_reinforcement_geometry1364' if a.reinforcement else 'b3_contact_layer_geometry1336');g=json.loads((geom/'mesh.json').read_text());q=np.array(g['world_reference_m'][0]);tet=np.array(g['tetrahedra']);mass=g['records'][0]['mass_kg'];dt=.0025;steps=20;count=len(q);half=count//2;young=g.get('material',{}).get('young_modulus_Pa',1e6)
 root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
 for plugin in ('AnimationLoop','Constraint.Lagrangian.Correction','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant','Mapping.Linear','MechanicalLoad'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 binary=BASE/'cad/build_default_control332/libReGripProductSequence.so';add(root,'RequiredPlugin',pluginName=binary);add(root,'FreeMotionAnimationLoop');add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-10',maxIterations=1000);add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0);add(root,'SparseLDLSolver',name='globalLinear',template='CompressedRowSparseMatrixd');add(root,'GenericConstraintCorrection')
 base=add(root,'Node',name='base');add(base,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q[::2]));add(base,'FixedProjectiveConstraint',indices=' '.join(map(str,range(half))))
 free=add(root,'Node',name='free');add(free,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q[1::2]));layer=add(root,'Node',name='layer');add(layer,'MeshTopology',position=flat(q),tetrahedra=flat(tet),triangles=flat(g['triangles']));add(layer,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q));add(layer,'UniformMass',totalMass=mass);add(layer,'TetrahedronFEMForceField',method='small',youngModulus=young,poissonRatio=.3);pairs=[]
 for i in range(half):pairs.extend([1,i,0,i])
 add(layer,'SubsetMultiMapping',template='Vec3d,Vec3d',input='@../free/dofs @../base/dofs',output='@dofs',indexPairs=' '.join(map(str,pairs)),mapMatrices=1)
 normal=q[1::2]-q[::2];normal/=np.linalg.norm(normal,axis=1)[:,None];force=-.001*normal/half
 add(layer,'ConstantForceField',indices=' '.join(map(str,range(1,count,2))),forces=flat(force));add(layer,'NativePointJournal',body='@dofs',filename=out/'states.csv');ET.ElementTree(root).write(out/'scene.scn')
 K=np.zeros((3*count,3*count));D=elastic(young,.3)
 for t in tet:
  V,B,_=element(q[t],D);ids=(3*t[:,None]+np.arange(3)).ravel();K[np.ix_(ids,ids)]+=V*B.T@D@B
 ids=(3*np.arange(1,count,2)[:,None]+np.arange(3)).ravel();K=K[np.ix_(ids,ids)];M=np.eye(3*half)*(mass/count);F=force.ravel();factor=cho_factor(M+dt*dt*K);u=np.zeros(3*half);v=u.copy();reference=[]
 for _ in range(steps):v=cho_solve(factor,M@v+dt*(F-K@u));u=u+dt*v;reference.append((u.copy(),v.copy()))
 cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
 pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),scene_sha256=sha(out/'scene.scn'),geometry_sha256=sha(geom/'mesh.json'),dt_s=dt,steps=steps,total_force_N=.001,mass_kg=mass,material=g.get('material','assumedE1MPa,nu.3,rho1000;not measured'),reference=f'CST linear tetra+UniformMass mass/{count}+BE;fixed bottom,free top;no damping',expected_runtime_s=5,child_limit_s=30,memory_GiB=4);(out/'preflight.json').write_text(json.dumps(pre,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());proc=guarded(cmd,out/'process',30);rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];errq=[];errv=[];bond=[]
 for r,(u,v) in zip(rows,reference):
  actualq=np.fromstring(r['q'],sep=' ').reshape(-1,3);actualv=np.fromstring(r['v'],sep=' ').reshape(-1,3);errq.append(float(abs(actualq[1::2]-(q[1::2]+u.reshape(-1,3))).max()));errv.append(float(abs(actualv[1::2]-v.reshape(-1,3)).max()));bond.append(float(abs(actualq[::2]-q[::2]).max()))
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));valid=proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==steps and max(errq,default=1)<=1e-12 and max(errv,default=1)<=1e-12 and max(bond,default=1)<=1e-12
 result=dict(status='PASS_LINEAR_MAPPED_COUPON_ONLY' if valid else 'FAIL_COUPON_EXECUTION_OR_REFERENCE',process=proc,outputs=len(rows),max_position_reference_error_m=max(errq,default=None),max_velocity_reference_error_m_s=max(errv,default=None),max_fixed_bond_error_m=max(bond,default=None),reference_endpoint_max_displacement_m=float(abs(reference[-1][0]).max()),scope='Small linear no-contact,no-cable,fixed-parent mapped-layer contract only. Not B3 large-FEM/moving-bond/contact or product validation.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
