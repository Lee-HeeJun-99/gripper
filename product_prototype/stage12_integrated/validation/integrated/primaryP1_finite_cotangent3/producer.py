"""Actual P1 finite surface row Jacobian and frozen-branch cotangent audit.
Every original row retained. Near-surface/nonunique signs flagged and excluded
from solve eligibility, never zeroed or reported as differentiability PASS.
"""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_port import left_jacobian
from primary_finite_surface_query import closest

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_finite_surface1/summary.json';s=json.loads(src.read_text());top_src=ROOT/'validation/integrated/primaryP1_finite_surface_independent2/summary.json';top=json.loads(top_src.read_text());local_src=ROOT/'validation/integrated/primaryP1_local_surface2/summary.json';local=json.loads(local_src.read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/s['output']['path']);topa=np.load(REPO/top['output']['path']);lf=np.load(REPO/local['output']['path']);rows=json.loads((REPO/s['rows']['path']).read_text());u=a['u_mm'];mo=int(a['motor_offset']);N=len(u);data={};surface={}
 for n in local['elastic_bodies']:
  X=a[n+'_points_mm'];t=a[n+'_tetra'];o=int(a[n+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);m=MeshTet(X.T,t.T);fi=m.boundary_facets();tri=m.facets[:,fi].T;parent=m.f2t[0,fi];normal=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);normal*=np.sign(np.sum(normal*(x[tri].mean(1)-x[t[parent]].mean(1)),1))[:,None];normal/=np.linalg.norm(normal,axis=1)[:,None];data[n]=dict(X=X,x=x,o=o,lookup={tuple(np.round(q,7)):i for i,q in enumerate(X)});surface[n]=dict(tri=tri,normal=normal)
 Jrow=[];Jcol=[];Jval=[];normals=[];fd=[];rng=np.random.default_rng(140714);selected=[]
 for i,row in enumerate(rows):
  owner=row['owner'];first=row['first'];p=data[owner];surf=surface[owner];tid=int(b['owner_triangle'][i])
  tri=surf['tri'][tid];q=b['first_points_mm'][i];cp=b['closest_points_mm'][i];d=q-cp;distance=np.linalg.norm(d);sign=-1 if topa['signed_gap_mm'][i]<0 else 1
  n=sign*d/distance if distance>1e-9 else surf['normal'][tid];normals.append(n)
  def add(cols,vals):Jrow.extend([i]*len(cols));Jcol.extend(cols);Jval.extend(vals)
  if first=='Motor':
   C=np.array([0,0,20])+u[mo:mo+3];tau=np.cross(q-C,n);add(list(range(mo,mo+6)),np.r_[n,left_jacobian(u[mo+3:mo+6]).T@tau].tolist())
  else:
   j=data[first]['lookup'][tuple(np.round(a['contact_points_mm'][i],7))];add((data[first]['o']+3*j+np.arange(3)).tolist(),n.tolist())
  weights=b['barycentric_weights'][i]
  for vertex,w in zip(tri,weights):add((p['o']+3*vertex+np.arange(3)).tolist(),(-w*n).tolist())
  # Separated finite-edge witnesses with full moving owner, including rigid
  # Motor point if present. Branch remains topologically separated under h.
  if distance>1e-3 and a['contact_force_N'][i]>1e-8 and np.count_nonzero(weights>1e-7)==2 and len(selected)<12:selected.append((i,row,tid,n,weights,sign))
 J=csr_matrix((Jval,(Jrow,Jcol)),shape=(2169,N));normals=np.array(normals);pressure=a['contact_force_N'];gc=J.T@pressure;res=lf['elastic_force_N']-gc+lf['bolt_force_pullback_N']-lf['applied_force_N'];wrench=np.zeros(6)
 for n,d in data.items():
  o=d['o'];f=gc[o:o+3*len(d['X'])].reshape(-1,3);wrench+=np.r_[f.sum(0),np.cross(d['x']*.001,f).sum(0)]
 mf=gc[mo:mo+3];mtau=np.linalg.solve(left_jacobian(u[mo+3:mo+6]).T,gc[mo+3:mo+6]);wrench+=np.r_[mf,mtau*.001+np.cross((np.array([0,0,20])+u[mo:mo+3])*.001,mf)]
 for i,row,tid,n,weights,sign in selected:
  p=data[row['owner']];surf=surface[row['owner']];q=b['first_points_mm'][i];tri=surf['tri'][tid];dv=rng.normal(size=3);dx=np.sin(p['X']@rng.normal(size=(3,3))*.02);qv=dv;analytic=float(n@qv-np.sum(weights[:,None]*dx[tri]*n));h=2e-7
  def value(t):
   x=(p['x']-q)+t*(dx-qv);tr=surf['tri'];nor=np.cross(x[tr[:,1]]-x[tr[:,0]],x[tr[:,2]]-x[tr[:,0]]);nor/=np.linalg.norm(nor,axis=1)[:,None];c=closest(np.zeros(3),x,tr,nor);return sign*c['distance_mm'],c
  attempts=[]
  for shrink in range(4):
   vals=[];features=[]
   for t in [h,-h,h/2,-h/2]:v,c=value(t);vals.append(v);features.append(c['triangle'])
   estimate=(4*(vals[2]-vals[3])/h-(vals[0]-vals[1])/(2*h))/3;err=abs(estimate-analytic);stable=all(k==tid for k in features);attempts.append(dict(h_mm=h,queried_triangles=features,error=err,branch_stable=stable))
   if stable:break
   h*=.5
  fd.append(dict(row=i,first=row['first'],owner=row['owner'],signed_gap_mm=float(topa['signed_gap_mm'][i]),source_triangle=tid,queried_triangles=features,branch_stable=stable,branch_step_attempts=attempts,analytic_N_per_N=analytic,Richardson=estimate,error=err))
 # Independent rigid-translation/rotation directions probe all2169Jacobianrows.
 rigid_errors=[]
 for axis in np.eye(3):
  d=np.zeros(N);r=np.zeros(N)
  for n,bod in data.items():
   o=bod['o'];d[o:o+3*len(bod['X'])]=np.tile(axis,len(bod['X']));r[o:o+3*len(bod['X'])]=np.cross(axis,bod['x']).ravel()
  d[mo:mo+3]=axis;C=np.array([0,0,20])+u[mo:mo+3];r[mo:mo+3]=np.cross(axis,C);r[mo+3:mo+6]=np.linalg.solve(left_jacobian(u[mo+3:mo+6]),axis);rigid_errors.append(dict(translation=float(np.max(abs(J@d))),rotation_mm=float(np.max(abs(J@r)))))
 checks=dict(all2169rows=J.shape==(2169,N),finite_weights=bool(np.all(np.isfinite(J.data))),allrow_rigid_work=max(max(v.values()) for v in rigid_errors)<1e-8,current_force=np.linalg.norm(wrench[:3])<1e-8,current_moment=np.linalg.norm(wrench[3:])<1e-10,separated_fullmoving_work=len(fd)>=2 and max(r['error'] for r in fd)<1e-8 and all(r['branch_stable'] for r in fd))
 np.savez_compressed(out/'cotangent.npz',J_data=J.data,J_indices=J.indices,J_indptr=J.indptr,J_shape=J.shape,contact_pullback_N=gc,unsolved_residual_N=res,normals=normals,signed_gaps_mm=topa['signed_gap_mm'],unresolved_near_surface=topa['unresolved_near_surface'])
 result=dict(status='ACTUAL_P1_FINITE_ROW_COTANGENT_PARTIAL_VALIDATION' if all(checks.values()) else 'ACTUAL_P1_FINITE_ROW_COTANGENT_CHECK_FAIL',candidate=s['candidate'],source=ref(src),topological_source=ref(top_src),local_support_source=ref(local_src),source_field=s['source_field'],producer=ref(out/'producer.py'),distance_implementation=ref(ROOT/'scripts/primary_finite_surface_query.py'),output=ref(out/'cotangent.npz'),checks={k:bool(v) for k,v in checks.items()},contact_rows=2169,Jacobian_nonzeros=J.nnz,separated_fullmoving_point_work=fd,rigid_motion_errors=rigid_errors,current_contact_wrench_N_Nm=wrench.tolist(),unsolved_stationarity_relative=float(np.linalg.norm(res)/max(np.linalg.norm(lf['applied_force_N']),1)),uncertified_near_surface_rows=int(topa['unresolved_near_surface'].sum()),uncertified_near_surface_active_rows=int(np.sum(topa['unresolved_near_surface']&(pressure>1e-8))),contact_update_eligible=False,contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['All2169rows retained, actual closestowner fullfiniteboundary and point/trianglebarycentric work pullback. Only separatededge witnesses test movingowner derivatives; query-centered displacements avoid largeglobal-coordinate cancellation. cotangent1 globalquery FDFAIL retained.','Nearsurface/nonsmooth tie rows use explicit representative ownerfacet direction for diagnostic residual only. Their normalcone/signedlinearization is UNQUALIFIED, not a contactsolve input or new equilibrium.','Oldpressure/boltforces/displacements reused only to measure unsolved residual, NOT transfer a solution or stress. All prior mesh/physicalBaseanchor/material/sourcecase/bearing/finitewire/friction/protector/globalenergy/full3Finger blocks preserved.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
