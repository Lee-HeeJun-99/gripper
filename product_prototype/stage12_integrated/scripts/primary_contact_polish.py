"""Exact active-set KKT polish of the existing linear unilateral contact energy.
All original gaps/bolt branches remain checked; no criterion or body is removed.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

def polish(K,f,C,Q,D,ks,gaps,pre,u0,p0):
 scale=.001;N=len(f);active=set(np.flatnonzero(p0>1e-8).tolist());pos=set(np.flatnonzero(ks*(D@u0)+pre>1e-8).tolist());history=[]
 # Coincident edges of fragmented faces may repeat exactly the same physical row.
 seen={};unique=[]
 for i in range(C.shape[0]):
  r=C.getrow(i);key=(tuple(r.indices.tolist()),tuple(np.round(r.data,14).tolist()),float(gaps[i]))
  if key not in seen:seen[key]=i;unique.append(i)
  elif i in active:active.discard(i);active.add(seen[key])
 unique=set(unique)
 for it in range(100):
  ids=np.array(sorted(active),dtype=int);bp=np.array(sorted(pos),dtype=int);Dp=D[bp];H=K+Dp.T@sparse.diags(ks[bp])@Dp;Ac=sparse.vstack([C[ids],Q],format='csc');A=sparse.bmat([[H*scale,Ac.T],[Ac,None]],format='csc');rhs=np.r_[f-Dp.T@np.full(len(bp),pre),-gaps[ids]/scale,np.zeros(Q.shape[0])];x=spsolve(A,rhs);assert np.isfinite(x).all(),'Nonfinite KKT state';u=x[:N]*scale;y=x[N:];g=C@u+gaps;pred=ks*(D@u)+pre;p=np.zeros(C.shape[0]);p[ids]=-y[:len(ids)];newpos=set(np.flatnonzero(pred>1e-9).tolist());worstgap=min(unique,key=lambda j:g[j]);worstpressure=ids[np.argmin(p[ids])] if len(ids) else None
  row=dict(iteration=it,active_contacts=len(ids),active_bolts=len(bp),min_gap_mm=float(g.min()),min_active_force_N=float(p[ids].min()) if len(ids) else 0,branch_changes=len(newpos^pos));history.append(row)
  if newpos!=pos:pos=newpos;continue
  if worstpressure is not None and p[worstpressure]<-1e-8:active.remove(int(worstpressure));continue
  if g[worstgap]<-1e-9:active.add(int(worstgap));continue
  return u,p,y[len(ids):],np.maximum(pred,0),history
 raise RuntimeError('KKT active-set polish did not close all original gaps/bolt branches in100iterations')
