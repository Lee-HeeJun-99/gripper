"""Independent actual STEP audit: socket clearance/takeup, index lead, pin corridors.
All contacts retain clearance; no torque/preload/axial retention is invented.
"""
import sys,json,shutil,math,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,overlap,bounds,volume,solid_count,translate,box,cyl
from build_stage1 import rotate
from OCP.BRepCheck import BRepCheck_Analyzer
from primary_captive59b import hexz
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_keeper60c/summary.json';cad=json.loads(cp.read_text());parts={n:read(REPO/r['path']) for n,r in cad['part_references'].items()};anchors=json.loads((REPO/cad['anchors']['path']).read_text())['groups'];old=json.loads((REPO/cad['parent']['path']).read_text());rows=[];tools=[];pinrows=[]
for g in anchors:
 assert not(ROOT/'runtime/STOP').exists();kn=g['name'];keeper=parts[kn]
 for y in g['ys']:
  bn=next(n for n in parts if (n.startswith('F0_RF') if g['name'].startswith('ROOT') else n.startswith('MOTOR_CAP_BOLT')) and abs((bounds(parts[n])[0]+bounds(parts[n])[3])/2-g['x'])<1e-6 and abs((bounds(parts[n])[1]+bounds(parts[n])[4])/2-y)<1e-6)
  bolt=parts[bn];lo=0.;hi=10.
  def displaced(deg):return translate(rotate(bolt,(g['x'],y,0),(0,0,1),deg),0,0,.5*deg/360)
  assert common(keeper,displaced(lo))<1e-8 and common(keeper,displaced(hi))>1e-8
  for i in range(20):
   mid=(lo+hi)/2
   if common(keeper,displaced(mid))>1e-8:hi=mid
   else:lo=mid
  rows.append(dict(bolt=bn,keeper=kn,head_loosen_contact_bracket_deg=[lo,hi],screw_lead_bracket_mm=[.5*lo/360,.5*hi/360],max_nearest_60deg_setting_error_mm=.5/12,max_backoff_only_setting_error_mm=.5/6,socket_initial_overlap_mm3=common(keeper,bolt),engagement_nominal_mm=1.25,engagement_after_max_oneway_index_and_takeup_mm=1.25-.5/6-.5*hi/360,contact_capacity_Nmm=None,actual_preload_N=None))
  top=g['headtop'];tool=hexz(g['x'],y,top-1.3,2.5,90-top+1.3);hits=[]
  for n,s in parts.items():
   if 'SOCKET_KEEPER' in n:continue # Correct assembly order: tighten BEFORE installing all keeper/pins.
   if overlap(bounds(tool),bounds(s)):
    v=common(tool,s)
    if v>1e-8:hits.append(dict(part=n,intersection_mm3=v))
  tools.append(dict(bolt=bn,hits_before_keeper_install=hits,after_install_tool_blocked=common(tool,keeper)>1e-8))
 # Entire axial shaft/eye approach swept volume along selected direction.
 # Cylinder eye bound encloses supplier EW<=1.8, EL<=3, not actual bent legs.
 start=np.array(g['pin_start']);axis=np.array(g['pin_axis']);direction=1 if kn=='CAP_SOCKET_KEEPER_7' else -1;tip=start+axis*(10 if direction==1 else 0);eye_start=tip if direction==1 else tip-axis*3
 eye=cyl(.9,tuple(eye_start),3,tuple(axis));eye_swept=cyl(.9,tuple(eye_start if direction==1 else eye_start-axis*20),23,tuple(axis));shaft_start=start if direction==1 else start-axis*20;shaft_swept=cyl(.45,tuple(shaft_start),30,tuple(axis));hits=[]
 for n,s in parts.items():
  if n==g['pin']:continue
  for label,q in [('shaft_continuous_20mm',shaft_swept),('eye_bound_continuous_20mm',eye_swept)]:
   if overlap(bounds(q),bounds(s)):
    v=common(q,s)
    if v>1e-8:hits.append(dict(part=n,bound=label,intersection_mm3=v))
 pinrows.append(dict(pin=g['pin'],insertion_axis=axis.tolist(),insertion_direction=direction,nominal_pin_shaft_mm=.9,eye_bound_diameter_mm=1.8,eye_bound_length_mm=3,hits=hits,installed_bent_legs_verified=False,source_minimum_strength_MPa=None))
# Preserve original geometry functions and prove two bodies are actually changed.
changes=[]
for n in ['F0_ROOT_BACK','MOTOR_CAP']:
 parent=read(REPO/old['part_references'][n]['path']);v=common(parent,parts[n]);changes.append(dict(part=n,removed_parent_mm3=volume(parent)-v,added_mm3=volume(parts[n])-v,source_parent=old['part_references'][n]))
checks=dict(canonical83=len(parts)==83 and all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]),eight_new_single_solids=all(solid_count(parts[q['part_ID']])==1 and BRepCheck_Analyzer(parts[q['part_ID']]).IsValid() for q in cad['changed']),two_actual_host_solid_changes=all(r['added_mm3']>1 and r['removed_parent_mm3']>.1 for r in changes),six_socket_takeup_bracketed=len(rows)==6 and all(r['head_loosen_contact_bracket_deg'][0]>0 for r in rows),six_torque_tools_clear_before_keepers=len(tools)==6 and all(not q['hits_before_keeper_install'] and q['after_install_tool_blocked'] for q in tools),continuous_shaft_and_source_eye_bounds_clear=all(not q['hits'] for q in pinrows))
dump(out/'summary.json',dict(status='ACTUAL83_KEEPER_GEOMETRY_TAKEUP_AND_SOURCE_ENVELOPE_AUDIT_LOCAL_PASS_NOT_RETENTION_OR_PRELOAD' if all(checks.values()) else 'ACTUAL83_KEEPER_GEOMETRY_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},screw_results=rows,tools=tools,pin_corridors=pinrows,actual_changed_host_volumes=changes,actual_pin_retention=False,split_pin_solid_implemented=False,finite_contact_elasticity_solved=False,full_system_contact_equilibrium=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,next_mechanism='Resolve actual60deg indexing/preload and installedsplit-pin eye/bentlegs before force certification. Socketclearance contact onset is not finite-area capacity; keeper/tongue/pin/bore/host compliance and all physicalDOFs must be solved.'))
print((out/'summary.json').read_text());raise SystemExit(0 if all(checks.values()) else 2)
