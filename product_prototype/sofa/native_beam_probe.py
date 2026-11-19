"""Installed native BeamFEM stock cantilever; mapped tip observer only.
Circular section differs from the rectangular solids and product laminate.
"""
import argparse,csv,json,math,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,add,flat,sha,guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--load',type=float,default=1e-5);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    meta=json.loads((BASE/'results/default_control332/summary.json').read_text())
    binary=ROOT/meta['build']/'libReGripProductSequence.so'
    if sha(binary)!=meta['binary_sha256']:raise ValueError('binary identity')
    records=[]
    for nx in (11,21,41):
        d=out/str(nx);d.mkdir();root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
        for plugin in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','MechanicalLoad',
                       'Mapping.NonLinear','ODESolver.Backward','SolidMechanics.FEM.Elastic',
                       'StateContainer','Topology.Container.Constant'):
            add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
        add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop')
        node=add(root,'Node',name='beam');add(node,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=25,
            absoluteResidualStoppingThreshold=1e-12,relativeInitialStoppingThreshold=1e-12,
            relativeSuccessiveStoppingThreshold=1e-12,printLog=1)
        add(node,'StaticSolver',newtonSolver='@newton');add(node,'SparseLDLSolver',template='CompressedRowSparseMatrixd')
        add(node,'MeshTopology',edges=flat([[i,i+1] for i in range(nx-1)]))
        add(node,'MechanicalObject',name='dofs',template='Rigid3d',position=flat([[x,0,0,0,0,0,1] for x in np.linspace(0,.1,nx)]))
        add(node,'FixedProjectiveConstraint',indices='0')
        add(node,'BeamFEMForceField',radius=.005,radiusInner=0,youngModulus=1e6,poissonRatio=.3)
        add(node,'ConstantForceField',indices=nx-1,forces=f'0 0 {-a.load:.17g} 0 0 0')
        tip=add(node,'Node',name='tip');add(tip,'MechanicalObject',name='point',position='0 0 0')
        add(tip,'RigidMapping',input='@../dofs',output='@point',index=nx-1)
        add(tip,'NativePointJournal',body='@point',filename=str(d/'tip.csv'))
        ET.ElementTree(root).write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/n).read_text() for n in ('stdout.log','stderr.log'))
        r=dict(nx=nx,process=process,status='FAIL',scene_sha256=sha(d/'scene.scn'))
        if process['exit_code']==0 and '[ERROR]' not in logs and 'Line search failed' not in logs:
            states=[np.fromstring(row['q'],sep=' ') for row in csv.DictReader((d/'tip.csv').open())]
            if len(states)==2 and all(np.isfinite(s).all() for s in states):
                r.update(status='COMPLETED_NATIVE_BEAM_DIAGNOSTIC',tip_deflection_m=float(-states[-1][2]),
                         repeat_difference_m=float(abs(states[1]-states[0]).max()))
        records.append(r)
    data=dict(scope='Native circular BeamFEM availability and static response only;not B3 qualification',
              source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',
              force_N=a.load,approximate_Euler_tip_m=a.load*.1**3/(3*1e6*math.pi*.005**4/4),records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

if __name__=='__main__':main()
