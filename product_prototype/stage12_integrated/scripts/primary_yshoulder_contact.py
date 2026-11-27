"""Finite owner triangle plane gap, exact virtual work and coverage.
New P1 shoulder contact operator only. Not an equilibrium solver or tie.
"""
import numpy as np

def evaluate(point,triangle,normal_sign=1.,pressure=0.):
 a,b,c=np.asarray(triangle);q=np.asarray(point);e1=b-a;e2=c-a;h=np.cross(e1,e2)*normal_sign;length=np.linalg.norm(h)
 if length<=1e-14:raise ValueError('Degenerate finite owner triangle')
 n=h/length;d=q-a;gap=float(n@d);dot=np.array([[e1@e1,e1@e2],[e1@e2,e2@e2]]);s,t=np.linalg.solve(dot,[d@e1,d@e2]);weights=np.array([1-s-t,s,t]);inside=bool(weights.min()>=-1e-8)
 # Plane-distance derivative, root point and all three independent owner vertices.
 v=pressure*(d-n*gap)/length*normal_sign;f1=np.cross(e2,v);f2=np.cross(v,e1);fp=pressure*n;ft=np.array([-fp-f1-f2,f1,f2]);return dict(gap_mm=gap,inside=inside,barycentric=weights,point_gradient=fp,triangle_gradient=ft,normal=n)

def local_step_bound(body_increments,motor_rotation_increment,limit=.05):
 """Algorithmic original localmodel limit, never a physical stiffness/restraint."""
 motion=max(np.linalg.norm(d,axis=1).max() for d in body_increments)
 rotation=np.linalg.norm(motor_rotation_increment);return min(1.,limit/max(motion,1e-300),limit/max(rotation,1e-300))
