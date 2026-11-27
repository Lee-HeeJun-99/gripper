"""Physical source-point loads at actual P1 current support pose.
Basewrench reconstructed from gravity/object/cable physicalsources, never from
subtracting an elastic/contact/reference residual. Hardware stays nonlocal.
"""
import json
import numpy as np
from skfem import MeshTet
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO
from primary_finite_port import ObjectiveRootPort,motor_pullback
from primary_seated_string import SeatedString
from primary_seated_finger_v2 import solve

class CurrentLoads:
 def __init__(self,model):
  self.model=model;self.a=model.a;self.seed=json.loads((ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json').read_text())[0];self.points=json.loads((ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json').read_text());self.old=json.loads((ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json').read_text());b=model.bodies['F0_ROOT_BACK'];self.rids=np.flatnonzero(abs(b['X'][:,0]-50.5)<1e-5);self.root=ObjectiveRootPort(b['X'][self.rids],self.a['Root_port_weights_mm2'][self.rids]);b=model.bodies['TEST_BASE'];p=b['X'];m=MeshTet(p.T,b['t'].T);tri=m.facets[:,m.boundary_facets()].T;tri=tri[np.all(abs(p[tri,2]-66)<1e-5,axis=1)];centers=np.array([[-44,-30],[-44,10],[86,-30],[86,10]]);tri=tri[np.min(np.linalg.norm(p[tri].mean(1)[:,None,:2]-centers[None,:,:],axis=2),axis=1)>4.7];area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)/2;w=np.zeros(len(p))
  for j in range(3):np.add.at(w,tri[:,j],area/3)
  self.bids=np.flatnonzero(w);self.base=ObjectiveRootPort(p[self.bids],w[self.bids])
 def __call__(self,u):
  model=self.model;ru=model.body_u(u,'F0_ROOT_BACK')[self.rids];R,c,B=self.root.pose(ru);tr=c*.001-R@(self.root.center*.001);z=u[model.mo:model.mo+6];Rm=Rotation.from_rotvec(z[3:]).as_matrix();C=np.array([0,0,.020])+z[:3]*.001;E=R@np.array([self.seed['cable_end_m'][0],0,self.seed['cable_end_m'][1]])+tr
  initial=SeatedString(self.points,Rm,C,E,.01125).solve(self.seed);parent=dict(root_R=R.tolist(),root_translation_m=tr.tolist(),motor_R=Rm.tolist(),motor_C_m=C.tolist(),actual_wire_center_radius_m=.01125,actual=initial);actual=solve(parent,self.seed,self.points);RW=np.array(actual['Root_origin_wrench_N_Nm']);MW=np.array(actual['Motor_origin_wrench_N_Nm']);dy=np.array([0,actual['string']['root_free_Y_shift_mm']*.001,0]);f=np.zeros(model.N);elastic=np.zeros(6);bodies=[]
  for name,b in model.bodies.items():
   mass=b['w']*b['rho']*1e-9;ff=np.zeros_like(b['X']);ff[:,2]=-mass*9.80665;model.scatter(f,name,ff);x=(b['X']+model.body_u(u,name))*.001;W=np.r_[ff.sum(0),np.cross(x,ff).sum(0)];elastic+=W;bodies.append(dict(part=name,mass_kg=float(mass.sum()),current_gravity_wrench_N_Nm=W.tolist()))
  rootf=np.zeros_like(model.bodies['F0_ROOT_BACK']['X']);rootf[self.rids]=self.root.pullback(ru,RW-np.r_[np.zeros(3),np.cross(dy,RW[:3])]);model.scatter(f,'F0_ROOT_BACK',rootf);f[model.mo:model.mo+6]=motor_pullback(z,MW);bu=model.body_u(u,'TEST_BASE')[self.bids];hardware=np.zeros(6);points=[]
  for name,hp in self.old['hardware_actual_mass_geometry'].items():
   m=hp['volume_mm3']*7900e-9;q=self.base.positions(bu,np.array(hp['centroid_mm'])[None,:]*.001)[0];ff=np.array([0,0,-m*9.80665]);hardware+=np.r_[ff,np.cross(q,ff)];points.append(dict(part=name,mass_kg=m,current_position_m=q.tolist()))
  HW=np.zeros_like(model.bodies['TEST_BASE']['X']);HW[self.bids]=self.base.pullback(bu,hardware);model.scatter(f,'TEST_BASE',HW)
  physical_base=-(RW+MW+elastic+hardware);BW=np.zeros_like(HW);BW[self.bids]=self.base.pullback(bu,physical_base);model.scatter(f,'TEST_BASE',BW)
  actual['string']={k:v for k,v in actual['string'].items() if k not in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')}
  detail=dict(upstream=actual,elastic_gravity=bodies,hardware_points=points,hardware_current_wrench_N_Nm=hardware.tolist(),physical_Base_wrench_N_Nm=physical_base.tolist(),root_freeY_increment_mm=float(dy[1]*1000),applied_current_wrench_N_Nm=model.wrench(u,f).tolist(),Base_residual_cancellation=False)
  return f,detail
