"""Actual full P1 assembly and eight positive nut-yaw stops, with free bolt spin.
Exact continuous axial envelopes cover smooth CAD, never screw threading.
"""
import json,sys,shutil,math
import numpy as np
from scipy.optimize import brentq,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,cyl,cut,fuse,translate
from mechanisms_stage1 import hex_axis
from primary_installed_stack42 import overlap_area
from primary_nutseat46b import STATIONS
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

def rotate(s,x,y,a):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(x,y,0),gp_Dir(0,0,1)),a);return BRepBuilderAPI_Transform(s,t,True).Shape()
def gap(a,AF):
 vs=np.array([[AF/math.sqrt(3)*math.cos(k*math.pi/3+a),AF/math.sqrt(3)*math.sin(k*math.pi/3+a)] for k in range(6)])
 normals=np.array([[math.cos(math.pi/6+k*math.pi/3),math.sin(math.pi/6+k*math.pi/3)] for k in range(6)])
 return float((4.1-normals@vs.T).min())
def main():
 out=ROOT/'validation/integrated/primaryP1_nutseat46_validation3';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_nutseat46b/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(s) for n,s in parts.items()};poses=[];sweeps=[];stops=[];seats=[];legacy=[];unitwork=[]
 late={n for n in parts if n.startswith(('SOCKET_KEEPER_','KEEPER_PIN_','KEEPER_NUT_'))}
 stage_late=late
 def hits(sh,exclude):
  b=bounds(sh);return [dict(part_ID=n,mm3=v) for n,s in parts.items() if n not in (exclude|stage_late) and overlap(b,bb[n]) and (v:=common(sh,s))>1e-8]
 for prefix,i,x,y,z0,z1,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists();bn=f'{prefix}_BOLT_{i}';nn=f'{prefix}_NUT_{i}';nut=parts[nn];bolt=parts[bn];headseat=z1+14
  # Nuts can be fed from below while bolts approach from above. Nut carrier
  # is a declared custom annular pusher:OD7.6/ID5.2,not a supplier wrench.
  # Its ID leaves bolt tip travel open throughout smooth-envelope insertion.
  for dz in [-25,-12,-5,-1,0]:poses.append(dict(operation='nut_aligned_bottom_feed_before_anchor_keepers',part=nn,dz_mm=dz,hits=hits(translate(nut,0,0,dz),{nn})))
  nutunion=cut(hex_axis((x,y,z0-25),(0,0,1),8,29.7),cyl(2.5,(x,y,z0-25.01),29.72))
  sweeps.append(dict(operation='continuous25mm_nut_bottom_feed_before_anchor_keepers',part=nn,hits=hits(nutunion,{nn})))
  carrier=cut(cyl(3.8,(x,y,z0-30),30),cyl(2.6,(x,y,z0-30.01),30.02))
  poses.append(dict(operation='custom7.6OD5.2ID_annular_nutcarrier_final',part=nn,hits=hits(carrier,set())))
  for dz in [30,12,5,1,0]:poses.append(dict(operation='bolt_top_feed_smooth_envelope',part=bn,dz_mm=dz,hits=hits(translate(bolt,0,0,dz),{bn,nn})))
  envelope=fuse(cyl(4.25,(x,y,headseat),35),cyl(2.5,(x,y,headseat-20),50))
  sweeps.append(dict(operation='continuous30mm_bolt_top_feed',part=bn,hits=hits(envelope,{bn,nn})))
  # Top4AF driver enters original 2.5mm deep drive;all paths enlarged union.
  tool=hex_axis((x,y,headseat+2.6),(0,0,1),3.9,32)
  poses.append(dict(operation='4AFdriver_top',part=bn,hits=hits(tool,set())))
  # Old19mm wide wrench approach is deliberately checked and rejected
  # as the adopted pockets replace that assembly mechanism.
  from incremental_stage1 import box
  oldtool=cut(box(x-9.5,y-9.5,z0+.2,19,19,4.2),box(x-9.6,y-4.1,z0+.1,19.2,8.2,4.4))
  legacy.append(dict(part=nn,old_wrench_hits=hits(oldtool,set())))
  for AF in [8.,7.78]:
   for sign in [-1,1]:
    a=sign*brentq(lambda a:gap(sign*a,AF),0,.3,xtol=1e-15)
    sample=nut if AF==8 else cut(hex_axis((x,y,z0),(0,0,1),AF,4.4),cyl(2.5,(x,y,z0-.01),4.42))
    below=common(rotate(sample,x,y,a-sign*1e-5),parts[parent]);above=common(rotate(sample,x,y,a+sign*1e-5),parts[parent])
    stops.append(dict(part=nn,AF_mm=AF,sign=sign,zero_contact_angle_rad=a,analytic_gap_mm=gap(a,AF),actual_below_mm3=below,actual_above_mm3=above,probe_offset_rad=1e-5))
  ha=overlap_area(bolt,parts['BENCH_ANCHOR_RAIL'] if prefix=='BENCH_MOUNT' else parts['BENCH_SUPPORT'],headseat)
  na=overlap_area(nut,parts[parent],z1)
  seats.append(dict(bolt_ID=bn,nut_ID=nn,head_seat_mm2=ha,nut_seat_mm2=na,grip_mm=14,nominal_overlap_mm=4.7,actual_nut_z_mm=bb[nn][2:6:3],effective_engagement_mm=None))
  # Source .8mm screw lead yields q = z_b-z_n-k(theta_b-theta_n).
  # Cage reacts theta_n only after its measured yaw gap. Bolt remains free.
  # Unit tension requires a real bolt moment,not fictitious fixed rotation.
  k=.8/(2*math.pi);C=np.array([[1.,-1.,-k,k],[0,0,0,1.]])
  target=np.array([1.,-1.,0,0]);r=linprog(np.zeros(2),A_eq=C.T,b_eq=target,bounds=[(None,None)]*2,method='highs')
  locked=np.c_[C.T,[0,0,1,0]];rl=linprog(np.zeros(3),A_eq=locked,b_eq=target,bounds=[(None,None)]*3,method='highs')
  unitwork.append(dict(bolt_ID=bn,nut_ID=nn,DOFs=['z_b','z_n','theta_b','theta_n'],constraint_jacobian=C.tolist(),cage_only_unit_axial_feasible=bool(r.success),mathematical_added_bolt_torque_feasible=bool(rl.success),required_bolt_torque_Nmm_per_N=float(rl.x[2]) if rl.success else None,actual_bolt_lock_implemented=False))
 # Restore all late components and explicitly verify keeper-last ordering
 # on the changed complete specimen. No collision exclusions survive final.
 stage_late=set()
 for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
  kn=f'SOCKET_KEEPER_{i}';pn=f'KEEPER_PIN_{i}';nn=f'KEEPER_NUT_{i}'
  for dz in [-30,-15,-8,-4,-2,-1,-.1,0]:poses.append(dict(operation='late_keeper_bottom_feed',part=kn,dz_mm=dz,hits=hits(translate(parts[kn],0,0,dz),{kn,pn,nn})))
  # The -40mm lateral start crosses a stand leg (preservedFAIL). Bring
  # the pin up at -20mm,then insert horizontally;validate both path legs.
  for dz in [-30,-15,-8,-4,0]:poses.append(dict(operation='late_crosspin_bottom_to_staging',part=pn,dx_mm=-20,dz_mm=dz,hits=hits(translate(parts[pn],-20,0,dz),{pn,nn})))
  from incremental_stage1 import box
  def stadium_x(x0,length,r):
   return fuse(fuse(cyl(r,(x0,y,20),length,(1,0,0)),cyl(r,(x0,y,50),length,(1,0,0))),box(x0,y-r,20,length,2*r,30))
  env=fuse(stadium_x(x-32,5,4.25),stadium_x(x-27,20,2.5))
  sweeps.append(dict(operation='continuous_crosspin30mm_vertical_to_staging',part=pn,hits=hits(env,{pn,nn})))
  env=fuse(cyl(4.25,(x-32,y,50),25,(1,0,0)),cyl(2.5,(x-27,y,50),40,(1,0,0)))
  sweeps.append(dict(operation='continuous_crosspin20mm_horizontal_from_staging',part=pn,hits=hits(env,{pn,nn})))
  for dx in [-20,-17,-10,-4,-1,0]:poses.append(dict(operation='late_crosspin_left_feed',part=pn,dx_mm=dx,hits=hits(translate(parts[pn],dx,0,0),{pn,nn})))
  for dx in [20,10,5,2,0]:poses.append(dict(operation='late_crossnut_right_feed',part=nn,dx_mm=dx,hits=hits(translate(parts[nn],dx,0,0),{nn})))
  poses.append(dict(operation='late_crosspin4AFtool',part=pn,hits=hits(hex_axis((x-35,y,50),(1,0,0),3.9,25.4),set())))
 checks=dict(full112part_hash_binding=True,final_no_interference=not d['interferences'],two_valid_single_changed_solids=all(r['valid'] and r['solids']==1 for r in d['changed']),all_finite_assembly_tools_clear=all(not r['hits'] for r in poses),continuous_nut_bolt_envelopes_clear=all(not r['hits'] for r in sweeps),eight_original_seats_preserved=all(abs(r['head_seat_mm2']-math.pi*(4.25**2-2.75**2))<1e-7 and abs(r['nut_seat_mm2']-(8**2*math.sqrt(3)/2-math.pi*2.75**2))<1e-7 for r in seats),all_nominal_and_minAF_yaw_stops=all(r['actual_below_mm3']<1e-8 and r['actual_above_mm3']>1e-8 for r in stops),old_wrench_route_explicitly_rejected=all(r['old_wrench_hits'] for r in legacy),nut_cage_does_not_hide_bolt_spin=all(not r['cage_only_unit_axial_feasible'] and r['mathematical_added_bolt_torque_feasible'] for r in unitwork))
 result=dict(status='ACTUAL_P1_EIGHT_NUT_REACTION_POCKETS_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_NUT_POCKET_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,actual_parts=112,poses=poses,continuous_sweeps=sweeps,nut_yaw_stops=stops,seats=seats,rejected_legacy_wrench=legacy,explicit_free_bolt_spin=unitwork,assembly_order=['Support and plate seat via unchanged keys;old anchor keepers last as before','Insert aligned nuts from below with annular pusher;feed bolt from above','Engage thread with real helical motion NOT certified by smooth CAD;nut takes up measured cage yaw','Drive4AFbolt from top while carrier keeps nut at seat;withdraw carrier after engagement','Reverse sequence for removal;no wrench enters8.2AFpocket'],accepted_physical_product_equilibria=0,operating_sourcefield=None,whole_system_release=False,limitations=['Custom nut carrier is a nominal declared tool envelope,not a purchased/rated tool or physical dexterity test','Continuous axial envelopes prove collision clearance only;thread helical assembly,preload and vibration resistance remain unqualified','Nominal eight nut cages are real positive yaw geometry;bolt rotation is explicitly free','Changed stand/plate mass,elasticity,notch/strength/material and ultimate support require new qualification;all22system gates unchanged'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failed_poses=[r for r in poses+sweeps if r['hits']])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
