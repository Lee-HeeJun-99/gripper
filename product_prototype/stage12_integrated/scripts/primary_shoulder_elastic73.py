"""Full actual new keeper elasticity against finite actual Root shoulder lands.
Static assumed-gravity reference only. Floating body, all six modes restored.
Complete clipped underside facets; no bottomface fixation or fictitious ties.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import qr
import osqp
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_keeper_finite72 import meshpart

def skew(v):
 x,y,z=v;return np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])
def clip(poly,xyz,ax,limit,sign):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=sign*(a@xyz[:,ax]-limit);db=sign*(b@xyz[:,ax]-limit)
  if da>=-1e-13:result.append(a)
  if (da<0<db) or(db<0<da):result.append(a+da/(da-db)*(b-a))
 return result

def main():
 start=time.monotonic();h=float(sys.argv[1]);tag=sys.argv[2];out=ROOT/'validation/integrated'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_shoulder73a/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());step=REPO/cad['part_references']['ROOT_SOCKET_KEEPER']['path'];p,t,tri,Vcad=meshpart(step,h,12);N=3*len(p);origin=np.array([60.,0.,-1.]);la,mu=lame_parameters(200000,.3);m=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N))
 for a in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(a,min(a+8000,len(t)))))
 xyz=p[t];D=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);vol=abs(np.linalg.det(D))/6;inv=np.linalg.inv(D);grad=inv[:,1:,:].transpose(0,2,1);weights=np.zeros(len(p))
 for j in range(4):np.add.at(weights,t[:,j],vol/4)
 f=np.zeros((len(p),3));f[:,2]=-7.9e-6*9.80665*weights;f=f.ravel();bottom=tri[np.all(abs(p[tri,2]+1)<1e-8,axis=1)];assert len(bottom)>0
 rects=[(57.,58.95,-2.,2.),(61.05,63.,-2.,2.),(58.95,61.05,-2.,-1.05),(58.95,61.05,1.05,2.)];rr=[];cc=[];vv=[];points=[];features=[];seen=set()
 for it,nd in enumerate(bottom):
  for ri,(xl,xh,yl,yh) in enumerate(rects):
   poly=list(np.eye(3))
   for ax,limit,sign in [(0,xl,1),(0,xh,-1),(1,yl,1),(1,yh,-1)]:
    poly=clip(poly,p[nd],ax,limit,sign)
    if not poly:break
   for bary in poly:
    pt=bary@p[nd];key=tuple(np.round(pt,11))
    if key in seen:continue
    seen.add(key);row=len(points);points.append(pt);features.append(dict(triangle=nd.tolist(),barycentric=bary.tolist(),rectangle=ri))
    for node,w in zip(nd,bary):rr.append(row);cc.append(3*node+2);vv.append(w)
 A=sparse.coo_matrix((vv,(rr,cc)),shape=(len(points),N)).tocsr();pts=np.array(points);RB=np.zeros((N,6));RB[:,:3]=np.tile(np.eye(3),(len(p),1))
 for i,pt in enumerate(p):RB[3*i:3*i+3,3:]=-skew(pt-origin)
 G=np.linalg.qr(RB)[0];L=.001;OBJ=.0001;P=K*(L*L/OBJ);F=f*L/OBJ;aug=sparse.bmat([[P,sparse.csc_matrix(G)],[sparse.csc_matrix(G.T),None]],format='csc');fac=splu(aug);rhs=np.c_[F,A.T.toarray()];ans=fac.solve(np.r_[rhs,np.zeros((6,rhs.shape[1]))]);U=ans[:N];C=np.asarray(A@U[:,1:]);C=(C+C.T)/2;hd=np.asarray(A@U[:,0]);B=np.asarray(A@RB);target=-RB.T@F;eq=B.T;_,r,piv=qr(eq.T,mode='economic',pivoting=True);rank=int(np.sum(abs(np.diag(r))>1e-10));sel=piv[:rank];E=eq[sel];v=target[sel]
 # Positive definite on active tractions up to redundant splitfacet representation.
 # ALL original six rigid balances and every clippedfacet gap verified afterward.
 dual=osqp.OSQP();dual.setup(P=sparse.csc_matrix(C),q=hd,A=sparse.vstack([sparse.csc_matrix(E),sparse.eye(len(pts))],format='csc'),l=np.r_[v,np.zeros(len(pts))],u=np.r_[v,np.full(len(pts),np.inf)],eps_abs=1e-11,eps_rel=1e-11,max_iter=100000,polishing=True,verbose=False);result=dual.solve();eta=result.x;lam=eta*OBJ/L
 if result.info.status_val not in [1,2]:
  dump(out/'summary.json',dict(status='ACTUAL_P1_SHOULDER_ELASTIC_SOLVER_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),solver_status=result.info.status,nodes=len(p),tetra=len(t),newly_qualified_system_gate_ids=[],whole_system_release=False));return 2
 ue=U[:,0]+U[:,1:]@eta;active=eta>1e-7;z=np.linalg.lstsq(B[active],-A[active]@ue,rcond=1e-11)[0];u=(ue+RB@z)*L;forces=(A.T@lam);res=K@u-forces-f;gap=A@u;energy=float(u@K@u/2);gauge=ans[-6:,0]+ans[-6:,1:]@eta
 uu=u.reshape(-1,3);DG=np.einsum('tai,taj->tij',uu[t],grad);strain=(DG+DG.transpose(0,2,1))/2;stress=2*mu*strain+la*np.trace(strain,axis1=1,axis2=2)[:,None,None]*np.eye(3);ef=np.einsum('tij,taj,t->tai',stress,grad,vol);internal=np.zeros((len(p),3))
 for j in range(4):np.add.at(internal,t[:,j],ef[:,j])
 independent_energy=float(np.sum(.5*np.sum(stress*strain,axis=(1,2))*vol));netforce=(forces+f).reshape(-1,3);wrench=np.r_[netforce.sum(0),np.cross(p+uu-origin,netforce).sum(0)];contactwrench=np.r_[forces.reshape(-1,3).sum(0),np.cross(p+uu-origin,forces.reshape(-1,3)).sum(0)];indres=internal.ravel()-forces-f
 # All untrimmed bottom facets inside the void are deliberately NOT wallcontact.
 # The exact retained supportpatches are vertices of fully clipped flatfacets.
 checks=dict(all83source_hashes=True,all_original6_rigid_balance=float(abs(eq@eta-target).max())<1e-8,original_all_elastic_force=float(abs(res).max())<1e-8,independent_element_force=float(abs(indres).max())<1e-8,independent_element_energy=abs(independent_energy-energy)<1e-12,all_deformed_body_wrenches=float(abs(wrench).max())<1e-8,all_complete_clipped_facet_gaps=float(gap.min())>=-1e-9,nonnegative_normal_force=float(lam.min())>=-1e-9,complementarity=float(abs(lam*gap).max())<1e-8,decomposition_gauge_reactions_zero=float(abs(gauge).max()*OBJ/L)<1e-8)
 dev=stress-np.trace(stress,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=uu,contact_nodal_force_N=forces.reshape(-1,3),gravity_nodal_force_N=f.reshape(-1,3),normal_force_N=lam,contact_points_mm=pts,contact_gap_mm=gap,element_volume_mm3=vol,stress_MPa=stress,element_vonMises_MPa=vm)
 dump(out/'contact_features.json',features);dump(out/'summary.json',dict(status='ACTUAL_P1_POSITIVE_SHOULDER_ELASTIC_GRAVITY_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_POSITIVE_SHOULDER_ELASTIC_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),STEP=ref(step),field=ref(out/'field.npz'),contact_features=ref(out/'contact_features.json'),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nodes=len(p),tetra=len(t),original_elastic_DOF=N,physical_fixed_keeper_DOF=0,free_rigid_body_DOF=6,rigid_reaction_rank=rank,neutral_inplane_modes='x/ytranslation and yaw carry zero imposedload; no fixation or stabilitycertification',contact_rows=len(pts),active_normal_rows=int(np.sum(lam>1e-9)),source_CAD_volume_mm3=Vcad,mesh_volume_mm3=float(vol.sum()),E_ASSUMED_MPa=200000,nu_ASSUMED=.3,density_ASSUMED_kg_mm3=7.9e-6,conditional_gravity_force_N=float(-f[2::3].sum()),maximum_displacement_mm=float(np.linalg.norm(uu,axis=1).max()),volume_mean_displacement_mm=(np.sum(weights[:,None]*uu,axis=0)/weights.sum()).tolist(),static_energy_Nmm=energy,independent_element_energy_Nmm=independent_energy,max_element_vonMises_MPa=float(vm.max()),minimum_complete_facet_gap_mm=float(gap.min()),maximum_original_force_residual_N=float(abs(res).max()),maximum_independent_force_residual_N=float(abs(indres).max()),deformed_keeper_wrench_residual_N_Nmm=wrench.tolist(),Root_equal_opposite_contact_wrench_N_Nmm=(-contactwrench).tolist(),minimum_multiplier_N=float(lam.min()),complementarity_Nmm=float(abs(lam*gap).max()),decomposition_gauge_reaction_N=float(abs(gauge).max()*OBJ/L),solver_status=result.info.status,solver_iterations=int(result.info.iter),accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Entire changedactualkeeper, finite Root boss lands and fullfacet barycentricforce pullbacks. Root is an explicit rigidcut support; actualhost/pin/boltnutthreads/preload/operatingcoupling UNSOLVED.','Typicaldensity/modulus, no materialminimum or strengthPASS. Elementstress is meshdependent and not a sourcedallowable/capacity.','Planar linearized undersidecontact; postdeformation finitepatchmovement/curvedSTEP/mesh1percent/basefinest/fullvector/time.1percent/globalenergy unqualified.','This is actualchangedproduct gravitysupport reference, NOT actual100g grasp/whole83body/release. Inplane neutral modes are free; lateral/yaw loads require actualslot/socket/pin contact.']))
 print(json.dumps(dict(checks=checks,nodes=len(p),tetra=len(t),energy=energy,maxdisp=float(np.linalg.norm(uu,axis=1).max()),wrench=wrench.tolist())),flush=True);return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
