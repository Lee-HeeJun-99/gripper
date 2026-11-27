"""Actual original P1 owner surface triangles, exact normalized-area differential.
This keeps all material-paired contact rows; finite-face coverage is checked
separately. A smooth average normal does not certify a closest-point contact.
"""
import numpy as np
from skfem import MeshTet
from primary_corotated_support import Support

class LocalSurfaceSupport(Support):
 def __init__(self,a,names):
  super().__init__(a,names)
  for row in self.groups:
   b=self.bodies[row['second']];p=b['X'];m=MeshTet(p.T,b['t'].T);tri=m.facets[:,m.boundary_facets()].T;n=row['n'];ax=int(np.argmax(abs(n)));value=row['q'][0,ax];tri=tri[np.all(abs(p[tri,ax]-value)<1e-6,axis=1)];cross=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]);sign=np.sign(cross@n);assert np.all(sign!=0);row['tri']=tri;row['sign']=sign
   # Each original owner node contributes normalized sum of adjacent planar
   # area vectors. Keep explicit row/triangle adjacency for independent audit.
   row['adj_row'],row['adj_tri']=np.nonzero(np.any(tri[None,:,:]==row['b'][:,None,None],axis=2));assert set(row['adj_row'])==set(range(len(row['ids'])))
 def contacts(self,u,pressure):
  gaps=np.zeros(len(pressure));g=np.zeros(self.N);details=[]
  for row in self.groups:
   ids=row['ids'];owner=row['second'];b=self.bodies[owner];x=b['X']+self.body_u(u,owner);tri=row['tri'];e1=x[tri[:,1]]-x[tri[:,0]];e2=x[tri[:,2]]-x[tri[:,0]];cross=np.cross(e1,e2)*row['sign'][:,None];ar,at=row['adj_row'],row['adj_tri'];h=np.zeros((len(ids),3));np.add.at(h,ar,cross[at]);length=np.linalg.norm(h,axis=1);assert length.min()>1e-12;n=h/length[:,None];xa=self.point(u,row['first'],row['q'],row.get('a'));xb=x[row['b']];d=xa-xb;gaps[ids]=np.einsum('ij,ij->i',d,n)+self.a['initial_gaps_mm'][ids];ff=pressure[ids,None]*n;self.add_points(g,u,row['first'],row.get('a'),row['q'],ff);self.add_points(g,u,owner,row['b'],row['q'],-ff)
   # Exact derivative of unit area sum. Includes ALL owner vertices involved;
   # omitting this term creates a spurious current spatial moment.
   v=pressure[ids,None]*(d-n*np.einsum('ij,ij->i',n,d)[:,None])/length[:,None];tv=np.zeros_like(cross);np.add.at(tv,at,v[ar]*row['sign'][at,None]);f1=np.cross(e2,tv);f2=np.cross(tv,e1);nodal=np.zeros_like(x)
   for j,fj in enumerate((-f1-f2,f1,f2)):np.add.at(nodal,tri[:,j],fj)
   self.scatter(g,owner,nodal);details.append(dict(label=row['label'],owner=owner,rows=len(ids),triangles=len(tri),area_normal_derivative_force_norm_N=float(np.linalg.norm(nodal)),maximum_pair_separation_mm=float(np.linalg.norm(d,axis=1).max())))
  return gaps,g,details
 def finite_coverage(self,u,pressure):
  rows=[]
  for row in self.groups:
   ids=row['ids'];b=self.bodies[row['second']];x=b['X']+self.body_u(u,row['second']);tri=row['tri'];v0=x[tri[:,0]];e1=x[tri[:,1]]-v0;e2=x[tri[:,2]]-v0;normal=np.cross(e1,e2);normal/=np.linalg.norm(normal,axis=1)[:,None];aa=np.sum(e1*e1,axis=1);bb=np.sum(e1*e2,axis=1);cc=np.sum(e2*e2,axis=1);det=aa*cc-bb*bb;xa=self.point(u,row['first'],row['q'],row.get('a'));outside=[];chosen=[];minmargin=[];outside_geometry=[]
   for j,q in enumerate(xa):
    d=q-v0;de=np.sum(d*e1,axis=1);df=np.sum(d*e2,axis=1);s=(cc*de-bb*df)/det;t=(aa*df-bb*de)/det;margin=np.minimum(np.minimum(s,t),1-s-t);valid=margin>=-1e-8;minmargin.append(float(margin.max()))
    if not np.any(valid):
     outside.append(j);chosen.append(None);best=float('inf');bestq=None;besttri=None
     for side in range(3):
      aa0=x[tri[:,side]];bb0=x[tri[:,(side+1)%3]];edge=bb0-aa0;tt=np.clip(np.sum((q-aa0)*edge,axis=1)/np.sum(edge*edge,axis=1),0,1);cp=aa0+tt[:,None]*edge;dist=np.linalg.norm(q-cp,axis=1);kk=int(np.argmin(dist))
      if dist[kk]<best:best=float(dist[kk]);bestq=cp[kk];besttri=kk
     plane=float((q-v0[besttri])@normal[besttri]);overhang=float(np.sqrt(max(0,best*best-plane*plane)));outside_geometry.append(dict(row=int(ids[j]),first_point_mm=q.tolist(),nearest_owner_edge_point_mm=bestq.tolist(),nearest_distance_mm=best,normal_separation_mm=plane,tangential_overhang_mm=overhang,old_pressure_N=float(pressure[ids[j]]),triangle=tri[besttri].tolist()))
    else:
     distance=abs(np.sum(d*normal,axis=1));distance[~valid]=np.inf;k=int(np.argmin(distance));chosen.append(dict(triangle=k,distance_mm=float(distance[k]),barycentric=[float(1-s[k]-t[k]),float(s[k]),float(t[k])]))
   outside=np.array(outside,dtype=int);rows.append(dict(label=row['label'],rows=len(ids),outside_rows=outside.tolist(),outside_active_rows=outside[pressure[ids][outside]>1e-8].tolist(),outside_active_force_sum_N=float(pressure[ids][outside].sum()),worst_best_barycentric_margin=min(minmargin),projected_triangle=chosen,outside_geometry=outside_geometry))
  return rows
