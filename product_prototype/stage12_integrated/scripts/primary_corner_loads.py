"""P1 free-station corner branch port wrenches, nominal strain and local stability.
Required loads, not resolved bolted joints,source minima or structural capacity.
"""
import json,sys,shutil
import numpy as np
from scipy.linalg import null_space
from scipy.optimize._numdiff import approx_derivative
from baseline_registry import ROOT,ref,dump
import primary_terminal_corner_v2 as contact
model=contact.model;tangent=contact.tangent

def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
def main():
 src=ROOT/'validation/finger'/sys.argv[1];out=ROOT/'validation/transmission'/sys.argv[2];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');rows=[]
 deps=[ROOT/'scripts/primary_terminal_corner_v2.py',ROOT/'scripts/primary_finger_equilibrium_v5.py',ROOT/'scripts/primary_finger_tangent_v5.py',src/'cases.json'];dump(out/'inputs.json',dict(inputs=[ref(p) for p in deps],scope='Same actual P1 source and finite-state applied loads,conditional typical stress,no allowance/connector strength claim'))
 for row in json.loads((src/'cases.json').read_text()):
  assert not(ROOT/'runtime/STOP').exists();n=row['n'];v=np.array(row['state']);s=row['corner_material_station_m'];T=row['T_N'];N=row['normal_N'];I=row['interface_tip_force_N'];f=np.array(row['corner_contact_force_local_N']);model.EXTRA_POINTS=[];tangent.EXTRA_POINTS=[];labels=model.constraints(v,n,row['object_inward_stop_m'])[1];ids=[labels.index(('interface',model.LP)),len(labels)-1]
  def laggrad(q):
   x=q[:-1];s=q[-1]*model.LP;j=tangent.constraints_jac(x,n,row['object_inward_stop_m']);pc,jc,ds=contact.corner(x,n,s)
   gv=tangent.gradient(x,n,T,model.E_RAIL,model.E_PET,model.width)-j[ids].T@[I,N]-jc.T@f
   return np.r_[gv,-model.LP*(ds@f)]
  q=np.r_[v,s/model.LP];H=approx_derivative(laggrad,q,method='3-point');skew=float(np.linalg.norm(H-H.T)/np.linalg.norm(H));pc,jc,ds=contact.corner(v,n,s);j=tangent.constraints_jac(v,n,row['object_inward_stop_m']);A=np.zeros((4,len(q)));A[:2,:-1]=j[ids];A[2:,:-1]=jc;A[2:,-1]=model.LP*ds;Z=null_space(A,rcond=1e-10);eigen=np.linalg.eigvalsh(Z.T@((H+H.T)/2)@Z)
  P=np.array(row['cable_port_m']);D=P-[0,.020];dist=np.linalg.norm(D);u=D/dist;k=.01125/dist;normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=np.array([0,.020])+.01125*normal;t=(Q-P)/np.linalg.norm(Q-P);tip=np.array(row['terminal_tip_m']);R=np.array([.0504,-.007]);C=np.array([0,.020]);root=T*t+[N,0];rootM=cross(P-R,T*t)+cross(tip-R,[N,0]);motor=-T*t;motorM=cross(Q-C,motor);total=root+motor;M=cross(R,root)+rootM+cross(C,motor)+motorM
  kr=np.diff(row['rail_angles_rad'])/(.077/n);kp=np.diff(row['PET_angles_rad'])/(.0862/n);er=np.array(row['rail_strain']);ep=np.array(row['PET_strain']);rmax=float(np.max(abs(np.r_[er+.0001*kr,er-.0001*kr])));pmax=float(np.max(abs(np.r_[ep+.00015*kp,ep-.00015*kp])))
  # Independent rest straight+wrapped cable at the same physical ports.
  from primary_module_design import route
  stroke=(route(0)['free']*.001-row['free_cable_m'])
  rows.append(dict(n=n,T_N=T,object_normal_N=N,stored_status=row['status'],frame_root_force_XZ_N=root.tolist(),frame_root_couple_about_Y_Nm=-rootM,motor_cradle_force_XZ_N=motor.tolist(),motor_cradle_couple_about_Y_Nm=-motorM,frame_total_external_force_XZ_N=total.tolist(),frame_total_external_couple_about_Y_Nm=-M,required_external_ground_force_XZ_N=(-total).tolist(),required_external_ground_couple_about_Y_Nm=M,force_loop_error_N=float(np.linalg.norm(total-[N,0])),moment_loop_error_Nm=abs(M-cross(tip,[N,0])),tendon_torque_Nm=T*.01125,cable_stroke_m=stroke,rail_peak_nominal_face_strain=rmax,PET_peak_nominal_face_strain=pmax,rail_typical_stress_MPa=model.E_RAIL*rmax/1e6,PET_typical_stress_MPa=model.E_PET*pmax/1e6,lagrangian_Hessian_relative_skew=skew,critical_dimension=int(Z.shape[1]),restricted_min_eigenvalue_J=float(eigen.min()),restricted_negative_curvature=bool(eigen.min()<-1e-9),allowable=None,capacity_qualified=False))
 result=dict(status='ACTUAL_P1_CORNER_PORT_WRENCH_AND_LOCAL_STABILITY_RESULTS',candidate=json.loads((src/'inputs.json').read_text())['candidate'],source=ref(src/'summary.json'),cases=ref(src/'cases.json'),inputs=ref(out/'inputs.json'),rows=rows,max_force_loop_error_N=max(r['force_loop_error_N'] for r in rows),max_moment_loop_error_Nm=max(r['moment_loop_error_Nm'] for r in rows),negative_restricted_curvature_rows=sum(r['restricted_negative_curvature'] for r in rows),whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Wrench balance gives applied Root/Motor/Ground resultants,NOT bolt/clamp/bearing/ground load distributions','Free material station included in local constrained Hessian; no global stability,dynamics,time or energy closure certificate','Typical nominal strip stress excludes notch/contact concentration; no minimum yield,fatigue,creep,cable or motor capacity','Existing frame mesh failure and motor current/source/protection/full3Finger gates remain'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
if __name__=='__main__':main()
