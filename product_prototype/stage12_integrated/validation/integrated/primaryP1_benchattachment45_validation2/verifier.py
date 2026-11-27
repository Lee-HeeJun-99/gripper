"""Independent actual bench interface seats, finite assembly and backlash audit.
No external plate clamp, preloaded screw, or simultaneous opposing key contacts.
"""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import brentq,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,box
from mechanisms_stage1 import hex_axis
from primary_installed_stack42 import overlap_area
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
PORTS=[(-65,-35),(107,-35),(-65,15),(107,15)]
KEYS=[(-25,-5),(65,-5)]
def main():
 out=ROOT/'validation/integrated/primaryP1_benchattachment45_validation2';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_benchattachment45/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(v) for n,v in s.items()};poses=[];seats=[]
 def hits(shape,exclude):
  b=bounds(shape);return [dict(part_ID=n,mm3=v) for n in s if n not in exclude and overlap(b,bb[n]) and (v:=common(shape,s[n]))>1e-8]
 through={n for n in s if n.startswith('BENCH_THROUGH_')}
 for dz in [-35,-20,-10,-5,-1,0]:poses.append(dict(operation='bench_plate_below_completed_stand_no_new_fasteners',dz_mm=dz,hits=hits(translate(s['EXTERNAL_BENCH_PLATE'],0,0,dz),{'EXTERNAL_BENCH_PLATE'}|through)))
 for i,(x,y) in enumerate(PORTS):
  assert not(ROOT/'runtime/STOP').exists();bn=f'BENCH_THROUGH_BOLT_{i}';nn=f'BENCH_THROUGH_NUT_{i}'
  for dz in [30,15,8,3,1,0]:poses.append(dict(operation='through_bolt_top_approach',station=i,dz_mm=dz,hits=hits(translate(s[bn],0,0,dz),{bn,nn})))
  for dz in [-20,-10,-5,-1,0]:poses.append(dict(operation='through_nut_bottom_approach_smooth_envelope',station=i,dz_mm=dz,hits=hits(translate(s[nn],0,0,dz),{nn})))
  poses.append(dict(operation='4AFsocket_top_tool',station=i,hits=hits(hex_axis((x,y,-121.4),(0,0,1),3.9,32),set())))
  # Published Bahco111M8 head envelope 19mm wide/4.2mm thick,130mm length.
  # A deliberately conservative enclosing jaw/handle rectangle with8AF void.
  # Corridor is only an envelope,not supplierjaw/continuous nut rotation.
  from incremental_stage1 import cut
  tool=cut(box(x-130 if x<20 else x-9.5,y-9.5,-142.45,139.5,19,4.2),box(x-9.6,y-4.1,-142.55,19.2,8.2,4.4))
  for dx in ([-30,-15,-5,0] if x<20 else [30,15,5,0]):
   poses.append(dict(operation='8AFpublished_enclosing_wrench_outboard_entry',station=i,dx_mm=dx,hits=hits(translate(tool,dx,0,0),set())))
  seats.append(dict(station=i,head_seat_mm2=overlap_area(s[bn],s['BENCH_SUPPORT'],-124),nut_seat_mm2=overlap_area(s[nn],s['EXTERNAL_BENCH_PLATE'],-138),head=refs[bn],nut=refs[nn],grip_mm=14,nominal_overlap_mm=4.7,effective_thread_engagement_mm=None))
 # Actual transformed solid probe;compare threshold with separate rectangle
 # containment calculation. No LP of simultaneously engaged opposing faces.
 def rot(v,a):
  t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(20,-5,0),gp_Dir(0,0,1)),a);return BRepBuilderAPI_Transform(v,t,True).Shape()
 keyshapes=[box(x-6,y-8,-134,12,16,4) for x,y in KEYS]
 plate=s['EXTERNAL_BENCH_PLATE'];angles=[]
 def geometric_gap(a):
  c=math.cos(a);sn=math.sin(a);g=[]
  for x,y in KEYS:
   for dx in [-6,6]:
    for dy in [-8,8]:
     X=20+c*(x+dx-20)-sn*dy;Y=-5+sn*(x+dx-20)+c*dy
     g.extend([6.1-abs(X-x),8.1-abs(Y-y)])
  return min(g)
 for sign in [-1,1]:
  a=sign*brentq(lambda t:geometric_gap(sign*t),0,.02,xtol=1e-15)
  below=sum(common(rot(k,a-sign*1e-6),plate) for k in keyshapes);above=sum(common(rot(k,a+sign*1e-6),plate) for k in keyshapes)
  angles.append(dict(sign=sign,zero_contact_angle_rad=a,analytic_gap_mm=geometric_gap(a),actual_BRep_below_mm3=below,actual_BRep_above_mm3=above))
 shifts=[]
 for axis in [0,1]:
  for sign in [-1,1]:
   row=dict(axis=axis,sign=sign,nominal_backlash_mm=.1)
   for tag,delta in [('below',.099),('above',.101)]:
    vec=[0,0,0];vec[axis]=sign*delta;row[tag+'_BRep_mm3']=sum(common(translate(k,*vec),plate) for k in keyshapes)
   shifts.append(row)
 # For each +/- horizontal force,only the corresponding two key walls are
 # active after0.1mm slip. Forces act at actual key/pocket wall midheights.
 # Target includes moment at z=-132 and y=-5, x=20. These are local unit tests.
 trials=[]
 for axis in [0,1]:
  for sign in [-1,1]:
   f=np.zeros(3);f[axis]=sign;cols=[]
   for x,y in KEYS:
    p=np.array([x,y,-132.]);p[axis]+=sign*(6.1 if axis==0 else 8.1)
    cols.append(np.r_[f,np.cross(p,f)])
   A=np.array(cols).T;t=np.r_[f,np.cross([20,-5,-132],f)];r=linprog(np.ones(2),A_eq=A,b_eq=t,bounds=(0,None),method='highs')
   trials.append(dict(axis=axis,sign=sign,columns_N_Nmm=A.tolist(),target_N_Nmm=t.tolist(),feasible=bool(r.success),reactions_N=r.x.tolist() if r.success else None,residual=float(abs(A@r.x-t).max()) if r.success else None,law='Only same-direction walls engaged after0.1mm translation;unpreloaded point resultant,not strength/equilibrium'))
 # Free complete stand+externalbench has no boundary traction at all.
 free=linprog(np.zeros(1),A_eq=np.zeros((6,1)),b_eq=[1,0,0,0,0,0],bounds=(0,None),method='highs')
 checks=dict(actual112parts=len(s)==112,no_final_interferences=not d['interferences'],changed_valid=all(r['valid'] and r['solids']==1 for r in d['changed']),finite_assembly_and_tools_clear=all(not p['hits'] for p in poses),four_head_seats=all(abs(r['head_seat_mm2']-math.pi*(4.25**2-2.75**2))<1e-7 for r in seats),four_nut_seats=all(abs(r['nut_seat_mm2']-(8**2*math.sqrt(3)/2-math.pi*2.75**2))<1e-7 for r in seats),actual_key_translation_stops=all(r['below_BRep_mm3']<1e-8 and r['above_BRep_mm3']>1e-8 for r in shifts),independent_key_yaw_stop=all(r['actual_BRep_below_mm3']<1e-8 and r['actual_BRep_above_mm3']>1e-8 for r in angles),unilateral_local_unit_shear=all(r['feasible'] and r['residual']<1e-8 for r in trials),free_external_plate_not_mislabeled_ground=not free.success)
 r=dict(status='ACTUAL_KEYED_BENCH_LOCAL_VALIDATION_PASS_GLOBAL_GROUND_UNQUALIFIED' if all(checks.values()) else 'ACTUAL_KEYED_BENCH_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,poses=poses,seats=seats,key_shift_probes=shifts,key_yaw_stops=angles,local_shear_trials=trials,free_complete_product_horizontal_equilibrium_feasible=bool(free.success),external_ground_traction=None,physical_operating_sourcefield=None,accepted_physical_equilibria=0,physical_uplift_capacity_N=None,effective_thread_engagement_mm=None,whole_system_release=False,limitations=['Finite bench plate is actual additional support geometry;ultimate floor/building attachment remains unspecified','Keyforces above are local unit tests after finite translation,not simultaneous opposing-face supports or operating solution','Yaw stops initially corner contact;no finite pressure/strength or keyplasticity certified','Smooththread geometry gives no axialcapacity;uplift/core/flank/preload/locking unresolved','Finite sampled insertion and conservative final tool corridor do not certify full continuousassembly or helicalthreading','Changedstand/bench require new physical mass/FE/contact and source material;mesh1percent/time.1percent/globalenergy unchanged'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,failed_poses=[p for p in poses if p['hits']],angles=angles,shifts=shifts)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
