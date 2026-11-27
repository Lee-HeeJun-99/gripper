"""Independent failed39row signed-feature P1 closest-feature and signed moving-work audit.
Orthogonal triangle projection, exhaustive segment search, outward tetra-face
orientation, extended-precision winding. Imports no producer geometry code.
"""
import sys,json,shutil,time
import numpy as np
from skfem import MeshTet
from scipy.sparse import csr_matrix
from baseline_registry import ROOT,REPO,ref,dump
T=np.longdouble

def query(q,x,tri,normals):
 v=x[tri]-q;a=v[:,0];e=v[:,1]-a;f=v[:,2]-a
 # Modified Gram-Schmidt plane coordinates, independent of producer cross
 # product barycentrics and original cancellation-prone2x2Gram inverse.
 el=np.sqrt(np.sum(e*e,1));eh=e/el[:,None];fp=f-np.sum(f*eh,1)[:,None]*eh;fl=np.sqrt(np.sum(fp*fp,1));fh=fp/fl[:,None]
 st=np.empty((len(tri),2),dtype=T);st[:,1]=-np.sum(a*fh,1)/fl;st[:,0]=(-np.sum(a*eh,1)-st[:,1]*np.sum(f*eh,1))/el
 p=a+st[:,0,None]*e+st[:,1,None]*f;w=np.c_[1-st.sum(1),st];dd=np.sum(p*p,1);dd[np.any(w<0,axis=1)]=np.inf;typ=np.zeros(len(tri),int)
 for j in range(3):
  ed=v[:,(j+1)%3]-v[:,j];z=np.clip(-np.sum(v[:,j]*ed,1)/np.sum(ed*ed,1),0,1);pt=v[:,j]+z[:,None]*ed;d2=np.sum(pt*pt,1);b=d2<dd;dd[b]=d2[b];p[b]=pt[b];w[b]=0;w[b,j]=1-z[b];w[b,(j+1)%3]=z[b];typ[b]=j+1
 k=int(np.argmin(dd));d=np.sqrt(dd[k]);sgn=1 if -p[k]@normals[k]>=0 else -1
 return dict(value=sgn*d,distance=d,k=k,weights=w[k],delta=-p[k],feature=tuple(sorted(tri[k][w[k]>T('1e-16')].tolist())),type=int(typ[k]))

