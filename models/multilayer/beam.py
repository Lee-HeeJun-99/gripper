"""Explicit EA/EI multilayer FEM, optional Timoshenko shear and unilateral contact.

Each node has (u,w,phi=dw/dx). Parameters are research inputs, not measured PET.
Wire actuation is an ideal eccentric tip moment T*e, not a tendon routing solver.
"""
from dataclasses import dataclass, asdict, replace
import math
import numpy as np

@dataclass(frozen=True)
class Design:
    length: float=100.
    layers: int=2
    nodes: int=21
    thickness: float=.4
    young: float=250.
    area: float=.7322329862910148
    inertia: float=.04266666666666668
    poisson: float=.32
    shear_correction: float=5/6
    timoshenko: bool=False
    load: float=1e-6
    coupling: float=1.
    connectors: tuple=tuple(range(1,21))
    wire_tension: float=0.
    wire_eccentricity: float=0.
    contact_gap: float | None=None
    contact_stiffness: float=1.

    def validate(self):
        if type(self.layers) is not int or type(self.nodes) is not int or not 1<=self.layers<=16 or not 3<=self.nodes<=101:
            raise ValueError('research resource bound: 1..16 layers, 3..101 nodes')
        scalars=[v for v in asdict(self).values() if type(v) is float]
        if not all(math.isfinite(v) for v in scalars):raise ValueError('nonfinite design')
        if min(self.length,self.thickness,self.young,self.area,self.inertia,self.shear_correction,self.contact_stiffness)<=0 or min(self.coupling,self.load,self.wire_tension)<0:
            raise ValueError('invalid physical parameter')
        if not -1<self.poisson<.5 or (self.contact_gap is not None and self.contact_gap<0):raise ValueError('invalid Poisson ratio/contact gap')
        if any(type(i) is not int or not 1<=i<self.nodes for i in self.connectors) or len(set(self.connectors))!=len(self.connectors):raise ValueError('invalid connectors')
        if self.layers*self.nodes*3>1500:raise ValueError('dense research FEM bounded to 1500 DOF')

def assemble(d):
    d.validate();n=d.nodes;size=3*n*d.layers;dx=d.length/(n-1)
    K=np.zeros((size,size));f=np.zeros(size)
    def ix(l,i,c):return 3*(l*n+i)+c
    shear=d.young/(2*(1+d.poisson))*d.area*d.shear_correction
    psi=12*d.young*d.inertia/(shear*dx**2) if d.timoshenko else 0.
    bend=d.young*d.inertia/(dx**3*(1+psi))*np.array([
        [12,6*dx,-12,6*dx],[6*dx,(4+psi)*dx**2,-6*dx,(2-psi)*dx**2],
        [-12,-6*dx,12,-6*dx],[6*dx,(2-psi)*dx**2,-6*dx,(4+psi)*dx**2]])
    for l in range(d.layers):
        for i in range(n-1):
            a=[ix(l,i,0),ix(l,i+1,0)];K[np.ix_(a,a)]+=d.young*d.area/dx*np.array([[1,-1],[-1,1]])
            a=[ix(l,i,1),ix(l,i,2),ix(l,i+1,1),ix(l,i+1,2)];K[np.ix_(a,a)]+=bend
        f[ix(l,n-1,1)]=-d.load/d.layers
        f[ix(l,n-1,2)]=-d.wire_tension*d.wire_eccentricity/d.layers
    B=[]
    for l in range(d.layers-1):
        for i in d.connectors:
            b=np.zeros(size);b[ix(l,i,0)]=-1;b[ix(l+1,i,0)]=1
            b[ix(l,i,2)]=b[ix(l+1,i,2)]=d.thickness/2;B.append(b)
    B=np.array(B).reshape((-1,size))
    fixed=[ix(l,0,c) for l in range(d.layers) for c in range(3)]
    free=np.array([i for i in range(size) if i not in fixed]);tips=[ix(l,n-1,1) for l in range(d.layers)]
    return K,f,B,free,tips

