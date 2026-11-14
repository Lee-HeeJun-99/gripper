"""V106 linear beam formulation with explicit axial area.

V109 radius matches rectangular bending I, but has circular A. Keep the
original SOFA radius; use its actual A here for an apples-to-apples check.
"""
import math
import numpy as np


def solve(k, n=11, connectors=None, area=None, load=1e-4):
    h=.4;length=30.;young=250.;inertia=8*h**3/12
    radius=(4*inertia/math.pi)**.25
    area=math.pi*radius**2 if area is None else area
    ndof=6*n;dx=length/(n-1)
    matrix=np.zeros((ndof,ndof));force=np.zeros(ndof)
    def idx(layer,node,component):return 3*(layer*n+node)+component
    for layer in range(2):
        for i in range(n-1):
            ids=[idx(layer,i,0),idx(layer,i+1,0)]
            matrix[np.ix_(ids,ids)]+=young*area/dx*np.array([[1,-1],[-1,1]])
            ids=[idx(layer,i,1),idx(layer,i,2),idx(layer,i+1,1),idx(layer,i+1,2)]
            matrix[np.ix_(ids,ids)]+=young*inertia/dx**3*np.array([
                [12,6*dx,-12,6*dx],[6*dx,4*dx**2,-6*dx,2*dx**2],
                [-12,-6*dx,12,-6*dx],[6*dx,2*dx**2,-6*dx,4*dx**2]])
        force[idx(layer,n-1,1)]=-load/2
    bs=[]
    for i in (range(1,n) if connectors is None else connectors):
        b=np.zeros(ndof);b[idx(0,i,0)]=-1;b[idx(1,i,0)]=1
        # V106 theta = dw/dx = -SOFA theta_y.
        b[idx(0,i,2)]=h/2;b[idx(1,i,2)]=h/2
        matrix+=k*np.outer(b,b);bs.append(b)
    fixed=[idx(layer,0,c) for layer in range(2) for c in range(3)]
    free=[i for i in range(ndof) if i not in fixed]
    q=np.zeros(ndof);q[free]=np.linalg.solve(matrix[np.ix_(free,free)],force[free])
    tip=-.5*(q[idx(0,n-1,1)]+q[idx(1,n-1,1)])
    slips=np.array([b@q for b in bs])
    return dict(deflection_mm=float(tip),effective_stiffness=float(load/tip),
                max_connector_slip_mm=float(max(abs(slips))),area=area,inertia=inertia,
                residual=float(max(abs((matrix@q-force)[free]))))
