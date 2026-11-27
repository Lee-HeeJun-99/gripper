"""Oriented local gap charts for a closed, outward oriented tetra boundary.

Unlike unsigned distance, a coplanar zero-gap face has a usable oriented chart.
Distinct nearest positions, disagreeing signs, or noncoplanar zero-gap normals
are rejected. This is not a continuous collision detector or force law.
"""
import numpy as np
from finite_face_union27 import Union,closest


class SignedBoundary(Union):
    def __init__(self,points,faces):
        super().__init__(points,faces)
        n=np.cross(self.triangles[:,1]-self.triangles[:,0],self.triangles[:,2]-self.triangles[:,0])
        self.normals=n/np.linalg.norm(n,axis=1)[:,None]

    def chart(self,q,tol=1e-10):
        q=np.asarray(q);ev=self.query(q,tie=tol)
        if ev['distance_mm']<=tol:
            ids=np.asarray(self.tree.query_ball_point(q,self.maxradius+2*tol),dtype=int)
            ds,pp,ww=closest(q,self.triangles[ids]);active=ds<=2*tol
            ids=ids[active];pp=pp[active];ww=ww[active];normals=self.normals[ids]
            if np.max(np.linalg.norm(normals-normals[0],axis=1))>1e-8:
                return dict(accepted=False,reason='NONCOPLANAR_ZERO_GAP_NORMALS',gap_mm=0.)
            # Same outward planar chart, including equivalent triangulation owners.
            n=normals[0];k=0;face=int(ids[k]);w=ww[k]
            return dict(accepted=True,reason='ORIENTED_COPLANAR_ZERO_GAP_CHART',gap_mm=float(n@(q-pp[k])),face=face,weights=w,
                        point_gradient=n,owner_gradient=-w[:,None]*n)
        if not ev['differentiable']:
            return dict(accepted=False,reason=ev['reason'],gap_mm=None)
        normals=self.normals[ev['tied_faces']]
        radial=ev['point_gradient'];dots=normals@radial
        if np.all(dots>1e-8):sign=1.
        elif np.all(dots<-1e-8):sign=-1.
        else:return dict(accepted=False,reason='MIXED_OR_TANGENT_ORIENTED_SIGNS',gap_mm=None)
        return dict(accepted=True,reason='UNIQUE_SIGNED_DISTANCE_CHART',gap_mm=sign*ev['distance_mm'],face=ev['face'],weights=ev['weights'],
                    point_gradient=sign*radial,owner_gradient=sign*ev['owner_gradient'])


def winding_number(q,triangles):
    """Independent whole-closed-surface solid angle for off-boundary audit points."""
    a,b,c=(triangles[:,i]-q for i in range(3))
    la,lb,lc=(np.linalg.norm(v,axis=1) for v in [a,b,c])
    numerator=np.einsum('ij,ij->i',a,np.cross(b,c))
    denominator=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
    return np.sum(2*np.arctan2(numerator,denominator))/(4*np.pi)
