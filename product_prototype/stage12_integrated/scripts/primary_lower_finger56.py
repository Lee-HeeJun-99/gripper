"""Current77part conditional upstream evaluation. Adds REAL downward object
friction force to Finger virtual work and both Root/external wrench ledgers.
Tension is an unknown solved against declared object normal, not prescribed curvature.
Reference support pose is evaluation-only, not a physical fixation or grasp certificate.
"""
import sys,json,shutil
import numpy as np
from scipy.optimize import root
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_spatial_string import W
from primary_local_gamma29 import LocalGammaString as SpatialString
from primary_support_feedback import body
import primary_terminal_corner_v2 as corner
import primary_finger_tangent_v5 as kin
from primary_gravity_pullback import G
from primary_gravity_swivel import ARM

def solve(parent,seed,points,gamma_mm,order=16,target_normal=None,object_down_N=0.,lower_station_m=.08578):
 axis=np.array(parent['root_R'])[:,1];dy=axis*gamma_mm*.001
 n=seed['n'];model=corner.model;model.EXTRA_POINTS=seed['extra_contact_stations_m'].copy();kin.EXTRA_POINTS=model.EXTRA_POINTS.copy();v0=np.array(seed['state']);delta=seed['object_inward_stop_m'];labels=model.constraints(v0,n,delta)[1];ids=[labels.index(('interface',model.LP)),len(labels)-1];norms=np.array(seed['corner_face_normals']).T
 Rr=np.array(parent['root_R']);tr=np.array(parent['root_translation_m']);Rm=np.array(parent['motor_R']);C=np.array(parent['motor_C_m']);grav=(Rr.T@np.array([0,0,-G]))[[0,2]];cable=SpatialString(points,Rm,C,np.zeros(3),parent['actual_wire_center_radius_m'],gamma_mm,order,axis=axis);cable.T=seed['T_N']
 def equations(z,details=False):
  v=z[:4*n];beta=z[4*n];lam=z[4*n+1:4*n+3];force=z[4*n+3:4*n+5];s=z[4*n+5]*model.LP;zz=z[4*n+6:-4] if target_normal is not None else z[4*n+6:];cable.T=float(z[-4]) if target_normal is not None else seed['T_N'];Ug,gg,ports,pp=body(points,v,n,beta,grav,True);P=ports['P'];ep=P+ARM*np.array([np.sin(beta),np.cos(beta)]);cable.E=Rr@np.array([ep[0],0,ep[1]])+tr
  c=cable.evaluate(zz,True);Fe=Rr.T@np.array(c['Fe_N']);F=Fe[[0,2]];tip=ports['tip'];Jtip=ports['Jtip'];pc,jc,ds=corner.corner(v,n,s);pc2,jc2,ds2=corner.corner(v,n,z[-1]*model.LP);fc2=z[-3:-1];j=kin.constraints_jac(v,n,delta);g=model.constraints(v,n,delta)[0];g[-1]=Rr[0,[0,2]]@tip+tr[0]+dy[0]-(.05-delta);j[-1]=Rr[0,[0,2]]@Jtip
  res=kin.gradient(v,n,0,model.E_RAIL,model.E_PET,model.width)+gg[:4*n]-F@ports['JP']-j[ids].T@lam-jc.T@force-jc2.T@fc2-(Rr.T@np.array([0.,0.,-object_down_N]))[[0,2]]@Jtip;torque=gg[-1]-F@(ARM*np.array([np.cos(beta),-np.sin(beta)]));eq=np.r_[res/1e-4,torque/1e-4,g[ids]/1e-3,(pc-corner.CORNER)/1e-3,ds@force,c['residual']]
  if target_normal is not None:eq=np.r_[eq,(lam[1]-target_normal)/.1,(pc2-np.array([.050,-.095]))/1e-3,ds2@fc2]
  return (eq,res,torque,c,ports,pp,g,lam,force,s,pc) if details else eq
 z0=np.r_[v0,seed['swivel_beta_rad'],seed['interface_tip_force_N'],seed['normal_N'],seed['corner_contact_force_local_N'],seed['corner_material_station_m']/model.LP,parent['actual']['solver_state']];z0=np.r_[z0,seed['T_N'],.05,.01,lower_station_m/model.LP] if target_normal is not None else z0;sol=root(equations,z0,tol=1e-10);z=sol.x;eq,res,torque,c,ports,pp,g,lam,fc,s,pc=equations(z,True);v=z[:4*n];beta=z[4*n];cone=np.linalg.solve(norms,fc);scale=np.r_[np.full(n,.077),np.full(n,.077e-4),np.full(n,.0862),np.full(n,.0862e-4)];fr=float(np.linalg.norm(np.r_[res/scale,torque/ARM]));model.EXTRA_POINTS=sorted(set(model.EXTRA_POINTS+model.feature_stations(v,n)+[s,z[-1]*model.LP]));g,labels=model.constraints(v,n,delta,96);g[-1]=Rr[0,[0,2]]@ports['tip']+tr[0]+dy[0]-(.05-delta)
 tipw=Rr@np.array([ports['tip'][0],0,ports['tip'][1]])+tr+dy;E=np.array(c['E_m']);F=np.array(c['Fe_N']);moving=[]
 for q,orig in zip(pp,[p for p in points if p['mode'] in ('rail','pet','terminal','swivel')]):
  xz=q['local_position_XZ_m'];pos=Rr@np.array([xz[0],orig['rest_centroid_m'][1],xz[1]])+tr+dy;moving.append(dict(part_ID=q['part_ID'],mass_kg=q['mass_kg'],position_m=pos.tolist(),mode=orig['mode']))
 fw=sum((W(np.array(q['position_m']),np.array([0,0,-q['mass_kg']*G])) for q in moving),np.zeros(6));RW=W(E,F)+W(tipw,[lam[1],0,-object_down_N])+fw;MW=np.array(c['motor_origin_wrench_N_Nm']);motor=next(p for p in points if p['part_ID']=='F0_MICRO_MOTOR');q=Rm@(np.array(motor['rest_centroid_m'])-[0,0,.020])+C;motorW=W(q,[0,0,-motor['mass_kg']*G]);MW+=motorW
 # All fixed Root-attached pieces, excluding the elastic Root and explicit connectors.
 excluded=['F0_MICRO_MOTOR','OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];hardware=[f'F0_RF{i}_{k}' for i in range(2) for k in ('BOLT','NUT')]+[f'MOTOR_CAP_{k}_{x}_{y}' for x in (-7,7) for y in (-29.5,-13.5) for k in ('BOLT','NUT')]+[f'{p}_{k}_{i}' for p in ('GROUND','FIXTURE') for k in ('BOLT','NUT') for i in range(4)]
 fixed=[];fixedW=np.zeros(6)
 for p in points:
  if p['mode']=='fixed' and p['part_ID'] not in excluded+hardware:
   q=Rr@np.array(p['rest_centroid_m'])+tr+dy;f=np.array([0,0,-p['mass_kg']*G]);fixedW+=W(q,f);fixed.append(dict(part_ID=p['part_ID'],mass_kg=p['mass_kg'],position_m=q.tolist()))
 RW+=fixedW;external=W(tipw,[lam[1],0,-object_down_N])+fw+fixedW+motorW+np.array(c['wire_gravity_wrench_N_Nm'])+np.array(c['rotor_gravity_wrench_N_Nm']);err=float(np.max(abs(RW+MW-external)));r,p,rr,tp,er,ep,_,_,_,_,_=model.state(v,n)
 pc2,_,ds2=corner.corner(v,n,z[-1]*model.LP);fc2=z[-3:-1];checks=dict(lower_contact_position=np.max(abs(pc2-[.05,-.095]))<1e-12,lower_contact_cone=min(fc2)>=0,lower_station=0<z[-1]*model.LP<model.LP,lower_material_tangent=abs(ds2@fc2)<1e-10,root_success=bool(sol.success),force=fr<1e-8,swivel=abs(torque)<1e-10,gaps=g.min()>=-1e-9,cone=min(cone)>=0,positive_contacts=min(lam)>=0,corner=np.max(abs(pc-corner.CORNER))<1e-12,station=0<s<model.LP,string_residual=max(abs(np.array(c['residual'])))<1e-8,flat_floor=max(abs(np.array(c['wrap_local_axial_minmax_m'])))<.0002,string_compression=c['wrap_min_normal_N_per_m']>0,no_artificial_bound=max(abs(v[:n]))<1.399 and max(abs(v[2*n:3*n]))<1.399 and max(abs(np.r_[er,ep]))<.00999,paired_wrench=err<1e-12)
 return dict(lower_corner_local_m=[.05,-.095],lower_corner_material_station_m=float(z[-1]*model.LP),lower_corner_force_local_N=fc2.tolist(),lower_corner_position_m=pc2.tolist(),upstream_gamma_mm=float(gamma_mm),upstream_gamma_generalized_force_N=float(axis@RW[:3]),status='CONDITIONAL_ROOT_LOCAL_CLEARANCE_PLANAR_FINGER_STRING' if all(checks.values()) else 'SPATIAL_FINGER_FAIL',n=n,state=v.tolist(),swivel_beta_rad=float(beta),normal_N=float(lam[1]),T_N=float(cable.T),object_downward_friction_N=float(object_down_N),target_normal_N=target_normal,interface_tip_force_N=float(lam[0]),corner_material_station_m=float(s),corner_force_N=fc.tolist(),corner_cone_N=cone.tolist(),force_equivalent_N=fr,swivel_torque_Nm=float(torque),minimum_dense_gap_m=float(g.min()),Root_origin_wrench_N_Nm=RW.tolist(),Motor_origin_wrench_N_Nm=MW.tolist(),fixed_Root_wrench_N_Nm=fixedW.tolist(),moving_mass_points=moving,fixed_mass_points=fixed,tip_world_m=tipw.tolist(),pair_wrench_error=err,checks={k:bool(v) for k,v in checks.items()},root_message=str(sol.message),string=c)
