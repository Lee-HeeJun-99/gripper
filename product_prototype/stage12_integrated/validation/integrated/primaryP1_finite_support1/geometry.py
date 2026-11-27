"""Query-centred extended precision finite triangle distance for actual P1.
No topology sign inferred from nearest triangle. All facets searched. Ties are
reported separately; a representative triangle never certifies a normal cone.
"""
import numpy as np
T=np.longdouble

def closest(q,x,tri,normals=None):
 q=np.asarray(q,dtype=T);v=np.asarray(x,dtype=T)[tri]-q
 a=v[:,0];e=v[:,1]-a;f=v[:,2]-a;n=np.cross(e,f);nn=np.sum(n*n,axis=1)
 assert np.all(nn>0)
 # Plane projection via cross products avoids subtraction of nearly equal
 # Gram products aa*cc-bb*bb on slender surface triangles.
 height=np.sum(a*n,axis=1)/nn;plane=height[:,None]*n
 rel=plane-a;s=np.sum(np.cross(rel,f)*n,axis=1)/nn;t=np.sum(np.cross(e,rel)*n,axis=1)/nn
 weights=np.stack([1-s-t,s,t],axis=1);valid=np.all(weights>=0,axis=1)
 point=plane.copy();dist2=np.sum(point*point,axis=1);dist2[~valid]=np.inf;feature=np.zeros(len(tri),dtype=int)
 for j in range(3):
  edge=v[:,(j+1)%3]-v[:,j];z=np.clip(-np.sum(v[:,j]*edge,axis=1)/np.sum(edge*edge,axis=1),0,1)
  cp=v[:,j]+z[:,None]*edge;dd=np.sum(cp*cp,axis=1);better=dd<dist2
  dist2[better]=dd[better];point[better]=cp[better];weights[better]=0;weights[better,j]=1-z[better];weights[better,(j+1)%3]=z[better];feature[better]=j+1
 k=int(np.argmin(dist2));distance=np.sqrt(dist2[k]);scale=np.max(np.sum(v*v,axis=2));roundoff=64*np.finfo(T).eps*max(scale,T(1))
 ties=np.flatnonzero(abs(dist2-dist2[k])<=roundoff)
 return dict(distance_mm=distance,triangle=k,point_mm=q+point[k],relative_point_mm=point[k],weights=weights[k],feature=int(feature[k]),candidate_triangles=ties,distances_squared_mm2=dist2,roundoff_distance_squared_mm2=roundoff)
