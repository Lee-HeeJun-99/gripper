"""Independent actual native surface experiment; no SDF force double counting."""
import csv,json,math,os
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import Sofa.Core
def seq(x):return ' '.join(map(str,x))
def outward(points,triangles):
    for a,b,c in triangles:
        if np.dot(np.cross(np.array(points[b])-points[a],np.array(points[c])-points[a]),np.array(points[a])+points[b]+points[c])<0:b,c=c,b
        yield a,b,c
def createScene(root):
    source=Path(os.environ['REGRIP_NATIVE_SOURCE']);out=Path(os.environ['REGRIP_NATIVE_OUT']);c=json.loads((source/'config.json').read_text());xml=ET.parse(source/'scene.scn').getroot();root.dt=c['dt'];root.gravity=[0,0,0]
    for i,name in enumerate(('AnimationLoop','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Mapping.NonLinear','Topology.Container.Constant')):root.addObject('RequiredPlugin',name='native'+str(i),pluginName='Sofa.Component.'+name)
    for e in xml:
        if e.tag in ('Node','DefaultAnimationLoop'):continue
        a=dict(e.attrib)
        if e.tag=='EulerImplicitSolver':a['name']='ode'
        if e.tag=='EigenSparseLU':a['template']='CompressedRowSparseMatrixd'
        root.addObject(e.tag,**a)
    root.addObject('FreeMotionAnimationLoop');solver=root.addObject('BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=True);root.addObject('CollisionPipeline',depth=10,verbose=0,draw=0);root.addObject('BruteForceBroadPhase');root.addObject('BVHNarrowPhase');root.addObject('MinProximityIntersection',alarmDistance=.01,contactDistance=float(os.environ['REGRIP_CONTACT_BUFFER']),useSurfaceNormals=True);root.addObject('CollisionResponse',response='FrictionContactConstraint',responseParams='mu='+str(c['mu']));body=root.addChild('Multilayer')
    for e in xml.find('Node'):
        if e.tag in ('ActiveIntervalContact','StickSlipContact'):continue
        a=dict(e.attrib)
        if 'filename' in a:a['filename']=str(out/Path(a['filename']).name)
        body.addObject(e.tag,**a)
    body.addObject('LinearSolverConstraintCorrection',linearSolver='@../solver',ODESolver='@../ode');n=c['nodes'];obj=c['object_index'];points=[];indices=[];triangles=[]
    for layer in range(obj//n):
        start=len(points)
        for i in range(n):
            for y,z in ((-4,-.1),(4,-.1),(4,.1),(-4,.1)):points.append([0,y,z]);indices.append(layer*n+i)
        for i in range(n-1):
            for j in range(4):a=start+4*i+j;b=start+4*i+(j+1)%4;triangles.extend([(a,b,b+4),(a,b+4,a+4)])
        triangles.extend([(start,start+2,start+1),(start,start+3,start+2)]);last=start+4*(n-1);triangles.extend([(last,last+1,last+2),(last,last+2,last+3)])
    film=body.addChild('film');film.addObject('MeshTopology',triangles=seq(i for t in triangles for i in t));film.addObject('MechanicalObject',name='points',template='Vec3d',position=seq(v for p in points for v in p));film.addObject('TriangleCollisionModel',group=1,bothSide=True);film.addObject('LineCollisionModel',group=1);film.addObject('PointCollisionModel',group=1);film.addObject('RigidMapping',input='@../dofs',output='@points',rigidIndexPerPoint=seq(indices),globalToLocalCoords=False)
    lat=int(os.environ['REGRIP_SURFACE_LAT']);lon=2*lat;radius=c['object_radius'];points=[[0,radius,0]];triangles=[]
    for i in range(1,lat):
        for j in range(lon):t=math.pi*i/lat;p=2*math.pi*j/lon;points.append([radius*math.sin(t)*math.cos(p),radius*math.cos(t),radius*math.sin(t)*math.sin(p)])
    points.append([0,-radius,0])
    for j in range(lon):triangles.append((0,1+j,1+(j+1)%lon))
    for i in range(lat-2):
        for j in range(lon):a=1+i*lon+j;b=1+i*lon+(j+1)%lon;triangles.extend([(a,b,b+lon),(a,b+lon,a+lon)])
    for j in range(lon):triangles.append((len(points)-1,1+(lat-2)*lon+j,1+(lat-2)*lon+(j+1)%lon))
    sphere=body.addChild('object');sphere.addObject('MeshTopology',triangles=seq(i for t in outward(points,triangles) for i in t));sphere.addObject('MechanicalObject',name='points',template='Vec3d',position=seq(v for p in points for v in p));sphere.addObject('TriangleCollisionModel',group=2);sphere.addObject('LineCollisionModel',group=2);sphere.addObject('PointCollisionModel',group=2);sphere.addObject('RigidMapping',input='@../dofs',output='@points',rigidIndexPerPoint=seq([obj]*len(points)),globalToLocalCoords=False)
    class Recorder(Sofa.Core.Controller):
        def __init__(self):super().__init__();self.step=0;self.stream=(out/'native.jsonl').open('x')
        def onAnimateEndEvent(self,event):
            self.step+=1
            if self.step%20:return
            state=body.dofs;lam=np.array(solver.constraintForces.value);J=state.constraint.value;impulse=(J.T@lam).reshape(-1).tolist() if J.shape[0]==len(lam) else None
            # Parent constraint rows have projective DOFs removed. Preserve the
            # ORIGINAL child contact Jacobians to recover physical reactions on
            # blocked guide/root DOFs, not infer them by cancelling external load.
            physical=np.zeros((obj+1,6));X=np.array(state.position.value);complete=True
            for child,owners in ((film.points,indices),(sphere.points,[obj]*len(points))):
                C=child.constraint.value
                if C.shape[0]!=len(lam):complete=False;continue
                # SOFA sparse child matrices omit unused trailing columns.
                # Zero-pad those DOFs explicitly; they carry no contact impulse.
                world=np.array(child.position.value);flat=np.array(C.T@lam).reshape(-1)
                if len(flat)>3*len(world):raise ValueError('child contact columns exceed state')
                forces=np.zeros_like(world);forces.reshape(-1)[:len(flat)]=flat
                for i,owner in enumerate(owners):physical[owner,:3]+=forces[i];physical[owner,3:]+=np.cross(world[i]-X[owner,:3],forces[i])
            self.stream.write(json.dumps(dict(time=float(root.time.value),X=state.position.value.tolist(),V=state.velocity.value.tolist(),lambda_impulse=lam.tolist(),generalized_impulse=impulse,unprojected_generalized_impulse=physical.reshape(-1).tolist() if complete else None),allow_nan=False)+'\n');self.stream.flush()
    root.addObject(Recorder());return root
