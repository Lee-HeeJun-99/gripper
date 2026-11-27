"""Independent value-only derivative verifier; imports no research producer.
Actual saved P1 field, original tetra, all material-paired rows/14connectors.
"""
import sys,json,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(src.read_text());assert sha(REPO/s['source_field']['path'])==s['source_field']['SHA256'];a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/s['output']['path']);u=b['u_mm'];mo=int(a['motor_offset']);names=s['elastic_bodies'];data={};groups=[]
 for n in names:
  X=a[n+'_points_mm'];t=a[n+'_tetra'];dx=X[t[:,1:]]-X[t[:,0,None]];vol=abs(np.linalg.det(dx))/6;w=np.zeros(len(X))
  for j in range(4):np.add.at(w,t[:,j],vol/4)
  data[n]=dict(X=X,t=t,dx=dx,V=vol,w=w,o=int(a[n+'_offset']),E=float(a[n+'_E_MPa']),nu=float(a[n+'_nu']))
 # Read only descriptive contact owners/normals from the immutable first
 # contrast result; row pairing is independently recovered by actual coordinates.
 description=json.loads((ROOT/'validation/integrated/primaryP1_corotated_support1/summary.json').read_text());desc={r['label']:r for r in description['contact_groups']}
 for label in np.unique(a['contact_label']):
  ids=np.flatnonzero(a['contact_label']==label);q=a['contact_points_mm'][ids];owner=desc[str(label)]['owner'];d=data[owner];p=d['X'];mesh=MeshTet(p.T,d['t'].T);tri=mesh.facets[:,mesh.boundary_facets()].T
  # Original saved C directly gives signed contact direction on the first body.
  row0=int(ids[0]);st,en=a['contact_C_indptr'][row0:row0+2];ci=a['contact_C_indices'][st:en];cv=a['contact_C_data'][st:en];normal=np.zeros(3);first=None
  for nn,dd in data.items():
   mask=(ci>=dd['o'])&(ci<dd['o']+3*len(dd['X']))
   if nn==owner:normal[(ci[mask]-dd['o'])%3]=-cv[mask]
   elif mask.any():first=nn
  if first is None:first='Motor'
  ax=int(np.argmax(abs(normal)));tri=tri[np.all(abs(p[tri,ax]-q[0,ax])<1e-6,axis=1)];cross=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]);sign=np.sign(cross@normal);lookup={tuple(np.round(v,7)):i for i,v in enumerate(p)};oi=np.array([lookup[tuple(np.round(v,7))] for v in q]);fi=None
  if first!='Motor':
   lookup={tuple(np.round(v,7)):i for i,v in enumerate(data[first]['X'])};fi=np.array([lookup[tuple(np.round(v,7))] for v in q])
  # Independent sparse incidence: normalize owner vertex sums, not producer's
  # row/triangle adjacency construction.
  groups.append(dict(ids=ids,q=q,owner=owner,first=first,oi=oi,fi=fi,tri=tri,sign=sign,label=str(label)))
 def uu(v,n):
  d=data[n];return v[d['o']:d['o']+3*len(d['X'])].reshape(-1,3)
 def elastic(v):
  total=0.
  for n,d in data.items():
   du=uu(v,n)[d['t'][:,1:]]-uu(v,n)[d['t'][:,0,None]];F=np.eye(3)+np.linalg.solve(d['dx'],du).transpose(0,2,1);sv=np.linalg.svd(F,compute_uv=False)-1;mu=d['E']/(2*(1+d['nu']));lam=d['E']*d['nu']/((1+d['nu'])*(1-2*d['nu']));total+=np.sum(d['V']*(mu*np.sum(sv*sv,axis=1)+.5*lam*np.sum(sv,axis=1)**2))
  return float(total)
 def contact(v):
  gaps=np.zeros(len(a['contact_force_N']))
  for r in groups:
   x=data[r['owner']]['X']+uu(v,r['owner']);tr=r['tri'];cross=np.cross(x[tr[:,1]]-x[tr[:,0]],x[tr[:,2]]-x[tr[:,0]])*r['sign'][:,None];ns=np.zeros_like(x)
   for j in range(3):np.add.at(ns,tr[:,j],cross)
   n=ns[r['oi']];n/=np.linalg.norm(n,axis=1)[:,None]
   if r['first']=='Motor':xa=(r['q']-[0,0,20])@Rotation.from_rotvec(v[mo+3:mo+6]).as_matrix().T+[0,0,20]+v[mo:mo+3]
   else:xa=data[r['first']]['X'][r['fi']]+uu(v,r['first'])[r['fi']]
   gaps[r['ids']]=np.sum(n*(xa-x[r['oi']]),axis=1)+a['initial_gaps_mm'][r['ids']]
  return gaps
 bolts=[]
 for row in a['bolt_D']:
  sides=[]
  for n,d in data.items():
   w=row[d['o']:d['o']+3*len(d['X'])].reshape(-1,3)[:,2]
   if np.any(w):sides.append((n,w))
  first,wa=next(x for x in sides if x[1].sum()>0);owner,wb=next(x for x in sides if x[1].sum()<0);wb=-wb;length=(wa@data[first]['X']-wb@data[owner]['X'])[2];bolts.append((first,owner,wa,wb,length))
 def extensions(v):
  poses={}
  for n,d in data.items():
   p=d['X'];w=d['w'];c0=np.average(p,axis=0,weights=w);cur=p+uu(v,n);c1=np.average(cur,axis=0,weights=w);R,_=Rotation.align_vectors(cur-c1,p-c0,weights=w);poses[n]=R.as_matrix()
  return np.array([poses[owner][:,2]@(wa@(data[first]['X']+uu(v,first))-wb@(data[owner]['X']+uu(v,owner)))-length for first,owner,wa,wb,length in bolts])
 pressure=a['contact_force_N'];bf=a['bolt_force_N'];values=np.array([elastic(u),float(pressure@contact(u)),float(bf@extensions(u))]);saved=np.array([s['corotated_elastic_energy_Nmm'],float(pressure@b['objective_gaps_mm']),float(bf@b['objective_extensions_mm'])]);grads=[b['elastic_force_N'],b['contact_force_pullback_N'],b['bolt_force_pullback_N']];rng=np.random.default_rng(14027);fd=[]
 # Independent smooth nodal fields use polynomials instead of producer sin
 # directions; scale rotations in Motor generalized coordinates explicitly.
 for j in range(10):
  dv=np.zeros(len(u))
  for n,d in data.items():
   p=d['X']/100;vec=(p@rng.normal(size=(3,3)))**2+p@rng.normal(size=(3,3));dv[d['o']:d['o']+3*len(p)]=vec.ravel()
  dv[mo:mo+3]=rng.normal(size=3);dv[mo+3:mo+6]=rng.normal(size=3)*.001;dv/=max(np.max(abs(dv)),1)
  def val(v):return np.array([elastic(v),float(pressure@contact(v)),float(bf@extensions(v))])
  h=1e-3;d1=(val(u+h*dv)-val(u-h*dv))/(2*h);d2=(val(u+h*.5*dv)-val(u-h*.5*dv))/h;estimate=(4*d2-d1)/3;analytic=np.array([g@dv for g in grads]);fd.append(dict(analytic_N=analytic.tolist(),Richardson_N=estimate.tolist(),error_N=abs(estimate-analytic).tolist()))
 errors=np.array([r['error_N'] for r in fd]);corrupt=grads[1].copy();corrupt[mo]+=.001;control=max(abs(float(corrupt@np.r_[np.zeros(mo),1,np.zeros(5)])-float(grads[1]@np.r_[np.zeros(mo),1,np.zeros(5)])),0)
 checks=dict(all2169rows=len(contact(u))==2169,all14branches=len(extensions(u))==14,value_agreement=float(np.max(abs(values-saved)))<1e-10,energy_derivative=float(errors[:,0].max())<1e-8,contact_derivative=float(errors[:,1].max())<1e-8,connector_derivative=float(errors[:,2].max())<1e-8,corruption_rejected=control>1e-4)
 result=dict(status='ACTUAL_P1_INDEPENDENT_LOCAL_SURFACE_WORK_PASS' if all(checks.values()) else 'ACTUAL_P1_INDEPENDENT_LOCAL_SURFACE_WORK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],saved_output=s['output'],verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},scalar_value_error_Nmm=(values-saved).tolist(),maximum_derivative_error_N=errors.max(0).tolist(),virtual_work=fd,corruption_detected_N=control,actual_coordinate_count=len(u),newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independent value-only energy/geometry definitions,10polynomialwholefielddirections. Confirms exact transpose work on actual saved geometry, not equilibrium/finite-facecontact/mesh/globalenergy certification.')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
