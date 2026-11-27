"""Independent full P2 saved-field virtual-work/force/energy audit, no assembled K.
Actual Root displacement relative to best-fit actual foot, with CAD degree3 moments.
"""
import sys,json,shutil,numpy as np
from skfem import MeshTet
from skfem.quadrature import get_quadrature_tet
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_quadratic56 import moments,mul
from primary_anchor_contact38 import common_faces,planar_triangles,tri_shape,surface_moment
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[];cp=ROOT/'cad/exports/primaryP1_integral55e/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());support=read(REPO/cad['part_references']['BENCH_SUPPORT']['path']);faces=[]
for n,z,label in [('F0_ROOT_BACK',-7,'Root'),('EXTERNAL_BENCH_PLATE',-130,'foot')]:
 for f in common_faces(support,read(REPO/cad['part_references'][n]['path']),2,z):faces.append((f,z,label))
L=np.zeros((3,4,4));L[0,0,0]=1;L[0,1,0]=L[0,0,1]=-1;L[1,1,0]=1;L[2,0,1]=1;one=np.zeros((4,4));one[0,0]=1;shapes=np.array([2*mul(a,a)-a for a in L]+[4*mul(L[i],L[j]) for i,j in [(0,1),(1,2),(0,2)]])
for name in sys.argv[2:]:
 path=ROOT/'validation/integrated'/name/'summary.json';d=json.loads(path.read_text());assert d['candidate']==ref(cp);assert sha(REPO/d['field']['path'])==d['field']['SHA256'];a=np.load(REPO/d['field']['path']);p=a['points_mm'];t=a['tetra'];pos=a['P2_points_mm'];ed=a['P2_element_nodes'];u=a['displacement_mm'];F=a['load_N'];m=MeshTet(p.T,t.T);dx=p[t[:,1:]]-p[t[:,0,None]];V=abs(np.linalg.det(dx))/6;iv=np.linalg.inv(dx);g=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);x,w=get_quadrature_tet(2);bc=np.vstack([1-x.sum(0),x]).T;mu=68900/(2*1.33);la=68900*.33/(1.33*.34);pairs=[(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)]
 def internal(U):
  force=np.zeros_like(U);energy=0.
  for first in range(0,len(t),1800):
   assert not(ROOT/'runtime/STOP').exists();sl=slice(first,min(first+1800,len(t)));gg=np.stack([(4*bc[:,i,None,None]-1)*g[None,sl,i,:] for i in range(4)]+[4*(bc[:,i,None,None]*g[None,sl,j,:]+bc[:,j,None,None]*g[None,sl,i,:]) for i,j in pairs],axis=2);G=np.einsum('qtai,taj->qtji',gg,U[ed[sl]]);eps=(G+G.swapaxes(-1,-2))/2;sig=2*mu*eps+la*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*np.eye(3);ww=6*w[:,None]*V[sl];ef=np.einsum('qtij,qtaj,qt->tai',sig,gg,ww);energy+=float(np.einsum('qtij,qtij,qt->',eps,sig,ww)/2)
   for j in range(10):np.add.at(force,ed[sl,j],ef[:,j])
  return force,energy
 fi,en=internal(u);bad=u.copy();bad[ed[0,4],2]+=1e-4;fb,eb=internal(bad);rigid=np.cross([1e-5,-2e-5,1e-5],pos)+[.002,-.003,.004];fr,er=internal(u+rigid);force=F.sum(0);moment=np.cross(pos,F).sum(0)*.001;negative=float(abs(fb-F).max());res=float(abs(fi-F).max());work=float(np.sum(F*u)/2);edges={tuple(x):len(p)+i for i,x in enumerate(m.edges.T)};assert np.max(abs(pos[len(p):]-(p[m.edges[0]]+p[m.edges[1]])/2))<1e-10;Mfit=np.zeros((6,6));rhs=np.zeros(6);ra=0.;rc=np.zeros(3);ru=np.zeros(3);area_errors=[];maxmom=0.
 body=dict(p=p,tri=m.facets[:,m.boundary_facets()].T)
 for face,z,label in faces:
  bb=np.array(bounds(face));area=0.
  for ns,pts in planar_triangles(body,2,z):
   if any(pts[:,k].max()<bb[k]-1e-8 or pts[:,k].min()>bb[k+3]+1e-8 for k in [0,1]):continue
   cs=BRepAlgoAPI_Common(face,tri_shape(pts)).Shape();ar,q,cov=surface_moment(cs)
   if ar<1e-10:continue
   mom=moments(cs,pts,32);maxmom=max(maxmom,abs(mom[0,0]/ar-1));ids=list(ns)+[edges[tuple(sorted((int(ns[i]),int(ns[j]))))] for i,j in [(0,1),(1,2),(0,2)]];X=np.zeros((3,4,4));X[:,0,0]=pts[0];X[:,1,0]=pts[1]-pts[0];X[:,0,1]=pts[2]-pts[0];A=np.zeros((3,6,4,4))
   for k in range(3):A[k,k]=one
   A[0,4]=X[2];A[0,5]=-X[1];A[1,3]=-X[2];A[1,5]=X[0];A[2,3]=X[1];A[2,4]=-X[0];U=np.einsum('aj,akl->jkl',u[ids],shapes)
   if label=='foot':
    for k in range(6):
     for j in range(3):rhs[k]+=np.sum(mul(A[j,k],U[j])*mom)
     for l in range(6):
      for j in range(3):Mfit[k,l]+=np.sum(mul(A[j,k],A[j,l])*mom)
   else:ra+=ar;rc+=np.sum(X*mom,axis=(1,2));ru+=np.sum(U*mom,axis=(1,2))
   area+=ar
  area_errors.append(abs(area/surface_moment(face)[0]-1))
 rc/=ra;ru/=ra;fit=np.linalg.solve(Mfit,rhs);relative=ru-fit[:3]-np.cross(fit[3:],rc);checks=dict(same_actual77parts=True,allDOF_force=res<1e-8,independent_energy=abs(en/work-1)<1e-8,producer_energy=abs(en/d['static_strain_energy_Nmm']-1)<1e-8,force=np.linalg.norm(force)<1e-8,moment=np.linalg.norm(moment)<1e-10,perturbed_edge_DOF_rejected=negative>1e-6,wrong_sign_rejected=abs(fi+F).max()>1e-6,rigid_force=abs(fr-fi).max()<1e-8,rigid_energy=abs(er/en-1)<1e-8,CAD_trace=max(area_errors)<.01,Green_area=maxmom<1e-8,producer_local_checks=all(d['checks'].values()))
 rows.append(dict(source=ref(path),checks={k:bool(v) for k,v in checks.items()},h_mm=d['h_mm'],static_strain_energy_Nmm=en,compliance_mm_N=2*en/(float(-a['ownweight_N'][:,2].sum())+.980665)**2,root_relative_to_best_fit_actual_foot_mm=relative.tolist(),independent_residual_N=res,force_balance_N=force.tolist(),moment_balance_Nm=moment.tolist(),perturbed_edge_residual_N=negative,rigid_force_error_N=float(abs(fr-fi).max()),rigid_energy_error=abs(er/en-1),halfwork_Nmm=work,raw_peak_VM_MPa=d['raw_peak_VM_MPa']))
 dump(out/'progress.json',dict(rows=rows));print(json.dumps(rows[-1]),flush=True)
