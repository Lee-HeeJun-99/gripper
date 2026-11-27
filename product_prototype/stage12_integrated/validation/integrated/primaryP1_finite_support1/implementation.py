"""Finite closed-boundary contact for the SAME actual P1 tetra support.
Original2169material first points and14axial branches preserved. Extends only
this product's existing Biot support; no new general simulator or CAD model.
"""
import numpy as np
from skfem import MeshTet
from primary_corotated_support import Support
from primary_surface_geometry import closest,T

class FiniteContactSupport(Support):
 def __init__(self,a,names):
  super().__init__(a,names);self.surfaces={}
  for name,b in self.bodies.items():
   m=MeshTet(b['X'].T,b['t'].T);ids=m.boundary_facets();tri=m.facets[:,ids].T.copy();parents=m.f2t[0,ids];X=b['X'];n=np.cross(X[tri[:,1]]-X[tri[:,0]],X[tri[:,2]]-X[tri[:,0]]);flip=np.sum(n*(X[tri].mean(1)-X[b['t'][parents]].mean(1)),1)<0;tri[flip]=tri[flip][:,[0,2,1]];self.surfaces[name]=tri
 def contacts(self,u,pressure):
  gaps=np.zeros(len(pressure));g=np.zeros(self.N);details=[];current={name:np.asarray(b['X']+self.body_u(u,name),dtype=T) for name,b in self.bodies.items()}
  for group in self.groups:
   name=group['second'];x=current[name];tri=self.surfaces[name];qvalues=self.point(u,group['first'],group['q'],group.get('a'));body=self.bodies[name];ff=np.zeros_like(body['X']);firstforce=[];winderr=[];interior=0;edge=0
   for j,i in enumerate(group['ids']):
    q=np.asarray(qvalues[j],dtype=T);c=closest(q,x,tri);face=tri[c['triangle']];w=c['weights'];normal=np.cross(x[face[1]]-x[face[0]],x[face[2]]-x[face[0]]);normal/=np.sqrt(normal@normal)
    if np.all(w>0):
     # Signed plane is smooth on the interior of the actual nearest facet.
     # No tinycoordinate residual normalization or arbitrary gap zeroing.
     gap=-c['relative_point_mm']@normal;n=normal;interior+=1
    else:
     # At a separatededge/vertex, topological sign cannot be borrowed from
     # one arbitrary nearest normal (prior28wrong-sign rows).
     v=x[tri]-q;length=np.sqrt(np.sum(v*v,axis=2));num=np.sum(v[:,0]*np.cross(v[:,1],v[:,2]),1);den=length.prod(1)+np.sum(v[:,0]*v[:,1],1)*length[:,2]+np.sum(v[:,1]*v[:,2],1)*length[:,0]+np.sum(v[:,2]*v[:,0],1)*length[:,1];winding=np.sum(2*np.arctan2(num,den))/(4*np.arccos(T(-1)));err=min(abs(winding),abs(abs(winding)-1));winderr.append(float(err));assert err<T('1e-5'),('unresolved winding',int(i),winding);assert c['distance_mm']>T('1e-12'),('nonsmooth zeroedge',int(i));sgn=-1 if abs(winding)>T('.5') else 1;gap=sgn*c['distance_mm'];n=-sgn*c['relative_point_mm']/c['distance_mm'];edge+=1
    gaps[i]=float(gap);f=np.asarray(n*pressure[i],dtype=float);firstforce.append(f)
    for vertex,weight in zip(face,w):ff[vertex]-=float(weight)*f
   self.add_points(g,u,group['first'],group.get('a'),group['q'],np.array(firstforce));self.scatter(g,name,ff);details.append(dict(label=group['label'],owner=name,rows=len(group['ids']),interior_faces=interior,separated_edges_vertices=edge,maximum_winding_integer_error=max(winderr,default=0.)))
  return gaps,g,details
