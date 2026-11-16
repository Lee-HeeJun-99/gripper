"""Exact point-to-planar-triangle distance (not a contact-area estimator)."""
import numpy as np

def point_triangles(point,triangles):
    triangle=np.asarray(triangles,dtype=float);p=np.asarray(point,dtype=float)
    if triangle.ndim!=3 or triangle.shape[1:]!=(3,3):raise ValueError('triangle array shape')
    a,b,c=triangle[:,0],triangle[:,1],triangle[:,2];ab=b-a;ac=c-a
    normal=np.cross(ab,ac);area_squared=np.sum(normal*normal,axis=1);regular=area_squared>0
    projection=a.copy();projection[regular]=p-normal[regular]*(np.sum((p-a[regular])*normal[regular],axis=1)/area_squared[regular])[:,None]
    s=np.zeros(len(a));t=s.copy()
    s[regular]=np.sum(np.cross(projection[regular]-a[regular],ac[regular])*normal[regular],axis=1)/area_squared[regular]
    t[regular]=np.sum(np.cross(ab[regular],projection[regular]-a[regular])*normal[regular],axis=1)/area_squared[regular]
    inside=regular&(s>=0)&(t>=0)&(s+t<=1)
    candidates=[]
    for first,last in ((a,b),(b,c),(c,a)):
        edge=last-first;length_squared=np.sum(edge*edge,axis=1);alpha=np.zeros(len(a));valid=length_squared>0
        alpha[valid]=np.sum((p-first[valid])*edge[valid],axis=1)/length_squared[valid]
        closest=first+np.clip(alpha,0,1)[:,None]*edge;candidates.append(closest)
    candidate=np.stack(candidates,axis=1);distances=np.sum((candidate-p)**2,axis=2);choice=distances.argmin(axis=1);closest=candidate[np.arange(len(a)),choice];closest[inside]=projection[inside]
    return np.linalg.norm(closest-p,axis=1),closest,int(np.count_nonzero(~regular))
