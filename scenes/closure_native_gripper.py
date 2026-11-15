"""Independent native triangle-surface/contact-constraint experiment.

Not a certified replacement for the line-skin benchmark. Surface width8mm and
thickness.2mm are research collision skins, NOT recalibrated beam EA/EI.
"""
import csv,json,math,os
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
import Sofa.Core

def seq(values):return ' '.join(map(str,values))
def triangles_outward(points,triangles):
    for a,b,c in triangles:
        u=[points[b][j]-points[a][j] for j in range(3)];v=[points[c][j]-points[a][j] for j in range(3)];cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if sum(cross[j]*(points[a][j]+points[b][j]+points[c][j]) for j in range(3))<0:b,c=c,b
        yield a,b,c

def createScene(root):
    source=Path(os.environ['REGRIP_NATIVE_SOURCE']);out=Path(os.environ['REGRIP_NATIVE_OUT']);c=json.loads((source/'config.json').read_text());xml=ET.parse(source/'scene.scn').getroot();root.dt=c['dt'];root.gravity=[0,0,0]
    for i,name in enumerate(('AnimationLoop','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Mapping.NonLinear','Topology.Container.Constant')):
        root.addObject('RequiredPlugin',name='native_req'+str(i),pluginName='Sofa.Component.'+name)
    for element in xml:
        if element.tag in ('Node','DefaultAnimationLoop'):continue
        attrs=dict(element.attrib)
        if element.tag=='EulerImplicitSolver':attrs['name']='ode'
        if element.tag=='EigenSparseLU':attrs['template']='CompressedRowSparseMatrixd'
        root.addObject(element.tag,**attrs)
    root.addObject('FreeMotionAnimationLoop')
    solver=root.addObject('BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=True)
    root.addObject('CollisionPipeline',depth=10,verbose=0,draw=0);root.addObject('BruteForceBroadPhase');root.addObject('BVHNarrowPhase')
    root.addObject('MinProximityIntersection',alarmDistance=.01,contactDistance=0)
    root.addObject('CollisionResponse',response='FrictionContactConstraint',responseParams='mu='+str(c['mu']))
    body=root.addChild('Multilayer')
    for element in xml.find('Node'):
        if element.tag in ('StickSlipContact','ActiveIntervalContact'):continue
        if element.tag=='IntegratedRecorder':element.set('filename',str(out/'native_state.txt'))
        body.addObject(element.tag,**dict(element.attrib))
    body.addObject('LinearSolverConstraintCorrection',linearSolver='@../solver',ODESolver='@../ode')
    n=c['nodes'];obj=c['object_index'];points=[];indices=[];triangles=[]
    for layer in range(4):
        offset=len(points)
        for i in range(n):
            for y,z in ((-4,-.1),(4,-.1),(4,.1),(-4,.1)):points.append([0,y,z]);indices.append(layer*n+i)
        for i in range(n-1):
            for side in range(4):a=offset+4*i+side;b=offset+4*i+(side+1)%4;triangles.extend([(a,b,b+4),(a,b+4,a+4)])
        triangles.extend([(offset,offset+2,offset+1),(offset,offset+3,offset+2)]);tip=offset+4*(n-1);triangles.extend([(tip,tip+1,tip+2),(tip,tip+2,tip+3)])
    fingers=body.addChild('film_surface');fingers.addObject('MeshTopology',triangles=seq(v for t in triangles for v in t));fingers.addObject('MechanicalObject',name='points',template='Vec3d',position=seq(v for p in points for v in p));fingers.addObject('TriangleCollisionModel',group=1,bothSide=True);fingers.addObject('LineCollisionModel',group=1);fingers.addObject('PointCollisionModel',group=1);fingers.addObject('RigidMapping',input='@../dofs',output='@points',rigidIndexPerPoint=seq(indices),globalToLocalCoords=False)
    radius=c['object_radius'];lat=int(os.environ.get('REGRIP_SURFACE_LAT','24'));lon=2*lat;points=[[0,radius,0]]
    for i in range(1,lat):
        for j in range(lon):theta=math.pi*i/lat;phi=2*math.pi*j/lon;points.append([radius*math.sin(theta)*math.cos(phi),radius*math.cos(theta),radius*math.sin(theta)*math.sin(phi)])
    points.append([0,-radius,0]);triangles=[]
    for j in range(lon):triangles.append((0,1+j,1+(j+1)%lon))
    for i in range(lat-2):
        for j in range(lon):a=1+i*lon+j;b=1+i*lon+(j+1)%lon;triangles.extend([(a,b,b+lon),(a,b+lon,a+lon)])
    bottom=len(points)-1
    for j in range(lon):triangles.append((bottom,1+(lat-2)*lon+j,1+(lat-2)*lon+(j+1)%lon))
    sphere=body.addChild('object_surface');sphere.addObject('MeshTopology',triangles=seq(v for t in triangles_outward(points,triangles) for v in t));sphere.addObject('MechanicalObject',name='points',template='Vec3d',position=seq(v for p in points for v in p));sphere.addObject('TriangleCollisionModel',group=2);sphere.addObject('LineCollisionModel',group=2);sphere.addObject('PointCollisionModel',group=2);sphere.addObject('RigidMapping',input='@../dofs',output='@points',rigidIndexPerPoint=seq([obj]*len(points)),globalToLocalCoords=False)
    class Recorder(Sofa.Core.Controller):
        def __init__(self):
            super().__init__();self.step=0;self.peak=0.;self.nonzero=0;self.stream=(out/'native_states.jsonl').open('x')
        def onAnimateEndEvent(self,event):
            self.step+=1
            forces=solver.constraintForces.value.tolist();peak=max(map(abs,forces),default=0);self.peak=max(self.peak,peak);self.nonzero+=int(peak>0)
            if self.step==int(os.environ.get('REGRIP_NATIVE_STEPS','48000')):(out/'reaction_diagnostics.json').write_text(json.dumps(dict(max_constraint_force_every_step=self.peak,nonzero_reaction_steps=self.nonzero)))
            if self.step%20:return
            state=body.dofs;matrix=state.constraint.value.tocoo();record=dict(time=float(root.time.value),X=state.position.value.tolist(),V=state.velocity.value.tolist(),constraint_matrix=dict(shape=list(matrix.shape),row=matrix.row.tolist(),col=matrix.col.tolist(),data=matrix.data.tolist()),constraint_forces=solver.constraintForces.value.tolist(),constraint_impulse=(state.constraint.value.T@np.array(solver.constraintForces.value)).reshape(-1).tolist() if state.constraint.value.shape[0]==len(solver.constraintForces.value) else None)
            self.stream.write(json.dumps(record,allow_nan=False)+'\n');self.stream.flush()
    root.addObject(Recorder());return root
