"""Paired full Root/Motor wrenches from same P1 gravity-loaded reduced model.
Conditional demand reconstruction, not cable local equilibrium or capacity.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_gravity_swivel import FreeSwivel,route
from primary_gravity_pullback import G,C,ROOT_POINT,RADIUS,rot,drot

def wrench(p,f):return np.r_[f,np.cross(p,f)]
def main():
 source=ROOT/'validation/finger'/sys.argv[1];mass=ROOT/'validation/finger'/sys.argv[2]/'mass_points.json';out=ROOT/'validation/transmission'/sys.argv[3];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');points=json.loads(mass.read_text());rows=[]
 for row in json.loads((source/'cases.json').read_text()):
  v=np.array(row['state']);n=row['n'];beta=row['swivel_beta_rad'];T=row['T_N'];factor=row['gravity_factor'];Ug,gradient,pp,ports=FreeSwivel(points).evaluate(np.r_[v,beta],n,factor,True);P=ports['P'];E=ports['E'];t=ports['t'];eta=ports['eta'];eps=1e-7
  def cable_rotor_U(P):
   _,_,_,_,angle,wc,_=route(P,beta);return G*factor*sum(i['mass_kg']*(wc[1] if i['mode']=='wire' else (C+rot(angle)@(np.array(i['rest_centroid_m'])[[0,2]]-C))[1]) for i in points if i['mode'] in ('wire','rotor'))
  dU=np.array([(cable_rotor_U(P+eps*np.eye(2)[i])-cable_rotor_U(P-eps*np.eye(2)[i]))/(2*eps) for i in range(2)]);F=T*t-dU;F3=np.array([F[0],0,F[1]]);E3=np.array([E[0],0,E[1]]);P3=np.array([P[0],0,P[1]]);root3=np.array([.0504,0,-.007]);motor3=np.array([0,0,.020]);tip=np.array([row['terminal_tip_m'][0],0,row['terminal_tip_m'][1]]);N3=np.array([row['normal_N'],0,0])
  finger=[i for i in pp if i['mode'] in ('rail','pet','terminal','swivel')];motor=[i for i in pp if i['mode'] in ('wire','rotor') or i['part_ID']=='F0_MICRO_MOTOR'];other=[i for i in pp if i not in finger and i not in motor]
  fw=wrench(E3,F3)+wrench(tip,N3)+sum((wrench(np.array(i['position_m']),np.array([0,0,-i['mass_kg']*G*factor])) for i in finger),np.zeros(6));mw=wrench(E3,-F3)+sum((wrench(np.array(i['position_m']),np.array([0,0,-i['mass_kg']*G*factor])) for i in motor),np.zeros(6));ow=sum((wrench(np.array(i['position_m']),np.array([0,0,-i['mass_kg']*G*factor])) for i in other),np.zeros(6));allg=sum((wrench(np.array(i['position_m']),np.array([0,0,-i['mass_kg']*G*factor])) for i in pp),np.zeros(6));total=fw+mw+ow;expected=wrench(tip,N3)+allg
  # Direct finite rigid virtual-work check, with moments in physical XYZ.
  rootlocal=fw.copy();rootlocal[3:]-=np.cross(root3,rootlocal[:3]);motorlocal=mw.copy();motorlocal[3:]-=np.cross(motor3,motorlocal[:3]);sw=[i for i in pp if i['mode']=='swivel'];swmoment=np.cross(E3-P3,F3)+sum((np.cross(np.array(i['position_m'])-P3,[0,0,-i['mass_kg']*G*factor]) for i in sw),np.zeros(3));sv=float(swmoment[1])
  # A straight free span cannot satisfy nonzero distributed transverse gravity.
  wire=next(i for i in points if i['mode']=='wire');wirelen=ports['wire_length'];linear=wire['mass_kg']/wirelen;lead=np.linalg.norm(ports['Q']-E);normal=np.array([-t[1],t[0]]);transverse=abs(np.array([0,-linear*G*factor])@normal);small_sag=transverse*lead**2/(8*max(np.linalg.norm(F),1e-30));scale=np.linalg.norm(total-expected)
  rows.append(dict(n=n,T_motor_equivalent_N=T,motor_applied_torque_Nm=T*RADIUS,normal_N=row['normal_N'],cable_exit_force_XZ_N=F.tolist(),gravity_cable_rotor_force_correction_XZ_N=(-dU).tolist(),Root_force_couple_XYZ_N_Nm=rootlocal.tolist(),Root_reference_m=root3.tolist(),Motor_force_couple_XYZ_N_Nm=motorlocal.tolist(),Motor_reference_m=motor3.tolist(),other_actual_mass_wrench_about_origin_N_Nm=ow.tolist(),full_product_external_wrench_about_origin_N_Nm=total.tolist(),required_Base_external_wrench_N_Nm=(-total).tolist(),direct_external_wrench_error=float(scale),free_swivel_physical_Y_moment_residual_Nm=sv,total_mass_kg=sum(i['mass_kg'] for i in pp),deformed_gravity_wrench_N_Nm=allg.tolist(),wire_transverse_unbalanced_N_per_m=float(transverse),small_sag_estimate_m=float(small_sag),small_sag_scope='Diagnostic string q_perp*L^2/(8T),not actual catenary/contact/clearance tolerance or acceptance bound',port_check_pass=bool(scale<1e-12 and abs(sv)<1e-8),local_cable_equilibrium_qualified=False))
 result=dict(status='ACTUAL_P1_GRAVITY_PAIRED_WRENCH_DEMANDS_CONDITIONAL_TAUT_CABLE',candidate=ref(ROOT/'cad/exports/primaryP1_fixture15/summary.json'),source=ref(source/'summary.json'),cases=ref(source/'cases.json'),mass=ref(mass),producer=ref(out/'producer.py'),rows=rows,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Root/Motor fullforcecouple are consistent reactions of prescribed-taut cable model; wire local transverse weight is unbalanced,so NOT final physical cable force certificate','Actual physical motorcase/bearings,Frame/Ground coupled compliance,thread/preload/physicalBaseanchor and friction not solved','T is actuator torque/radius,not constant actual cable tension or protected peak','Conditional density/COM/typical moduli and fixed static orientation; no globalenergy,dt or strength qualification'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(r['port_check_pass'] for r in rows) else 2)
if __name__=='__main__':main()
