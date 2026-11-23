"""Explicit unit-conditioned mesh query;input/output SI,internal millimetres.

Trimesh uses fixed numerical thresholds in its closest-triangle routine. Small
SI triangles can be misclassified. Scaling geometry AND query points changes
neither physical geometry nor any SOFA/contact acceptance tolerance.
"""
import numpy as np
import trimesh

def closest_si(mesh,points):
 points=np.asarray(points,dtype=float)
 if not np.isfinite(points).all() or not np.isfinite(mesh.vertices).all():raise ValueError('finite geometry required')
 conditioned=trimesh.Trimesh(vertices=np.asarray(mesh.vertices)*1000.,faces=mesh.faces,process=False)
 point,distance,triangle=trimesh.proximity.closest_point_naive(conditioned,points*1000.)
 return point/1000.,distance/1000.,triangle

def triangle_reference(point,triangle):
 """Independent face/three-edge minimization in dimensionless local coordinates."""
 triangle=np.asarray(triangle,float);point=np.asarray(point,float)
 origin=triangle[0];scale=max(np.linalg.norm(triangle[1]-origin),np.linalg.norm(triangle[2]-origin),np.linalg.norm(triangle[2]-triangle[1]))
 if not scale>0:raise ValueError('degenerate triangle')
 t=(triangle-origin)/scale;p=(point-origin)/scale;u=t[1];v=t[2];normal=np.cross(u,v);n2=normal@normal
 if not n2>0:raise ValueError('degenerate triangle')
 projected=p-normal*((p@normal)/n2);den=(u@u)*(v@v)-(u@v)**2
 if not den>0:raise ValueError('undefined barycentric coordinates')
 b=((projected@u)*(v@v)-(projected@v)*(u@v))/den;c=((projected@v)*(u@u)-(projected@u)*(u@v))/den
 candidates=[]
 if b>=0 and c>=0 and b+c<=1:candidates.append(projected)
 for i,j in ((0,1),(1,2),(2,0)):
  edge=t[j]-t[i];norm=edge@edge
  if not norm>0:raise ValueError('degenerate edge')
  candidates.append(t[i]+edge*np.clip(((p-t[i])@edge)/norm,0,1))
 q=min(candidates,key=lambda x:np.linalg.norm(p-x))
 return origin+scale*q
