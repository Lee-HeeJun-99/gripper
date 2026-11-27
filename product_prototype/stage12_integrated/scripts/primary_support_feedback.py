"""Actual P1 saved elastic support feedback: explicit 3D compatibility and planar contrast.
No old field is promoted to new hardware or a fully coupled/3D product solution.
"""
import sys,json,shutil,argparse
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import root
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,ref,sha,dump
import primary_terminal_corner_v2 as corner
import primary_finger_tangent_v5 as kin
from primary_gravity_pullback import G,RADIUS,FREE0,rot,drot,BETA0,P0
from primary_gravity_swivel import ARM

C0=np.array([0.,.020])
def skew(r):
 x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
def fit(p,u):
 center=p.mean(0);A=np.concatenate([np.column_stack((np.eye(3),-skew(q-center))) for q in p]);z=np.linalg.lstsq(A,u.ravel(),rcond=None)[0];res=(A@z).reshape(-1,3)-u
 return dict(center_mm=center.tolist(),translation_mm=z[:3].tolist(),rotation_rad=z[3:].tolist(),max_fit_error_mm=float(np.linalg.norm(res,axis=1).max()),rms_fit_error_mm=float(np.sqrt(np.mean(res*res))),nodes=len(p)),z,center

def body(points,v,n,beta,grav,detail=False):
 rail,pet,R,dR,jr,P,JP,tip,JT,t0=kin.terminal(v,n);U=0.;grad=np.zeros(4*n+1);pp=[]
 for item in points:
  mode=item['mode']
  if mode not in ('rail','pet','terminal','swivel'):continue
  q=np.array(item['rest_centroid_m'])[[0,2]];J=np.zeros((2,4*n+1));m=item['mass_kg']
  if mode in ('rail','pet'):
   ispet=mode=='pet';data=pet if ispet else rail;s=item['material_station_m'];pt,j,_,_=kin.point(data,s);a,e,h,_,_=data;i=min(int(s/h),n-1);u=(s-i*h)/h;angle=(1-u)*a[i]+u*a[i+1];offset=q-[.05015 if ispet else .0504,-.007-s];q=pt+rot(angle)@offset;da=np.zeros(2*n)
   if i:da[i-1]=1-u
   da[i]=u;j+=np.outer(drot(angle)@offset,da);J[:,2*n if ispet else 0:4*n if ispet else 2*n]=j
  elif mode=='terminal':
   offset=q-[.0504,-.084];q=rail[3][-1]+R@offset;J[:,:4*n]=jr;J[:,n-1]+=dR@offset
  else:
   offset=q-P0;q=P+rot(beta-BETA0)@offset;J[:,:4*n]=JP;J[:,-1]=drot(beta-BETA0)@offset
  U-=m*grav@q;grad-=m*grav@J
  if detail:pp.append(dict(part_ID=item['part_ID'],mass_kg=m,local_position_XZ_m=q.tolist()))
 return U,grad,dict(P=P,JP=JP,tip=tip,Jtip=JT),pp

class String:
 def __init__(self,points,C,pitch,grav,order=16):
  self.points=points;self.C=C;self.pitch=pitch;self.grav=grav;z,w=leggauss(order);self.u=(z+1)/2;self.weights=w/2;self.mu=next(p['mass_kg'] for p in points if p['mode']=='wire')/(FREE0+.006)
 def evaluate(self,P,beta,eta,phi,T):
  r=RADIUS;C=self.C;gx,gz=self.grav;E=P+ARM*np.array([np.sin(beta),np.cos(beta)]);Q=C+r*np.array([np.cos(phi),np.sin(phi)]);tq=np.array([-np.sin(phi),np.cos(phi)]);start=np.pi/2-eta-self.pitch;arc=r*(start-phi);length=FREE0-arc;tail=C+rot(eta+self.pitch)@[-.003,r]
  torque=0.;rotors=[]
  for p in self.points:
   if p['mode']!='rotor':continue
   q=rot(eta+self.pitch)@(np.array(p['rest_centroid_m'])[[0,2]]-C0);torque+=p['mass_kg']*(q[1]*gx-q[0]*gz);rotors.append(dict(part_ID=p['part_ID'],mass_kg=p['mass_kg'],local_position_XZ_m=(C+q).tolist()))
  torque+=self.mu*r*r*(gx*(np.cos(phi)-np.cos(start))-gz*(np.sin(start)-np.sin(phi)));torque+=self.mu*.006*((tail-C)[1]*gx-(tail-C)[0]*gz);S=T-torque/r;h0=-S*tq
  def integral(s):
   ss=np.asarray(s);h=h0-self.mu*ss[...,None,None]*self.u[:,None]*self.grav;unit=h/np.sqrt(np.sum(h*h,axis=-1))[...,None];return ss[...,None]*np.einsum('...ij,i->...j',unit,self.weights)
  end=Q+integral(length);Fe=S*tq+self.mu*self.grav*length;positions=Q+integral(length*self.u);moment_free=length*np.einsum('ij,i->j',positions,self.weights);moment_wrap=r*r*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc;wc=(moment_free+moment_wrap+.006*tail)/(FREE0+.006)
  return dict(E=E,Q=Q,end=end,Fe=Fe,S=S,length=length,arc=arc,wire_centroid=wc,rotors=rotors,torque_gravity=torque,integral=integral)

