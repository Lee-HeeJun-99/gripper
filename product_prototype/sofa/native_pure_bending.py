"""Exact linear-elastic pure-bending reference at nu=0; native FEM solves only.

u=(-k*x*z,0,k*x*x/2), sigma_xx=-E*k*z. End traction integrated
consistently on actual triangle/Q4 faces; other faces traction free.
This is a diagnostic material/load, not a new B3 material assumption.
"""
import argparse,csv,itertools,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--thickness-scale',type=float,default=1.)
    p.add_argument('--models',nargs='+',choices=['tetra','hexa'],default=['tetra','hexa']);a=p.parse_args()
    if a.thickness_scale<=0:raise ValueError('positive section required')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];curvature=.01;E=1e6
    for cross,case in [(3,'native_traction_cross3_389'),(5,'native_traction_cross5_390')]:
        for model,nx in itertools.product(a.models,(21,41,81)):
            source=BASE/'results'/case/f'{model}_{nx}'/'scene.scn'
            d=out/f'{model}_{nx}_cross{cross}';d.mkdir();tree=ET.parse(source);root=tree.getroot()
            topology=root.find('.//MeshTopology');q=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3)
            q[:,2]*=a.thickness_scale
            topology.set('position',flat(q));root.find('.//MechanicalObject').set('position',flat(q))
            forces=np.zeros_like(q);tip=set(np.flatnonzero(q[:,0]==.1))
            if model=='tetra':
                tets=np.fromstring(topology.get('tetrahedra'),sep=' ',dtype=int).reshape(-1,4)
                for tet in tets:
                    for face in itertools.combinations(tet,3):
                        if not all(i in tip for i in face):continue
                        points=q[list(face)];area=np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))/2
                        for i in face:forces[i,0]+=-E*curvature*area*(sum(q[j,2] for j in face)+q[i,2])/12
            else:
                hexes=np.fromstring(topology.get('hexahedra'),sep=' ',dtype=int).reshape(-1,8)
                signs=np.array([[-1,-1],[1,-1],[1,1],[-1,1]])
                for h in hexes:
                    face=[h[i] for i in (1,2,6,5)]
                    if not all(i in tip for i in face):continue
                    points=q[face]
                    area=np.linalg.norm(np.cross(points[1]-points[0],points[3]-points[0]))
                    for s,t in itertools.product((-1/np.sqrt(3),1/np.sqrt(3)),repeat=2):
                        N=(1+signs[:,0]*s)*(1+signs[:,1]*t)/4
                        forces[face,0]+=-E*curvature*area/4*N*(N@points[:,2])
            ids=sorted(tip);load=root.find('.//ConstantForceField');load.set('indices',' '.join(map(str,ids)));load.set('forces',flat(forces[ids]))
            ff=root.find('.//TetrahedronFEMForceField') if model=='tetra' else root.find('.//HexahedronFEMForceField')
            ff.set('poissonRatio','0');root.find('.//NativePointJournal').set('filename',str(d/'states.csv'))
            tree.write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/n).read_text() for n in ('stdout.log','stderr.log'))
            moment=np.cross(q,forces).sum(axis=0)
            r=dict(model=model,nx=nx,cross=cross,process=process,scene_sha256=sha(d/'scene.scn'),
                   resultant_force_N=forces.sum(axis=0).tolist(),end_moment_Nm=moment.tolist(),status='FAIL_NATIVE_SOLVE')
            if process['exit_code']==0 and '[ERROR]' not in logs and 'Line search failed' not in logs and 'failed to converge' not in logs:
                rows=list(csv.DictReader((d/'states.csv').open()))
                if len(rows)==2:
                    actual=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3);u=actual-q
                    exact=np.zeros_like(q);exact[:,0]=-curvature*q[:,0]*q[:,2];exact[:,2]=curvature*q[:,0]**2/2
                    error=np.max(abs(u-exact))
                    r.update(status='COMPLETED_PURE_BENDING_DIAGNOSTIC',max_field_error_m=float(error),
                             relative_field_error=float(error/np.max(abs(exact))),tip_m=float(u[ids,2].mean()),
                             state_sha256=sha(d/'states.csv'))
            records.append(r)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(dict(scope='Exact linear nu=0 pure-bending diagnostic,not B3/contact/time certification',thickness_scale=a.thickness_scale,curvature_per_m=curvature,exact_tip_m=curvature*.1**2/2,records=records),indent=2))
    print(json.dumps([{k:r[k] for k in ('model','nx','cross','status','relative_field_error') if k in r} for r in records],indent=2))

if __name__=='__main__':main()
