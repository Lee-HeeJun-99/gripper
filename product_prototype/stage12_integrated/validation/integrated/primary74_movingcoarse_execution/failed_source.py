"""Actual P1 shoulder: reclip MOVING facets and differentiate material trim.
Conditional gravity, linear elastic constitutive contrast; not a system release.
All six keeper modes retained. No contact points advected from reference trim.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import qr
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
import osqp
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_keeper_finite72 import meshpart
from primary_shoulder_elastic73b import skew,clip
RECTS=[(57.,58.95,-2.,2.),(61.05,63.,-2.,2.),(58.95,61.05,-2.,-1.05),(58.95,61.05,1.05,2.)]
def polygon(xyz,rect):
 poly=list(np.eye(3,dtype=xyz.dtype))
 xl,xh,yl,yh=rect
 for ax,limit,sign in [(0,xl,1),(0,xh,-1),(1,yl,1),(1,yh,-1)]:
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   da=sign*(a@xyz[:,ax]-limit);db=sign*(b@xyz[:,ax]-limit)
   if da.real>=-1e-13:result.append(a)
   if (da.real<0<db.real) or(db.real<0<da.real):result.append(a+da/(da-db)*(b-a))
  poly=result
  if not poly:break
 return poly

def geometry(p,bottom,u,derivative=True):
 pos=p+u;rr=[];cc=[];vv=[];g=[];points=[];features=[]
 for ti,nd in enumerate(bottom):
  xyz=pos[nd]
  for ri,rect in enumerate(RECTS):
   poly=polygon(xyz,rect)
   if len(poly)<3:continue
   # Zero-area intersections are not a finite contact patch.
   pp=np.array(poly)@xyz
   if np.linalg.norm(np.cross(pp[1]-pp[0],pp[2]-pp[0]))<1e-16 and len(poly)==3:continue
   derivatives=np.zeros((len(poly),9))
   if derivative:
    for j in range(9):
     z=xyz.astype(complex);z.flat[j]+=1e-25j;pc=polygon(z,rect);assert len(pc)==len(poly)
     derivatives[:,j]=np.array([(b@z)[2].imag/1e-25 for b in pc])
   for k,b in enumerate(poly):
    row=len(g);pt=b@xyz;g.append(pt[2]+1);points.append(pt);features.append(dict(triangle=nd.tolist(),triangle_index=ti,rectangle=ri,vertex=k,barycentric=b.tolist()))
    if derivative:
     for j,v in enumerate(derivatives[k]):
      if abs(v)>1e-16:rr.append(row);cc.append(3*nd[j//3]+j%3);vv.append(v)
 A=sparse.coo_matrix((vv,(rr,cc)),shape=(len(g),3*len(p))).tocsr()
 return np.array(g),A,np.array(points),features

def main():
 start=time.monotonic();h=float(sys.argv[1]);tag=sys.argv[2];out=ROOT/'validation/integrated'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_shoulder73a/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO[r['path'] if False else 'x']) for r in [])
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);step=REPO/cad['part_references']['ROOT_SOCKET_KEEPER']['path'];p,t,tri,Vcad=meshpart(step,h,12);N=3*len(p);la,mu=lame_parameters(200000,.3);m=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 vol=abs(np.linalg.det(np.concatenate([np.ones((len(t),4,1)),p[t]],axis=2)))/6;w=np.zeros(len(p))
 for j in range(4):np.add.at(w,t[:,j],vol/4)
 f=np.zeros((len(p),3));f[:,2]=-7.9e-6*9.80665*w*Vcad/vol.sum();f=f.ravel();RB=np.zeros((N,6));RB[:,:3]=np.tile(np.eye(3),(len(p),1))
 for i,pt in enumerate(p):RB[3*i:3*i+3,3:]=-skew(pt-[60,0,-1])
 G=np.linalg.qr(RB)[0];L=.001;OBJ=.0001;P=K*L**2/OBJ;F=f*L/OBJ;fac=splu(sparse.bmat([[P,sparse.csc_matrix(G)],[sparse.csc_matrix(G.T),None]],format='csc'));bottom=tri[np.all(abs(p[tri,2]+1)<1e-8,axis=1)]
 u=np.zeros((len(p),3));journal=[];derivative_error=None;oldenergy=None
 for it in range(20):
  assert not(ROOT/'runtime/STOP').exists();gap,A,pts,features=geometry(p,bottom,u)
  if it==0:
   rng=np.random.default_rng(74);d=rng.normal(size=u.shape);eps=1e-7;gp,_,_,fp=geometry(p,bottom,u+eps*d,False);gm,_,_,fm=geometry(p,bottom,u-eps*d,False)
   keys=lambda fs:[(x['triangle_index'],x['rectangle'],x['vertex']) for x in fs]
   if keys(fp)==keys(features)==keys(fm):derivative_error=float(abs((gp-gm)/(2*eps)-A@d.ravel()).max())
  rhs=np.c_[F,A.T.toarray()];ans=fac.solve(np.r_[rhs,np.zeros((6,rhs.shape[1]))]);U=ans[:N];C=np.asarray(A@U[:,1:]);C=(C+C.T)/2;hd=np.asarray(A@U[:,0])+(gap-A@u.ravel())/L;B=np.asarray(A@RB);eq=B.T;target=-RB.T@F;_,r,piv=qr(eq.T,mode='economic',pivoting=True);rank=int(np.sum(abs(np.diag(r))>1e-10));sel=piv[:rank]
  solver=osqp.OSQP();solver.setup(P=sparse.csc_matrix(C),q=hd,A=sparse.vstack([sparse.csc_matrix(eq[sel]),sparse.eye(len(gap))],format='csc'),l=np.r_[target[sel],np.zeros(len(gap))],u=np.r_[target[sel],np.full(len(gap),np.inf)],eps_abs=1e-11,eps_rel=1e-11,max_iter=100000,polishing=True,verbose=False);sol=solver.solve()
  if sol.info.status_val not in [1,2]:
   dump(out/'summary.json',dict(status='MOVING_ACTUAL_LAND_QP_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),solver_status=sol.info.status,journal=journal,nodes=len(p),tetra=len(t),accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False));return 2
  eta=sol.x;lam=eta*OBJ/L;ue=U[:,0]+U[:,1:]@eta;active=eta>1e-7;z=np.linalg.lstsq(B[active],-hd[active]-C[active]@eta,rcond=1e-11)[0];un=(ue+RB@z).reshape(-1,3)*L
  gn,An,pn,fn=geometry(p,bottom,un);same=len(gn)==len(gap) and [(q['triangle_index'],q['rectangle'],q['vertex']) for q in fn]==[(q['triangle_index'],q['rectangle'],q['vertex']) for q in features]
  force=A.T@lam;res=K@un.ravel()-force-f;energy=float(un.ravel()@K@un.ravel()/2);entry=dict(iteration=it,rows=len(gap),solver_status=sol.info.status,minimum_reclipped_gap_mm=float(gn.min()),max_force_residual_N=float(abs(res).max()),energy_Nmm=energy,delta_mm=float(abs(un-u).max()),same_topology=same);journal.append(entry);print(json.dumps(entry),flush=True)
  np.savez_compressed(out/f'iterate_{it:02}.npz',displacement_mm=un,normal_force_N=lam,contact_points_mm=pts)
  u=un
  if same and abs(An.T@lam-force).max()<1e-10 and gn.min()>=-1e-9 and abs(res).max()<1e-8 and (oldenergy is not None and abs(energy-oldenergy)<1e-14):break
  oldenergy=energy
 # Recompute force from FINAL moving clipped geometry; reject rather than remap if topology changed.
 gap,A,pts,features=geometry(p,bottom,u);assert len(lam)==len(gap);c=(A.T@lam).reshape(-1,3);res=K@u.ravel()-c.ravel()-f;wrench=np.r_[(c+f.reshape(-1,3)).sum(0),np.cross(p+u-[60,0,-1],c+f.reshape(-1,3)).sum(0)]
 checks=dict(all83hashes=True,moving_clipped_gaps=gap.min()>=-1e-9,nonnegative=lam.min()>=-1e-9,complementarity=abs(lam*gap).max()<1e-8,elastic_force=abs(res).max()<1e-8,deformed_wrench=abs(wrench).max()<1e-8,directional_derivative=derivative_error is not None and derivative_error<1e-6)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=u,contact_nodal_force_N=c,gravity_nodal_force_N=f.reshape(-1,3),normal_force_N=lam,contact_points_mm=pts,contact_gap_mm=gap)
 dump(out/'contact_features.json',features);dump(out/'summary.json',dict(status='ACTUAL_P1_MOVING_LAND_CONDITIONAL_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_MOVING_LAND_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),STEP=ref(step),field=ref(out/'field.npz'),contact_features=ref(out/'contact_features.json'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),h_mm=h,static_energy_Nmm=energy,maximum_displacement_mm=float(np.linalg.norm(u,axis=1).max()),directional_derivative_error=derivative_error,deformed_wrench_residual_N_Nmm=wrench.tolist(),maximum_force_residual_N=float(abs(res).max()),minimum_gap_mm=float(gap.min()),complementarity_Nmm=float(abs(lam*gap).max()),journal=journal,physical_fixed_keeper_DOF=0,free_rigid_modes=6,conditional_weight_N=float(-f[2::3].sum()),source_CAD_volume_mm3=Vcad,assumed_E_MPa=200000,assumed_nu=.3,assumed_density_kg_mm3=7.9e-6,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Actual full keeper with moving clipped finite Root lands and complexstep materialtrim force pullback; rigid Root cut, gravity only.','Linear constitutive contrast; objectivity, both normalcones, curvedSTEP, spatial/time/globalenergy and real pin/slot/bolt/preload remain independently required.','All83body operating equilibrium and source-backed strength unqualified.']))
 return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
