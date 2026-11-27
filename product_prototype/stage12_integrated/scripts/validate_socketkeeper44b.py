"""Actual keeper assembly, backlash and contact virtual-work tests.
No material strength/operating equilibrium claim; thread connector is conditional.
"""
import sys,json,math,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,volume
from mechanisms_stage1 import hex_axis
from validate_nutcapture43 import spin

def main():
 out=ROOT/'validation/integrated/primaryP1_socketkeeper44c_validation2';out.mkdir();shutil.copyfile(__file__,out/'verifier.py')
 cp=ROOT/'cad/exports/primaryP1_socketkeeper44c/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(s) for n,s in parts.items()}
 def hits(s,exclude):
  b=bounds(s);return [dict(part_ID=n,common_mm3=v) for n in parts if n not in exclude and overlap(b,bb[n]) and (v:=common(s,parts[n]))>1e-8]
 poses=[];stops=[]
 for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
  assert not(ROOT/'runtime/STOP').exists()
  kn=f'SOCKET_KEEPER_{i}';pn=f'KEEPER_PIN_{i}';nn=f'KEEPER_NUT_{i}';bn=f'ANCHOR_BOLT_{i}'
  for dz in [-30,-15,-8,-4,-2,-1,-.1,0]:poses.append(dict(operation='keeper_bottom_insert_pin_absent',station=i,dz_mm=dz,hits=hits(translate(parts[kn],0,0,dz),{kn,pn,nn})))
  for dx in [-40,-25,-15,-8,-4,-1,0]:poses.append(dict(operation='crosspin_left_insert_nut_absent',station=i,dx_mm=dx,hits=hits(translate(parts[pn],dx,0,0),{pn,nn})))
  for dx in [20,10,5,2,0]:poses.append(dict(operation='nut_right_approach_smooth_thread_envelope',station=i,dx_mm=dx,hits=hits(translate(parts[nn],dx,0,0),{nn})))
  tool=hex_axis((x-35,y,50),(1,0,0),3.9,25.4);poses.append(dict(operation='pin4AFdrive_tool',station=i,hits=hits(tool,set())))
  # Anchor bolt can be torqued with keeper absent; same actual socket corridor.
  tool=hex_axis((x,y,30),(0,0,1),3.9,27.4);poses.append(dict(operation='anchor4AFdrive_before_keeper',station=i,hits=hits(tool,{kn,pn,nn})))
  for mechanism,moving,fixed in [('socket',parts[bn],parts[kn]),('base_key',parts[kn],parts['TEST_BASE'])]:
   for sign in [-1,1]:
    lo=0.;hi=.25;assert common(spin(moving,x,y,sign*hi),fixed)>1e-8
    for _ in range(26):
     mid=(lo+hi)/2
     if common(spin(moving,x,y,sign*mid),fixed)>1e-8:hi=mid
     else:lo=mid
    stops.append(dict(station=i,mechanism=mechanism,sign=sign,clear_rad=lo,interference_rad=hi,plus001_mm3=common(spin(moving,x,y,sign*(hi+.001)),fixed)))
  # Retention is actual transverse bearing, not an axial tie.
  poses.append(dict(operation='retained_keeper_down_0.2mm',station=i,expected_interference=True,hits=hits(translate(parts[kn],0,0,-.2),{kn,nn})))
 lead=.8/(2*math.pi)
 # Explicit z, bolt/nut/keeper/base/receiver angles. Connector has physical
 # screw work ratio but no core/flank stiffness/strength qualification yet.
 J=np.array([[1,-lead,lead,0,0,0],[0,1,0,-1,0,0],[0,0,0,1,-1,0],[0,0,1,0,0,-1],[0,0,0,0,1,-1]],float)
 target=np.array([1,0,0,0,0,0.])
 def solve(rows):
  A=J[rows].T;r=linprog(np.zeros(len(rows)),A_eq=A,b_eq=target,bounds=[(None,None)]*len(rows),method='highs');return dict(feasible=bool(r.success),status=int(r.status),reactions=None if not r.success else r.x.tolist(),residual=None if not r.success else float(abs(A@r.x-target).max()))
 full=solve([0,1,2,3,4]);no_keeper=solve([0,3,4]);no_key=solve([0,1,3,4]);no_receiver_key=solve([0,1,2,3])
 # Analytical contact lever at first hex contact, independent of BRep volume:
 # hex key3.9AF in4AFsocket, rectangular8x10 key in12? x gap .1 each.
 socket_angle=math.pi/6-math.acos(2/(3.9/math.sqrt(3)))
 key_angle=math.asin(4.1/math.sqrt(4**2+5**2))-math.atan2(4,5)
 # Independent polygon clipping resolves the SAME1e-8mm3 detection threshold.
 # Zero-contact angle and finite-volume detection angle are distinct.
 def area(poly):return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2) if poly else 0.
 def clip(poly,n,c):
  out=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   da=np.dot(n,a)-c;db=np.dot(n,b)-c
   if da<=0:out.append(a)
   if (da<=0)!=(db<=0):out.append((np.array(a)+(np.array(b)-a)*da/(da-db)).tolist())
  return out
 def independent_overlap(kind,t):
  if kind=='socket':
   r=3.9/math.sqrt(3);poly=[[r*math.cos(k*math.pi/3),r*math.sin(k*math.pi/3)] for k in range(6)];full=area(poly)
   for k in range(6):
    a=math.pi/6+k*math.pi/3+t;poly=clip(poly,[math.cos(a),math.sin(a)],2.)
   return max(0.,full-area(poly))*2.4
  p=[[a*math.cos(t)-b*math.sin(t),a*math.sin(t)+b*math.cos(t)] for a,b in [(-4,-5),(4,-5),(4,5),(-4,5)]];full=area(p)
  p=clip(clip(p,[1,0],4.1),[-1,0],4.1);return max(0.,full-area(p))*6
 detection={}
 for kind in ['socket','base_key']:
  lo=0.;hi=.1
  for _ in range(38):
   mid=(lo+hi)/2
   if independent_overlap(kind,mid)>1e-8:hi=mid
   else:lo=mid
  detection[kind]=(lo+hi)/2
 volume_errors=[abs(independent_overlap(r['mechanism'],r['sign']*(r['interference_rad']+.001))-r['plus001_mm3']) for r in stops]
 socket_lever=(3.9/math.sqrt(3))*math.sin(math.pi/6-socket_angle)
 key_lever=5*math.cos(key_angle)-4*math.sin(key_angle)
 # Two opposed normal contacts, each carries half reaction torque.
 contact_forces=dict(socket_N_per_axial_N=lead/(2*socket_lever),base_key_N_per_axial_N=lead/(2*key_lever))
 work=[]
 for j in range(20):
  q=np.sin(np.arange(6)+j);lam=np.array([1.,lead,lead,-lead,lead]);work.append(float(abs(q@(J.T@lam)-(J@q)@lam)))
 expected_poses=[p for p in poses if p.get('expected_interference')];clearposes=[p for p in poses if not p.get('expected_interference')]
 checks=dict(actual94parts=len(parts)==94,valid_single_solids=all(c['valid'] and c['solids']==1 for c in d['changed']),no_final_interference=not d['interferences'],all_recorded_assembly_tool_poses_clear=all(not p['hits'] for p in clearposes),actual_pin_retains_keeper=all(any(h['part_ID']==f"KEEPER_PIN_{p['station']}" for h in p['hits']) for p in expected_poses),both_rotation_stops=all(s['plus001_mm3']>1e-8 for s in stops),independent_socket_angle=all(abs((s['clear_rad']+s['interference_rad'])/2-detection['socket'])<3e-7 for s in stops if s['mechanism']=='socket'),independent_key_angle=all(abs((s['clear_rad']+s['interference_rad'])/2-detection['base_key'])<3e-7 for s in stops if s['mechanism']=='base_key'),independent_intersection_volumes=max(volume_errors)<1e-7,explicit_work_balance=full['feasible'] and full['residual']<1e-10 and max(work)<1e-12,missing_keeper_rejected=not no_keeper['feasible'],missing_base_key_rejected=not no_key['feasible'],missing_receiver_key_rejected=not no_receiver_key['feasible'])
 r=dict(status='ACTUAL_KEEPER_LOCAL_VALIDATION_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_KEEPER_LOCAL_VALIDATION_FAIL',candidate=ref(cp),producer=ref(out/'verifier.py'),checks=checks,poses=poses,rotation_stops=stops,independent_angles_rad=dict(socket=socket_angle,base_key=key_angle),independent_detection_angles_rad=detection,independent_volume_error_max_mm3=max(volume_errors),backlash_sum_rad=socket_angle+key_angle,contact_force_levers_mm=dict(socket=socket_lever,base_key=key_lever),conditional_contact_normal_forces=contact_forces,explicit_connector_J=J.tolist(),unit_axial=full,missing_keeper=no_keeper,missing_base_key=no_key,missing_receiver_key=no_receiver_key,virtual_work_error_max=max(work),thread_pitch_mm=.8,thread_lead_mm_per_rad=lead,pin_grip_mm=14,nut_nominal_height_mm=4.7,pin_projection_mm=1.3,physical_equilibrium_accepted=False,sourcefield=None,thread_core_flank_engagement_material_preload_qualified=False,external_fixture=None,limitations=['Finite insertion/tool samples only;not continuous collision or true helical thread assembly','Positive rotational stops have backlash;the LP tests engaged bilateral signed torque reactions,not unloaded equilibrium or certified contact pressure','Retention pin uses smooth threaded envelope;transverse bearing proven geometrically,retaining nut thread/locking/material minimum unqualified','No physical operating force,finitebody strength,mesh/time/globalenergy or external support certification'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,failposes=[p for p in clearposes if p['hits']],angles=r['independent_angles_rad'])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
