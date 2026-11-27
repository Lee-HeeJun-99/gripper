"""Finite triangle-union distance and material virtual-work operator.

No contact force law or equilibrium solve. Distinct tied normals and zero
distance are explicitly nonsmooth; callers must not use an averaged Jacobian.
The bounding-sphere search is conservative, including every possible minimizer.
"""
import numpy as np
from scipy.spatial import cKDTree


def closest(q, triangles):
    t = np.asarray(triangles)
    e, f = t[:, 1]-t[:, 0], t[:, 2]-t[:, 0]
    d = q-t[:, 0]
    aa, ab, bb = (np.einsum('ij,ij->i', a, b)
                  for a, b in [(e,e),(e,f),(f,f)])
    det = aa*bb-ab*ab
    if np.any(det <= 1e-20):
        raise ValueError('Degenerate owner triangle')
    de, df = np.einsum('ij,ij->i',d,e), np.einsum('ij,ij->i',d,f)
    u, v = (de*bb-df*ab)/det, (df*aa-de*ab)/det
    w = np.column_stack([1-u-v,u,v])
    p = np.einsum('ni,nij->nj',w,t)
    ds = np.sum((q-p)**2, axis=1)
    ds[w.min(axis=1)<0] = np.inf
    for i,j in [(0,1),(1,2),(2,0)]:
        edge = t[:,j]-t[:,i]
        a = np.clip(np.einsum('ij,ij->i',q-t[:,i],edge)/np.sum(edge**2,axis=1),0,1)
        pp = t[:,i]+a[:,None]*edge
        dd = np.sum((q-pp)**2,axis=1)
        use = dd<ds
        p[use],ds[use] = pp[use],dd[use]
        ww=np.zeros_like(w);ww[:,i]=1-a;ww[:,j]=a;w[use]=ww[use]
    return np.sqrt(ds),p,w


class Union:
    def __init__(self, points, faces):
        self.points,self.faces=np.asarray(points),np.asarray(faces)
        self.triangles=self.points[self.faces]
        self.centers=self.triangles.mean(axis=1)
        self.radius=np.linalg.norm(self.triangles-self.centers[:,None],axis=2).max(axis=1)
        self.maxradius=self.radius.max()
        self.tree=cKDTree(self.centers)

    def query(self,q,exhaustive=False,tie=1e-10):
        q=np.asarray(q)
        if exhaustive:
            ids=np.arange(len(self.faces))
        else:
            _,seed=self.tree.query(q)
            bound=closest(q,self.triangles[[seed]])[0][0]
            ids=np.asarray(self.tree.query_ball_point(q,bound+self.maxradius+tie),dtype=int)
            lower=np.linalg.norm(self.centers[ids]-q,axis=1)-self.radius[ids]
            ids=ids[lower<=bound+tie]
        ds,ps,ws=closest(q,self.triangles[ids])
        best=ds.min(); active=np.where(ds<=best+tie)[0]
        k=int(active[0]); face=int(ids[k]);p=ps[k];w=ws[k]
        if best<=tie:
            return dict(distance_mm=float(best),face=face,point=p,weights=w,
                        differentiable=False,reason='ZERO_DISTANCE_OR_GRAZING',candidates=len(ids),ties=len(active))
        normals=(q-ps[active])/ds[active,None]
        unique=bool(np.max(np.linalg.norm(normals-normals[0],axis=1))<1e-8)
        n=(q-p)/ds[k]
        return dict(distance_mm=float(ds[k]),face=face,point=p,weights=w,
                    point_gradient=n,owner_gradient=-w[:,None]*n,
                    differentiable=unique,reason='UNIQUE_DISTANCE_GRADIENT' if unique else 'DISTINCT_FACE_TIE',
                    candidates=len(ids),ties=len(active),
                    feature=['VERTEX','EDGE','FACE'][max(0,int(np.sum(w>1e-10))-1)],
                    tied_faces=ids[active].tolist())


def boundary(points,tetra):
    faces=np.concatenate([tetra[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]])
    opposite=np.concatenate([tetra[:,i] for i in [3,2,1,0]])
    _,ix,counts=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True)
    ix=ix[counts==1];faces=faces[ix].copy();opposite=opposite[ix]
    t=points[faces];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
    flip=np.einsum('ij,ij->i',n,points[opposite]-t.mean(axis=1))>0
    faces[flip]=faces[flip][:,[0,2,1]]
    return faces
