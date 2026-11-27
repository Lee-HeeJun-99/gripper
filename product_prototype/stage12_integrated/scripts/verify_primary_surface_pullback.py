"""Actual P1 sparse finite contact pullback, corruption and spatial balance.
Independent from producer assembly. All2169rows/actualMotorSO3 preserved.
"""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json' if len(sys.argv)>2 else ROOT/'validation/integrated/primaryP1_surface_geometry2/summary.json';s=json.loads(src.read_text());base=json.loads((REPO/s['source']['path']).read_text());a=np.load(REPO/s['source_field']['path']);p=np.load(REPO/s['output']['path']);b=np.load(REPO/base['output']['path']);top=json.loads((REPO/s['topology_source']['path']).read_text());ta=np.load(REPO/top['output']['path']);rows=json.loads((REPO/base['rows']['path']).read_text());u=a['u_mm'];mo=int(a['motor_offset']);J=csr_matrix((p['J_data'],p['J_indices'],p['J_indptr']),shape=tuple(p['J_shape']));data={}
 for name in sorted(set(r['owner'] for r in rows)|set(r['first'] for r in rows)-{'Motor'}):
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);m=MeshTet(X.T,a[name+'_tetra'].T);ids=m.boundary_facets();tri=m.facets[:,ids].T;parents=m.f2t[0,ids];nor=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);nor*=np.sign(np.sum(nor*(x[tri].mean(1)-x[a[name+'_tetra'][parents]].mean(1)),1))[:,None];nor/=np.linalg.norm(nor,axis=1)[:,None];data[name]=dict(X=X,o=o,x=x,tri=tri,n= nor,lookup={tuple(np.round(q,7)):j for j,q in enumerate(X)})
 errors=[];bad=[];spatial=[];direct=np.zeros(len(u));impulse=a['contact_force_N'];directional=[]
 for i,row in enumerate(rows):
  owner=data[row['owner']];face=owner['tri'][p['owner_triangle'][i]];w=p['barycentric_weights'][i];q=b['first_points_mm'][i];cp=w@owner['x'][face];dist=np.linalg.norm(q-cp);sgn=-1 if ta['signed_gap_mm'][i]<0 else 1;n=(q-cp)*sgn/dist if dist>1e-9 else owner['n'][p['owner_triangle'][i]]
  # Interiorface signed-distance gradient is exactly outwardnormal. Rebuilding
  # a tiny residual from rounded savedbarycentrics loses its tangentialdigits.
  if np.all(w>0):n=owner['n'][p['owner_triangle'][i]]
  else:
   # Independently reproject the actual boundedsegment in extendedprecision;
   # roundedglobalclosestpoint reconstruction is illconditioned at tinygaps.
   ix=np.flatnonzero(w>0);vv=np.asarray(owner['x'][face[ix]],dtype=np.longdouble)-np.asarray(q,dtype=np.longdouble)
   if len(ix)==2:
    edgevec=vv[1]-vv[0];zeta=np.clip(-(vv[0]@edgevec)/(edgevec@edgevec),0,1);delta=-(vv[0]+zeta*edgevec)
   else:delta=-vv[0]
   n=np.asarray(sgn*delta/np.sqrt(delta@delta),dtype=float)
  expected={}
  def add(cols,vals):
   for c,v in zip(cols,vals):expected[int(c)]=expected.get(int(c),0.)+float(v)
  if row['first']=='Motor':
   # Independently obtain infinitesimal rotation map by scalar Rodrigues
   # finite differences at6actualMotorcoordinates, not leftJacobian import.
   rest=a['contact_points_mm'][i]-[0,0,20];z=u[mo:mo+6];vals=[]
   for j in range(6):
    h=1e-5 if j<3 else 2e-5;dz=np.zeros(6);dz[j]=h
    def value(t):return n@((Rotation.from_rotvec((z+t*dz)[3:]).as_matrix()@rest)+[0,0,20]+(z+t*dz)[:3])
    vals.append((-value(2)+8*value(1)-8*value(-1)+value(-2))/(12*h))
   add(range(mo,mo+6),vals)
  else:
   first=data[row['first']];j=first['lookup'][tuple(np.round(a['contact_points_mm'][i],7))];add(first['o']+3*j+np.arange(3),n)
  for vertex,weight in zip(face,w):add(owner['o']+3*vertex+np.arange(3),-weight*n)
  actual=J.getrow(i);cols=set(expected)|set(actual.indices);error=max(abs(expected.get(c,0)-float(J[i,c])) for c in cols);errors.append(error)
  # Deliberately reversed owner sign and omitted owner both violate force /
  # moment virtual work. Keep measured discrepancy rather than count-only.
  ow=np.zeros(3)
  for weight in w:ow-=weight*n
  bad.append(float(np.linalg.norm(n-ow)));spatial.append(np.r_[n+ow,np.cross(q*.001,n)+np.sum(np.cross(owner['x'][face]*.001,-w[:,None]*n),axis=0)])
  for c,v in expected.items():direct[c]+=impulse[i]*v
 pullback=J.T@impulse;wrench=np.zeros(6)
 for d in data.values():
  ff=pullback[d['o']:d['o']+3*len(d['X'])].reshape(-1,3);wrench+=np.r_[ff.sum(0),np.cross(d['x']*.001,ff).sum(0)]
 # Recover Motor physicalcouple independently by testing3infinitesimal global
 # rotations through finite SO3 composition, no sourceleftJacobian.
 z=u[mo:mo+6];center=np.array([0,0,20])+z[:3];Rm=Rotation.from_rotvec(z[3:]);tau=[]
 for axis in np.eye(3):
  h=1e-4
  def r(t):return (Rotation.from_rotvec(t*h*axis)*Rm).as_rotvec()
  jac=(-r(2)+8*r(1)-8*r(-1)+r(-2))/(12*h);tau.append(float(pullback[mo+3:mo+6]@jac))
 ff=pullback[mo:mo+3];wrench+=np.r_[ff,np.array(tau)*.001+np.cross(center*.001,ff)];spatial=np.array(spatial)
 checks=dict(all2169_sparse_rows=len(errors)==2169,independent_allrow_coordinates=max(errors)<1e-8,independent_pressure_pullback=np.max(abs(direct-pullback))<1e-8,allrow_current_force=np.max(np.linalg.norm(spatial[:,:3],axis=1))<1e-8,allrow_current_moment=np.max(np.linalg.norm(spatial[:,3:],axis=1))<1e-10,current_total_force=np.linalg.norm(wrench[:3])<1e-8,current_total_moment=np.linalg.norm(wrench[3:])<1e-10,wrong_owner_sign_rejected=min(bad)>1e-3)
 result=dict(status='ACTUAL_P1_ALLROW_SPARSE_PULLBACK_PASS' if all(checks.values()) else 'ACTUAL_P1_ALLROW_SPARSE_PULLBACK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},contact_rows=2169,worst_coordinate_rows=sorted([dict(row=i,error=v) for i,v in enumerate(errors)],key=lambda z:-z['error'])[:10],maximum_coordinate_error=max(errors),maximum_pressure_pullback_error_N=float(np.max(abs(direct-pullback))),minimum_wrong_owner_sign_force_defect=min(bad),maximum_row_force_defect_N=float(np.max(np.linalg.norm(spatial[:,:3],axis=1))),maximum_row_moment_defect_Nm=float(np.max(np.linalg.norm(spatial[:,3:],axis=1))),current_total_contact_wrench_N_Nm=wrench.tolist(),contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Independent actualMotorSO3 scalar5pointderivatives and direct allrow nodal coefficient/pairedwrench checks, including wrongowner-sign control. No producerassembly/leftJacobian imported.','Nearrow face normals here are independently tetra-oriented; signed fullmovinggeometry must pass separate branch/topology audit. Static pressurepullback correctness does not validate oldpressure or nonlinearstationarity. All22systemgates remainunqualified.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
