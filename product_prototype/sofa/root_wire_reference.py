"""Independent planar circular-wrap reference, NOT a SOFA solver/component."""
import argparse,json,math,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def circular_path(a,b,r):
 a=np.asarray(a,float);b=np.asarray(b,float)
 if r<=0 or min(np.linalg.norm(a),np.linalg.norm(b))<=r:raise ValueError('external endpoints required')
 u=math.atan2(a[1],a[0])+math.acos(r/np.linalg.norm(a))
 v=math.atan2(b[1],b[0])-math.acos(r/np.linalg.norm(b))
 angle=(v-u)%(2*math.pi)
 if not 1e-8<angle<2*math.pi-1e-8:raise ValueError('branch transition is not differentiable here')
 ta=r*np.array([math.cos(u),math.sin(u)]);tb=r*np.array([math.cos(v),math.sin(v)])
 la=np.linalg.norm(a-ta);lb=np.linalg.norm(b-tb)
 return la+lb+r*angle,ta,tb,(a-ta)/la,(b-tb)/lb

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);x=p.parse_args();out=BASE/'results'/x.tag;out.mkdir(exist_ok=False)
 r=.002;a=np.array([r,-.01]);b=np.array([-.01,r]);length,ta,tb,da,db=circular_path(a,b,r)
 fd=[]
 for endpoint in range(2):
  for axis in range(2):
   h=1e-7;ap=a.copy();am=a.copy();bp=b.copy();bm=b.copy()
   if endpoint==0:ap[axis]+=h;am[axis]-=h
   else:bp[axis]+=h;bm[axis]-=h
   fd.append((circular_path(ap,bp,r)[0]-circular_path(am,bm,r)[0])/(2*h))
 gradient=np.r_[da,db];tension=1.5;forces=tension*np.array([da,db]);torque=float(ta[0]*forces[0,1]-ta[1]*forces[0,0]+tb[0]*forces[1,1]-tb[1]*forces[1,0])
 rotation_errors=[]
 for theta in (.1,1.,2.):
  rot=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
  rotation_errors.append(abs(circular_path(rot@a,rot@b,r)[0]-length))
 rejected=False
 try:circular_path([0,0],b,r)
 except ValueError:rejected=True
 err=float(abs(np.array(fd)-gradient).max());passed=err<1e-8 and abs(length-(.02+r*math.pi/2))<1e-14 and abs(torque)<1e-14 and max(rotation_errors)<1e-14 and rejected
 d=dict(status='PASS_INDEPENDENT_CIRCULAR_BRANCH_REFERENCE_ONLY' if passed else 'FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),radius_m=r,endpoints_m=[a.tolist(),b.tolist()],tangent_points_m=[ta.tolist(),tb.tolist()],length_m=length,arc_length_m=r*math.pi/2,endpoint_gradient=gradient.tolist(),finite_difference_gradient=fd,maximum_gradient_error=err,rotation_length_errors_m=rotation_errors,branch_tension_N=tension,pulley_force_N=forces.sum(axis=0).tolist(),spin_torque_Nm=torque,invalid_endpoint_rejected=rejected,scope='Independent massless inextensible frictionless wire on a fixed circular locus. Equal branch tension is an ASSUMPTION. Axle receives resultant,spin torque zero. Circular surface spin leaves locus/path unchanged. Smooth chosen tangent/wrap branch only;no general 3D,contact birth,friction,Native sliding implementation,measured data or holding certification.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
