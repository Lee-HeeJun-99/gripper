"""Actual P1 socket-head bolt full-solid Neumann sensitivity, NOT installed thread law.
No support is fixed. Actual head bearing annulus and terminal end are loaded.
Terminal end traction is a declared counterfactual; thread flanks/preload absent.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import qr
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_body34 import meshpart
from primary_anchor_pointfine39 import common_faces,map_patch
from primary_motor_bearing_wrenches import faces
from incremental_stage1 import read
from validate_base_anchor36 import props

def main():
 tag,part,h=sys.argv[1:4];h=float(h);out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text())
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());rp=cad['part_references'][part];shape=read(REPO/rp['path']);base=read(REPO/cad['part_references']['TEST_BASE']['path']);seat=common_faces(shape,base,2,60);tip=faces(shape,2,80);assert len(seat)==len(tip)==1
 dump(out/'inputs.json',dict(candidate=ref(cp),actual_part=rp,producer=ref(out/'producer.py'),h_mm=h,curvature=24,E_MPa=200000.,nu=.3,material_status='conditional typical steel;NOT source minimum',boundary='self-balanced unit head-seat -Z / actual terminal-end +Z traction;terminal source counterfactual,not installed nut thread',physical_fixed_DOF=0))
 assert not(ROOT/'runtime/STOP').exists();p,t,tri,V=meshpart(REPO/rp['path'],h,24);N=3*len(p);m=MeshTet(p.T,t.T);la,mu=lame_parameters(200000.,.3);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 body=dict(p=p,tri=tri);F=np.zeros((N,2));journals=[map_patch(body,face,2,z,np.array(d,float),j,F) for j,(face,z,d) in enumerate([(seat[0],60,[0,0,-1]),(tip[0],80,[0,0,1])])];f=(F[:,0]+F[:,1])[:,None];origin=p.mean(0);R=np.zeros((N,6))
 for j,e in enumerate(np.eye(3)):R[:,j]=np.broadcast_to(e,p.shape).ravel();R[:,j+3]=np.cross(e,p-origin).ravel()/25
 Q=R.T/len(p)
 if len(sys.argv)>4 and sys.argv[4]=='sparsegauge':
  # Algebraic quotient only: restore every DOF and original mean rigid gauge.
  _,_,pivot=qr(R.T,mode='economic',pivoting=True);anchors=np.sort(pivot[:6]);free=np.setdiff1d(np.arange(N),anchors);dual=np.linalg.solve(R.T@Q.T,R.T@f);balanced=f-Q.T@dual;u=np.zeros_like(f);u[free]=splu((K[free][:,free]/200000.).tocsc(),permc_spec='MMD_AT_PLUS_A').solve(balanced[free]/200000.);u-=R@np.linalg.solve(Q@R,Q@u)
 else:
  A=sparse.bmat([[K/200000.,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc');sol=splu(A).solve(np.vstack([f/200000.,np.zeros((6,1))]));u=sol[:N];dual=sol[N:]*200000.
 res=K@u-f;C=float((f.T@u)[0,0]);work=float((u.T@K@u)[0,0]);net=np.r_[f.reshape(-1,3).sum(0),np.cross(p,f.reshape(-1,3)).sum(0)];geomV=float(abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]])).sum()/6)
 np.savez_compressed(out/'fields.npz',points_mm=p,tetra=t,boundary_triangles=tri,U=u,F=f,port_F=F,dual=dual,Q=Q,R=R)
 nominal=20/(200000.*np.pi*2.5**2);checks=dict(force=float(abs(res).max())<1e-8,moment_Nm=float(abs(net[3:]).max())*.001<1e-10,no_gauge_support=float(abs(Q.T@dual).max())<1e-8,positive_compliance=C>0,finite=bool(np.isfinite(u).all()),work=abs(work-C)/C<1e-8)
 dump(out/'summary.json',dict(status='ACTUAL_P1_FULL_BOLT_CONDITIONAL_NEUMANN_LOCAL_PASS' if all(checks.values()) else 'ACTUAL_P1_FULL_BOLT_CONDITIONAL_NEUMANN_FAIL',candidate=ref(cp),actual_part_ID=part,actual_part=rp,inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),fields=ref(out/'fields.npz'),boundary_journal=journals,checks=checks,nodes=len(p),tetra=len(t),fixed_DOF=0,rigid_gauges=6,E_MPa=200000.,nu=.3,h_mm=h,algebraic_solver='sparsequotient_restored' if len(sys.argv)>4 else 'bordered',CAD_volume_mm3=V,mesh_volume_mm3=geomV,unit_load_wrench_N_Nmm=net.tolist(),force_residual_N=float(abs(res).max()),gauge_force_N=float(abs(Q.T@dual).max()),unit_compliance_mm_N=C,strain_work_Nmm=work,nominal20mm_major_shank_mm_N=nominal,full_bolt_to_uniform20mm_ratio=C/nominal,physical_stack_qualified=False,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Actual socket/head/fullshank geometry,not ideal coupon;terminal axial source is counterfactual,NOT physical thread transfer.','Actual nut/head contact pressure,threadcore/flank/engagement/preload/material minimum remain unresolved.','Conditional typical steel only;no strength or operating load qualification.']));print(json.dumps(dict(checks=checks,compliance=C,nodes=len(p))))
if __name__=='__main__':main()
