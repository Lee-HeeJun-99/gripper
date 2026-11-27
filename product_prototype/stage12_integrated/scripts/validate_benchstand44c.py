"""Actual four-port stand stack and unilateral ground wrench test."""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,volume
from mechanisms_stage1 import hex_axis
from primary_installed_stack42 import overlap_area
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def main():
 out=ROOT/'validation/integrated/primaryP1_benchstand44c_validation';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_benchstand44c/summary.json';d=json.loads(cp.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(v) for n,v in s.items()};poses=[];seats=[]
 def hits(shape,exclude):
  b=bounds(shape);return [dict(part_ID=n,mm3=v) for n in s if n not in exclude and overlap(b,bb[n]) and (v:=common(shape,s[n]))>1e-8]
 mounts={n for n in s if n.startswith('BENCH_MOUNT_')}
 for dz in [-35,-20,-10,-5,-1,0]:poses.append(dict(operation='complete_primary_lowered_to_stand_equivalent',stand_dz_mm=dz,hits=hits(translate(s['BENCH_SUPPORT'],0,0,dz),{'BENCH_SUPPORT'}|mounts)))
 for i,(x,y) in enumerate([(-59,-58),(101,-58),(-59,39),(101,39)]):
  assert not(ROOT/'runtime/STOP').exists();bn=f'BENCH_MOUNT_BOLT_{i}';nn=f'BENCH_MOUNT_NUT_{i}'
  for dz in [30,15,8,3,1,0]:poses.append(dict(operation='mount_bolt_top_approach',station=i,dz_mm=dz,hits=hits(translate(s[bn],0,0,dz),{bn,nn})))
  for dz in [-20,-10,-5,-1,0]:poses.append(dict(operation='mount_nut_bottom_approach_smooth_envelope',station=i,dz_mm=dz,hits=hits(translate(s[nn],0,0,dz),{nn})))
  poses.append(dict(operation='4AFsocket_top_tool',station=i,hits=hits(hex_axis((x,y,76.6),(0,0,1),3.9,30),set())))
  # Nominal 8AF open-wrench jaw region,not full supplier handle/jaw profile.
  seats.append(dict(station=i,bolt=refs[bn],nut=refs[nn],head_seat_mm2=overlap_area(s[bn],s['BENCH_ANCHOR_RAIL'],74),nut_seat_mm2=overlap_area(s[nn],s['BENCH_SUPPORT'],60),grip_mm=14,nominal_overlap_mm=4.7,tipprojection_mm=1.3,effective_thread_engagement_mm=None))
 e=TopExp_Explorer(s['BENCH_SUPPORT'],TopAbs_FACE);bottom=[]
 while e.More():
  f=TopoDS.Face_s(e.Current());b=bounds(f)
  if abs(b[2]+130)<1e-7 and abs(b[5]+130)<1e-7:
   g=GProp_GProps();BRepGProp.SurfaceProperties_s(f,g);bottom.append(dict(area_mm2=g.Mass(),bounds_mm=b))
  e.Next()
 # Actual rectangular foot normal cone;pressure can be represented at corners
 # for resultant feasibility. No hidden friction,adhesion or signed pressure.
 corners=[[-95,-75],[137,-75],[137,65],[-95,65]]
 A=np.array([[0,0,1,y,-x,0] for x,y in corners],float).T
 trials=[]
 for label,target in [('vertical1N',[0,0,1,0,0,0]),('horizontal1N_with1Nnormal',[1,0,1,0,0,0]),('yaw1Nmm_with1Nnormal',[0,0,1,0,0,1]),('inside_roll50Nmm',[0,0,1,50,0,0]),('outside_roll80Nmm',[0,0,1,80,0,0]),('inside_pitch90Nmm',[0,0,1,0,90,0]),('outside_pitch100Nmm',[0,0,1,0,100,0])]:
  target=np.array(target,float);r=linprog(np.zeros(4),A_eq=A,b_eq=target,bounds=[(0,None)]*4,method='highs');trials.append(dict(name=label,target_N_Nmm=target.tolist(),feasible=bool(r.success),status=int(r.status),corner_normals_N=None if not r.success else r.x.tolist(),residual=None if not r.success else float(abs(A@r.x-target).max())))
 # Independent analytic support polygon predicate,not another LP.
 def analytic(t):
  fx,fy,fz,mx,my,mz=t
  return abs(fx)<1e-12 and abs(fy)<1e-12 and abs(mz)<1e-12 and fz>0 and -95<=-my/fz<=137 and -75<=mx/fz<=65
 checks=dict(actual103parts=len(s)==103,no_interferences=not d['interferences'],all_changed_valid=all(c['valid'] and c['solids']==1 for c in d['changed']),finite_insertion_tool_poses_clear=all(not p['hits'] for p in poses),four_actual_head_seats=all(abs(r['head_seat_mm2']-(math.pi*(4.25**2-2.75**2)))<1e-7 for r in seats),four_actual_nut_seats=all(abs(r['nut_seat_mm2']-(8**2*math.sqrt(3)/2-math.pi*2.75**2))<1e-7 for r in seats),actual_ground_area=abs(sum(r['area_mm2'] for r in bottom)-32480)<1e-7,ground_LP_matches_independent_support_polygon=all(r['feasible']==analytic(r['target_N_Nmm']) for r in trials),horizontal_and_yaw_rejected=not trials[1]['feasible'] and not trials[2]['feasible'])
 r=dict(status='ACTUAL_STAND_LOCAL_VALIDATION_PASS_SYSTEM_GROUND_FAIL' if all(checks.values()) else 'ACTUAL_STAND_LOCAL_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,poses=poses,seats=seats,ground_bottom_faces=bottom,ground_corners_mm=corners,ground_columns=A.tolist(),ground_wrench_trials=trials,ground_model='Unilateral frictionless normal-only planar support at actual foot,no artificial clamping',physical_operating_sourcefield=None,accepted_physical_equilibria=0,physical_material_strength_preload_thread_qualified=False,system_ground_full_wrench_qualified=False,whole_system_release=False,limitations=['Insertion and tool checks are finite samples,not continuous assembly','Nominal smooth thread geometry does not establish engagement law/preload/locking;source min material absent','Ground rank3 normal wrench cone fails horizontal and yaw loads;this is an explicit physical blocker','No full spanner handle profile/tool rotation or strength/mesh/time/globalenergy qualification'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,failed_poses=[p for p in poses if p['hits']],trials=trials)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