def winding(q,x,tri):
 v=x[tri]-q;l=np.sqrt(np.sum(v*v,axis=2));num=np.sum(v[:,0]*np.cross(v[:,1],v[:,2]),1);den=l.prod(1)+np.sum(v[:,0]*v[:,1],1)*l[:,2]+np.sum(v[:,1]*v[:,2],1)*l[:,0]+np.sum(v[:,2]*v[:,0],1)*l[:,1]
 return np.sum(2*np.arctan2(num,den))/(4*np.arccos(T(-1)))

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_surface_geometry3/summary.json';s=json.loads(src.read_text());base=json.loads((REPO/s['source']['path']).read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/base['output']['path']);p=np.load(REPO/s['output']['path']);rows=json.loads((REPO/base['rows']['path']).read_text());top=json.loads((REPO/s['topology_source']['path']).read_text());topa=np.load(REPO/top['output']['path']);u=a['u_mm'];data={}
 for name in sorted(set(r['owner'] for r in rows)):
  X=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);x=np.asarray(X+u[o:o+3*len(X)].reshape(-1,3),dtype=T);mesh=MeshTet(X.T,t.T);ids=mesh.boundary_facets();tri=mesh.facets[:,ids].T;parent=mesh.f2t[0,ids];n=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);flip=np.sum(n*(x[tri].mean(1)-x[t[parent]].mean(1)),1)<0;n[flip]*=-1;n/=np.sqrt(np.sum(n*n,1))[:,None];oriented=tri.copy();oriented[flip]=oriented[flip][:,[0,2,1]];dx=np.asarray(np.sin(X@np.array([[.011,.007,-.003],[.005,-.009,.004],[.008,.003,.006]])),dtype=T);data[name]=dict(x=x,tri=tri,n=n,oriented=oriented,dx=dx)
 tests=[];near=[];distance_errors=[];changed=[];maxweight=0.;all_converged=True;unsigned=[];signed=[];normals=[];ties_detected=[]
 prior_path=ROOT/'validation/integrated/primaryP1_surface_branches1/summary.json';prior=json.loads(prior_path.read_text());selected=prior['failed_work_rows'];assert len(selected)==39
 for i in selected:
  row=rows[i]
  if i%100==0:
   assert not(ROOT/'runtime/STOP').exists();print('row',i,'seconds',time.monotonic()-start,flush=True)
  d=data[row['owner']];x=d['x'];tri=d['tri'];q=np.asarray(b['first_points_mm'][i],dtype=T);c=query(q,x,tri,d['n']);distance_errors.append(float(abs(c['distance']-p['distance_mm'][i])));unsigned.append(float(c['distance']));normal=d['n'][c['k']]
  if c['distance']<=T('1e-9'):
   wind=winding(q,x,d['oriented']);plane=-c['delta']@normal*-1;sign=-1 if abs(wind)>T('.5') else 1;werr=min(abs(wind),abs(abs(wind)-1));sgap=sign*c['distance'];near.append(dict(row=i,winding=float(wind),winding_integer_error=float(werr),signed_gap_mm=float(sgap),oriented_plane_gap_mm=float(c['delta']@normal),weights=[float(z) for z in c['weights']],feature_nodes=list(c['feature']),facet=c['k'],sign_agreement=bool(sign*(c['delta']@normal)>=0)))
  else:
   sign=-1 if topa['signed_gap_mm'][i]<0 else 1;sgap=sign*c['distance']
  signed.append(float(sgap));n=sign*c['delta']/c['distance'] if c['distance']>T('1e-9') else normal
  if len(c['feature'])==3:n=normal
  normals.append(n)
  # First and owner move independently. Sourcefield polynomialdX plus
  # row-specific first velocity; allfacet query at each of4stencilpoints.
  dv=np.array([np.sin(i*.31),np.cos(i*.13),np.sin(i*.27+.4)],dtype=T);dx=d['dx'];face=tri[c['k']];analytic=n@dv-np.sum(c['weights'][:,None]*dx[face]*n);attempts=[];consecutive=0;passed=False
  for hstr in ['2e-7','1e-7','5e-8','2.5e-8','1.25e-8','6.25e-9','3.125e-9','1.5625e-9','7.8125e-10','3.90625e-10','1.953125e-10','9.765625e-11','4.8828125e-11','2.44140625e-11','1.220703125e-11','6.103515625e-12','3.0517578125e-12','1.52587890625e-12']:
   h=T(hstr);vals=[];features=[]
   for factor in [T(1),T(-1),T('.5'),T('-.5')]:
    moved=(x-q)+factor*h*(dx-dv);ct=query(np.zeros(3,dtype=T),moved,tri,d['n']);features.append(ct['feature'])
    # Separated branch keeps independent topology sign. Near-surface face
    # gets current outward plane sign; winding checked independently above.
    if len(ct['feature'])!=3:vals.append(sign*ct['distance'])
    else:
     tt=tri[ct['k']];nn=np.cross(moved[tt[1]]-moved[tt[0]],moved[tt[2]]-moved[tt[0]]);nn/=np.sqrt(nn@nn)
     if nn@d['n'][ct['k']]<0:nn=-nn
     vals.append(ct['distance']*(1 if ct['delta']@nn>=0 else -1))
   estimate=(4*(vals[2]-vals[3])/h-(vals[0]-vals[1])/(2*h))/3;err=abs(estimate-analytic);stable=all(f==c['feature'] for f in features);ok=stable and err<T('1e-8');consecutive=consecutive+1 if ok else 0
   attempts.append(dict(h_mm=float(h),feature_stable=stable,features=[list(f) for f in features],error=float(err),derivative=float(estimate)))
   if consecutive>=3:passed=True;break
  all_converged &= passed
  test=dict(row=i,owner=row['owner'],distance_mm=float(c['distance']),signed_gap_mm=float(sgap),base_feature=list(c['feature']),analytic=float(analytic),qualified_three_successive_steps=passed,attempts=attempts)
  tests.append(test)
  if any(not z['feature_stable'] for z in attempts):changed.append(i)
 signed=np.array(signed);nearok=all(z['winding_integer_error']<1e-5 and z['sign_agreement'] for z in near);checks=dict(all39failed_rows=len(tests)==39,independent_unsigned_distance=max(distance_errors)<1e-8,selected_near_topology_and_plane_sign=nearok,allrow_moving_work_three_successive=all_converged)
 dump(out/'rows.json',tests);dump(out/'near_topology.json',near);np.savez_compressed(out/'signed_geometry.npz',signed_gap_mm=signed,normals=np.array(normals,dtype=float),unsigned_distance_mm=unsigned)
 fail=[z['row'] for z in tests if not z['qualified_three_successive_steps']];pressure=a['contact_force_N'][selected];positive=(signed>1e-8)&(pressure>1e-8)
 result=dict(status='ACTUAL_P1_FAILED_ROWS_SIGNED_BRANCH_WORK_PASS' if all(checks.values()) else 'ACTUAL_P1_FAILED_ROWS_SIGNED_BRANCH_WORK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),rows=ref(out/'rows.json'),near_topology=ref(out/'near_topology.json'),output=ref(out/'signed_geometry.npz'),checks={k:bool(v) for k,v in checks.items()},contact_rows=len(tests),failed_work_rows=fail,rows_with_feature_transition=changed,near_surface_rows=len(near),near_winding_max_integer_error=max((z['winding_integer_error'] for z in near),default=0.),maximum_unsigned_distance_error_mm=max(distance_errors),prior_allrow_result=ref(prior_path),selected_original_rows=selected,positive_gap_with_old_pressure=int(positive.sum()),old_pressure_on_positive_gap_N=float(pressure[positive].sum()),penetrations=int(np.sum(signed<-1e-8)),maximum_complementarity_Nmm=float(np.max(abs(signed*pressure))),contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Previouslyfailed39rows one smoothpolynomial movingowner/first direction at18declared dyadicsteps;3consecutive feature-stable derivative agreements required1e-8. Failedlargersteps retained; no convergence/physicalcriterion relaxed. Not allcoordinate Hessian/semismoothsolver certification.','Nearrows independently signed by extendedprecision winding and outwardtetface plane. A fullnormalcone is still required if supportfeature is edge/vertex or nonunique; no row dropped or gap zeroed.','Currentoldpressure complementarity remains rejected. No new equilibrium/stress/mesh/finitewire/sourcecapacity/physicalanchor/globalenergy/full3Finger certification.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
