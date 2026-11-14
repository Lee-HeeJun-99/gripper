"""V1.0.8: staged controls for beam baseline / solver / tangential coupling.

DO NOT interpret completion as a validated physical jamming model.
Always check 00 V105 reference first. Custom ForceField derived from V107.
"""
from pathlib import Path
import csv, math
import numpy as np
import Sofa.Core
from sofa_v105_reference import create_scene as v105_create
from sofa_v107_reference import TangentialPairForceField

HERE=Path(__file__).resolve().parent
N=11; L=30.0; H=.4; WIDTH=8.; E=250.; NU=.32; F=1e-4; END=.30
PLUGINS=['Sofa.Component.AnimationLoop','Sofa.Component.Constraint.Projective',
'Sofa.Component.LinearSolver.Direct','Sofa.Component.LinearSolver.Iterative',
'Sofa.Component.ODESolver.Backward','Sofa.Component.Mass',
'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.StateContainer',
'Sofa.Component.Topology.Container.Constant','Sofa.Component.MechanicalLoad',
'Sofa.Component.Mapping.NonLinear','Sofa.Component.Visual']

def rad():return (4*(WIDTH*H**3/12)/math.pi)**.25

class Recorder108(Sofa.Core.Controller):
    def __init__(self, root, dofs, points, field, case, dt, k, axial_load):
        super().__init__()
        self.root=root;self.dofs=dofs;self.points=points;self.field=field
        self.case=case;self.dt=dt;self.k=k;self.axial_load=axial_load
        self.n=0;self.initial=None;self.initial_points=None;self.fp=None;self.done=False
        self.path=HERE/('result_V108_'+case+'.csv')
    def onAnimateBeginEvent(self,event):
        if self.initial is not None:return
        self.initial=np.asarray(self.dofs.position.value,dtype=float).copy()
        self.initial_points=np.asarray(self.points.position.value,dtype=float).copy()
        self.fp=self.path.open('w',newline='',encoding='utf-8-sig')
        self.writer=csv.writer(self.fp)
        self.writer.writerow(['time_s','case','k_per_pair','dt_s','axial_pair_force','tip_deflection_mm',
        'tip_velocity_z_mm_s','max_x_slip_mm','max_y_rel_mm','max_z_rel_mm',
        'max_mapped_movement_mm','max_rigid_movement_mm','mean_abs_rotation_quat_xyz',
        'max_x_contact_force_proxy','shear_energy_proxy','addForce_calls','addDForce_calls','status'])
        self.fp.flush();print('[V108] CSV',self.path,flush=True)
    def onAnimateEndEvent(self,event):
        if self.done or self.initial is None:return
        self.n+=1;t=self.n*self.dt
        pos=np.asarray(self.dofs.position.value,dtype=float)
        vel=np.asarray(self.dofs.velocity.value,dtype=float)
        pts=np.asarray(self.points.position.value,dtype=float)
        delta=pts[N:]-pts[:N]
        slip=delta[1:,0]
        tip=-.5*((pos[N-1,2]-self.initial[N-1,2])+(pos[2*N-1,2]-self.initial[2*N-1,2]))
        vz=.5*(vel[N-1,2]+vel[2*N-1,2])
        sx=float(np.max(np.abs(slip)))
        sy=float(np.max(np.abs(delta[1:,1])))
        sz=float(np.max(np.abs(delta[1:,2])))
        pm=float(np.max(np.linalg.norm(pts-self.initial_points,axis=1)))
        rm=float(np.max(np.linalg.norm(pos[:,:3]-self.initial[:,:3],axis=1)))
        rot=float(np.mean(np.linalg.norm(pos[:,3:6],axis=1)))
        shear=.5*self.k*float(np.sum(slip**2))
        fmax=self.k*sx
        checks=(t,tip,vz,sx,sy,sz,pm,rm,rot,shear,fmax)
        if not all(math.isfinite(x) for x in checks):status='INVALID_NONFINITE'
        elif abs(tip)>1 or pm>1 or rm>1 or abs(vz)>1e5:status='INVALID_LARGE_DISPLACEMENT'
        elif t>=END-1e-12:status='COMPLETE'
        else:status='OK'
        self.writer.writerow([round(t,9),self.case,self.k,self.dt,self.axial_load,tip,vz,sx,sy,sz,pm,rm,rot,fmax,
                              shear,self.field.force_calls if self.field else 0,
                              self.field.dforce_calls if self.field else 0,status])
        if self.n<=3 or self.n%max(1,round(.01/self.dt))==0 or status!='OK':
            print('[V108]',self.case,'t',round(t,6),'tip',round(tip,8),
                  'slip',round(sx,9),'rot',round(rot,8),'status',status,flush=True)
            self.fp.flush()
        if status!='OK':
            self.done=True;self.fp.close();self.fp=None
    def __del__(self):
        try:
            if self.fp is not None:self.fp.close()
        except Exception:pass

