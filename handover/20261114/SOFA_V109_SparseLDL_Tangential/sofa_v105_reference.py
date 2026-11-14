"""V1.0.5: controlled mapped-beam spring diagnostics for SOFA 26.06.
Uses the successfully launched V104 interface, and *never* writes SOFA Data at runtime.
This is NOT a friction, jamming, or true directional-shear implementation.
"""
import csv
import math
from pathlib import Path
import Sofa.Core

HERE = Path(__file__).resolve().parent
L = 30.0
N = 11
T = 0.4
WIDTH = 8.0
E = 250.0
POISSON = .32
F_TOTAL = 1e-4
DAMPING = 1e-5
STOP = .30
PLUGINS = [
    'Sofa.Component.AnimationLoop',
    'Sofa.Component.Constraint.Projective',
    'Sofa.Component.LinearSolver.Direct',
    'Sofa.Component.ODESolver.Backward',
    'Sofa.Component.Mass',
    'Sofa.Component.SolidMechanics.FEM.Elastic',
    'Sofa.Component.StateContainer',
    'Sofa.Component.Topology.Container.Constant',
    'Sofa.Component.MechanicalLoad',
    'Sofa.Component.Visual',
    'Sofa.Component.Mapping.NonLinear',
    'Sofa.Component.SolidMechanics.Spring',
]

def radius():
    return (4 * (WIDTH*T**3/12.)/math.pi)**.25

def scene_basics(root,dt):
    for i, p in enumerate(PLUGINS):
        root.addObject('RequiredPlugin', name='req'+str(i), pluginName=p)
    root.dt=dt
    root.gravity=[0.,0.,0.]
    root.addObject('DefaultAnimationLoop')
    root.addObject('EulerImplicitSolver', rayleighMass=.2, rayleighStiffness=.1)
    root.addObject('SparseLDLSolver',name='globalLDL', template='CompressedRowSparseMatrixd')
    root.addObject('VisualStyle',displayFlags='showBehaviorModels showVisualModels showForceFields')
    root.addObject('InteractiveCamera', name='camera',position=[15.,-60.,25.],
                   lookAt=[15.,0.,0.],zNear=.01,zFar=300.)

def add_beam(root,label,z,point_y_offset):
    node = root.addChild(label)
    poses=[[L*i/(N-1),0.,z,0.,0.,0.,1.] for i in range(N)]
    dofs=node.addObject('MechanicalObject',name='dofs',template='Rigid3d',
                        position=poses,showObject=True,showObjectScale=.25)
    node.addObject('MeshTopology',name='edges',lines=[[i,i+1] for i in range(N-1)])
    node.addObject('UniformMass',totalMass=1e-5)
    node.addObject('BeamFEMForceField',radius=radius(),radiusInner=0.,
                   youngModulus=E,poissonRatio=POISSON)
    node.addObject('FixedProjectiveConstraint',indices=[0])
    node.addObject('ConstantForceField',indices=[N-1],forces=[[0.,0.,-F_TOTAL/2.,0.,0.,0.]])
    iface=node.addChild('Interface')
    # RigidMapping with globalToLocalCoords=True, matching V104 working scenes.
    # Points start on common z=0 interface. Upper layer can be offset in Y (width direction).
    pos=[[L*i/(N-1),point_y_offset,0.] for i in range(N)]
    pts=iface.addObject('MechanicalObject',name='points',template='Vec3d',
                        position=pos,showObject=True,showObjectScale=.12)
    iface.addObject('RigidMapping',template='Rigid3d,Vec3d',input='@../dofs',
                    output='@points',rigidIndexPerPoint=list(range(N)),
                    globalToLocalCoords=True)
    return dofs,pts

