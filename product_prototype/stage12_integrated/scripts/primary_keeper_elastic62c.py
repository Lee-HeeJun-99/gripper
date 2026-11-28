"""Full actual keeper 3D Neumann torque reference; NOT solved contact or strength.
Affine continuum wrench-distributed tractions on real plug end and tongue bottom surfaces are
explicit conditional load contrasts. All DOFs restored, no physical fixation.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.linalg import qr
from scipy.sparse.linalg import spsolve
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_body34 import meshpart,wrenchmat
h=float(sys.argv[1]);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_clocked62a/summary.json';cad=json.loads(cp.read_text());step=REPO/cad['part_references']['ROOT_SOCKET_KEEPER']['path'];assert sha(step)==cad['part_references']['ROOT_SOCKET_KEEPER']['SHA256'];source=ROOT/'validation/integrated/primaryP1_contacts62/summary.json';sr=json.loads(source.read_text());cases=json.loads((source.parent/'rows.json').read_text());forces=[]
for i in range(2):forces.append(max(sum(q['coefficient_N'] for q in c['reactions'] if q['label']=='root_connector_'+str(i)) for c in cases if c['feasible'] and c['explicit_unknown_host_resultant_port']))
torque=np.array(forces)*.5/(2*np.pi);E=200000.;nu=.3
p,t,tri,V=meshpart(step,h,8);N=3*len(p);m=MeshTet(p.T,t.T);la,mu=lame_parameters(E,nu);el=ElementVector(ElementTetP1());K=sparse.csr_matrix((N,N))
for first in range(0,len(t),8000):
 assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
F=np.zeros((len(p),3));ports=[]
def apply(facets,target,label):
 assert len(facets)>0,(label,'no facets');M=np.zeros((6,6));qs=[]
 for ns in facets:
  pts=p[ns];area=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]))/2
  for bc in np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]):
   x=bc@pts;H=wrenchmat(x[None,:])[0];M+=area/3*(H@H.T);qs.append((ns,bc,area/3,H))
 coeff=np.linalg.solve(M,target);local=np.zeros_like(F)
 for ns,bc,w,H in qs:
  f=H.T@coeff
  for n,b in zip(ns,bc):local[n]+=w*b*f
 F[:]+=local;W=wrenchmat(p).transpose(1,0,2).reshape(6,-1)@local.ravel();ports.append(dict(label=label,triangles=len(facets),area_mm2=sum(q[2] for q in qs),target_wrench_N_Nmm=target.tolist(),actual_wrench_N_Nmm=W.tolist(),traction='Exact triangle quadrature of affine continuum wrench distribution; not unilateral flank/pin pressure'))
for y,T in zip([-16,16],torque):
 ids=tri[np.all(abs(p[tri,2]+1.25)<1e-7,axis=1)&np.all(abs(p[tri,1]-y)<1.5,axis=1)]
 apply(ids,np.array([0.,0,0,0,0,T]),'actual_plug_bottom_'+str(y))
ids=tri[np.all(abs(p[tri,2]+2.9)<1e-7,axis=1)]
apply(ids,np.array([0.,0,0,0,0,-sum(torque)]),'actual_tongue_bottom_RETURN_REFERENCE_NOT_PIN_CONTACT')
center=p.mean(0);R=np.zeros((N,6))
for j,e in enumerate(np.eye(3)):R[:,j]=np.tile(e,len(p));R[:,j+3]=np.cross(e,p-center).ravel()
_,_,pv=qr(R.T,mode='economic',pivoting=True);gauge=np.sort(pv[:6]);free=np.setdiff1d(np.arange(N),gauge);u=np.zeros(N);u[free]=spsolve(K[free][:,free].tocsc(),F.ravel()[free]);u-=R@np.linalg.lstsq(R,u,rcond=None)[0];res=K@u-F.ravel();u3=u.reshape(-1,3);det=np.linalg.det(np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1)));vol=abs(det)/6;iv=np.linalg.inv(p[t[:,1:]]-p[t[:,0,None]]);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1);G=np.einsum('tai,taj->tij',u3[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=sig-np.trace(sig,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));energy=.5*float(u@K@u);ee=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));halfwork=.5*float(F.ravel()@u);w=(wrenchmat(p).transpose(1,0,2).reshape(6,-1)@F.ravel());ratio=np.linalg.det(np.transpose((p+u3)[t[:,1:]]-(p+u3)[t[:,0,None]],(0,2,1)))/det
checks=dict(actual_CAD_hash=True,force_balance=float(abs(w[:3]).max())<1e-8,moment_balance=float(abs(w[3:]).max())<1e-8,all_original_DOF_residual=float(abs(res).max())<1e-8,volume=abs(vol.sum()/V-1)<.01,positive_deformed_elements=bool(ratio.min()>0),finite=bool(np.isfinite(u).all()),energy_work=abs(energy/halfwork-1)<1e-8,independent_element_energy=abs(ee/energy-1)<1e-8)
np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,displacement_mm=u3,load_N=F,residual_N=res,vm_MPa=vm)
dump(out/'summary.json',dict(status='ACTUAL_KEEPER_FULL_SOLID_CONDITIONAL_NEUMANN_TORQUE_REFERENCE_NOT_CONTACT' if all(checks.values()) else 'ACTUAL_KEEPER_NEUMANN_REFERENCE_FAIL',candidate=ref(cp),STEP=ref(step),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),source=ref(source),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nodes=len(p),tetra=len(t),E_ASSUMED_MPa=E,nu_ASSUMED=nu,material_minimum_MPa=None,root_cut_envelope_N=forces,torque_Nmm=torque.tolist(),ports=ports,CAD_volume_mm3=V,mesh_volume_mm3=float(vol.sum()),volume_error=abs(vol.sum()/V-1),physical_fixed_DOF=0,all_original_DOF_restored=True,original_residual_N=float(abs(res).max()),static_energy_Nmm=energy,independent_element_energy_Nmm=ee,halfwork_Nmm=halfwork,maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),raw_maximum_vm_MPa=float(vm.max()),minimum_deformed_volume_ratio=float(ratio.min()),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Real entire clocked Root keeper, not ideal coupon; explicitly prescribed end/tongue wrench distribution is not actual unilateral hex/tongue/pin contact','Envelope maxima may come from different necessary cut cases; not an accepted83body equilibrium','Finite elastic typical/reference material only; no source-minimum strength/process or sharp-notch stress certification','Six rigid gauges removed algebraically and restored; no physical host/bolt spin fixed','Static energy/halfwork identity is not global coupled stored-energy closure']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),energy=energy,raw_vm=float(vm.max()))));raise SystemExit(0 if all(checks.values()) else 2)
