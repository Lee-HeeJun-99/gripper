"""Native straight solid cantilever diagnostic; not a replacement product solver.

Rectangular section and full end clamp differ deliberately from thin bonded B3.
Euler-Bernoulli is a comparison, not an exact 3-D elasticity reference.
"""
import argparse
import csv
import itertools
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from native_bending_coupon import BASE, ROOT, add, flat, sha, guarded


def main():
    csv.field_size_limit(64*1024*1024)
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--load', type=float, default=1e-3)
    parser.add_argument('--cross', type=int, default=3)
    parser.add_argument('--nx', type=int, nargs='+', default=[11,21,41])
    parser.add_argument('--models', nargs='+', choices=['tetra','hexa'], default=['tetra','hexa'])
    parser.add_argument('--tip-load', choices=['uniform-node','uniform-traction','consistent-surface'], default='uniform-traction')
    parser.add_argument('--axis', choices=['x','z'], default='z')
    parser.add_argument('--poisson', type=float, default=.3)
    args = parser.parse_args()
    out = BASE/'results'/args.tag
    out.mkdir(exist_ok=False)
    meta = json.loads((BASE/'results/default_control332/summary.json').read_text())
    binary = ROOT/meta['build']/'libReGripProductSequence.so'
    if sha(binary) != meta['binary_sha256']:
        raise ValueError('journal binary mismatch')
    records = []
    for model in args.models:
        for nx in args.nx:
            d = out/f'{model}_{nx}'
            d.mkdir()
            q = np.array(list(itertools.product(np.linspace(0,.1,nx),
                         np.linspace(-.005,.005,args.cross), np.linspace(-.005,.005,args.cross))))
            def idx(i,j,k): return i*args.cross**2+j*args.cross+k
            hexes, tets = [], []
            for i,j,k in itertools.product(range(nx-1),range(args.cross-1),range(args.cross-1)):
                hexes.append([idx(i,j,k),idx(i+1,j,k),idx(i+1,j+1,k),idx(i,j+1,k),
                              idx(i,j,k+1),idx(i+1,j,k+1),idx(i+1,j+1,k+1),idx(i,j+1,k+1)])
                for perm in itertools.permutations(range(3)):
                    p = np.array([i,j,k]); vertices=[idx(*p)]
                    for axis in perm:
                        p=p.copy();p[axis]+=1;vertices.append(idx(*p))
                    if np.linalg.det((q[vertices[1:]]-q[vertices[0]]).T)<0:
                        vertices[1],vertices[2]=vertices[2],vertices[1]
                    tets.append(vertices)
            root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
            for plugin in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct',
                           'Mass','MechanicalLoad','ODESolver.Backward','SolidMechanics.FEM.Elastic',
                           'StateContainer','Topology.Container.Constant'):
                add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
            add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop')
            node=add(root,'Node',name='solid')
            add(node,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=25,
                absoluteResidualStoppingThreshold=1e-12,relativeInitialStoppingThreshold=1e-12,
                relativeSuccessiveStoppingThreshold=1e-12,printLog=1)
            add(node,'StaticSolver',newtonSolver='@newton')
            add(node,'SparseLDLSolver',template='CompressedRowSparseMatrixMat3x3d')
            add(node,'MeshTopology',position=flat(q),**{('tetrahedra' if model=='tetra' else 'hexahedra'):flat(tets if model=='tetra' else hexes)})
            add(node,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q))
            add(node,'UniformMass',totalMass=.001)
            add(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(q[:,0]==0))))
            add(node,'TetrahedronFEMForceField' if model=='tetra' else 'HexahedronFEMForceField',
                method='small',youngModulus=1e6,poissonRatio=args.poisson)
            tip=np.flatnonzero(q[:,0]==.1)
            weights=np.ones((args.cross,args.cross))
            if args.tip_load in ('uniform-traction','consistent-surface'):
                weights[[0,-1],:]*=.5;weights[:,[0,-1]]*=.5
            weights=weights.ravel()/weights.sum()
            if args.tip_load=='consistent-surface' and model=='tetra':
                weights=np.zeros(len(tip));tip_index={v:i for i,v in enumerate(tip)}
                for tet in tets:
                    for face in itertools.combinations(tet,3):
                        if all(v in tip_index for v in face):
                            points=q[list(face)];area=np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))/2
                            for v in face:weights[tip_index[v]]+=area/3
                weights/=weights.sum()
            direction=np.array([1.,0,0]) if args.axis=='x' else np.array([0.,0,-1.])
            add(node,'ConstantForceField',indices=' '.join(map(str,tip)),forces=flat([args.load*w*direction for w in weights]))
            add(node,'NativePointJournal',body='@dofs',filename=str(d/'states.csv'))
            ET.ElementTree(root).write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/name).read_text() for name in ('stdout.log','stderr.log'))
            r=dict(model=model,nx=nx,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_SOLVE')
            residuals=[float(v) for v in re.findall(r'\* Residual norm = ([0-9.eE+-]+)',logs)]
            r['last_logged_residual_N']=residuals[-1] if residuals else None
            if process['exit_code']==0 and '[ERROR]' not in logs and 'Line search failed' not in logs and 'failed to converge' not in logs:
                rows=list(csv.DictReader((d/'states.csv').open()))
                states=[np.fromstring(row['q'],sep=' ').reshape(-1,3) for row in rows]
                if len(states)==2 and all(np.isfinite(x).all() for x in states):
                    u=states[-1]-q
                    determinants=[np.linalg.det((states[-1][t[1:]]-states[-1][t[0]]).T)/np.linalg.det((q[t[1:]]-q[t[0]]).T) for t in tets]
                    projection=u[tip]@direction
                    r.update(status='COMPLETED_STATIC_DIAGNOSTIC',tip_m=float(projection.mean()),
                             repeat_difference_m=float(np.max(abs(states[-1]-states[0]))),
                             minimum_tet_determinant_ratio=float(min(determinants)),
                             external_half_work_J=float(args.load*np.dot(weights,projection)/2),
                             strain_energy_J=None,reaction_N=None,state_sha256=sha(d/'states.csv'))
            records.append(r)
    result=dict(scope='Native solid beam diagnostic only; no B3,contact,cable,time or product qualification',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),
                sdk='/home/ubuntu/SOFA/v26.06.00',force_N=args.load,E_Pa=1e6,nu=args.poisson,load_axis=args.axis,
                geometry_m=[.1,.01,.01],tip_load=args.tip_load,cross_nodes=args.cross,
                approximate_Euler_tip_m=args.load*.1**3/(3*1e6*(.01*.01**3/12)) if args.axis=='z' else None,
                exact_axial_tip_m=args.load*.1/(1e6*.01*.01) if args.axis=='x' and args.poisson==0 else None,records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
