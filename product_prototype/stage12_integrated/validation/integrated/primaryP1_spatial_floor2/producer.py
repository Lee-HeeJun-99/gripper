"""Actual P1 smooth finite spool floor / massive spatial string shooting.
Frozen saved elastic support poses and Finger XZ; Root Y is an unloaded mode,
solved from zero world-Y string force, never an imposed physical support.
"""
import sys,json,shutil
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.optimize import root
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_gravity_pullback import G,RADIUS,FREE0,rot
from primary_support_feedback import fit
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder


def W(q,f):return np.r_[f,np.cross(q,f)]
class SpatialString:
 def __init__(self,points,Rm,C,E,r,order=16,factor=1):
  self.points=points;self.R=Rm;self.C=C;self.E=E;self.r=r;self.a=Rm[:,1];self.ex=Rm[:,0];self.ez=Rm[:,2];self.order=order
  z,w=leggauss(order);self.u=(z+1)/2;self.weights=w/2;self.mu=next(p['mass_kg'] for p in points if p['mode']=='wire')/(FREE0+.006);self.gravity=np.array([0,0,-G*factor]);self.w=self.mu*self.gravity
 def vec(self,theta):return np.cos(theta)*self.ex+np.sin(theta)*self.ez,-np.sin(theta)*self.ex+np.cos(theta)*self.ez
 def free(self,A,h,L,detail=False):
  def integ(s):
   ss=np.asarray(s);hh=h-ss[...,None,None]*self.u[:,None]*self.w;return ss[...,None]*np.einsum('...ij,i->...j',hh/np.linalg.norm(hh,axis=-1)[...,None],self.weights)
  end=A+integ(L);moment=L*np.einsum('ij,i->j',A+integ(L*self.u),self.weights)
  return end,h-self.w*L,moment,(A+integ(np.linspace(0,L,65))) if detail else None
 def evaluate(self,z,details=False):
  hA=self.R@z[:3];l0=z[3]*.001;phi=z[4];l1=z[5]*.001;eta=z[6];dy=z[7]*.001
  A=self.C+self.R@np.array([RADIUS*np.sin(eta),0,RADIUS*np.cos(eta)])
  B,hB,m0,p0=self.free(A,hA,l0,details);b=self.R.T@(B-self.C);theta0=np.arctan2(b[2],b[0]);er,et=self.vec(theta0);pt=hB@et;py=hB@self.a
  def ode(theta,y):
   yy,pt,py=y[:3];er,et=self.vec(theta);H=np.hypot(pt,py);ds=self.r*H/pt;q=self.C+self.r*er+yy*self.a
   return np.r_[self.r*py/pt,-(self.w@et)*ds,-(self.w@self.a)*ds,ds,q*ds]
  sol=solve_ivp(ode,(theta0,phi),np.r_[b[1],pt,py,0.,np.zeros(3)],rtol=2e-11,atol=1e-13,dense_output=details)
  yy,pt,py,Lw=sol.y[:4,-1];er,et=self.vec(phi);Q=self.C+self.r*er+yy*self.a;hQ=pt*et+py*self.a
  end,hE,m1,p1=self.free(Q,hQ,l1,details);E=self.E+np.array([0,dy,0]);Fe=-hE
  xz=rot(eta)@[-.003,RADIUS];tail=self.C+self.R@np.array([xz[0],0,xz[1]])
  moment=m0+sol.y[4:,-1]+m1+.006*tail;wireW=W(moment*self.mu,self.gravity) # cross(mu*integral(q ds),g), force replaced below
  wireW[:3]=self.mu*(l0+Lw+l1+.006)*self.gravity
  rotorW=np.zeros(6);rotors=[]
  for p in self.points:
   if p['mode']!='rotor':continue
   q=np.array(p['rest_centroid_m'])-np.array([0,0,.020]);xz=rot(eta)@q[[0,2]];q=self.C+self.R@np.array([xz[0],q[1],xz[1]]);rotorW+=W(q,p['mass_kg']*self.gravity);rotors.append(dict(part_ID=p['part_ID'],mass_kg=p['mass_kg'],position_m=q.tolist()))
  MW=W(E,-Fe)+wireW+rotorW;torque=(MW[3:]-np.cross(self.C,MW[:3]))@self.a
  residual=np.r_[(end-E)/.001,(np.hypot(b[0],b[2])-self.r)/.001,hB@self.vec(theta0)[0],(l0+Lw+l1-FREE0)/.001,(torque-self.T*RADIUS)/.01,Fe[1]]
  if not details:return residual
  th=np.linspace(theta0,phi,129);ys=sol.sol(th);pw=np.array([self.C+self.r*self.vec(t)[0]+y*self.a for t,y in zip(th,ys[0])]);ptt=ys[1];pyy=ys[2];HH=np.hypot(ptt,pyy);lamb=ptt**2/(HH*self.r)-np.array([self.w@self.vec(t)[0] for t in th]);curve=np.vstack([p0,pw,p1]);local=(self.R.T@(curve-self.C).T).T
  return dict(residual=residual.tolist(),state=z.tolist(),E_m=E.tolist(),A_m=A.tolist(),B_m=B.tolist(),Q_m=Q.tolist(),end_m=end.tolist(),Fe_N=Fe.tolist(),motor_origin_wrench_N_Nm=MW.tolist(),wire_gravity_wrench_N_Nm=wireW.tolist(),rotor_gravity_wrench_N_Nm=rotorW.tolist(),rotors=rotors,curve_m=curve.tolist(),wrap_local_axial_minmax_m=[float(ys[0].min()),float(ys[0].max())],wrap_min_normal_N_per_m=float(lamb.min()),contact_start_theta_rad=float(theta0),departure_theta_rad=float(phi),contact_length_m=float(Lw),lead_length_m=float(l0),free_length_m=float(l1),motor_axis_torque_Nm=float(torque),target_motor_axis_torque_Nm=self.T*RADIUS,minimum_tension_N=float(min(np.linalg.norm(hA),np.linalg.norm(hE),HH.min())),root_free_Y_shift_mm=float(z[7]),wrap_curve_m=pw.tolist(),lead_curve_m=p0.tolist(),free_curve_m=p1.tolist(),ODE_success=bool(sol.success))
 def solve(self,seed):
  self.T=seed['T_N'];alpha=np.arccos(self.r/RADIUS);eta=seed['rotor_angle_rad'];theta=np.pi/2-eta-alpha;_,et=self.vec(theta);hA=self.R.T@(-seed['wire_start_tension_N']*et);l0=np.sqrt(RADIUS**2-self.r**2)
  z0=np.r_[hA,l0*1000,seed['drum_tangent_phi_rad'],seed['wire_free_length_m']*1000,eta,0.]
  sol=root(self.evaluate,z0,tol=1e-10);res=self.evaluate(sol.x,True);res['root_success']=bool(sol.success);res['root_message']=str(sol.message);res['residual_max']=float(np.max(abs(sol.fun)));res['checks']=dict(root_success=bool(sol.success),residual=res['residual_max']<1e-8,length_positive=min(res['lead_length_m'],res['contact_length_m'],res['free_length_m'])>0,compression=res['wrap_min_normal_N_per_m']>0,tension=res['minimum_tension_N']>0,flat_floor_axial=max(abs(np.array(res['wrap_local_axial_minmax_m'])))<.0002,ODE_success=res['ODE_success']);res['checks']={k:bool(v) for k,v in res['checks'].items()};return res

