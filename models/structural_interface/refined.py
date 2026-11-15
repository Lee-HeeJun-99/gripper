"""Independent small-planar FEM; all-interface extrema, never connector-only."""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
def solve(k,connectors,nodes,material):
    if nodes not in (21,41,81,161) or not np.isfinite(k) or k<0 or len(set(connectors))!=len(connectors) or any(type(i)is not int or i not in range(1,11) for i in connectors):raise ValueError('FEM physical-grid input')
    h=100/(nodes-1);nd=6*nodes;K=lil_matrix((nd,nd));F=np.zeros(nd);bu=np.array([-1,0,0,1,0,0]);bs=np.array([0,-1,h/2,0,1,h/2]);bb=np.array([0,0,-1,0,0,1]);ke=material['EA']/h*np.outer(bu,bu)+material['GAz']/h*np.outer(bs,bs)+material['EIy']/h*np.outer(bb,bb)
    for layer in (0,1):
        for i in range(nodes-1):
            ids=np.arange(3*(layer*nodes+i),3*(layer*nodes+i)+6)
            for a in range(6):
                for b in range(6):K[ids[a],ids[b]]+=ke[a,b]
        F[3*((layer+1)*nodes-1)+1]=-5e-7
    for position in connectors:
        i=position*(nodes-1)//10;ids=[3*i,3*i+2,3*(nodes+i),3*(nodes+i)+2];b=np.array([-1,-.2,1,-.2])
        for a in range(4):
            for c in range(4):K[ids[a],ids[c]]+=k*b[a]*b[c]
    K=K.tocsr();free=np.array([i for i in range(nd) if (i//3)%nodes]);u=np.zeros(nd);u[free]=spsolve(K[free][:,free],F[free]);slip=u[3*nodes::3]-u[:3*nodes:3]-.2*(u[3*nodes+2::3]+u[2:3*nodes:3]);res=float(abs((K@u-F)[free]).max()/5e-7);tip=float(-np.mean(u[[3*(nodes-1)+1,3*(2*nodes-1)+1]]));rotation=float(abs(u[2::3]).max())
    if not np.isfinite(u).all() or res>=1e-3 or tip<=0 or rotation>=.005:raise ValueError('FEM equilibrium/small-rotation gate')
    return dict(nodes=nodes,tip_deflection_mm=tip,max_slip_mm=float(abs(slip).max()),relative_residual=res,max_rotation=rotation,maximum_location_mm=float(np.argmax(abs(slip))*h),origin='INDEPENDENT LINEAR FEM, not SOFA grasp')
def qualified(k,connectors,material):
    records=[]
    for n in (21,41,81,161):
        r=solve(k,connectors,n,material);records.append(r)
        if len(records)>1:
            a=records[-2];error=max(abs(a[key]/r[key]-1) for key in ('tip_deflection_mm','max_slip_mm'))
            if error<.01:return r,records,error
    raise ValueError('whole-interface mesh qualification failed through161nodes')