contrasts=[]
for i,a in enumerate(rows):
 for b in rows[i+1:]:
  changes=dict(energy=abs(b['static_strain_energy_Nmm']/a['static_strain_energy_Nmm']-1),compliance=abs(b['compliance_mm_N']/a['compliance_mm_N']-1),root_objective_relative_displacement=float(np.linalg.norm(np.array(b['root_relative_to_best_fit_actual_foot_mm'])-a['root_relative_to_best_fit_actual_foot_mm'])/np.linalg.norm(a['root_relative_to_best_fit_actual_foot_mm'])));contrasts.append(dict(h_mm=[a['h_mm'],b['h_mm']],relative_changes=changes,original1percent=all(v<.01 for v in changes.values())))
local=all(all(r['checks'].values()) for r in rows);mesh=len(rows)>=2 and all(c['original1percent'] for c in contrasts);dump(out/'summary.json',dict(status='ACTUAL_PRODUCT_P2_LOCAL_AUDITS_PASS_MESH_PASS_NOT_RELEASE' if local and mesh else 'ACTUAL_PRODUCT_P2_LOCAL_AUDITS_PASS_MESH_FAIL_NOT_RELEASE' if local else 'ACTUAL_PRODUCT_P2_FIELD_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),moment_adapter=ref(ROOT/'scripts/primary_quadratic56.py'),rows=rows,mesh_contrasts=contrasts,all_fields_local_checks=local,original1percent_allpairs=mesh,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['P2sameactualsupport/same100gverticaltest/ownweight/affinefootNeumannreference,notgrasp/hostclosure','OriginalP1meshFAILpreserved;ordercontrastdoesnotretroactivelyqualifyit','Exactdegree3bestfitfootmetric replaces historicalcentroid-onlyintegration approximation withoutchanging physical criterion','mesh1percent,dt.1percent/globalenergy/full3Finger/source-minimum/strength/100goperating remain independentlyrequired']))
raise SystemExit(0 if local else 2)
