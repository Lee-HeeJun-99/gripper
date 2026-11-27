"""Same actual P1 floor spatial string coupled to existing finite planar Rail/PET.
Full world cable forces, free RootY, fixed world-X object stop; one-way saved
support transforms. This does not add out-of-plane rod constitutive physics.
"""
import sys,json,shutil
import numpy as np
from scipy.optimize import root
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_spatial_string import W
from primary_seated_string import SeatedString as SpatialString
from primary_support_feedback import body
import primary_terminal_corner_v2 as corner
import primary_finger_tangent_v5 as kin
from primary_gravity_pullback import G
from primary_gravity_swivel import ARM

def solve(parent,seed,points,order=16):
 n=seed['n'];model=corner.model;model.EXTRA_POINTS=seed['extra_contact_stations_m'].copy();kin.EXTRA_POINTS=model.EXTRA_POINTS.copy();v0=np.array(seed['state']);delta=seed['object_inward_stop_m'];labels=model.constraints(v0,n,delta)[1];ids=[labels.index(('interface',model.LP)),len(labels)-1];norms=np.array(seed['corner_face_normals']).T
 Rr=np.array(parent['root_R']);tr=np.array(parent['root_translation_m']);Rm=np.array(parent['motor_R']);C=np.array(parent['motor_C_m']);grav=(Rr.T@np.array([0,0,-G]))[[0,2]];cable=SpatialString(points,Rm,C,np.zeros(3),parent['actual_wire_center_radius_m'],order);cable.T=seed['T_N']
 def equations(z,details=False):
  v=z[:4*n];beta=z[4*n];lam=z[4*n+1:4*n+3];force=z[4*n+3:4*n+5];s=z[4*n+5]*model.LP;zz=z[4*n+6:];Ug,gg,ports,pp=body(points,v,n,beta,grav,True);P=ports['P'];ep=P+ARM*np.array([np.sin(beta),np.cos(beta)]);cable.E=Rr@np.array([ep[0],0,ep[1]])+tr
  c=cable.evaluate(zz,True);Fe=Rr.T@np.array(c['Fe_N']);F=Fe[[0,2]];tip=ports['tip'];Jtip=ports['Jtip'];pc,jc,ds=corner.corner(v,n,s);j=kin.constraints_jac(v,n,delta);g=model.constraints(v,n,delta)[0];g[-1]=Rr[0,[0,2]]@tip+tr[0]-(.05-delta);j[-1]=Rr[0,[0,2]]@Jtip
  res=kin.gradient(v,n,0,model.E_RAIL,model.E_PET,model.width)+gg[:4*n]-F@ports['JP']-j[ids].T@lam-jc.T@force;torque=gg[-1]-F@(ARM*np.array([np.cos(beta),-np.sin(beta)]));eq=np.r_[res/1e-4,torque/1e-4,g[ids]/1e-3,(pc-corner.CORNER)/1e-3,ds@force,c['residual']]
  return (eq,res,torque,c,ports,pp,g,lam,force,s,pc) if details else eq
 z0=np.r_[v0,seed['swivel_beta_rad'],seed['interface_tip_force_N'],seed['normal_N'],seed['corner_contact_force_local_N'],seed['corner_material_station_m']/model.LP,parent['actual']['solver_state']];sol=root(equations,z0,tol=1e-10);z=sol.x;eq,res,torque,c,ports,pp,g,lam,fc,s,pc=equations(z,True);v=z[:4*n];beta=z[4*n];cone=np.linalg.solve(norms,fc);scale=np.r_[np.full(n,.077),np.full(n,.077e-4),np.full(n,.0862),np.full(n,.0862e-4)];fr=float(np.linalg.norm(np.r_[res/scale,torque/ARM]));model.EXTRA_POINTS=sorted(set(model.EXTRA_POINTS+model.feature_stations(v,n)+[s]));g,labels=model.constraints(v,n,delta,48);g[-1]=Rr[0,[0,2]]@ports['tip']+tr[0]-(.05-delta)
 dy=np.array([0,c['root_free_Y_shift_mm']*.001,0]);tipw=Rr@np.array([ports['tip'][0],0,ports['tip'][1]])+tr+dy;E=np.array(c['E_m']);F=np.array(c['Fe_N']);moving=[]
 for q,orig in zip(pp,[p for p in points if p['mode'] in ('rail','pet','terminal','swivel')]):
  xz=q['local_position_XZ_m'];pos=Rr@np.array([xz[0],orig['rest_centroid_m'][1],xz[1]])+tr+dy;moving.append(dict(part_ID=q['part_ID'],mass_kg=q['mass_kg'],position_m=pos.tolist(),mode=orig['mode']))
 fw=sum((W(np.array(q['position_m']),np.array([0,0,-q['mass_kg']*G])) for q in moving),np.zeros(6));RW=W(E,F)+W(tipw,[lam[1],0,0])+fw;MW=np.array(c['motor_origin_wrench_N_Nm']);motor=next(p for p in points if p['part_ID']=='F0_MICRO_MOTOR');q=Rm@(np.array(motor['rest_centroid_m'])-[0,0,.020])+C;motorW=W(q,[0,0,-motor['mass_kg']*G]);MW+=motorW
 # All fixed Root-attached pieces, excluding the elastic Root and explicit connectors.
 excluded=['F0_MICRO_MOTOR','OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];hardware=[f'F0_RF{i}_{k}' for i in range(2) for k in ('BOLT','NUT')]+[f'MOTOR_CAP_{k}_{x}_{y}' for x in (-7,7) for y in (-29.5,-13.5) for k in ('BOLT','NUT')]+[f'{p}_{k}_{i}' for p in ('GROUND','FIXTURE') for k in ('BOLT','NUT') for i in range(4)]
 fixed=[];fixedW=np.zeros(6)
 for p in points:
  if p['mode']=='fixed' and p['part_ID'] not in excluded+hardware:
   q=Rr@np.array(p['rest_centroid_m'])+tr+dy;f=np.array([0,0,-p['mass_kg']*G]);fixedW+=W(q,f);fixed.append(dict(part_ID=p['part_ID'],mass_kg=p['mass_kg'],position_m=q.tolist()))
 RW+=fixedW;external=W(tipw,[lam[1],0,0])+fw+fixedW+motorW+np.array(c['wire_gravity_wrench_N_Nm'])+np.array(c['rotor_gravity_wrench_N_Nm']);err=float(np.max(abs(RW+MW-external)));r,p,rr,tp,er,ep,_,_,_,_,_=model.state(v,n)
 checks=dict(root_success=bool(sol.success),force=fr<1e-8,swivel=abs(torque)<1e-10,gaps=g.min()>=-1e-9,cone=min(cone)>=0,positive_contacts=min(lam)>=0,corner=np.max(abs(pc-corner.CORNER))<1e-12,station=0<s<model.LP,string_residual=max(abs(np.array(c['residual'])))<1e-8,flat_floor=max(abs(np.array(c['wrap_local_axial_minmax_m'])))<.0002,string_compression=c['wrap_min_normal_N_per_m']>0,no_artificial_bound=max(abs(v[:n]))<1.399 and max(abs(v[2*n:3*n]))<1.399 and max(abs(np.r_[er,ep]))<.00999,paired_wrench=err<1e-12)
 return dict(status='CONDITIONAL_SPATIAL_STRING_PLANAR_FINGER_EQUILIBRIUM' if all(checks.values()) else 'SPATIAL_FINGER_FAIL',n=n,state=v.tolist(),swivel_beta_rad=float(beta),normal_N=float(lam[1]),T_N=seed['T_N'],interface_tip_force_N=float(lam[0]),corner_material_station_m=float(s),corner_force_N=fc.tolist(),corner_cone_N=cone.tolist(),force_equivalent_N=fr,swivel_torque_Nm=float(torque),minimum_dense_gap_m=float(g.min()),Root_origin_wrench_N_Nm=RW.tolist(),Motor_origin_wrench_N_Nm=MW.tolist(),fixed_Root_wrench_N_Nm=fixedW.tolist(),moving_mass_points=moving,fixed_mass_points=fixed,tip_world_m=tipw.tolist(),pair_wrench_error=err,checks={k:bool(v) for k,v in checks.items()},root_message=str(sol.message),string=c)

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();source=ROOT/'validation/integrated/primaryP1_seated_string1/summary.json';parent=json.loads(source.read_text());seedsrc=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedsrc.read_text())[0];mass=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';points=json.loads(mass.read_text());dump(out/'inputs.json',dict(candidate=parent['candidate'],parent=ref(source),seed=ref(seedsrc),mass=ref(mass),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_spatial_string.py'),ref(ROOT/'scripts/primary_seated_string.py'),ref(ROOT/'scripts/primary_support_feedback.py'),ref(ROOT/'scripts/primary_finger_tangent_v5.py'),ref(ROOT/'scripts/primary_terminal_corner_v2.py')]))
 r=solve(parent,seed,points);dump(out/'curves.json',{k:r['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')});dump(out/'state.json',r)
 result=dict(status=r['status'],candidate=parent['candidate'],inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),state=ref(out/'state.json'),curves=ref(out/'curves.json'),checks=r['checks'],normal_N=r['normal_N'],normal_change_from_old=float(r['normal_N']/seed['normal_N']-1),Root_origin_wrench_N_Nm=r['Root_origin_wrench_N_Nm'],Motor_origin_wrench_N_Nm=r['Motor_origin_wrench_N_Nm'],root_free_Y_shift_mm=r['string']['root_free_Y_shift_mm'],force_equivalent_N=r['force_equivalent_N'],newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Fullworldspatialstringwithactual11.25mmseatedradiusandfreeRootY; rodconstitutivemodelremainsexistingplanarRail/PET,notfull3Drod.','Frozenparent19supporttransforms,new20elasticfrontcontact/footprintsnotyetrecoupled. PhysicalfreeRootYnotpositiveretention.','RootwrenchincludesmovingANDfixedRootattachedweights; hardwareandfiniteelasticbodyweightsareseparatekernelloads.','No mesh/time/materialminimum/globalenergy/case/bearing/strength/friction/protector/full3FingerStage1/Stage3qualification.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(result['checks'].values()) else 2)
if __name__=='__main__':main()
