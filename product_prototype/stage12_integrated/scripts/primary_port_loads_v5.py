"""Actual P1 conditional finite-state port wrench and constrained stability audit.
No connector force distribution or strength claim is inferred from wrench sums.
"""
import sys,json,shutil
import numpy as np
from scipy.linalg import null_space
from scipy.optimize._numdiff import approx_derivative
from baseline_registry import ROOT,REPO,ref,dump,sha
import primary_finger_equilibrium_v5 as model
import primary_finger_tangent_v5 as tangent

def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
def main():
 src=ROOT/'validation/finger'/sys.argv[1];out=ROOT/'validation/transmission'/sys.argv[2];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');states=json.loads((src/'cases.json').read_text());rows=[]
 for row in states:
  assert not(ROOT/'runtime/STOP').exists();n=row['n'];v=np.array(row['state']);T=row['T_N'];N=row['normal_N'];model.EXTRA_POINTS=row['extra_contact_stations_m'];tangent.EXTRA_POINTS=model.EXTRA_POINTS.copy();J=tangent.constraints_jac(v,n,row['object_inward_stop_m']);lam=np.array(row['multipliers_N']);active=np.flatnonzero(lam>1e-9)
  def laggradient(x):return tangent.gradient(x,n,T,model.E_RAIL,model.E_PET,model.width)-tangent.constraints_jac(x,n,row['object_inward_stop_m']).T@lam
  H=approx_derivative(laggradient,v,method='3-point');skew=float(np.linalg.norm(H-H.T)/max(np.linalg.norm(H),1e-30));Z=null_space(J[active],rcond=1e-10) if len(active) else np.eye(len(v));Hc=Z.T@((H+H.T)/2)@Z;eigen=np.linalg.eigvalsh(Hc);minimum=float(eigen.min()) if len(eigen) else None
  P=np.array(row['cable_port_m']);D=P-[0,.020];dist=np.linalg.norm(D);u=D/dist;k=.01125/dist;normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=np.array([0,.020])+.01125*normal;t=(Q-P)/np.linalg.norm(Q-P);tip=np.array(row['terminal_tip_m']);R=np.array([.0504,-.007]);C=np.array([0,.020])
  finger_root_force=-T*t-[N,0];finger_root_couple=-(cross(P-R,T*t)+cross(tip-R,[N,0]));frame_root=-finger_root_force;frame_root_couple=-finger_root_couple;motor=-T*t;motor_couple=cross(Q-C,motor)
  total=frame_root+motor;totalmoment=cross(R,frame_root)+frame_root_couple+cross(C,motor)+motor_couple
  force_error=float(np.linalg.norm(total-[N,0]));moment_error=abs(totalmoment-cross(tip,[N,0]))
  rail_eps=np.array(row['rail_strain']);pet_eps=np.array(row['PET_strain']);kr=np.diff(row['rail_angles_rad'])/(.077/n);kp=np.diff(row['PET_angles_rad'])/(.0862/n)
  # Conditional nominal strip strain only; excludes geometric notch/contact concentration.
  rmax=float(np.max(abs(np.r_[rail_eps+.0001*kr,rail_eps-.0001*kr])));pmax=float(np.max(abs(np.r_[pet_eps+.00015*kp,pet_eps-.00015*kp])))
  rows.append(dict(n=n,T_N=T,object_normal_N=N,stored_status=row['status'],frame_root_force_XZ_N=frame_root.tolist(),frame_root_couple_about_Y_Nm=-frame_root_couple,motor_cradle_force_XZ_N=motor.tolist(),motor_cradle_couple_about_Y_Nm=-motor_couple,frame_total_external_force_XZ_N=total.tolist(),frame_total_external_couple_about_Y_Nm=-totalmoment,required_external_Ground_wrench='Negative of reported frame total; NOT measured/distributed support reaction',force_loop_error_N=force_error,moment_loop_error_Nm=moment_error,full_constraint_positive_multiplier_rows=len(active),critical_subspace_dimension=int(Z.shape[1]),lagrangian_Hessian_relative_skew=skew,restricted_min_eigenvalue_J=minimum,restricted_negative_curvature=bool(minimum is not None and minimum< -1e-9),rail_peak_nominal_elastic_face_strain=rmax,PET_peak_nominal_elastic_face_strain=pmax,rail_typical_E_times_face_strain_MPa=model.E_RAIL*rmax/1e6,PET_typical_E_times_face_strain_MPa=model.E_PET*pmax/1e6,allowable=None,capacity_qualified=False))
 result=dict(status='ACTUAL_P1_CONDITIONAL_PORT_WRENCH_AND_STABILITY_RESULTS',candidate=json.loads((src/'inputs.json').read_text())['candidate'],source=ref(src/'summary.json'),cases=ref(src/'cases.json'),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_finger_equilibrium_v5.py'),ref(ROOT/'scripts/primary_finger_tangent_v5.py')],rows=rows,max_force_loop_error_N=max(r['force_loop_error_N'] for r in rows),max_moment_loop_error_Nm=max(r['moment_loop_error_Nm'] for r in rows),negative_restricted_curvature_rows=sum(r['restricted_negative_curvature'] for r in rows),scope='Conditional solved/rejected P1 finite-strip states; true terminal/cable offsets and separate PET. Wrench accounting and local critical-subspace screen only.',limitations=['Root and motor port wrenches are externally demanded resultants from stated equilibrium, NOT resolved bolt/clamp/bearing reactions','Restricted nonnegative Hessian is not full unilateral cone/global stability or dynamic consistency proof','Material/section/torsion/contact assumptions and failed rows remain; no allowable or safety claim','External Ground fixture not measured; frame mesh FAIL retained','No friction/time/global-energy/threeFinger100mm grasp qualification'],whole_system_release=False,newly_qualified_system_gate_ids=[])
 dump(out/'summary.json',result);print(json.dumps({k:r for k,r in result.items() if k!='rows'}))
if __name__=='__main__':main()
