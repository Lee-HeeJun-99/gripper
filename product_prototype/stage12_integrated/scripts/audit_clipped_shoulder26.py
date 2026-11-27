"""Independent integral and finite-domain audit of actual P1 material quadrature."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/sys.argv[1]/'summary.json';s=json.loads(src.read_text());out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert sha(REPO/s['quadrature']['path'])==s['quadrature']['SHA256'];groups=json.loads((REPO/s['quadrature']['path']).read_text());checks={};metrics=[];direction=json.loads((ROOT/'validation/integrated/primaryP1_ycapture_globalization3/summary.json').read_text());d=np.array(direction['historical_relative_Root_translation_mm']);alpha=direction['local_alpha']
 for g in groups:
  rows=g['rows'];q=np.array([r['root_point_mm'] for r in rows]);w=np.array([r['area_mm2'] for r in rows]);sign=g['sign'];rtri=np.array(g['root_all_triangles_mm']);ftri=np.array(g['owner_all_triangles_mm']);ridx=np.array([r['root_triangle'] for r in rows]);fidx=np.array([r['owner_triangle'] for r in rows]);rw=np.array([r['root_barycentric'] for r in rows]);fw=np.array([r['owner_barycentric'] for r in rows]);qr=np.einsum('ni,nij->nj',rw,rtri[ridx]);qf=np.einsum('ni,nij->nj',fw,ftri[fidx]);A=w.sum();center=np.array([64,20*sign,-4.7]);mom=(w[:,None]*q).sum(0);second=np.einsum('n,ni,nj->ij',w,q,q);expected=A*np.outer(center,center);expected[0,0]+=A*8**2/12;expected[2,2]+=A*3.4**2/12
  # Independent scalar signed-volume plane distance, no imported producer operator.
  def gaps(a,b):
   h=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);h*=(-sign*np.sign(h[:,1]))[:,None];return np.einsum('ni,ni->n',a-b[:,0],h)/np.linalg.norm(h,axis=1)
  gap=gaps(qr,ftri[fidx]);close=gaps(qr+np.array([0,sign*.1,0]),ftri[fidx]);points=q+alpha*d;bounds=np.array([[60,68],[-6.5,-3.]])
  # Entire planar shoulder bounds derive from actual owner vertices, not invented planes.
  lo=ftri[:,:,[0,2]].min(axis=(0,1));hi=ftri[:,:,[0,2]].max(axis=(0,1));assert np.max(abs(np.c_[lo,hi]-bounds))<1e-7
  margin=np.minimum(points[:,[0,2]]-lo,hi-points[:,[0,2]]).min();limits=[]
  for axis,j in [(0,0),(2,1)]:
   if d[axis]>0:limits.extend(((hi[j]-q[:,axis])/d[axis]).tolist())
   elif d[axis]<0:limits.extend(((lo[j]-q[:,axis])/d[axis]).tolist())
  first_feature=min(limits) if limits else None
  # Unit normal pressure is a virtual-load probe, not accepted reaction. Torque
  # tested for both sides about fixed global origin using reference material area.
  normal=np.array([0,-sign,0]);force=A*normal;moment=np.cross(mom,normal);uniform1Nforce=force/A;uniform1Nmoment=moment/A
  # Independent pure rigid transform invariance of scalar gap; rotation includes all axes.
  axis=np.array([1.,2.,3.]);axis/=np.linalg.norm(axis);K=np.array([[0,-axis[2],axis[1]],[axis[2],0,-axis[0]],[-axis[1],axis[0],0]]);R=np.eye(3)+np.sin(.4)*K+(1-np.cos(.4))*(K@K);shift=np.array([1.,-2.,3.]);qh=qr@R.T+shift;th=ftri[fidx]@R.T+shift;h=np.cross(th[:,1]-th[:,0],th[:,2]-th[:,0]);n0=np.cross(ftri[fidx,1]-ftri[fidx,0],ftri[fidx,2]-ftri[fidx,0]);orientation=-sign*np.sign(n0[:,1]);rgap=np.einsum('ni,ni->n',qh-th[:,0],h*orientation[:,None])/np.linalg.norm(h,axis=1)
  rec=dict(mesh_level=g['mesh_level'],sign=sign,area_mm2=float(A),centroid_mm=(mom/A).tolist(),area_error_mm2=abs(float(A)-27.2),first_moment_error_mm3=float(abs(mom-A*center).max()),second_moment_error_mm4=float(abs(second-expected).max()),root_reconstruction_error_mm=float(abs(qr-q).max()),owner_reconstruction_error_mm=float(abs(qf[:,[0,2]]-q[:,[0,2]]).max()),nominal_gap_error_mm=float(abs(gap-.1).max()),closed_gap_error_mm=float(abs(close).max()),rigid_gap_error_mm=float(abs(rgap-gap).max()),archived_direction_local_alpha=alpha,minimum_finite_face_margin_mm=float(margin),first_finite_face_exit_alpha=float(first_feature),virtual_unit_pressure_force_N=force.tolist(),virtual_unit_pressure_moment_Nmm=moment.tolist(),virtual_distributed1N_force_N=uniform1Nforce.tolist(),virtual_distributed1N_moment_Nmm=uniform1Nmoment.tolist(),operating_reaction_claimed=False)
  metrics.append(rec)
 checks=dict(area=all(r['area_error_mm2']<1e-8 for r in metrics),linear_moment=all(r['first_moment_error_mm3']<1e-8 for r in metrics),quadratic_moment=all(r['second_moment_error_mm4']<1e-7 for r in metrics),material_point_reconstruction=all(max(r['root_reconstruction_error_mm'],r['owner_reconstruction_error_mm'])<1e-10 for r in metrics),gap_and_closure=all(max(r['nominal_gap_error_mm'],r['closed_gap_error_mm'])<1e-10 for r in metrics),rigid_objectivity=all(r['rigid_gap_error_mm']<1e-10 for r in metrics),finite_local_sample_domain=all(r['minimum_finite_face_margin_mm']>0 and r['first_finite_face_exit_alpha']>alpha for r in metrics),negative_area_control=abs(metrics[0]['area_mm2']-28)>.7,negative_owner_omission_detected=abs(metrics[0]['virtual_unit_pressure_force_N'][1])>27)
 dump(out/'summary.json',dict(status='ACTUAL_P1_INDEPENDENT_MATERIAL_AREA_LOAD_AUDIT_PASS' if all(checks.values()) else 'ACTUAL_P1_INDEPENDENT_MATERIAL_AREA_LOAD_AUDIT_FAIL',candidate=s['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},metrics=metrics,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_equilibria=0,limitations=['Complete initial shoulder-overlap quadrature verified, not full Root/Frame contact or fivebody solve.','Finite domain test concerns interior material quadrature samples; it cannot certify continuous swept surface, physical force equilibrium or edge normal cones.','Virtual pressure/distributed1N probes are not nominal operating reactions at open0.1mmgap and not a strength/capacity test.','New sourcefield not constructed. All22gates and Stage3 remain blocked.']));print(json.dumps(dict(checks=checks,metrics=metrics)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
