"""Installed BeamAdapter RECTANGULAR rail reference; no custom FEM/ODE solver.
Stock rectangular section disables shear terms (Asy=Asz=0); torsion unqualified.
"""
import argparse,csv,json,math,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,add,flat,sha,guarded

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--load',type=float,default=1e-6)
    p.add_argument('--nx',type=int,nargs='+',default=[21,41,81]);p.add_argument('--precurve',action='store_true')
    p.add_argument('--solver',choices=['direct','graph-cg'],default='direct')
    p.add_argument('--newton-iterations',type=int,default=30);a=p.parse_args()
    if not 1<=a.newton_iterations<=200:raise ValueError('bounded native Newton budget required')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sdk=Path('/home/ubuntu/SOFA/v26.06.00')
    plugin=sdk/'plugins/BeamAdapter/lib/libBeamAdapter.so'
    deps=subprocess.check_output(['ldd',str(plugin)],text=True)
    if any('libSofa' in line and '=>' in line and str(sdk) not in line for line in deps.splitlines()):raise ValueError('mixed BeamAdapter ABI')
    (out/'ldd.txt').write_text(deps)
    identity=json.loads((BASE/'results/default_control332/summary.json').read_text());journal=ROOT/identity['build']/'libReGripProductSequence.so'
    if sha(journal)!=identity['binary_sha256']:raise ValueError('journal mismatch')
    records=[];E=250e6;by=.002;hz=.0005
    for nx in a.nx:
        d=out/str(nx);d.mkdir();s=np.linspace(0,.1,nx);q=np.array([[x,0,0,0,0,0,1] for x in s])
        if a.precurve:
            for i,x in enumerate(s):
                if x>.07:
                    radius=.03/math.radians(40);theta=(x-.07)/radius
                    q[i]=[.07+radius*math.sin(theta),0,radius*(1-math.cos(theta)),0,-math.sin(theta/2),0,math.cos(theta/2)]
        root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
        for name in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','MechanicalLoad',
                     'Mapping.NonLinear','ODESolver.Backward','StateContainer','Topology.Container.Constant'):
            add(root,'RequiredPlugin',pluginName='Sofa.Component.'+name)
        add(root,'RequiredPlugin',pluginName=str(plugin));add(root,'RequiredPlugin',pluginName=str(journal));add(root,'DefaultAnimationLoop')
        if a.solver=='graph-cg':add(root,'RequiredPlugin',pluginName='Sofa.Component.LinearSolver.Iterative')
        node=add(root,'Node',name='rail');add(node,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=a.newton_iterations,
            maxNbIterationsLineSearch=12,absoluteResidualStoppingThreshold=1e-12,relativeInitialStoppingThreshold=1e-12,
            relativeSuccessiveStoppingThreshold=1e-12,printLog=1)
        add(node,'StaticSolver',newtonSolver='@newton')
        if a.solver=='direct':add(node,'SparseLDLSolver',template='CompressedRowSparseMatrixd')
        else:add(node,'CGLinearSolver',template='GraphScattered',iterations=2000,tolerance=1e-16,threshold=1e-30)
        add(node,'MeshTopology',name='topology',edges=flat([[i,i+1] for i in range(nx-1)]))
        add(node,'MechanicalObject',template='Rigid3d',name='dofs',position=flat(q))
        add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(s<=.005))))
        add(node,'BeamInterpolation',name='interpolation',crossSectionShape='rectangular',lengthY=by,lengthZ=hz,
            defaultYoungModulus=E,defaultPoissonRatio=.3,dofsAndBeamsAligned=1,straight=0 if a.precurve else 1)
        add(node,'AdaptiveBeamForceFieldAndMass',name='elastic',interpolation='@interpolation',computeMass=0)
        add(node,'ConstantForceField',indices=nx-1,forces=f'0 0 {-a.load:.17g} 0 0 0')
        centers=add(node,'Node',name='centers');add(centers,'MechanicalObject',name='points',position=flat(np.zeros((nx,3))))
        add(centers,'RigidMapping',input='@../dofs',output='@points',rigidIndexPerPoint=' '.join(map(str,range(nx))),globalToLocalCoords=0)
        add(centers,'NativePointJournal',body='@points',filename=str(d/'states.csv'));ET.ElementTree(root).write(d/'scene.scn')
        process=guarded([sdk/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'));r=dict(nx=nx,process=process,status='FAIL_NATIVE_BEAM_SOLVE',scene_sha256=sha(d/'scene.scn'))
        if process['exit_code']==0 and not any(x in logs for x in ('[ERROR]','Line search failed','failed to converge')):
            rows=list(csv.DictReader((d/'states.csv').open()))
            if len(rows)==2:
                states=[np.fromstring(row['q'],sep=' ').reshape(-1,3) for row in rows]
                if all(np.isfinite(x).all() for x in states):
                    r.update(status='COMPLETED_NATIVE_RECTANGULAR_BEAM_DIAGNOSTIC',tip_m=float(-(states[-1]-q[:,:3])[-1,2]),
                             repeat_difference_m=float(np.max(abs(states[1]-states[0]))),max_rest_error_m=float(np.max(abs(states[-1]-q[:,:3]))))
        records.append(r)
    reference=a.load*.095**3/(3*E*(by*hz**3/12)) if not a.precurve else None
    data=dict(scope='Rectangular native BeamAdapter bending only;NOT Skin/attachment/torsion/contact/time/B3 certification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),
        sdk=str(sdk),beamadapter_binary_sha256=sha(plugin),journal_binary_sha256=sha(journal),E_Pa=E,section_m=[by,hz],
        force_N=a.load,solver=a.solver,newton_iteration_budget=a.newton_iterations,precurved_stress_free_assumption=a.precurve,approximate_small_deflection_Euler_tip_m=reference,records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

if __name__=='__main__':main()
