"""Independent linear small-planar FEM of midpoint rod, NOT a grasp simulation."""
import numpy as np
def solve(k=0.,connectors=(),nodes=11,layers=2,length=100.,height=.4,load=1e-6,EA=183.058246575,GA=57.7835,EI=10.6666666666667):
    if not all(np.isfinite(v) for v in (k,length,height,load,EA,GA,EI)) or k<0 or min(length,height,EA,GA,EI)<=0 or nodes not in (11,21,41) or layers not in (2,4,8) or len(set(connectors))!=len(connectors) or any(type(i) is not int or not 1<=i<nodes for i in connectors):raise ValueError('linear FEM input')
    nd=3*nodes*layers;K=np.zeros((nd,nd));F=np.zeros(nd);h=length/(nodes-1);bu=np.array([-1,0,0,1,0,0]);bs=np.array([0,-1,h/2,0,1,h/2]);bb=np.array([0,0,-1,0,0,1]);Ke=EA/h*np.outer(bu,bu)+GA/h*np.outer(bs,bs)+EI/h*np.outer(bb,bb)
    for l in range(layers):
        for i in range(nodes-1):idx=np.arange(3*(l*nodes+i),3*(l*nodes+i)+6);K[np.ix_(idx,idx)]+=Ke
        F[3*((l+1)*nodes-1)+1]=-load/layers
    for l in range(layers-1):
        for i in connectors:
            idx=np.array([3*(l*nodes+i),3*(l*nodes+i)+2,3*((l+1)*nodes+i),3*((l+1)*nodes+i)+2]);b=np.array([-1,-height/2,1,-height/2]);K[np.ix_(idx,idx)]+=k*np.outer(b,b)
    free=np.array([i for i in range(nd) if (i//3)%nodes]);u=np.zeros(nd);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free]);res=float(abs((K@u-F)[free]).max()/abs(load/layers));tip=float(-np.mean([u[3*((l+1)*nodes-1)+1] for l in range(layers)]));slips=[u[3*((l+1)*nodes+i)]-u[3*(l*nodes+i)]-height/2*(u[3*(l*nodes+i)+2]+u[3*((l+1)*nodes+i)+2]) for l in range(layers-1) for i in range(nodes)];rotation=float(abs(u[2::3]).max())
    if res>=1e-3 or tip<=0 or rotation>=.005 or not np.isfinite(u).all():raise ValueError('linear model physical scope/equilibrium failed')
    return dict(tip_deflection_mm=tip,max_slip_mm=float(max(map(abs,slips))),relative_residual=res,max_rotation=rotation,energy=float(.5*u@K@u),condition_number=float(np.linalg.cond(K[np.ix_(free,free)])),config=dict(k=k,connectors=list(connectors),nodes=nodes,layers=layers,length=length,height=height,load=load,EA=EA,GA=GA,EI=EI),origin='INDEPENDENT LINEAR FEM, not actual SOFA or real measurements')
