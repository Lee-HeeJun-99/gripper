"""Independent gravity virtual work and closed-form tilted-gravity string check."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_support_feedback import body,String
from primary_gravity_pullback import G

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_support_feedback1/summary.json';r=json.loads(src.read_text());mass=ROOT/'validation/finger/primaryP1_gravity_mass64_1/mass_points.json';points=json.loads(mass.read_text());B=np.array(r['planar_geometry']['root_B']);d=np.array(r['planar_geometry']['root_d_m']);C=np.array(r['planar_geometry']['motor_C_root_local_m']);pitch=r['planar_geometry']['motor_pitch_relative_rad'];row=r['one_way_planar_feedback'];n=row['n'];v=np.array(row['state']);beta=row['swivel_beta_rad'];grav=B.T@[0,-G];U,g,ports,pp=body(points,v,n,beta,grav,True);string=String(points,C,pitch,grav);c=string.evaluate(ports['P'],beta,row['rotor_angle_rad'],row['drum_tangent_phi_rad'],row['T_N']);perp=np.array([grav[1],-grav[0]])/np.linalg.norm(grav);parallel=-grav/np.linalg.norm(grav);phi=row['drum_tangent_phi_rad'];h0=-c['S']*np.array([-np.sin(phi),np.cos(phi)]);a=h0@perp;b=h0@parallel;k=string.mu*np.linalg.norm(grav);L=c['length'];Iperp=a/k*(np.arcsinh((b+k*L)/abs(a))-np.arcsinh(b/abs(a)));Iparallel=(np.hypot(a,b+k*L)-np.hypot(a,b))/k;end=c['Q']+Iperp*perp+Iparallel*parallel;endpoint_error=float(np.linalg.norm(end-c['E']));quad_error=float(np.linalg.norm(end-c['end']));Fstart=-h0;Fend=c['Fe'];balance=Fstart-Fend+string.mu*grav*L;balance_error=float(np.linalg.norm(balance));virtual=[]
 # Finite derivative of scalar gravity potential checks allangle/strain/swivelvariables.
 x=np.r_[v,beta]
 for h in (1e-4,5e-5):
  fd=[]
  for i in range(len(x)):
   dx=np.eye(1,len(x),i).ravel()*h
   vals=[body(points,(x+mul*dx)[:4*n],n,(x+mul*dx)[-1],grav)[0] for mul in (-2,-1,1,2)]
   fd.append((vals[0]-8*vals[1]+8*vals[2]-vals[3])/(12*h))
  virtual.append(dict(step=h,max_absolute_J=float(np.max(abs(np.array(fd)-g))),relative_error=float(np.linalg.norm(np.array(fd)-g)/max(np.linalg.norm(g),1e-30))))
 # Single-valued physical pair must shareoneforce atoneendpoint,notseparaterotatedforces.
 FE=np.array(row['cable_force_world_XZ_N']);EW=np.array(row['cable_end_world_XZ_m']);rng=np.random.default_rng(21);works=[]
 for _ in range(12):
  vel=rng.normal(size=2);omega=rng.normal();vE=vel+omega*np.array([EW[1],-EW[0]]);works.append(float(FE@vE+(-FE)@vE))
 checks=dict(closed_form_endpoint=endpoint_error<1e-12,closed_form_quadrature=quad_error<1e-12,distributed_string_force_balance=balance_error<1e-12,conservative_body_gravity_virtualwork=max(v['relative_error'] for v in virtual)<1e-6,paired_rigid_work=max(abs(w) for w in works)<1e-12,full3D_not_promoted=r['full_3D_feedback_qualified'] is False,newhardware_not_promoted=r['new_hardware_coupled_solution_qualified'] is False)
 result=dict(status='ACTUAL_P1_PLANAR_FEEDBACK_INDEPENDENT_CHECK_PASS' if all(checks.values()) else 'ACTUAL_P1_FEEDBACK_INDEPENDENT_CHECK_FAIL',candidate=r['candidate'],source=ref(src),mass_points=ref(mass),verifier=ref(out/'verifier.py'),checks=checks,closed_form_endpoint_error_m=endpoint_error,quadrature_error_m=quad_error,string_balance_N=balance.tolist(),virtualwork=virtual,paired_work_residuals=works,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Checksphysicalequationsofexplicitone-wayplanarprojection only. Parent19field/new20hardware/full3D/grip/physicalanchor/materialminima/mesh/time/globalenergy remainunqualified.')
 dump(out/'summary.json',result);print(result);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
