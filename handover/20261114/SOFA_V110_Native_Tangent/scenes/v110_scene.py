"""Native rigid-DOF tangential FF; SOFA v26.06 Windows research prototype.
Note: stand-alone scene cannot validate without compiling matching ABI DLL first.
"""
import csv, math
from pathlib import Path
import numpy as np
import Sofa.Core

HERE=Path(__file__).resolve().parent
N=11; L=30.; H=.4; WIDTH=8.; E=250.; NU=.32; F=.0001; END=.30

def radius():return (4*(WIDTH*H**3/12)/math.pi)**.25

class Recorder(Sofa.Core.Controller):
    def __init__(self, root,dofs,case,k,dt):
        super().__init__(); self.root=root;self.dofs=dofs;self.case=case;self.k=k;self.dt=dt
        self.initial=None;self.fp=None;self.done=False;self.step=0
        self.path=HERE/('result_V110_'+case+'.csv')
    def onAnimateBeginEvent(self,event):
        if self.initial is not None:return
        self.initial=np.asarray(self.dofs.position.value,dtype=float).copy()
        self.fp=self.path.open('w',newline='',encoding='utf-8-sig')
        self.writer=csv.writer(self.fp)
        self.writer.writerow(['time_s','case','stiffness','dt_s','tip_deflection_mm',
          'tip_velocity_z_mm_s','max_shear_x_mm','shear_energy','mean_abs_rotation_quat_xyz','status'])
        self.fp.flush();print('[V110] CSV:',self.path,flush=True)
    def onAnimateEndEvent(self,event):
        if self.done or self.initial is None:return
        self.step+=1;t=self.step*self.dt
        pos=np.asarray(self.dofs.position.value,dtype=float)
        vel=np.asarray(self.dofs.velocity.value,dtype=float)
        tip=-.5*((pos[N-1,2]-self.initial[N-1,2])+(pos[2*N-1,2]-self.initial[2*N-1,2]))
        vz=.5*(vel[N-1,2]+vel[2*N-1,2])
        # Linearized rigid-contact shear consistent with native ForceField
        slips=pos[N+1:2*N,0]-pos[1:N,0]-H*(pos[N+1:2*N,4]+pos[1:N,4])
        slip=float(np.max(np.abs(slips)))
        energy=float(.5*self.k*np.sum(slips*slips))
        rotation=float(np.mean(np.linalg.norm(pos[:,3:6],axis=1)))
        if not all(math.isfinite(x) for x in (tip,vz,slip,energy,rotation)):status='INVALID_NONFINITE'
        elif abs(tip)>1 or abs(vz)>1e5:status='INVALID_LARGE_DISPLACEMENT'
        elif t>=END-1e-12:status='COMPLETE'
        else:status='OK'
        self.writer.writerow([round(t,9),self.case,self.k,self.dt,tip,vz,slip,energy,rotation,status])
        if self.step<=3 or self.step%max(1,round(.01/self.dt))==0 or status!='OK':
            print('[V110]',self.case,round(t,6),'tip',round(tip,8),'slip',round(slip,9),status,flush=True)
            self.fp.flush()
        if status!='OK':self.done=True;self.fp.close();self.fp=None
    def __del__(self):
        try:
            if self.fp:self.fp.close()
        except Exception:pass

def create_scene(root,case='00_FREE',k=0.,dt=.0005):
    plugins=['Sofa.Component.AnimationLoop','Sofa.Component.Constraint.Projective',
        'Sofa.Component.LinearSolver.Direct','Sofa.Component.ODESolver.Backward',
        'Sofa.Component.Mass','Sofa.Component.SolidMechanics.FEM.Elastic',
        'Sofa.Component.StateContainer','Sofa.Component.Topology.Container.Constant',
        'Sofa.Component.MechanicalLoad']
    for i,name in enumerate(plugins):root.addObject('RequiredPlugin',name='req'+str(i),pluginName=name)
    if k>0:root.addObject('RequiredPlugin',name='nativePlugin',pluginName='SofaTangentialV110')
    root.dt=dt;root.gravity=[0.,0.,0.]
    root.addObject('DefaultAnimationLoop')
    root.addObject('EulerImplicitSolver',rayleighMass=.2,rayleighStiffness=.1)
    root.addObject('SparseLDLSolver',name='globalLDL',template='CompressedRowSparseMatrixd')
    poses=[[L*i/(N-1),0.,z,0.,0.,0.,1.] for z in [-H/2,H/2] for i in range(N)]
    body=root.addChild('Bilayer')
    dofs=body.addObject('MechanicalObject',name='dofs',template='Rigid3d',position=poses,
        showObject=True,showObjectScale=.25)
    lines=[[i,i+1] for i in range(N-1)]+[[N+i,N+i+1] for i in range(N-1)]
    body.addObject('MeshTopology',name='edges',lines=lines)
    body.addObject('UniformMass',totalMass=2e-5)
    body.addObject('BeamFEMForceField',radius=radius(),radiusInner=0.,youngModulus=E,poissonRatio=NU)
    body.addObject('FixedProjectiveConstraint',indices=[0,N])
    body.addObject('ConstantForceField',indices=[N-1,2*N-1],forces=[
        [0.,0.,-F/2,0.,0.,0.],[0.,0.,-F/2,0.,0.,0.]])
    if k>0:
        body.addObject('TangentialRigidForceField',name='tangential',stiffness=k,
                       layerThickness=H,nodesPerLayer=N,includeRoot=False)
    root.addObject(Recorder(root,dofs,case,k,dt))
    print('[V110] scene',case,'K=',k,'dt=',dt,flush=True)
    return root
