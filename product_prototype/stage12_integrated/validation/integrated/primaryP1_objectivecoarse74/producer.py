"""Actual P1 moving finite-land contact with objective StVK elasticity.
Three explicit neutral pose gauges, zero reactions required; no physical fixing.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import qr
from baseline_registry import ROOT,REPO,ref,dump
from primary_moving_land74 import geometry

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated'/sys.argv[2];d=json.loads((src/'summary.json').read_text());a=np.load(src/'field.npz');p=a['points_mm'];t=a['tetra'];tri=a['boundary_triangles'];u=a['displacement_mm'].ravel();f=a['gravity_nodal_force_N'].ravel();N=len(u);la=200000*.3/(1.3*.4);mu=200000/2.6;L=.001;OBJ=.0001
 xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6
 dofs=(3*t[:,:,None]+np.arange(3)).reshape(len(t),12);ir=np.repeat(dofs,12,axis=1).ravel();ic=np.tile(dofs,(1,12)).ravel()
 bottom=tri[np.all(abs(p[tri,2]+1)<1e-8,axis=1)]
 G=np.zeros((3,N));G[0,0::3]=1;G[1,1::3]=1;G[2,0::3]=-p[:,1];G[2,1::3]=p[:,0]-60;G/=np.linalg.norm(G,axis=1)[:,None];gaugetarget=G@u
 active=set(np.flatnonzero(a['normal_force_N']>1e-9).tolist());journal=[];lastkeys=None;lam=None
 def elastic(y,tangent=True):
   uu=y.reshape(-1,3);DG=np.einsum('tai,taj->tij',uu[t],grad);FG=DG+np.eye(3);EE=(FG.transpose(0,2,1)@FG-np.eye(3))/2;SS=2*mu*EE+la*np.trace(EE,axis1=1,axis2=2)[:,None,None]*np.eye(3);PK=FG@SS
   ef=np.einsum('tij,taj,t->tai',PK,grad,vol);ff=np.zeros((len(p),3))
   for jj in range(4):np.add.at(ff,t[:,jj],ef[:,jj])
   en=float(np.sum((mu*np.sum(EE*EE,axis=(1,2))+.5*la*np.trace(EE,axis1=1,axis2=2)**2)*vol))
   if not tangent:return ff.ravel(),en,None
   H=np.zeros((len(t),4,3,4,3));B=FG@FG.transpose(0,2,1)
   for ii in range(3):
    for kk in range(3):
     aa=(SS if ii==kk else np.zeros_like(SS))+la*FG[:,ii,:,None]*FG[:,kk,None,:]+mu*FG[:,kk,:,None]*FG[:,ii,None,:]+mu*B[:,ii,kk,None,None]*np.eye(3)
     H[:,:,ii,:,kk]=np.einsum('taj,tjl,tbl,t->tab',grad,aa,grad,vol)
   KT=sparse.coo_matrix((H.reshape(len(t),144).ravel(),(ir,ic)),shape=(N,N)).tocsc();return ff.ravel(),en,KT

 for it in range(35):
  assert not(ROOT/'runtime/STOP').exists();gap,A,pts,features=geometry(p,bottom,u.reshape(-1,3));keys=[(q['triangle_index'],q['rectangle'],q['vertex']) for q in features]
  if lastkeys is not None and keys!=lastkeys:raise RuntimeError('Contact topology changed; bounded Newton requires physical feature transition handling')
  lastkeys=keys;ids=np.array(sorted(active),int);C=A[ids].toarray();_,r,piv=qr(C.T,mode='economic',pivoting=True);rank=int(np.sum(abs(np.diag(r))>1e-10));ids=ids[piv[:rank]];C=sparse.vstack([A[ids],sparse.csr_matrix(G)],format='csc');rhs=np.r_[-gap[ids]+A[ids]@u,gaugetarget]/L
  internal,en,KT=elastic(u);P=KT*L*L/OBJ;right=P@(u/L)-(internal-f)*L/OBJ
  system=sparse.bmat([[P,-C.T],[C,None]],format='csc');ans=splu(system).solve(np.r_[right,rhs]);un=ans[:N]*L;reactions=ans[N:]*OBJ/L
  gn,An,pn,fn=geometry(p,bottom,un.reshape(-1,3));assert [(q['triangle_index'],q['rectangle'],q['vertex']) for q in fn]==keys;lam=np.zeros(len(gap));lam[ids]=reactions[:-3];force=An.T@lam;internal,en,_=elastic(un,False);res=internal-force-f;neg=np.flatnonzero(lam<-1e-9);viol=np.flatnonzero(gn<-1e-9)
  entry=dict(iteration=it,active=len(ids),gap_mm=float(gn.min()),force_residual_N=float(abs(res).max()),minimum_lambda_N=float(lam.min()),gauge_reaction_N=float(abs(reactions[-3:]).max()),energy_Nmm=en,delta_mm=float(abs(un-u).max()));journal.append(entry);print(json.dumps(entry),flush=True);np.savez_compressed(out/f'iterate_{it:02}.npz',displacement_mm=un.reshape(-1,3),normal_force_N=lam);u=un
  if len(neg):active.discard(int(neg[np.argmin(lam[neg])]))
  elif len(viol):active.update(viol[np.argsort(gn[viol])[:8]].tolist())
  elif abs(res).max()<1e-8 and abs(lam*gn).max()<1e-8:break
 gap,A,pts,features=geometry(p,bottom,u.reshape(-1,3));force=(A.T@lam).reshape(-1,3);internal,en,_=elastic(u,False);net=force+f.reshape(-1,3);wrench=np.r_[net.sum(0),np.cross(p+u.reshape(-1,3)-[60,0,-1],net).sum(0)];checks=dict(elastic_force=float(abs(internal-force.ravel()-f).max())<1e-8,complete_moving_gap=gap.min()>=-1e-9,nonnegative=lam.min()>=-1e-9,complementarity=float(abs(lam*gap).max())<1e-8,deformed_wrench=float(abs(wrench).max())<1e-8,neutral_gauge_reactions_zero=journal[-1]['gauge_reaction_N']<1e-8)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=u.reshape(-1,3),contact_nodal_force_N=force,gravity_nodal_force_N=f.reshape(-1,3),normal_force_N=lam,contact_points_mm=pts,contact_gap_mm=gap)
 dump(out/'contact_features.json',features);dump(out/'summary.json',dict(status='ACTUAL_P1_OBJECTIVE_MOVING_LAND_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_OBJECTIVE_MOVING_LAND_FAIL',candidate_reference=d['candidate_reference'],producer=ref(out/'producer.py'),initial=ref(src/'summary.json'),field=ref(out/'field.npz'),contact_features=ref(out/'contact_features.json'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),h_mm=d['h_mm'],static_energy_Nmm=en,elastic_law='SaintVenantKirchhoff_totalLagrangian_assumed',journal=journal,deformed_wrench_N_Nmm=wrench.tolist(),physical_fixed_keeper_DOF=0,numerical_neutral_gauges=['meanX','meanY','yaw'],accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Explicit neutral pose gauges require independent zeroreaction check; actual slot/pin/bolts/preload UNSOLVED.','Objective elasticity with movingfinite Root lands, typical200GPa/.3 only; no sourceallowable strength or wholeproduct certification.']))
 return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
