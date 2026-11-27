"""Reimported primary product assembly paths and conditional physical load contract."""
import argparse,json,math,shutil,sys,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,translate,common,bounds,overlap,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
from primary_module_design import route,Ry,tr

def derivative(f,x,h=1e-3):return (f(x-2*h)-8*f(x-h)+8*f(x+h)-f(x+2*h))/(12*math.radians(h))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 deps=[src,ROOT/'scripts/primary_module_design.py',ROOT/'models/standard_drive/batch6_sources1/reviewed.json',ROOT/'validation/transmission/batch6_operating1/summary.json',ROOT/'models/materials/primary_material_contract1.json',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
 dump(out/'inputs.json',dict(candidate=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(p) for p in deps],predeclared=dict(intersection_mm3_max=1e-8,derivative_relative_max=1e-6,force_balance_N_max=1e-9,moment_balance_Nmm_max=1e-8),scope='Nominal actual reimported product; sampled assembly, NOT CCD or thread tightening. Prescribed0..60deg, typical elastic energy reference,100g future3Finger equal friction scenarios; NOT equilibrium or capacity.'))
 s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(x) for n,x in s.items()};valid={n:bool(BRepCheck_Analyzer(x).IsValid() and solid_count(x)==1) for n,x in s.items()}
 final=[];pairs=0
 for n,m in itertools.combinations(s,2):
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(s[m],s[n]) # reversed operand order, independent STEP import
   if v>1e-8:final.append(dict(a=n,b=m,common_mm3=v))
 fixed=['OPEN_FRAME','GROUND_PLATE','TEST_BASE']+[n for n in s if n.startswith('FIXTURE_')]+[n for n in s if n.startswith('GROUND_') and n!='GROUND_PLATE']
 drive=[n for n in s if n.startswith(('F0_MICRO','F0_STOCK','F0_SPOOL','F0_SET')) or n.startswith('F0_DRUM')]
 finger=[n for n in s if n.startswith('F0_') and n not in drive and not n.startswith(('F0_RF','F0_TENDON'))]
 stages=[('finger_lift_slide_lower',finger,[(-v,0,0) for v in (80,40,20,14)]+[(-14,0,z) for z in (1,2,3)]+[(-v,0,3) for v in (10,3,1,0)]+[(0,0,z) for z in (2,1,0)]),('drive_vertical',drive,[(0,0,v) for v in (80,30,12,6,3,1,0)]),('cap_vertical',['MOTOR_CAP'],[(0,0,v) for v in (80,30,12,6,3,1,0)])]
 rows=[];assemblyhits=[];comparisons=0
 for stage,names,poses in stages:
  for shift in poses:
   assert not (ROOT/'runtime/STOP').exists();local=[]
   for n in names:
    q=translate(s[n],*shift);qb=bounds(q)
    for m in fixed:
     if overlap(qb,bb[m]):
      comparisons+=1;v=common(q,s[m])
      if v>1e-8:local.append(dict(moving=n,fixed=m,common_mm3=v))
   rows.append(dict(stage=stage,shift_mm=shift,hits=local));assemblyhits.extend(local)
  fixed+=names
 # Root fasteners installed after lateral insertion; tools pass through real roof/ground holes.
 for n in [n for n in s if n.startswith('F0_RF') or n.startswith('MOTOR_CAP_BOLT') or n.startswith('MOTOR_CAP_NUT')]:
  nut='NUT' in n;poses=(20,10,3,1,0) if not nut else (-20,-10,-3,-1,0)
  for dz in poses:
   assert not (ROOT/'runtime/STOP').exists();q=translate(s[n],0,0,dz);local=[]
   for m in fixed:
    if overlap(bounds(q),bb[m]):
     comparisons+=1;v=common(q,s[m])
     if v>1e-8:local.append(dict(moving=n,fixed=m,common_mm3=v))
   rows.append(dict(stage='fastener_'+n,shift_mm=[0,0,dz],hits=local));assemblyhits.extend(local)
  fixed.append(n)
 # Smooth tool approach to existing RF head top, intended head excluded.
 tools=[]
 for y in (-16,16):
  q=cyl(1.5,(64,y,0),60);hits=[]
  for n in s:
   if n.startswith(('F0_RF','GROUND_BOLT','GROUND_NUT')):continue
   if overlap(bounds(q),bb[n]):
    v=common(q,s[n])
    if v>1e-8:hits.append(dict(part=n,common_mm3=v))
  tools.append(dict(tool='RF_driver_'+str(y),radius_mm=1.5,hits=hits))
 # Direct route across actual rigid parts; flexible bodies excluded explicitly.
 motion=[];motionhits=[];g0=route(0);P0=g0['P'];b0=g0['b']
 for deg in (0,15,30,45,60):
  g=route(deg);dvec=g['E']-g['Q'];wire=cyl(.25,tuple(g['Q']),float(np.linalg.norm(dvec)),tuple(dvec/np.linalg.norm(dvec)));hits=[]
  for n,x in s.items():
   if n.endswith(('SKIN','RAIL_L','RAIL_R')) or n=='F0_TENDON_WIRE':continue
   if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')):
    rr=Ry(g['b']-b0);x=tr(x,rr,g['P']-rr@P0)
   elif 'TERMINAL' in n or n.startswith(('F0_SWIVEL_AXLE','F0_SWIVEL_SLEEVE','F0_SWIVEL_SPACER')):x=tr(x,g['r'],g['shift'])
   if overlap(bounds(wire),bounds(x)):
    v=common(wire,x)
    if v>1e-8:hits.append(dict(part=n,common_mm3=v))
  motion.append(dict(angle_deg=deg,straight_tendon_hits=hits));motionhits.extend(hits)
 facts=json.loads((ROOT/'models/standard_drive/batch6_sources1/reviewed.json').read_text());old=json.loads((ROOT/'validation/transmission/batch6_operating1/summary.json').read_text());k=old['conditional_rotational_stiffness_Nm_rad']*1000 # Nmm/rad
 stall=facts['motor']['extrapolated_stall_torque_kgcm']*.0980665;rowsload=[];derrs=[];loops=[]
 def inward(deg):
  a=math.radians(deg);g=route(deg);end=g['r']@np.array([50.,0,-100.])+g['shift'];return 50-end[0]
 for deg in range(0,61):
  g=route(deg);ds=-derivative(lambda x:route(x)['free'],deg);dx=derivative(inward,deg);ds2=-derivative(lambda x:route(x)['free'],deg,5e-4)
  derrs.append(abs(ds-ds2)/max(abs(ds),1e-30))
  for mu in (.2,.4,.8):
   N=.1*9.80665/(3*mu);T=(N*dx+k*math.radians(deg))/ds;tau=T*.01125
   speed_required_rpm=ds*(math.pi/3)/11.25*60/(2*math.pi) # 60deg per second design scenario
   current=.1+1.5*tau/stall;rpm=310*(1-tau/stall)
   F=T*g['t'];R=np.array([50.4,0,-7]);C=np.array([0.,0,20.]);mr=np.cross(g['P']-R,F);mm=np.cross(g['Q']-C,-F)
   loop=np.cross(R,F)+mr+np.cross(C,-F)+mm
   loops.append(float(np.linalg.norm(loop)))
   rowsload.append(dict(angle_deg=deg,mu_assumed=mu,normal_per_finger_N=N,stroke_mm=g0['free']-g['free'],stroke_derivative_mm_rad=ds,inward_derivative_mm_rad=dx,conditional_tension_N=T,conditional_torque_Nm=tau,ideal_linear_current_A=current,ideal_available_rpm=rpm,required_rpm_1s=speed_required_rpm,current_general_recommendation_screen=bool(current<=.4),speed_screen=bool(rpm>=speed_required_rpm),root_tendon_only_force_N=F.tolist(),root_tendon_only_moment_Nmm=mr.tolist(),motor_body_force_N=(-F).tolist(),motor_body_couple_Nmm=mm.tolist(),root_tendon_moment_divided_by_14mm_N=abs(mr[1])/14,warning='Tendon-only local load loop, excludes actual object-contact/body equilibrium.Moment divided by14mm is a dimensional diagnostic, NOT a bolt or contact reaction.'))
 checks=dict(all_reimported_single_valid_solids=all(valid.values()),nominal_final_no_volume_interference=not final,sampled_ordered_assembly_clear=not assemblyhits,RF_tool_approach_clear=all(not t['hits'] for t in tools),five_pose_straight_route_clear=not motionhits,positive_inward_stroke_all61=all(x['stroke_derivative_mm_rad']>0 for x in rowsload),derivative_refinement=max(derrs)<1e-6,tendon_loop_moment_balance=max(loops)<1e-8,finite_positive_conditional_demand=all(math.isfinite(x['conditional_tension_N']) and x['conditional_tension_N']>0 for x in rowsload))
 checks={k:bool(v) for k,v in checks.items()}
 dump(out/'assembly.json',dict(stages=rows,comparisons=comparisons,hits=assemblyhits,tools=tools,partition=dict(finger=finger,drive=drive),limitations=['Finite samples only, no continuous CCD','Cable threading, finite wire bends and nipple installation sequence not certified','Smooth hardware envelopes do not verify actual thread assembly/tightening','Finger module inner assembly reuses prior geometry, not newly manufactured evidence']))
 dump(out/'loads.json',dict(rows=rowsload,derivative_relative_error_max=max(derrs),tendon_loop_moment_error_Nmm_max=max(loops),conditional_rotational_stiffness_Nmm_rad=k,stroke_mm=route(0)['free']-route(60)['free'],minimum_stroke_derivative_mm_rad=min(x['stroke_derivative_mm_rad'] for x in rowsload),tension_range_N=[min(x['conditional_tension_N'] for x in rowsload),max(x['conditional_tension_N'] for x in rowsload)],current_screen_failures=sum(not x['current_general_recommendation_screen'] for x in rowsload),speed_screen_failures=sum(not x['speed_screen'] for x in rowsload),normal_load_basis='100g weight shared by three future identical fingers with unmeasured mu .2/.4/.8; not single-finger100g or verified grasp',uncertainty='Typical curvature stiffness only; no finite coupled equilibrium, material minima, losses, inertia or friction lower bound. Stall is not protected peak or capacity.',source=ref(ROOT/'models/standard_drive/batch6_sources1/reviewed.json')))
 unmet=json.loads((ROOT/'validation/finger/batch6_wide_cycle1/summary.json').read_text())['remaining_system_gate_ids']
 result=dict(status='PRIMARY_PRODUCT_PARTIAL_SCREEN_PASS' if all(checks.values()) else 'PRIMARY_PRODUCT_VALIDATION_FAIL',task_id='goal_primary_gravity_port_interfaces',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(s),checks=checks,invalid_solids=[n for n,v in valid.items() if not v],final_interferences=final,final_exact_pairs=pairs,assembly=ref(out/'assembly.json'),loads=ref(out/'loads.json'),route_motion=motion,remaining_system_gate_ids=unmet,newly_qualified_system_gate_ids=[],whole_system_release=False,capacity_qualified=False,SOFA_runs=0,next_mechanism='Complete same-primary cable anchor threading/bend/retention and motor axial-support interfaces; actual coupled finite Finger demand and connector reactions before strength/protection closure. Preserve conditional motor current failures.')
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,assemblyhits=assemblyhits,tools=tools,motionhits=motionhits)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
