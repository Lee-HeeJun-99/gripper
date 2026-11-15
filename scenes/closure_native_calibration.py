"""Native triangle-plane / free rigid-sphere force-unit and stick/slip calibration.

Not a gripper. Horizontal load is accompanied by an EXPLICIT external couple
to avoid conflating free rolling with tangential stick in the sub-limit stage.
"""
import os,json,math
from pathlib import Path
import numpy as np
import Sofa.Core
def createScene(root):
    out=Path(os.environ['REGRIP_NATIVE_OUT']);root.dt=.001;root.gravity=[0,0,0]
    names=('AnimationLoop','ODESolver.Backward','LinearSolver.Direct','StateContainer','Mass','MechanicalLoad','Topology.Container.Constant','Constraint.Projective','Collision.Detection.Algorithm','Collision.Detection.Intersection','Collision.Geometry','Collision.Response.Contact','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','Mapping.NonLinear')
    for i,name in enumerate(names):root.addObject('RequiredPlugin',name='req'+str(i),pluginName='Sofa.Component.'+name)
    root.addObject('FreeMotionAnimationLoop');root.addObject('EulerImplicitSolver',name='ode',rayleighMass=0,rayleighStiffness=0);root.addObject('EigenSparseLU',name='solver')
    solver=root.addObject('BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-12,maxIterations=1000,computeConstraintForces=True)
    root.addObject('CollisionPipeline');root.addObject('BruteForceBroadPhase');root.addObject('BVHNarrowPhase');root.addObject('LocalMinDistance',alarmDistance=.01,contactDistance=.001);root.addObject('CollisionResponse',response='FrictionContactConstraint',responseParams='mu=0.3')
    ground=root.addChild('Ground');ground.addObject('MeshTopology',position='-10 -10 0 10 -10 0 10 10 0 -10 10 0',triangles='0 1 2 0 2 3');ground.addObject('MechanicalObject',template='Vec3d',name='dofs',position='-10 -10 0 10 -10 0 10 10 0 -10 10 0');ground.addObject('FixedProjectiveConstraint',indices='0 1 2 3');ground.addObject('TriangleCollisionModel',simulated=False,moving=False,group=1)
    ground.addObject('LineCollisionModel',simulated=False,moving=False,group=1);ground.addObject('PointCollisionModel',simulated=False,moving=False,group=1)
    ball=root.addChild('FreeSphere');state=ball.addObject('MechanicalObject',template='Rigid3d',name='dofs',position='0 0 1.001 0 0 0 1');ball.addObject('DiagonalMass',template='Rigid3d,Rigid3d',vertexMass='.01 1 .4 0 0 0 .4 0 0 0 .4');force=ball.addObject('ConstantForceField',indices='0',forces='0 0 -.01 0 0 0');ball.addObject('LinearSolverConstraintCorrection',linearSolver='@../solver',ODESolver='@../ode')
    # LMD does not register RigidSphere/Triangle intersections in this SDK.
    # Use actual mapped triangle/edge/point geometry, not an unsupported pair.
    points=[[0,0,-1],[0,0,1],[-1,0,0],[1,0,0],[0,-1,0],[0,1,0]];triangles=[(0,2,4),(0,4,3),(0,3,5),(0,5,2),(1,4,2),(1,3,4),(1,5,3),(1,2,5)]
    surface=ball.addChild('surface');surface.addObject('MeshTopology',position=points,triangles=triangles);surface.addObject('MechanicalObject',template='Vec3d',position=points);surface.addObject('TriangleCollisionModel',group=2,bothSide=True);surface.addObject('LineCollisionModel',group=2);surface.addObject('PointCollisionModel',group=2);surface.addObject('RigidMapping',input='@../dofs')
    class Observer(Sofa.Core.Controller):
        def __init__(self):super().__init__();self.step=0;self.current=np.array([0.,0.,-.01,0.,0.,0.]);self.stream=(out/'native.jsonl').open('x')
        def onAnimateBeginEvent(self,event):
            t=float(root.time.value);fx=0 if t<.5 else (.001 if t<1 else (.005 if t<1.5 else 0));fz=.01 if 1.5<=t<2 else -.01
            self.current=np.array([fx,0,fz,0,-fx,0]);force.forces.value=[self.current.tolist()]
        def onAnimateEndEvent(self,event):
            self.step+=1
            if self.step%10:return
            J=state.constraint.value;lam=np.array(solver.constraintForces.value);fc=np.asarray(J.T@lam).reshape(-1).tolist() if J.shape[0]==len(lam) else None
            self.stream.write(json.dumps(dict(time=float(root.time.value),X=state.position.value.tolist(),V=state.velocity.value.tolist(),external=self.current.tolist(),constraint_wrench=fc,lambda_raw=lam.tolist(),J_shape=list(J.shape)),allow_nan=False)+'\n');self.stream.flush()
    root.addObject(Observer());return root
