"""Independent finite differences and virtual work; no whole Finger approval."""
import argparse,json,math
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,ref,dump
import rod_point_jacobian as rod
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/contact'/a.tag;out.mkdir(parents=True,exist_ok=False)
    n=12;L=.0862;q=np.linspace(.03,.9,n)+.002*np.sin(np.arange(n));M=np.array([[math.cos(.7),math.sin(.7)],[-math.sin(.7),math.cos(.7)]]);shift=np.array([-.01,.02]);rows=[]
    for i,t,side in [(0,.3,-1),(4,.43,1),(11,.91,0)]:
        point,J=rod.point(rod.prepare(q,L),i,t,side,M,shift);eps=1e-6
        fd=np.column_stack([(rod.point(rod.prepare(q+eps*np.eye(n)[j],L),i,t,side,M,shift)[0]-rod.point(rod.prepare(q-eps*np.eye(n)[j],L),i,t,side,M,shift)[0])/(2*eps) for j in range(n)])
        error=np.linalg.norm(J-fd)/np.linalg.norm(J);force=np.array([.013,-.007]);v=np.cos(np.arange(n));work=abs(force@(J@v)-(J.T@force)@v)
        rows.append(dict(segment=i,relative_J_error=float(error),virtual_work_absolute_error_J=float(work)))
    # Away from corner/face ties: compare independent SDF central differences.
    wallrows=[];fc=np.array([-.03363880995,-.095]);fr=.08350880995
    for point in (np.array([.052,-.0913]),np.array([.0461,-.081]),np.array([.051,-.098])):
        value,N=rod.walls(point,fc,fr);eps=1e-8
        fd=np.column_stack([(rod.walls(point+eps*np.eye(2)[j],fc,fr)[0]-rod.walls(point-eps*np.eye(2)[j],fc,fr)[0])/(2*eps) for j in range(2)])
        wallrows.append(float(np.max(abs(N-fd))))
    ok=all(r['relative_J_error']<1e-6 and r['virtual_work_absolute_error_J']<1e-12 for r in rows) and max(wallrows)<1e-6
    result=dict(status='PASS' if ok else 'FAIL',scope='STATIC MATERIAL POINT KINEMATIC / SDF JACOBIAN AND VIRTUAL WORK ONLY',rows=rows,wall_gradient_errors=wallrows,producer=ref(Path(__file__)),implementation=ref(Path(rod.__file__)),product_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
