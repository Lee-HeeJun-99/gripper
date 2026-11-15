"""Native triangle-plane / free rigid BOX force-unit and stick/slip calibration.

Not a gripper. A finite flat box face supports a physical center-of-pressure
shift. No object pose constraint or artificial balancing moment is applied.
"""
import os,json,math
from pathlib import Path
import numpy as np
import Sofa.Core
def createScene(root):
    out=Path(os.environ['REGRIP_NATIVE_OUT']);root.dt=float(os.environ.get('REGRIP_NATIVE_DT','.001'));root.gravity=[0,0,0]
    names=('AnimationLoop','ODESolver.Backward','LinearSolver.Direct','StateContainer','Mass','MechanicalLoad','Topology.Container.Constant','Constraint.Projective','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Mapping.NonLinear')
    for i,name in enumerate(names):root.addObject('RequiredPlugin',name='req'+str(i),pluginName='Sofa.Component.'+name)
    root.addObject('FreeMotionAnimationLoop')
    solver=root.addObject('BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-12,maxIterations=1000,computeConstraintForces=True)
    root.addObject('CollisionPipeline');root.addObject('BruteForceBroadPhase');root.addObject('BVHNarrowPhase');root.addObject(os.environ.get('REGRIP_INTERSECTOR','LocalMinDistance'),alarmDistance=.01,contactDistance=.001);root.addObject('CollisionResponse',response='FrictionContactConstraint',responseParams='mu=0.3')
    ground=root.addChild('Ground');ground.addObject('MeshTopology',position='-10 -10 0 10 -10 0 10 10 0 -10 10 0',triangles='0 1 2 0 2 3');ground.addObject('MechanicalObject',template='Vec3d',name='dofs',position='-10 -10 0 10 -10 0 10 10 0 -10 10 0');ground.addObject('FixedProjectiveConstraint',indices='0 1 2 3');ground.addObject('TriangleCollisionModel',simulated=False,moving=False,group=1)
    ground.addObject('LineCollisionModel',simulated=False,moving=False,group=1);ground.addObject('PointCollisionModel',simulated=False,moving=False,group=1)
    ball=root.addChild('FreeSphere');state=ball.addObject('MechanicalObject',template='Rigid3d',name='dofs',position='0 0 1.001 0 0 0 1');ball.addObject('UniformMass',template='Rigid3d',mstate='@dofs',vertexMass='.01 1 .6666666666666666 0 0 0 .6666666666666666 0 0 0 .6666666666666666');force=ball.addObject('ConstantForceField',template='Rigid3d',indices='0',forces='0 0 -.01 0 0 0')
    # The linear solver must be scoped to the SAME state as this correction.
    # A root solver also containing the floor gave a wrong local-index compliance.
    ball.addObject('EulerImplicitSolver',name='ode',rayleighMass=0,rayleighStiffness=0);ball.addObject('EigenSparseLU',name='solver',template='CompressedRowSparseMatrixd');ball.addObject('LinearSolverConstraintCorrection',linearSolver='@solver',ODESolver='@ode')
    # LMD does not register RigidSphere/Triangle intersections in this SDK.
    # Use actual mapped triangle/edge/point geometry, not an unsupported pair.
    points=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];triangles=[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(1,5,6),(1,6,2),(2,6,7),(2,7,3),(3,7,4),(3,4,0)]
    triangles=[(a,c,b) if np.dot(np.cross(np.array(points[b])-points[a],np.array(points[c])-points[a]),np.array(points[a])+points[b]+points[c])<0 else (a,b,c) for a,b,c in triangles]
    surface=ball.addChild('surface');surface.addObject('MeshTopology',position=points,triangles=triangles);surface.addObject('MechanicalObject',template='Vec3d',position=points);surface.addObject('TriangleCollisionModel',group=2,bothSide=True);surface.addObject('LineCollisionModel',group=2);surface.addObject('PointCollisionModel',group=2);surface.addObject('RigidMapping',input='@../dofs')
    class Observer(Sofa.Core.Controller):
        def __init__(self):super().__init__();self.step=0;self.current=np.array([0.,0.,-.01,0.,0.,0.]);self.stream=(out/'native.jsonl').open('x')
        def onAnimateBeginEvent(self,event):
            t=float(root.time.value);fx=0 if t<.5 else (.001 if t<1 else (.005 if t<1.5 else 0));fz=.01 if 1.5<=t<2 else -.01
            self.current=np.array([fx,0,fz,0,0,0]);force.forces.value=[self.current.tolist()]
        def onAnimateEndEvent(self,event):
            self.step+=1
            if self.step%round(.01/float(root.dt.value)):return
            J=state.constraint.value;lam=np.array(solver.constraintForces.value);fc=np.asarray(J.T@lam).reshape(-1).tolist() if J.shape[0]==len(lam) else None
            self.stream.write(json.dumps(dict(time=float(root.time.value),X=state.position.value.tolist(),V=state.velocity.value.tolist(),external=self.current.tolist(),constraint_wrench=fc,lambda_raw=lam.tolist(),J_shape=list(J.shape),surface_min_z=float(surface.getMechanicalState().position.value[:,2].min()),J=J.toarray().tolist()),allow_nan=False)+'\n');self.stream.flush()
    root.addObject(Observer());return root
