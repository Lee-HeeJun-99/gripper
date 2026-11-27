"""Actual all-row P1 finite nearest-surface/owner work validation.
Use original tetra, all2169rows, current saved field; no equilibrium claimed.
"""
import sys,json,shutil,time
import numpy as np
from skfem import MeshTet
from scipy.spatial.transform import Rotation
from scipy.sparse import csr_matrix
from baseline_registry import ROOT,REPO,ref,dump
from primary_surface_geometry import closest,T
from primary_finite_port import left_jacobian

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');shutil.copyfile(ROOT/'scripts/primary_surface_geometry.py',out/'geometry.py')
 src=ROOT/'validation/integrated/primaryP1_finite_surface1/summary.json';base=json.loads(src.read_text());top_src=ROOT/'validation/integrated/primaryP1_finite_surface_independent2/summary.json';top=json.loads(top_src.read_text());a=np.load(REPO/base['source_field']['path']);old=np.load(REPO/base['output']['path']);topa=np.load(REPO/top['output']['path']);rows=json.loads((REPO/base['rows']['path']).read_text());u=a['u_mm'];mo=int(a['motor_offset']);data={}
 for name in sorted(set(r['owner'] for r in rows)|set(r['first'] for r in rows)-{'Motor'}):
  X=a[name+'_points_mm'];tet=a[name+'_tetra'];o=int(a[name+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);m=MeshTet(X.T,tet.T);fi=m.boundary_facets();tri=m.facets[:,fi].T;parent=m.f2t[0,fi];nor=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);flip=np.sum(nor*(x[tri].mean(1)-x[tet[parent]].mean(1)),1)<0;nor[flip]*=-1;nor/=np.linalg.norm(nor,axis=1)[:,None];data[name]=dict(X=X,x=x,o=o,tri=tri,normal=nor,lookup={tuple(np.round(q,7)):j for j,q in enumerate(X)})
 R=[];C=[];V=[];dist=[];tids=[];weights=[];points=[];tests=[];changed=[];near=[];ties=[];rng=np.random.default_rng(140714)
 selected=[244,258,263]
 # Exact same random directions as cotangent3 for the3prior witnesses.
 directions={i:rng.normal(size=3) for i in []}
 for i,row in enumerate(rows):
  d=data[row['owner']];q=np.asarray(old['first_points_mm'][i],dtype=T);x=np.asarray(d['x'],dtype=T);c=closest(q,x,d['tri']);k=c['triangle'];face=d['tri'][k];w=c['weights'];distance=c['distance_mm'];sign=-1 if topa['signed_gap_mm'][i]<0 else 1
  n=-sign*c['relative_point_mm']/distance if distance>1e-9 else d['normal'][k]
  if np.all(w>0):n=d['normal'][k]
  dist.append(float(distance));tids.append(k);weights.append(w);points.append(c['point_mm']);ties.append(len(c['candidate_triangles']))
  if k!=int(old['owner_triangle'][i]) or np.max(abs(w-old['barycentric_weights'][i]))>1e-8:changed.append(dict(row=i,old_triangle=int(old['owner_triangle'][i]),new_triangle=k,old_weights=old['barycentric_weights'][i].tolist(),new_weights=[float(z) for z in w],weight_change=float(np.max(abs(w-old['barycentric_weights'][i]))),distance_change_mm=float(distance-abs(old['gap_mm'][i]))))
  def add(cols,vals):R.extend([i]*len(cols));C.extend(cols);V.extend(np.asarray(vals,dtype=float).tolist())
  if row['first']=='Motor':
   center=np.array([0,0,20])+u[mo:mo+3];tau=np.cross(q-center,n);add(list(range(mo,mo+6)),np.r_[n,left_jacobian(u[mo+3:mo+6]).T@tau])
  else:
   fd=data[row['first']];j=fd['lookup'][tuple(np.round(a['contact_points_mm'][i],7))];add(fd['o']+3*j+np.arange(3),n)
  for vertex,bw in zip(face,w):add(d['o']+3*vertex+np.arange(3),-bw*n)
  if distance<=1e-9:
   # Retain complete incident feature; enumerate oriented normals at the
   # actual nearest simplex, no artificial extension or zeroed old pressure.
   support=face[np.asarray(w)>1e-12];incident=np.flatnonzero(np.all(np.isin(support,d['tri']) if False else np.stack([np.any(d['tri']==v,axis=1) for v in support]),axis=0));normals=d['normal'][incident];spread=float(np.max(np.linalg.norm(normals-normals[0],axis=1)))
   near.append(dict(row=i,owner=row['owner'],first=row['first'],distance_mm=float(distance),feature_nodes=support.tolist(),incident_facets=incident.tolist(),normal_spread=spread,pressure_N=float(a['contact_force_N'][i]),representative_only=True))
  if i in selected:
   dv=np.asarray(rng.normal(size=3),dtype=T);dx=np.asarray(np.sin(d['X']@rng.normal(size=(3,3))*.02),dtype=T);analytic=np.dot(n,dv)-np.sum(w[:,None]*dx[face]*n);attempts=[]
   for hstr in ['2e-7','1e-7','5e-8','2.5e-8','1.25e-8','6.25e-9','3.125e-9','1.5625e-9']:
    h=T(hstr);vals=[];features=[];simplices=[]
    for hmul in [1,-1,T('.5'),T('-.5')]:
     ct=closest(np.zeros(3,dtype=T),(x-q)+hmul*h*(dx-dv),d['tri']);vals.append(sign*ct['distance_mm']);features.append(ct['triangle']);simplices.append(sorted(d['tri'][ct['triangle']][ct['weights']>T('1e-16')].tolist()))
    estimate=(4*(vals[2]-vals[3])/h-(vals[0]-vals[1])/(2*h))/3;error=abs(estimate-analytic);attempts.append(dict(h_mm=float(h),triangles=features,simplices=simplices,feature_stable=all(z==sorted(face[w>T('1e-16')].tolist()) for z in simplices),error=float(error),derivative=float(estimate)))
   consecutive=0;qualified=False
   for z in attempts:
    consecutive=consecutive+1 if z['feature_stable'] and z['error']<1e-8 else 0
    qualified |= consecutive>=3
   tests.append(dict(qualified_three_successive_steps=qualified,row=i,analytic=float(analytic),attempts=attempts,maximum_error=float(max(z['error'] for z in attempts)),minimum_error=float(min(z['error'] for z in attempts)),old_triangle=int(old['owner_triangle'][i]),new_triangle=k))
 J=csr_matrix((V,(R,C)),shape=(2169,len(u)));rigid=[]
 for axis in np.eye(3):
  tr=np.zeros(len(u));rot=np.zeros(len(u))
  for d in data.values():
   o=d['o'];tr[o:o+3*len(d['X'])]=np.tile(axis,len(d['X']));rot[o:o+3*len(d['X'])]=np.cross(axis,d['x']).ravel()
  center=np.array([0,0,20])+u[mo:mo+3];tr[mo:mo+3]=axis;rot[mo:mo+3]=np.cross(axis,center);rot[mo+3:mo+6]=np.linalg.solve(left_jacobian(u[mo+3:mo+6]),axis);rigid.append(dict(translation=float(np.max(abs(J@tr))),rotation_mm=float(np.max(abs(J@rot)))))
 checks=dict(all2169rows=len(dist)==2169,independent_prior_distance=float(np.max(abs(np.array(dist)-topa['unsigned_distance_mm'])))<1e-8,all_simplex_weights=float(np.min(weights))>=0,all_rigid_work=max(max(z.values()) for z in rigid)<1e-8,fullmoving_separated_queries=len(tests)==3 and all(z['qualified_three_successive_steps'] for z in tests))
 np.savez_compressed(out/'geometry.npz',distance_mm=dist,owner_triangle=tids,barycentric_weights=np.array(weights,dtype=float),closest_points_mm=np.array(points,dtype=float),J_data=J.data,J_indices=J.indices,J_indptr=J.indptr,J_shape=J.shape,near_rows=[z['row'] for z in near])
 dump(out/'near_features.json',near);dump(out/'changed_features.json',changed)
 result=dict(status='ACTUAL_P1_EXTENDED_FINITE_QUERY_PARTIAL_PASS' if all(checks.values()) else 'ACTUAL_P1_EXTENDED_FINITE_QUERY_CHECK_FAIL',candidate=base['candidate'],source=ref(src),source_field=base['source_field'],topology_source=ref(top_src),producer=ref(out/'producer.py'),geometry_implementation=ref(out/'geometry.py'),output=ref(out/'geometry.npz'),near_features=ref(out/'near_features.json'),changed_features=ref(out/'changed_features.json'),checks={k:bool(v) for k,v in checks.items()},contact_rows=2169,changed_triangle_or_weights=len(changed),maximum_prior_unsigned_distance_error_mm=float(np.max(abs(np.array(dist)-topa['unsigned_distance_mm']))),separated_fullmoving_tests=tests,rigid_work_errors=rigid,near_surface_rows=len(near),near_surface_active_rows=sum(z['pressure_N']>1e-8 for z in near),near_surface_normal_spread_max=max(z['normal_spread'] for z in near),precision_bits=np.finfo(T).nmant,maximum_roundoff_tied_triangles=max(ties),contact_update_eligible=False,contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['All2169originalqueries on actual current tetra boundary, allfacets searched; local cross-product plane and extendedprecision avoid sliver Gram cancellation. No CAD/BOM change.','Nearsurface and roundoff ties retained and enumerated, not certified normals or zeroed gaps. Distances agreeing does not certify barycentrics or fullquery derivative.','No new equilibrium/stress/contactsolve/globalenergy/mesh/physicalanchor/sourceparts/finitewire/friction/protector/full3Finger certification. All22systemgates remainunqualified.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
