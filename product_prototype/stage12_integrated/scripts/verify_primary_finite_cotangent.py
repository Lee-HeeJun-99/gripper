"""Independent extended-precision fixed-edge virtual work at actual P1 rows.
No producer/closestpoint implementation imported. Full movingowner and Motor
coordinate differences; branch-local derivative, NOT near-surface normalcone.
"""
import sys,json,shutil
import numpy as np
from scipy.sparse import csr_matrix
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump

def rot(v):
 T=np.longdouble;v=np.array(v,dtype=T);t=np.sqrt(v@v);S=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]],dtype=T);return np.eye(3,dtype=T)+np.sin(t)/t*S+(1-np.cos(t))/(t*t)*S@S

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_finite_cotangent3/summary.json';s=json.loads(src.read_text());base=json.loads((REPO/s['source']['path']).read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/base['output']['path']);c=np.load(REPO/s['output']['path']);J=csr_matrix((c['J_data'],c['J_indices'],c['J_indptr']),shape=tuple(c['J_shape']));u=a['u_mm'];mo=int(a['motor_offset']);T=np.longdouble;tests=[]
 for test in s['separated_fullmoving_point_work']:
  i=test['row'];owner=test['owner'];X=a[owner+'_points_mm'];tet=a[owner+'_tetra'];o=int(a[owner+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);mesh=MeshTet(X.T,tet.T);tri=mesh.facets[:,mesh.boundary_facets()].T;face=tri[int(b['owner_triangle'][i])];w=b['barycentric_weights'][i];ix=np.flatnonzero(w>1e-7);assert len(ix)==2;edgeids=face[ix];rest=np.array(a['contact_points_mm'][i],dtype=T);z0=np.r_[np.array(u[mo:mo+6],dtype=T),np.array(x[edgeids].ravel(),dtype=T)];sign=1 if c['signed_gaps_mm'][i]>=0 else -1
  def value(z):
   q=rot(z[3:6])@(rest-np.array([0,0,20],dtype=T))+np.array([0,0,20],dtype=T)+z[:3];aa=z[6:9];bb=z[9:12];e=bb-aa;v=((q-aa)@e)/(e@e);assert 0<v<1;d=q-aa-v*e;return T(sign)*np.sqrt(d@d)
  cols=np.r_[np.arange(mo,mo+6),o+3*edgeids[0]+np.arange(3),o+3*edgeids[1]+np.arange(3)];analytic=np.array(J.getrow(i)[:,cols].toarray()).ravel();est=[]
  for j in range(12):
   h=T('2e-8') if 3<=j<6 else T('2e-6');dz=np.zeros(12,dtype=T);dz[j]=h;v=(-value(z0+2*dz)+8*value(z0+dz)-8*value(z0-dz)+value(z0-2*dz))/(12*h);est.append(float(v))
  error=abs(np.array(est)-analytic);wrong=analytic.copy();wrong[6:]*=-1;negative=float(np.max(abs(wrong-np.array(est))));tests.append(dict(row=i,owner=owner,coordinate_count=12,edge_nodes=edgeids.tolist(),source_signed_gap_mm=float(c['signed_gaps_mm'][i]),fixed_edge_value_mm=float(value(z0)),maximum_derivative_error=float(error.max()),translation_error_N_per_N=float(max(error[:3].max(),error[6:].max())),Motor_rotation_error_mm=float(error[3:6].max()),wrong_owner_sign_detected=negative,derivatives=est,analytic=analytic.tolist()))
 checks=dict(actual_selected_rows=len(tests)==3,Motor_and_owner_derivatives=max(t['maximum_derivative_error'] for t in tests)<1e-8,wrong_owner_sign_rejected=min(t['wrong_owner_sign_detected'] for t in tests)>1e-3,fullpart_branch_tests=all(t['branch_stable'] for t in s['separated_fullmoving_point_work']))
 result=dict(status='ACTUAL_P1_INDEPENDENT_FINITE_EDGE_COTANGENT_PASS' if all(checks.values()) else 'ACTUAL_P1_FINITE_EDGE_INDEPENDENT_CHECK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},coordinate_derivatives=sum(t['coordinate_count'] for t in tests),maximum_derivative_error=max(t['maximum_derivative_error'] for t in tests),precision_bits=int(np.finfo(T).nmant),actual_edge_tests=tests,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independent12coordinates/actualMotorSO3+owneredge at3actualfinitegaprows, extendedprecision5point scalar derivatives. Fullnearestsurface branch checks are source3directiontests. NOT certification of65nearsurface rows,64active normalcones, equilibrium/contactmesh/physicalanchor/globalenergy/full3Finger.')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