class Recorder(Sofa.Core.Controller):
    def __init__(self,case,root,lower,upper,p1,p2,k,dt,selected,rest):
        super().__init__()
        self.case=case;self.root=root;self.lower=lower;self.upper=upper
        self.p1=p1;self.p2=p2;self.k=float(k);self.dt=float(dt)
        self.selected=list(selected);self.rest=float(rest)
        self.n=0;self.base=None;self.points0=None;self.done=False
        self.fp=None;self.writer=None
        self.path=HERE/('result_V105_'+case+'.csv')
    def onAnimateBeginEvent(self,event):
        if self.base is not None:return
        self.base=(float(self.lower.position.value[-1][2]),float(self.upper.position.value[-1][2]))
        a=self.p1.position.value;b=self.p2.position.value
        self.points0=([[float(v) for v in p] for p in a],[[float(v) for v in p] for p in b])
        self.fp=self.path.open('w',newline='',encoding='utf-8-sig')
        self.writer=csv.writer(self.fp)
        self.writer.writerow(['time_s','case','k_per_spring','dt_s','active_springs','rest_mm',
            'tip_deflection_mm','tip_velocity_z_mm_s','max_x_slip_mm','max_y_rel_mm',
            'max_z_rel_mm','max_rel_distance_mm','max_displacement_from_initial_mm',
            'max_spring_extension_mm','spring_energy_proxy','translational_kinetic_proxy',
            'external_work_proxy','status'])
        self.fp.flush()
        print('[V105] CSV:',self.path,flush=True)
    def onAnimateEndEvent(self,event):
        if self.done or self.base is None:return
        self.n+=1
        t=self.n*self.dt
        lo=self.lower.position.value;up=self.upper.position.value
        vlo=self.lower.velocity.value;vup=self.upper.velocity.value
        dz=(self.base[0]-float(lo[-1][2])+self.base[1]-float(up[-1][2]))/2.
        vz=(float(vlo[-1][2])+float(vup[-1][2]))/2.
        a=self.p1.position.value;b=self.p2.position.value
        diffs=[[float(x[j])-float(y[j]) for j in range(3)] for x,y in zip(a,b)]
        maxx=max(abs(d[0]) for d in diffs)
        maxy=max(abs(d[1]) for d in diffs)
        maxz=max(abs(d[2]) for d in diffs)
        distances=[math.sqrt(sum(v*v for v in d)) for d in diffs]
        maxdist=max(distances)
        aa,bb=self.points0
        move=max(math.sqrt(sum((float(p[j])-q[j])**2 for j in range(3)))
                 for now,init in ((a,aa),(b,bb)) for p,q in zip(now,init))
        ex=[distances[i]-self.rest for i in self.selected]
        maxext=max((abs(v) for v in ex),default=0.)
        spring_e=.5*self.k*sum(v*v for v in ex)
        # Proxy excludes rotational kinetic energy and does NOT equal SOFA total energy.
        m=1e-5/N
        kinetic=.5*m*sum(sum(float(v[j])**2 for j in range(3)) for v in list(vlo)+list(vup))
        work=F_TOTAL*dz
        checks=[t,dz,vz,maxx,maxy,maxz,maxdist,move,maxext,spring_e,kinetic,work]
        if not all(math.isfinite(v) for v in checks): status='INVALID_NONFINITE'
        elif abs(dz)>1. or move>1. or abs(vz)>1e5:status='INVALID_LARGE_DISPLACEMENT'
        elif t>=STOP-1e-12:status='COMPLETE'
        else:status='OK'
        self.writer.writerow([round(t,9),self.case,self.k,self.dt,len(self.selected),self.rest,
                              dz,vz,maxx,maxy,maxz,maxdist,move,maxext,spring_e,
                              kinetic,work,status])
        if self.n<=3 or self.n%max(1,round(.01/self.dt))==0 or status!='OK':
            print('[V105]',self.case,'t=',round(t,7),'tip=',round(dz,8),
                  'movement=',round(move,7),'max_extension=',round(maxext,7),
                  'status=',status,flush=True)
            self.fp.flush()
        if status!='OK':
            self.done=True;self.fp.flush();self.fp.close();self.fp=None
    def __del__(self):
        try:
            if self.fp is not None:self.fp.close()
        except Exception:pass

def create_scene(root,case,k,dt,connections='all',initial_offset_y=0.):
    """Only changes #connections, initial point separation, stiffness, and dt."""
    scene_basics(root,dt)
    low,p1=add_beam(root,'Lower',-.2,0.)
    up,p2=add_beam(root,'Upper',+.2,initial_offset_y)
    selected=list(range(1,N)) if connections=='all' else ([N-1] if connections=='one' else [])
    rest=abs(float(initial_offset_y))
    if k>0 and selected:
        root.addObject('SpringForceField',name='interfaceSprings',template='Vec3d',
            object1='@Lower/Interface/points',object2='@Upper/Interface/points',
            springsIndices1=selected,springsIndices2=selected,
            stiffness=float(k),damping=DAMPING,lengths=[rest]*len(selected))
    root.addObject(Recorder(case,root,low,up,p1,p2,k,dt,selected,rest))
    print('[V105] scene',case,'k=',k,'dt=',dt,'springs=',len(selected),
          'offset_y=',initial_offset_y,'rest=',rest,flush=True)
    return root
