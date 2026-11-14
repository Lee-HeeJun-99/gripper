"""V1.0.7: experimental tangential-only SOFA Python force field.

IMPORTANT: require the Windows SOFA v26.06 user to runtime-test.
A single 2N-node Rigid3d state has TWO DISCONNECTED sets of beam elements.
The mapped interface owns all 2N Vec3d points so cross-layer K acts inside
ONE ForceFieldVec3d with force AND tangent (addDForce) implemented.
"""
import csv
import math
from pathlib import Path
import numpy as np
import Sofa.Core

HERE=Path(__file__).resolve().parent
N=11; L=30.0; H=0.4; WIDTH=8.0; E=250.0; NU=0.32
F=1e-4; END=0.30
PLUGINS=['Sofa.Component.AnimationLoop','Sofa.Component.Constraint.Projective',
'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
'Sofa.Component.Mass','Sofa.Component.SolidMechanics.FEM.Elastic',
'Sofa.Component.StateContainer','Sofa.Component.Topology.Container.Constant',
'Sofa.Component.MechanicalLoad','Sofa.Component.Mapping.NonLinear','Sofa.Component.Visual']

def rad(): return (4*(WIDTH*H**3/12)/math.pi)**0.25

class TangentialPairForceField(Sofa.Core.ForceFieldVec3d):
    """E=0.5*k*sum((x_upper-x_lower-reference_slip)**2), x-only.

    Active pairs 1..N-1. Linear stiffness with exact -k*B.T*B in mapped-space.
    Nonlinear rigid mapping projects reaction forces and lever-arm torques.
    """
    def __init__(self,k=0.01,n=N,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.k=float(k); self.n=int(n)
        self.reference_slip=np.zeros(self.n-1,dtype=float)
        self.force_calls=0;self.dforce_calls=0;self.last_kfactor=None
    def addForce(self,m,forces,pos,vel):
        arr=np.asarray(pos.value,dtype=float)
        if len(arr)!=2*self.n:
            raise RuntimeError('V107: mapped interface should contain 2N points; got '+str(len(arr)))
        slip=(arr[self.n+1:,0]-arr[1:self.n,0])-self.reference_slip
        with forces.writeableArray() as output:
            output[1:self.n,0] += self.k*slip
            output[self.n+1:2*self.n,0] -= self.k*slip
        self.force_calls+=1
    def addDForce(self,m,df,dx):
        deriv=np.asarray(dx.value,dtype=float)
        dslip=deriv[self.n+1:2*self.n,0]-deriv[1:self.n,0]
        kfac_get=getattr(m,'kFactor',None)
        factor=float(kfac_get()) if callable(kfac_get) else 1.0
        self.last_kfactor=factor
        with df.writeableArray() as output:
            output[1:self.n,0] += factor*self.k*dslip
            output[self.n+1:2*self.n,0] -= factor*self.k*dslip
        self.dforce_calls+=1

class Recorder(Sofa.Core.Controller):
    def __init__(self,root,dofs,pts,forcefield,case,dt,k):
        super().__init__()
        self.root=root;self.dofs=dofs;self.pts=pts;self.ff=forcefield
        self.case=case;self.dt=float(dt);self.k=float(k)
        self.initial=None;self.initial_pts=None;self.n=0;self.done=False;self.fp=None
        self.path=HERE/('result_V107_'+case+'.csv')
    def onAnimateBeginEvent(self,event):
        if self.initial is not None:return
        self.initial=np.asarray(self.dofs.position.value,dtype=float).copy()
        self.initial_pts=np.asarray(self.pts.position.value,dtype=float).copy()
        self.fp=self.path.open('w',newline='',encoding='utf-8-sig')
        self.writer=csv.writer(self.fp)
        self.writer.writerow(['time_s','case','k_per_pair','dt_s','tip_deflection_mm',
        'tip_velocity_z_mm_s','max_tangential_slip_x_mm','max_normal_separation_z_mm',
        'max_lateral_separation_y_mm','interface_energy','max_mapped_movement_mm',
        'force_calls','dforce_calls','last_kfactor','status'])
        self.fp.flush();print('[V107] writing',str(self.path),flush=True)
    def onAnimateEndEvent(self,event):
        if self.initial is None or self.done:return
        self.n+=1;t=self.n*self.dt
        cur=np.asarray(self.dofs.position.value,dtype=float)
        vel=np.asarray(self.dofs.velocity.value,dtype=float)
        pts=np.asarray(self.pts.position.value,dtype=float)
        delta=pts[N:2*N,:]-pts[:N,:]
        tip=-0.5*((cur[N-1,2]-self.initial[N-1,2])+(cur[2*N-1,2]-self.initial[2*N-1,2]))
        vz=0.5*(vel[N-1,2]+vel[2*N-1,2])
        slip=float(np.max(np.abs(delta[1:,0])))
        gapz=float(np.max(np.abs(delta[1:,2])))
        gapy=float(np.max(np.abs(delta[1:,1])))
        energy=0.5*self.k*float(np.sum(delta[1:,0]**2))
        moved=float(np.max(np.linalg.norm(pts-self.initial_pts,axis=1)))
        nums=[t,tip,vz,slip,gapz,gapy,energy,moved]
        if not all(math.isfinite(x) for x in nums):status='INVALID_NONFINITE'
        elif abs(tip)>1 or moved>1 or abs(vz)>1e5:status='INVALID_LARGE_DISPLACEMENT'
        elif t>=END-1e-10:status='COMPLETE'
        else:status='OK'
        self.writer.writerow([round(t,10),self.case,self.k,self.dt,tip,vz,slip,gapz,gapy,
            energy,moved,self.ff.force_calls if self.ff else 0,
            self.ff.dforce_calls if self.ff else 0,
            self.ff.last_kfactor if self.ff else '',status])
        if self.n<=3 or self.n%max(1,round(.01/self.dt))==0 or status!='OK':
            print('[V107]',self.case,'t=',round(t,7),'tip=',round(tip,9),
                  'slip=',round(slip,9),'addF=',self.ff.force_calls if self.ff else 0,
                  'addDF=',self.ff.dforce_calls if self.ff else 0,'status=',status,flush=True)
            self.fp.flush()
        if status!='OK':
            self.done=True;self.fp.close();self.fp=None
    def __del__(self):
        try:
            if self.fp:self.fp.close()
        except Exception:pass

def create_scene(root,case='TANGENT_K001_DT05',k=0.01,dt=0.0005,method='tangential'):
    for i,plugin in enumerate(PLUGINS):root.addObject('RequiredPlugin',name='req'+str(i),pluginName=plugin)
    root.dt=float(dt);root.gravity=[0.,0.,0.]
    root.addObject('DefaultAnimationLoop')
    root.addObject('EulerImplicitSolver',rayleighMass=.2,rayleighStiffness=.1)
    # Iterative linear solver calls Python addDForce (no Python addKToMatrix required).
    root.addObject('CGLinearSolver',name='globalCG',iterations=1000,
                   tolerance=1e-12,threshold=1e-14)
    poses=[]
    for z in [-H/2,H/2]:
        for i in range(N):poses.append([L*i/(N-1),0.,z,0.,0.,0.,1.])
    body=root.addChild('Bilayer')
    dofs=body.addObject('MechanicalObject',name='dofs',template='Rigid3d',position=poses,
                        showObject=True,showObjectScale=.25)
    lines=[[i,i+1] for i in range(N-1)]+[[N+i,N+i+1] for i in range(N-1)]
    body.addObject('MeshTopology',name='edges',lines=lines)
    body.addObject('UniformMass',totalMass=2e-5)
    body.addObject('BeamFEMForceField',radius=rad(),radiusInner=0.,
                   youngModulus=E,poissonRatio=NU)
    body.addObject('FixedProjectiveConstraint',indices=[0,N])
    body.addObject('ConstantForceField',indices=[N-1,2*N-1],
                   forces=[[0.,0.,-F/2,0.,0.,0.],[0.,0.,-F/2,0.,0.,0.]])
    interface=body.addChild('Interface')
    points=[[L*i/(N-1),0.,0.] for _layer in range(2) for i in range(N)]
    pts=interface.addObject('MechanicalObject',name='points',template='Vec3d',
                            position=points,showObject=True,showObjectScale=.10)
    interface.addObject('RigidMapping',template='Rigid3d,Vec3d',input='@../dofs',
                        output='@points',rigidIndexPerPoint=list(range(2*N)),
                        globalToLocalCoords=True)
    ff=None
    if method=='tangential' and k>0:
        ff=interface.addObject(TangentialPairForceField(name='TangentialCoupling',k=k,n=N))
    elif method!='free' and method!='tangential':
        raise ValueError('method must be free or tangential')
    root.addObject(Recorder(root,dofs,pts,ff,case,dt,k))
    print('[V107] case=',case,'method=',method,'k=',k,'dt=',dt,'two disconnected beam chains',flush=True)
    return root