def create_combined_scene(root,case,solver='ldl',k=0.,dt=.0005,axial_force=0.):
    for i,p in enumerate(PLUGINS):root.addObject('RequiredPlugin',name='req'+str(i),pluginName=p)
    root.dt=dt;root.gravity=[0.,0.,0.]
    root.addObject('DefaultAnimationLoop')
    root.addObject('EulerImplicitSolver',rayleighMass=.2,rayleighStiffness=.1)
    if solver=='ldl':root.addObject('SparseLDLSolver',name='globalLDL',template='CompressedRowSparseMatrixd')
    elif solver=='cg':root.addObject('CGLinearSolver',name='globalCG',iterations=1000,tolerance=1e-12,threshold=1e-14)
    else:raise ValueError('Unknown solver')
    poses=[[L*i/(N-1),0.,z,0.,0.,0.,1.] for z in [-H/2,H/2] for i in range(N)]
    body=root.addChild('Bilayer')
    dofs=body.addObject('MechanicalObject',name='dofs',template='Rigid3d',position=poses,
                        showObject=True,showObjectScale=.25)
    lines=[[i,i+1] for i in range(N-1)]+[[N+i,N+i+1] for i in range(N-1)]
    body.addObject('MeshTopology',name='edges',lines=lines)
    body.addObject('UniformMass',totalMass=2e-5)
    body.addObject('BeamFEMForceField',radius=rad(),radiusInner=0.,youngModulus=E,poissonRatio=NU)
    body.addObject('FixedProjectiveConstraint',indices=[0,N])
    # identical vertical loading to reference. Optional opposite X forces on tips
    # to stimulate measurable interface slip independent of bending.
    lower_force=[axial_force,0.,-F/2,0.,0.,0.]
    upper_force=[-axial_force,0.,-F/2,0.,0.,0.]
    body.addObject('ConstantForceField',indices=[N-1,2*N-1],forces=[lower_force,upper_force])
    iface=body.addChild('Interface')
    pts=iface.addObject('MechanicalObject',name='points',template='Vec3d',
          position=[[L*i/(N-1),0.,0.] for _ in range(2) for i in range(N)],
          showObject=True,showObjectScale=.12)
    iface.addObject('RigidMapping',template='Rigid3d,Vec3d',input='@../dofs',
            output='@points',rigidIndexPerPoint=list(range(2*N)),globalToLocalCoords=True)
    ff=None
    if k>0:
        ff=iface.addObject(TangentialPairForceField(name='TangentialCoupling',k=k,n=N))
    root.addObject(Recorder108(root,dofs,pts,ff,case,dt,k,axial_force))
    print('[V108] case',case,'solver',solver,'k',k,'dt',dt,'axial_force',axial_force,flush=True)
    return root

def create_scene(root,case='00_REFERENCE',mode='reference',solver='ldl',k=0.,dt=.0005,axial_force=0.):
    if mode=='reference':
        # EXACT V105 implementation (separate BeamFEM chains, direct LDL).
        return v105_create(root,case='V108_'+case,k=0.,dt=dt,connections='none',initial_offset_y=0.)
    return create_combined_scene(root,case,solver,k,dt,axial_force)
