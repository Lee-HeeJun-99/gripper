"""PSD audit using actual public solved Euler matrices,not surrogate force queries."""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigh
from curve_common import OUT,sha,write_json


def matrices(path):
    with path.open()as f:
        reader=csv.reader(f);meta=next(reader)
        if meta[0]!='meta':raise ValueError('actual MBK metadata absent')
        d=int(meta[1]);M=np.zeros((d,d));A=M.copy()
        for kind,r,c,value in reader:
            if kind not in('M','A'):raise ValueError('unknown matrix')
            (M if kind=='M'else A)[int(r),int(c)]=float(value)
    return list(map(float,meta[2:])),M,A


def certificate(M,A,h,alpha,beta,indices,length):
    ld=np.longdouble;u=np.array(indices);mass=M[np.ix_(u,u)].astype(ld);actual=A[np.ix_(u,u)].astype(ld)
    scale=np.array([1/length if i%6>=3 else 1 for i in indices],dtype=ld)
    denominator=ld(h)*(ld(h)+ld(beta));weighted=(1+ld(h)*ld(alpha))*mass
    J=(weighted-actual)/denominator;C=ld(alpha)*mass-ld(beta)*(J+J.T)/2
    S=C*scale[:,None]*scale[None,:]
    eigenvalues,vectors=eigh(np.asarray(S,dtype=float),subset_by_index=[0,0],check_finite=True,driver='evr')
    v=vectors[:,0].astype(ld);physical=v*scale;power=physical@C@physical
    # Conservative input-roundoff envelope,not a regularizer of C or a gate change.
    envelope=abs(ld(alpha))*abs(mass)+abs(ld(beta))*(abs(weighted)+abs(actual))/denominator
    bound=128*np.finfo(float).eps*(abs(physical)@envelope@abs(physical))
    return dict(minimum_eigenvalue=float(eigenvalues[0]),candidate_velocity_quadratic_damping=float(power),input_roundoff_envelope=float(bound),status='FAIL'if power < -bound else'EXPERIMENTAL',meaning='FAIL is a negative damping direction beyond conservative assembly-roundoff envelope;nonnegative minimum is not a general trajectory/physical-material certificate',velocity_vector=list(map(float,physical)),dof_indices=indices)


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',default='profile4',choices=('profile4','release17'));a=p.parse_args();path=OUT/('damping_'+a.stage);target=path/'psd_assessment_v1.json'
    if target.exists():raise ValueError('refuse old PSD evidence')
    summary=json.loads((path/'summary.json').read_text())
    if summary['status']!='PASS'or any(summary['instrumentation_state_difference'].values()):raise ValueError('actual probe trajectory purity prerequisite')
    root=ET.parse(path/'scene.scn').getroot();body=root.find('Node');contact=body.find('CurvedMaterialContact');object_index=int(contact.get('objectIndex'));nodes=int(body.find('FrameLayerNetwork').get('nodesPerLayer'))
    if contact.get('shape')!='0'or object_index!=6*nodes:raise ValueError('restricted planar six-layer/Sphere mass scope')
    if body.find('PartialFixedProjectiveConstraint').get('fixedDirections')!='0 1 0 1 0 1':raise ValueError('unexpected planar projection')
    roots={int(i)for i in body.find('FixedProjectiveConstraint').get('indices').split()}
    if roots!=set(range(0,object_index,nodes)):raise ValueError('unexpected root constraints')
    free=[6*i+j for i in range(object_index)if i not in roots for j in(0,2,4)]+list(range(6*object_index,6*object_index+6));obj=list(range(6*object_index,6*object_index+6));radius=float(contact.get('radius'))
    rows=[];M0=None
    for file in sorted(path.glob('matrix_*.csv'),key=lambda p:int(p.stem.rsplit('_',1)[-1])):
        meta,M,A=matrices(file);time,end,h,alpha,beta=meta
        if M0 is None:M0=M
        mass_error=float(np.max(np.abs(M[np.ix_(free,free)]-M0[np.ix_(free,free)])))
        if mass_error:raise ValueError('projected mass not constant;cannot infer begin-state J from end-state M')
        rows.append(dict(begin_time=time,end_time=end,dt=h,projected_mass_error=mass_error,actual_matrix_sha256=sha(file),free_system=certificate(M,A,h,alpha,beta,free,radius),object_only=certificate(M,A,h,alpha,beta,obj,radius)))
    write_json(target,dict(status='FAIL'if any(r['free_system']['status']=='FAIL'for r in rows)else'EXPERIMENTAL',snapshots=rows,scope='C=alpha*M-beta*sym(J),inferred from ACTUAL public solved A=(1+h*alpha)M-h(h+beta)J. Planar free DOFs and isotropic Sphere only;actual projected M checked bitwise constant. Angular velocities normalized by reference radius via congruence;PSD sign invariant. Not a proof that this is the cause of friction convergence failure.',source=sha(__file__)))
    print([(r['begin_time'],r['free_system']['status'],r['free_system']['candidate_velocity_quadratic_damping'],r['object_only']['candidate_velocity_quadratic_damping'])for r in rows])


if __name__=='__main__':main()