def main():
 tag=sys.argv[1];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 cadsrc=ROOT/'cad/exports/primaryP1_retention20/summary.json';cad=json.loads(cadsrc.read_text());spool=cad['part_references']['F0_SPOOL'];assert sha(REPO/spool['path'])==spool['SHA256'];s=read(REPO/spool['path']);it=TopExp_Explorer(s,TopAbs_FACE);floors=[]
 while it.More():
  f=TopoDS.Face_s(it.Current());ad=BRepAdaptor_Surface(f)
  if ad.GetType()==GeomAbs_Cylinder and 10<ad.Cylinder().Radius()<11.1:floors.append(dict(radius_mm=ad.Cylinder().Radius(),bounds_mm=bounds(f)))
  it.Next()
 assert len(floors)==1 and abs(floors[0]['radius_mm']-10.93)<1e-9;r=(floors[0]['radius_mm']+.25)*.001
 source=ROOT/'validation/integrated/primaryP1_chain0_h5_point1/summary.json';saved=json.loads(source.read_text());fp=REPO/saved['field']['path'];assert sha(fp)==saved['field']['SHA256'];f=np.load(fp);p=f['F0_ROOT_BACK_points_mm'];off=int(f['F0_ROOT_BACK_offset']);u=f['u_mm'][off:off+3*len(p)].reshape(-1,3);sel=abs(p[:,0]-50.5)<1e-5;fitrow,z,center=fit(p[sel],u[sel]);anchor=np.array([50.4,0,-7.]);ur=z[:3]+np.cross(z[3:],anchor-center);Rr=Rotation.from_rotvec(z[3:]).as_matrix();tr=(anchor+ur)*.001-Rr@(anchor*.001);Rm=Rotation.from_rotvec(saved['motor_rigid_rotation_rad']).as_matrix();C=np.array([0,0,.020])+np.array(saved['motor_rigid_translation_mm'])*.001
 masssrc=ROOT/'validation/finger/primaryP1_gravity_mass64_1/mass_points.json';points=json.loads(masssrc.read_text());seedsrc=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedsrc.read_text())[0];E0=np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]]);E=Rr@E0+tr
 dump(out/'inputs.json',dict(candidate=ref(cadsrc),parts=cad['part_references'],parent_field=ref(source),field=ref(fp),seed=ref(seedsrc),mass_points=ref(masssrc),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_support_feedback.py'),ref(ROOT/'scripts/primary_gravity_pullback.py')],floor=floors[0],actual_seated_wire_center_radius_m=r,old_planar_radius_m=RADIUS,scope='One-wayspatialstringactualfloor/freeRootYfeedback; frozenFingerXZ/supportposes. No newelastic20solve orphysicalmeasurement.'))
 model=SpatialString(points,Rm,C,E,r);actual=model.solve(seed);higher=SpatialString(points,Rm,C,E,r,32).solve(seed);zero=SpatialString(points,np.eye(3),np.array([0,0,.020]),E0,r).solve(seed)
 dump(out/'curves.json',dict(actual={k:actual.pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')},higher={k:higher.pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')},zero={k:zero.pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')}))
 qerr=float(np.max(abs(np.array(actual['Fe_N'])-higher['Fe_N'])));result=dict(status='ACTUAL_P1_SPATIAL_FLOOR_STRING_PARTIAL' if all(actual['checks'].values()) else 'ACTUAL_P1_SPATIAL_FLOOR_STRING_FAIL',candidate=ref(cadsrc),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),curves=ref(out/'curves.json'),floor=floors[0],actual_wire_center_radius_m=r,root_fit=fitrow,root_R=Rr.tolist(),root_translation_m=tr.tolist(),motor_R=Rm.tolist(),motor_C_m=C.tolist(),actual=actual,quadrature32=higher,zero_support=zero,quadrature_force_max_N=qerr,checks=dict(actual=all(actual['checks'].values()),quadrature=qerr<1e-8,zero=all(zero['checks'].values())),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Full3Dmassivestringfrictionlesssmoothcylinderfloorwithrealfiniteaxialwidth; independentBRepclearanceandbalanceverifierrequired.','Actualseatedradius11.18mm differsold11.25mmfreefloatingcenterline. Endpointheldatold32FingerXZ,notnewFinger/spatialswivelstationarity.','Parent19supportposesnotnew20elasticcontactsolution. RootYshiftzerocableforceisfrictionlessmodeequilibrium,notphysicalretention.','No sourcecase/bearing/thread/minima/protector/friction/globalenergy/full3Finger/Stage3certificate.']);dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('actual','quadrature32','zero_support','limitations')}));raise SystemExit(0 if all(result['checks'].values()) else 2)
if __name__=='__main__':main()