def solve(seed,points,C,pitch,B,d,order=16):
 n=seed['n'];model=corner.model;model.EXTRA_POINTS=seed['extra_contact_stations_m'].copy();kin.EXTRA_POINTS=model.EXTRA_POINTS.copy();v0=np.array(seed['state']);delta=seed['object_inward_stop_m'];labels=model.constraints(v0,n,delta)[1];ids=[labels.index(('interface',model.LP)),len(labels)-1];norms=np.array(seed['corner_face_normals']).T;grav=B.T@np.array([0.,-G]);string=String(points,C,pitch,grav,order);T=seed['T_N']
 def equations(z,detail=False):
  v=z[:4*n];beta,eta,phi=z[4*n:4*n+3];lam=z[4*n+3:4*n+5];force=z[4*n+5:4*n+7];s=z[-1]*model.LP;Ug,gg,ports,pp=body(points,v,n,beta,grav,detail);c=string.evaluate(ports['P'],beta,eta,phi,T);pc,jc,ds=corner.corner(v,n,s);j=kin.constraints_jac(v,n,delta);g=model.constraints(v,n,delta)[0];g[-1]=B[0]@ports['tip']+d[0]-(.05-delta);j[-1]=B[0]@ports['Jtip'];res=kin.gradient(v,n,0,model.E_RAIL,model.E_PET,model.width)+gg[:4*n]-c['Fe']@ports['JP']-j[ids].T@lam-jc.T@force;torque=gg[-1]-c['Fe']@(ARM*np.array([np.cos(beta),-np.sin(beta)]));eq=np.r_[res/1e-4,torque/1e-4,(c['end']-c['E'])/1e-3,g[ids]/1e-3,(pc-corner.CORNER)/1e-3,ds@force]
  return (eq,res,torque,c,ports,pp,g,j,lam,force,s,pc,ds) if detail else eq
 z0=np.r_[v0,seed['swivel_beta_rad'],seed['rotor_angle_rad'],seed['drum_tangent_phi_rad'],seed['interface_tip_force_N'],seed['normal_N'],seed['corner_contact_force_local_N'],seed['corner_material_station_m']/model.LP];sol=root(equations,z0,tol=1e-10);z=sol.x;v=z[:4*n];beta,eta,phi=z[4*n:4*n+3];eq,res,torque,c,ports,pp,g,j,lam,fc,s,pc,ds=equations(z,True);cone=np.linalg.solve(norms,fc);scale=np.r_[np.full(n,.077),np.full(n,.077e-4),np.full(n,.0862),np.full(n,.0862e-4)];force_res=float(np.linalg.norm(np.r_[res/scale,torque/ARM]));model.EXTRA_POINTS=sorted(set(model.EXTRA_POINTS+model.feature_stations(v,n)+[s]));g,labels=model.constraints(v,n,delta,48);g[-1]=B[0]@ports['tip']+d[0]-(.05-delta);r,p,tr,tp,er,ep,R,P,tip,_,_=model.state(v,n);U,_=model.energy(v,n,0);checks=dict(root_success=bool(sol.success),force=force_res<1e-8,gaps=g.min()>=-1e-9,cone=min(cone)>=0,positive_contacts=min(lam)>=0,corner=np.max(abs(pc-corner.CORNER))<1e-12,station=0<s<model.LP,cable_end=np.max(abs(c['end']-c['E']))<1e-12,cable_tension=c['S']>0,no_artificial_bound=max(abs(v[:n]))<1.399 and max(abs(v[2*n:3*n]))<1.399 and max(abs(np.r_[er,ep]))<.00999)
 # Independent finite rigid-body paired wrench identity at actual deformedworldpositions.
 def W(q,f):return np.r_[f,q[1]*f[0]-q[0]*f[1]]
 E=B@c['E']+d;F=B@c['Fe'];tipw=B@tip+d;normal=np.array([lam[1],0.]);fingerweight=sum((W(B@np.array(q['local_position_XZ_m'])+d,[0,-q['mass_kg']*G]) for q in pp),np.zeros(3));motorweight=sum((W(B@np.array(q['local_position_XZ_m'])+d,[0,-q['mass_kg']*G]) for q in c['rotors']),np.zeros(3));wiremass=next(p['mass_kg'] for p in points if p['mode']=='wire');motorweight+=W(B@c['wire_centroid']+d,[0,-wiremass*G]);motoritem=next(p for p in points if p['part_ID']=='F0_MICRO_MOTOR');cm=B@C+d;motorweight+=W(cm,[0,-motoritem['mass_kg']*G]);rw=W(E,F)+W(tipw,normal)+fingerweight;mw=W(E,-F)+motorweight;ext=W(tipw,normal)+fingerweight+motorweight;pair=float(np.max(abs(rw+mw-ext)))
 checks['paired_wrench_accounting']=pair<1e-12
 result=dict(status='CONDITIONAL_PLANAR_SUPPORT_FEEDBACK_CONTRAST' if all(checks.values()) else 'PLANAR_SUPPORT_FEEDBACK_FAIL',n=n,T_N=T,normal_N=float(lam[1]),state=v.tolist(),swivel_beta_rad=float(beta),rotor_angle_rad=float(eta),drum_tangent_phi_rad=float(phi),force_equivalent_N=force_res,minimum_dense_gap_m=float(g.min()),corner_material_station_m=float(s),corner_contact_force_local_N=fc.tolist(),corner_cone_N=cone.tolist(),rail_tip_local_m=r[-1].tolist(),terminal_tip_world_XZ_m=tipw.tolist(),cable_end_world_XZ_m=E.tolist(),cable_force_world_XZ_N=F.tolist(),stored_energy_J=U,root_origin_wrench_FX_FZ_MY_N_Nm=rw.tolist(),motor_origin_wrench_FX_FZ_MY_N_Nm=mw.tolist(),paired_external_error=pair,checks={k:bool(v) for k,v in checks.items()},root_message=str(sol.message),scope='One-wayplanarprojection ofparent19supportfield on sameP1 geometry. New20nutfootprintnotyetrecoupled; full3Dmotoraxis/freeY/cableexit unresolved. Not actual3D equilibrium/mesh/strength/globalenergy approval.')
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('tag');a=ap.parse_args();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/a.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 fieldsrc=ROOT/'validation/integrated/primaryP1_chain0_h5_point1/summary.json';saved=json.loads(fieldsrc.read_text());fp=REPO/saved['field']['path'];assert sha(fp)==saved['field']['SHA256'];f=np.load(fp);cadsrc=ROOT/'cad/exports/primaryP1_retention20/summary.json';cad=json.loads(cadsrc.read_text());parent=json.loads((REPO/saved['candidate']['path']).read_text());assert all(cad['part_references'][n]==parent['part_references'][n] for n in ['F0_ROOT_BACK','OPEN_FRAME','MOTOR_CAP','GROUND_PLATE','F0_MICRO_MOTOR'])
 name='F0_ROOT_BACK';p=f[name+'_points_mm'];off=int(f[name+'_offset']);u=f['u_mm'][off:off+3*len(p)].reshape(-1,3);sel=abs(p[:,0]-50.5)<1e-5;fitrow,z,center=fit(p[sel],u[sel]);anchor=np.array([50.4,0,-7.]);ur=z[:3]+np.cross(z[3:],anchor-center);Rr=Rotation.from_rotvec(z[3:]).as_matrix();Um=np.array(saved['motor_rigid_translation_mm']);Rm=Rotation.from_rotvec(saved['motor_rigid_rotation_rad']).as_matrix();Rpoint=anchor*.001;tr=(anchor+ur)*.001-Rr@Rpoint;C3=np.array([0.,0,.020]);tm=Um*.001+C3-Rm@C3
 seedsrc=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedsrc.read_text())[0];masssrc=ROOT/'validation/finger/primaryP1_gravity_mass64_1/mass_points.json';points=json.loads(masssrc.read_text());E=np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]]);Q=np.array([seed['cable_tangent_m'][0],0,seed['cable_tangent_m'][1]]);Eroot=Rr@E+tr;Emotor=Rm@E+tm;Qmotor=Rm@Q+tm;axisangle=float(np.arccos(np.clip((Rr@np.array([0,1.,0]))@(Rm@np.array([0,1.,0])),-1,1)));F0=np.array([seed['cable_exit_force_XZ_N'][0],0,seed['cable_exit_force_XZ_N'][1]]);badforce=Rr@F0-Rm@F0
 thetaR=z[4];thetaM=np.array(saved['motor_rigid_rotation_rad'])[1];B=rot(thetaR);d=(anchor+ur)[[0,2]]*.001-B@(anchor[[0,2]]*.001);Cm=(C3+Um*.001)[[0,2]];C=B.T@(Cm-d);pitch=thetaM-thetaR
 dump(out/'inputs.json',dict(candidate=ref(cadsrc),parent_field_summary=ref(fieldsrc),field=ref(fp),seed=ref(seedsrc),mass_points=ref(masssrc),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_gravity_catenary.py'),ref(ROOT/'scripts/primary_gravity_swivel.py'),ref(ROOT/'scripts/primary_finger_tangent_v5.py'),ref(ROOT/'scripts/primary_terminal_corner_v2.py')],criteria=dict(force_N=1e-8,gap_m_min=-1e-9),scope='MeasuredSAVEDnumericalparent19field,notphysicalmeasurement. No newcontactsolve/refinement or timeoutretry. FitactualRootx50.5face; fullmotor6DOF. Planarcontrastexplicitlyexcludes3Dtilt/freeY andnew20hardwarefeedback.'))
 zero=solve(seed,points,C0,0.,np.eye(2),np.zeros(2));actual=solve(seed,points,C,pitch,B,d);refined=solve(seed,points,C,pitch,B,d,32);zeroerr=float(np.max(abs(np.array(zero['state'])-seed['state'])));quaderr=abs(actual['normal_N']/refined['normal_N']-1)
 # Coordinate-gauge covariant relative geometry check, nophysicalfreeYfixationclaim.
 rotg=Rotation.from_rotvec([.1,-.2,.05]).as_matrix();dg=np.array([.01,-.02,.03]);before=Rr.T@(Qmotor-Eroot);after=(rotg@Rr).T@((rotg@Qmotor+dg)-(rotg@Eroot+dg));gaugeerr=float(np.max(abs(before-after)))
 result=dict(status='ACTUAL_P1_SUPPORT_FEEDBACK_PARTIAL_3D_UNRESOLVED',candidate=ref(cadsrc),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),root_fit=fitrow,root_anchor_translation_mm=ur.tolist(),motor_translation_mm=Um.tolist(),root_rotation_rad=z[3:].tolist(),motor_rotation_rad=saved['motor_rigid_rotation_rad'],motor_relative_to_root_axis_tilt_rad=axisangle,old_cable_endpoint_split_mm=((Eroot-Emotor)*1000).tolist(),naively_separately_rotated_paired_force_residual_N=badforce.tolist(),relative_geometry_global_gauge_error_m=gaugeerr,planar_geometry=dict(root_B=B.tolist(),root_d_m=d.tolist(),motor_C_root_local_m=C.tolist(),motor_pitch_relative_rad=float(pitch)),zero_feedback=zero,one_way_planar_feedback=actual,quadrature32_feedback=refined,zero_state_max_error=zeroerr,quadrature16_32_normal_relative=quaderr,normal_change_relative_from_parent=float(actual['normal_N']/seed['normal_N']-1),checks=dict(zero_reproduces_parent=zeroerr<1e-8,global_coordinate_covariance=gaugeerr<1e-12,planar_stationary=all(actual['checks'].values()),quadrature_normal=quaderr<.001),full_3D_feedback_qualified=False,new_hardware_coupled_solution_qualified=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Full6DOFmotor andactualRootfit are parent19savedsolution,not20solution. Hardwarefootprint/compliance/weightchange requiresnewcoarsesolve afterfeedbackformulation.','Root/MotorfreeYare unrestrainedphysicalmodes: selectedgaugeYoffset isNOTmeasuredretention or auniquephysicalprediction. Relativeaxis tilt cannot beremovedbycommongaugerotation.','Existingplanarstring cannotcertifytilteddrum/cableexit/freeYbalance. Reportedplanarprojectioncontrast mustNOT bepromotedto3Dforceclosure orunchangednormalforce.','Rootfacefiterror measuresnonrigidity; affinefitnot actualRail/pin/clamptraction. ObjectfixedglobalXstopmaintainedinplanarcontrast.','Independentpairedwrenchidentityisaccounting,notglobalenergy/capacity/physicalanchor. No fine/gap retry,mesh/timePASS or protecteddevice.'])
 dump(out/'summary.json',result);print({k:v for k,v in result.items() if k not in ['zero_feedback','one_way_planar_feedback','quadrature32_feedback','limitations']});raise SystemExit(0 if all(result['checks'].values()) else 2)
if __name__=='__main__':main()
