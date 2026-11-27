"""Actual eight installed socket key/cotter geometry and explicit screw DOFs.
Conditional unit work is not physical installed thread strength or equilibrium.
"""
import json,sys,shutil,math
import numpy as np
from scipy.optimize import brentq,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,fuse,box,cyl
from primary_socketcage47d import STATIONS,cotter
from validate_nutseat46c import rotate
from mechanisms_stage1 import hex_axis
TAG=sys.argv[1] if len(sys.argv)>1 else 'primaryP1_socketcage47_validation3'
CAD=sys.argv[2] if len(sys.argv)>2 else 'primaryP1_socketcage47d'
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/TAG;out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports'/CAD/'summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(s) for n,s in parts.items()};poses=[];stops=[];ret=[];work=[]
 newpins={n for n in parts if '_SPLIT_PIN_' in n};newkeys={n for n in parts if '_SOCKET_KEY_' in n};late=newpins|newkeys
 def hits(sh,excluded):
  b=bounds(sh);return [dict(part_ID=n,common_mm3=v) for n,s in parts.items() if n not in excluded and overlap(b,bb[n]) and (v:=common(sh,s))>1e-8]
 for prefix,i,x,y,seat,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();kn=f'{prefix}_SOCKET_KEY_{i}';pn=f'{prefix}_SPLIT_PIN_{i}';bn=f'{prefix}_BOLT_{i}';key=parts[kn];pin=parts[pn];z=seat+8.2
  # Keys inserted after existing bolts/nuts and driver withdrawn. Pins last.
  for dz in [25,12,6,3,1,0]:poses.append(dict(operation='key_top_insert_before_pins',part=kn,dz_mm=dz,hits=hits(translate(key,0,0,dz),newpins|{kn})))
  straight=cotter(x,y,z,False)
  for dx in [-25,-15,-8,-3,-1,0]:poses.append(dict(operation='straight_splitpin_left_insert',part=pn,dx_mm=dx,hits=hits(translate(straight,dx,0,0),newpins|{pn})))
  # Declared custom plier jaws envelopes at both legs,approached from top.
  for sy in [-1,1]:
   tool=box(x+8,y+(1 if sy>0 else -5),z-1.1,5,4,15)
   poses.append(dict(operation='nominal_top_plier_jaw_access',part=pn,side=sy,hits=hits(tool,newpins)))
  # Actual geometry supports torque with finite angular gaps.
  a=brentq(lambda a:4.5*(math.cos(a)+math.sin(a))-4.6,0,.2,xtol=1e-15)
  b=brentq(lambda a:(3.9/math.sqrt(3))*math.cos(math.pi/6-a)-2,0,.2,xtol=1e-15)
  for sign in [-1,1]:
   stops.append(dict(part=kn,sign=sign,key_cage_angle_rad=sign*a,socket_key_angle_rad=sign*b,serial_backlash_bound_rad=a+b,cage_below_mm3=common(rotate(key,x,y,sign*(a-1e-5)),parts[parent]),cage_above_mm3=common(rotate(key,x,y,sign*(a+1e-5)),parts[parent]),socket_below_mm3=common(rotate(key,x,y,sign*(b-1e-5)),parts[bn]),socket_above_mm3=common(rotate(key,x,y,sign*(b+1e-5)),parts[bn])))
  ret.append(dict(key=kn,pin=pn,key_rise_0p14_mm3=common(translate(key,0,0,.14),pin),key_rise_0p16_mm3=common(translate(key,0,0,.16),pin),key_and_pin_rise_0p31_cage_mm3=common(translate(fuse(key,pin),0,0,.31),parts[parent]),pin_left_0p5_cage_mm3=common(translate(pin,-.5,0,0),parts[parent]),pin_right_0p5_cage_mm3=common(translate(pin,.5,0,0),parts[parent]),pin_undeformed_CAD=ref(out/'verifier.py'),forming_capacity_N=None))
  k=.8/(2*math.pi);C=np.array([[1,-1,-k,k,0],[0,0,0,1,0],[0,0,1,0,-1],[0,0,0,0,1]],float);target=np.array([1,-1,0,0,0.]);sol=linprog(np.zeros(4),A_eq=C.T,b_eq=target,bounds=[(None,None)]*4,method='highs');controls=[]
  for omitted in [1,2,3]:
   A=np.delete(C,omitted,axis=0);r=linprog(np.zeros(3),A_eq=A.T,b_eq=target,bounds=[(None,None)]*3,method='highs');controls.append(dict(removed=['screw','nutcage','socket','cage'][omitted],unit_axial_feasible=bool(r.success)))
  work.append(dict(bolt=bn,DOFs=['z_b','z_n','theta_b','theta_n','theta_key'],constraint_jacobian=C.tolist(),engaged_nominal_unit_axial_feasible=bool(sol.success),residual=float(abs(C.T@sol.x-target).max()) if sol.success else None,multipliers=sol.x.tolist() if sol.success else None,required_socket_and_cage_torque_Nmm_per_N=k,removed_reaction_controls=controls,installed_capacity_N=None,actual_operating_equilibrium=False))
 checks=dict(hash_bound_all128parts=len(parts)==128,final_interferences_zero=not d['interferences'],new_solids_valid_single=all(r['valid'] and r['solids']==1 for r in d['changed']),keys_insert_without_collisions=all(not r['hits'] for r in poses if r['operation']=='key_top_insert_before_pins'),straight_pins_insert_without_collisions=all(not r['hits'] for r in poses if r['operation']=='straight_splitpin_left_insert'),nominal_plier_jaw_access=all(not r['hits'] for r in poses if r['operation']=='nominal_top_plier_jaw_access'),all_finite_socket_and_key_stops=all(r['cage_below_mm3']<1e-8 and r['cage_above_mm3']>1e-8 and r['socket_below_mm3']<1e-8 and r['socket_above_mm3']>1e-8 for r in stops),axial_key_retention=all(r['key_rise_0p14_mm3']<1e-8 and r['key_rise_0p16_mm3']>1e-8 and r['key_and_pin_rise_0p31_cage_mm3']>1e-8 for r in ret),pin_geometric_bidirectional_retention=all(r['pin_left_0p5_cage_mm3']>1e-8 and r['pin_right_0p5_cage_mm3']>1e-8 for r in ret),explicit_screw_torque_transfer_and_missing_reaction_failure=all(r['engaged_nominal_unit_axial_feasible'] and all(not c['unit_axial_feasible'] for c in r['removed_reaction_controls']) for r in work))
 result=dict(status='ACTUAL_P1_SOCKET_CAGE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_SOCKET_CAGE_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),actual_parts=len(parts),checks=checks,poses=poses,stops=stops,axial_retention=ret,conditional_unit_work=work,accepted_physical_product_equilibria=0,operating_sourcefield=None,effective_thread_engagement_mm=None,installed_thread_capacity_N=None,external_ground_attachment=None,whole_system_release=False,limitations=['Finite collision samples only;continuous path and helical threading not certified','Nominal splitpin represented by custom eye/halfround shaft and circular splayed tips;not verified supplier CAD or ISOconformity','Bending/removal springback/reuse/ductility/toolrating and strength unqualified;no forming simulation or hardware','Socket screw moment is conditional unit work with actualnominal geometry afterbacklash;no physical equilibrium,threadfit/preload/strength/globalenergy certificate','External bench plate stillfree;changed support/receiver FE/contact/mass invalid'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failed_poses=[r for r in poses if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