def solve(d):
    K,f,B,free,tips=assemble(d);K=K+d.coupling*B.T@B
    q=np.zeros(len(f));active=np.zeros(len(tips),dtype=bool)
    for iteration in range(20):
        M=K.copy();rhs=f.copy()
        if d.contact_gap is not None:
            for i,on in zip(tips,active):
                if on:M[i,i]+=d.contact_stiffness;rhs[i]-=d.contact_stiffness*d.contact_gap
        q[free]=np.linalg.solve(M[np.ix_(free,free)],rhs[free])
        new=np.array([q[i]<-d.contact_gap for i in tips]) if d.contact_gap is not None else active
        if np.array_equal(active,new):break
        active=new
    else:raise RuntimeError('contact active set not converged')
    residual=K@q-f
    reaction=np.zeros(len(tips))
    if d.contact_gap is not None:
        for j,i in enumerate(tips):reaction[j]=d.contact_stiffness*max(0.,-d.contact_gap-q[i]);residual[i]-=reaction[j]
    slips=B@q;tip=-float(np.mean(q[tips]));rot=max(abs(q[2::3]));norm=max(d.load,d.wire_tension*abs(d.wire_eccentricity)/d.length,1e-15)
    all_slips=[q[3*((l+1)*d.nodes+i)]-q[3*(l*d.nodes+i)]+d.thickness/2*(q[3*(l*d.nodes+i)+2]+q[3*((l+1)*d.nodes+i)+2]) for l in range(d.layers-1) for i in range(1,d.nodes)]
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(residual)):raise ValueError('nonfinite FEM solution')
    return dict(deflection_mm=tip,max_connector_slip_mm=float(max(abs(slips),default=0)),max_interface_slip_mm=max(map(abs,all_slips),default=0.),max_rotation_rad=float(rot),
        residual=float(max(abs(residual[free]))),normalized_residual=float(max(abs(residual[free]))/norm),
        energy=float(.5*q@K@q),external_work=float(f@q),contact_reaction=float(sum(reaction)),
        contact_penetration_mm=float(max([max(0.,-d.contact_gap-q[i]) for i in tips],default=0)) if d.contact_gap is not None else 0.,
        small_rotation_validated=bool(rot<.005),equilibrium=True,config=asdict(d),displacement=q.tolist())

def spring_slider(slip,plastic,k,capacity):
    """Elastic-perfectly-plastic tangential return mapping. Compression prescribed.

    capacity=mu*pressure*tributary_area (model F). No vacuum seal/contact mechanics.
    Free energy=.5*k*(s-z)^2. Plastic dissipation=capacity*abs(dz)>=0.
    """
    if not all(math.isfinite(v) for v in (slip,plastic,k,capacity)) or k<=0 or capacity<0:raise ValueError('invalid slider')
    trial=k*(slip-plastic);force=float(np.clip(trial,-capacity,capacity));new=slip-force/k
    return dict(traction=force,plastic=new,tangent=k if abs(trial)<capacity else 0.,
        elastic_energy=.5*force*force/k,dissipation=capacity*abs(new-plastic))

def friction_path(d,loads,pressure,mu,width):
    """Incremental quasi-static return mapping coupled to the independent FEM."""
    if min(pressure,mu)<0 or width<=0 or not all(math.isfinite(v) for v in (pressure,mu,width)) or d.coupling<=0:raise ValueError('invalid friction inputs')
    if d.contact_gap is not None or d.wire_tension:raise ValueError('friction+contact/wire integration not yet validated')
    K,f,B,free,tips=assemble(d);plastic=np.zeros(len(B));q=np.zeros(len(f));records=[]
    # Voronoi tributary area covers span excluding clamp cell; tip gets half cell.
    positions=sorted(d.connectors);bounds=[0.]+[(a+b)*d.length/(2*(d.nodes-1)) for a,b in zip(positions,positions[1:])]+[d.length]
    areas=np.diff(bounds)*width if positions else np.array([])
    capacity=np.tile(mu*pressure*areas,d.layers-1);diss=0.
    for load in loads:
        if not math.isfinite(load):raise ValueError('nonfinite load')
        external=f.copy()
        for i in tips:external[i]=-load/d.layers
        for iteration in range(40):
            slip=B@q;trial=d.coupling*(slip-plastic);traction=np.clip(trial,-capacity,capacity)
            residual=K@q+B.T@traction-external
            if max(abs(residual[free]))<1e-12:break
            tangent=d.coupling*(abs(trial)<capacity)
            J=K+B.T@(tangent[:,None]*B)
            increment=np.linalg.solve(J[np.ix_(free,free)],-residual[free])
            q[free]+=increment
        else:raise RuntimeError('friction equilibrium not converged')
        new=slip-traction/d.coupling;incremental=float(np.sum(capacity*abs(new-plastic)));plastic=new;diss+=incremental
        records.append(dict(load=load,deflection_mm=-float(np.mean(q[tips])),max_slip_mm=float(max(abs(slip),default=0)),
            residual=float(max(abs(residual[free]))),dissipation=incremental,cumulative_dissipation=diss,
            stored_energy=float(.5*q@K@q+.5*np.sum(traction**2/d.coupling)),
            max_traction=float(max(abs(traction),default=0)),max_capacity=float(max(capacity,default=0)),
            yielded=int(sum(abs(trial)>=capacity)),iterations=iteration+1))
    return records
