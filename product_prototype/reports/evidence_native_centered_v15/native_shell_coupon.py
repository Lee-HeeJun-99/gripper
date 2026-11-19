"""Stock TriangleFEM + FastTriangularBendingSprings flat thin-strip reference.
Uses physical E,t,D directly, no fitted multiplier. NOT B3 force/potential equivalence.
Euler strip comparison is approximate; zero-load precurve checks reference stress.
"""
import argparse,csv,itertools,json,math,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,add,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--load',type=float,default=1e-6)
    p.add_argument('--precurve',action='store_true')
    p.add_argument('--solver',choices=['direct','graph-cg','native-pcg'],default='direct')
    p.add_argument('--cg-tolerance',type=float,default=1e-16)
    p.add_argument('--probe-rest',action='store_true')
    p.add_argument('--nx',type=int,nargs='+',default=[21,41,81]);p.add_argument('--ny',type=int,nargs='+',default=[3,5]);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    identity=json.loads((BASE/'results/default_control332/summary.json').read_text());binary=ROOT/identity['build']/'libReGripProductSequence.so'
    if sha(binary)!=identity['binary_sha256']:raise ValueError('journal identity')
    E=250e6;h=.0001;nu=0.;D=E*h**3/(12*(1-nu**2));records=[]
    for nx,ny in itertools.product(a.nx,a.ny):
        d=out/f'{nx}_{ny}';d.mkdir();q=np.array(list(itertools.product(np.linspace(0,.1,nx),np.linspace(-.01,.01,ny),[0.])))
        if a.precurve:
            # Same manufactured distal40deg/70–100mm concept,NOT driven deformation.
            for v in q:
                if v[0]>.07:
                    r=.03/math.radians(40);theta=(v[0]-.07)/r
                    v[0]=.07+r*math.sin(theta);v[2]=r*(1-math.cos(theta))
        triangles=[]
        for i,j in itertools.product(range(nx-1),range(ny-1)):
            b=i*ny+j;triangles.extend([[b,b+ny,b+ny+1],[b,b+ny+1,b+1]])
        root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
        for plugin in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','Mass','MechanicalLoad',
                       'ODESolver.Backward','SolidMechanics.FEM.Elastic','SolidMechanics.Spring',
                       'StateContainer','Topology.Container.Constant','Topology.Container.Dynamic'):
            add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
        add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop');node=add(root,'Node',name='shell')
        if a.solver!='direct':root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.LinearSolver.Iterative'))
        if a.solver=='native-pcg':
            for plugin in ('LinearSystem','LinearSolver.Preconditioner'):
                root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.'+plugin))
        add(node,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=25,
            absoluteResidualStoppingThreshold=1e-12,relativeInitialStoppingThreshold=1e-12,relativeSuccessiveStoppingThreshold=1e-12,printLog=1)
        add(node,'StaticSolver',newtonSolver='@newton')
        if a.solver=='direct':add(node,'SparseLDLSolver',template='CompressedRowSparseMatrixMat3x3d')
        elif a.solver=='graph-cg':add(node,'CGLinearSolver',template='GraphScattered',iterations=2000,tolerance=a.cg_tolerance,threshold=1e-30,printLog=1)
        else:
            add(node,'PreconditionedMatrixFreeSystem',assemblingRate=1)
            add(node,'PCGLinearSolver',name='pcg',iterations=2000,tolerance=a.cg_tolerance,preconditioner='@preconditioner')
            add(node,'JacobiPreconditioner',name='preconditioner',template='DiagonalMatrix')
        add(node,'MeshTopology',name='topology',position=flat(q),triangles=flat(triangles))
        add(node,'EdgeSetGeometryAlgorithms');add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q))
        add(node,'UniformMass',totalMass=.001);add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(q[:,0]<=.005))))
        add(node,'TriangleFEMForceField',name='membrane',method='small',youngModulus=E,poissonRatio=nu,thickness=h,planeStrain=0)
        add(node,'FastTriangularBendingSprings',name='bending',bendingStiffness=D,topology='@topology')
        if a.probe_rest:
            observer,compiled_source=compiled_observer('410')
            root.insert(0,ET.Element('RequiredPlugin',pluginName=str(observer)))
            add(node,'NativeElasticMatrixObserver',body='@dofs',elastic='@bending',filename=str(d/'rest_probe'),probePositions=flat(q))
            (out/'compiled_observer.cpp').write_bytes(compiled_source.read_bytes())
        tip=np.arange((nx-1)*ny,nx*ny);weights=np.ones(ny);weights[[0,-1]]=.5;weights/=weights.sum()
        add(node,'ConstantForceField',indices=' '.join(map(str,tip)),forces=flat([[0,0,-a.load*w] for w in weights]))
        add(node,'NativePointJournal',body='@dofs',filename=str(d/'states.csv'));ET.ElementTree(root).write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/n).read_text() for n in ('stdout.log','stderr.log'))
        record=dict(nx=nx,ny=ny,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_SOLVE')
        if a.probe_rest and (d/'rest_probe.probe.csv').exists():
            f=np.array([[float(r[k]) for k in ('fx_N','fy_N','fz_N')] for r in csv.DictReader((d/'rest_probe.probe.csv').open())])
            record['initial_native_bending_force_norm_N']=float(np.linalg.norm(f))
        if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge')):
            rows=list(csv.DictReader((d/'states.csv').open()))
            if len(rows)==2:
                states=[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]
                if all(np.isfinite(s).all() for s in states):
                    record.update(status='COMPLETED_NATIVE_SHELL_DIAGNOSTIC',tip_m=float(-(states[-1]-q)[tip,2].mean()),
                        rest_change_m=float(np.max(abs(states[-1]-q))),repeat_difference_m=float(np.max(abs(states[-1]-states[0]))),
                        actual_q_sha256=sha(d/'states.csv'))
        records.append(record)
    result=dict(scope='Native flat thin-strip bending diagnostic,NOT calibrated isotropic shell or B3/contact/time certification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),
        binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',E_Pa=E,thickness_m=h,nu=nu,bending_D_Nm=D,
        force_N=a.load,solver=a.solver,cg_tolerance=a.cg_tolerance,manufactured_precurve=a.precurve,
        rest_probe_binary_sha256=sha(compiled_observer('410')[0]) if a.probe_rest else None,
        approximate_Euler_tip_m=a.load*.095**3/(3*E*(.02*h**3/12)),records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
