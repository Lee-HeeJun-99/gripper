"""Independent current Finger dead-load virtual-work and wrench ledger audit.
No static energy identity is presented as coupled/global stored-energy closure.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
import primary_terminal_corner_v2 as corner
from primary_support_feedback import body
from primary_gravity_swivel import ARM
from primary_gravity_pullback import G
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_operating56/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text());points=json.loads((REPO/inp['mass_points']['path']).read_text());seed=json.loads((REPO/inp['seed']['path']).read_text())[0];rows=[];model=corner.model
for item in d['results']:
 assert not(ROOT/'runtime/STOP').exists();assert sha(REPO/item['state']['path'])==item['state']['SHA256'];r=json.loads((REPO/item['state']['path']).read_text());v=np.array(r['state']);n=r['n'];beta=r['swivel_beta_rad'];model.EXTRA_POINTS=seed['extra_contact_stations_m'];labels=model.constraints(v,n,seed['object_inward_stop_m'])[1];idx=labels.index(('interface',model.LP));s=r['corner_material_station_m'];fc=np.array(r['corner_force_N']);Fe=np.array(r['string']['Fe_N'])[[0,2]];Fo=np.array([r['normal_N'],-r['object_downward_friction_N']]);li=r['interface_tip_force_N'];z=np.r_[v,beta]
 def potential(z,omit=False):
  vv=z[:-1];bb=z[-1];Ug,_,ports,_=body(points,vv,n,bb,np.array([0.,-G]));U=model.energy(vv,n,0)[0];ep=ports['P']+ARM*np.array([np.sin(bb),np.cos(bb)]);g=model.constraints(vv,n,seed['object_inward_stop_m'])[0][idx];pc=corner.corner(vv,n,s)[0];f=Fo.copy()
  if omit:f[1]=0
  return U+Ug-Fe@ep-f@ports['tip']-li*g-fc@pc
 deriv=[];negative=[];refine=[]
 for j in range(4):
  direction=np.sin(np.arange(len(z))*(.67+j*.17)+j);direction/=np.linalg.norm(direction)
  def fd(h,omit=False):return (potential(z-2*h*direction,omit)-8*potential(z-h*direction,omit)+8*potential(z+h*direction,omit)-potential(z+2*h*direction,omit))/(12*h)
  a=fd(2e-5);b=fd(1e-5);deriv.append(b);refine.append(abs(a-b));negative.append(fd(1e-5,True))
 tip=np.array(r['tip_world_m']);obj=np.array([r['normal_N'],0,-r['object_downward_friction_N']]);external=np.r_[obj,np.cross(tip,obj)]
 for q in r['moving_mass_points']+r['fixed_mass_points']:
  f=np.array([0,0,-q['mass_kg']*G]);external+=np.r_[f,np.cross(q['position_m'],f)]
 motor=next(q for q in points if q['part_ID']=='F0_MICRO_MOTOR');mf=np.array([0,0,-motor['mass_kg']*G]);external+=np.r_[mf,np.cross(motor['rest_centroid_m'],mf)];external+=np.array(r['string']['wire_gravity_wrench_N_Nm'])+np.array(r['string']['rotor_gravity_wrench_N_Nm']);pair=np.array(r['Root_origin_wrench_N_Nm'])+r['Motor_origin_wrench_N_Nm'];err=float(abs(external-pair).max());checks=dict(independent_virtualwork=max(abs(np.array(deriv)))<1e-10,finite_difference_refinement=max(refine)<1e-10,independent_wrench=err<1e-12,normal_target=abs(r['normal_N']-.980665/(3*.8))<1e-8,producer_local_checks=all(r['checks'].values()),friction_omission_negative_control=(max(abs(np.array(negative)))>1e-6 if item['object_weight_fraction']>0 else True))
 rows.append(dict(object_weight_fraction=item['object_weight_fraction'],T_N=r['T_N'],normal_N=r['normal_N'],downward_friction_N=r['object_downward_friction_N'],friction_ratio=r['object_downward_friction_N']/r['normal_N'],checks={k:bool(v) for k,v in checks.items()},independent_virtualwork_directional_J=deriv,omitting_object_friction_residual_J=negative,derivative_refinement_error_J=max(refine),independent_external_wrench_N_Nm=external.tolist(),Root_plus_Motor_wrench_N_Nm=pair.tolist(),independent_wrench_error=err,motor_axis_torque_Nm=r['string']['motor_axis_torque_Nm']))
 dump(out/'progress.json',rows);print(json.dumps(rows[-1]),flush=True)
checks=dict(all_fresh_states=all(all(r['checks'].values()) for r in rows),fully_loaded_five_states=len(rows)==5 and rows[-1]['object_weight_fraction']==1,full_mu_assumption_at_limit=abs(rows[-1]['friction_ratio']-.8)<1e-12);dump(out/'summary.json',dict(status='ACTUAL_PRODUCT_UPSTREAM_FRICTION_LOAD_INDEPENDENT_VIRTUALWORK_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_PRODUCT_UPSTREAM_FRICTION_LOAD_AUDIT_FAIL',candidate=d['candidate'],source=ref(src),producer=ref(out/'producer.py'),checks=checks,rows=rows,vertical_friction_tension_increase_fraction=rows[-1]['T_N']/rows[0]['T_N']-1,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Fourdeterministic directional finite-difference virtualwork checks are independent numericchecks,not globalenergy orfull3Dcontactcertificate','mu=.8unmeasuredandfullyutilized,zero frictionmargin;contactpoint/normalaredeclaredreferencecuts','Root/Motorcutwrenchesarefreshbutnotactualcontacttractions;support/host/friction/stick/gap/strength/full3Fingerremain']))
raise SystemExit(0 if all(checks.values()) else 2)
