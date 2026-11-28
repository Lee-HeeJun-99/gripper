"""Actual lower M5 assembly/support gauge on same P1 feet specimen.
Nominal proposed removable annular nut pusher and4mmAF driver access gauges.
No supplier handle/torque/ergonomic or actual threaded tightening certification.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,common,bounds,overlap,translate,export
from primary_captive59b import hexz
from primary_clocked62 import spin
from OCP.BRepCheck import BRepCheck_Analyzer
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/q['path'])==q['SHA256'] for q in cad['part_references'].values());parts={n:read(REPO/q['path']) for n,q in cad['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};floor=-170.;stations=[(-65,-35),(107,-35),(-65,15),(107,15)];rows=[];gauges=[]
def hits(s,excluded=()):
 b=bounds(s);r=[]
 for n,p in parts.items():
  if n in excluded or not overlap(b,bb[n]):continue
  assert not(ROOT/'runtime/STOP').exists();v=common(s,p)
  if v>1e-8:r.append(dict(part_ID=n,intersection_mm3=v))
 return r
for i,(x,y) in enumerate(stations):
 nut=parts['BENCH_THROUGH_NUT_'+str(i)];bolt=parts['BENCH_THROUGH_BOLT_'+str(i)];poses=[]
 # Nuts are supported before insertion of bolts, socket keys and retaining pins.
 absent=[n for n in parts if n.startswith(('BENCH_THROUGH_BOLT','BENCH_THROUGH_SOCKET_KEY','BENCH_THROUGH_SPLIT_PIN'))]+['BENCH_THROUGH_NUT_'+str(i)]
 for dz in [-20,-15,-10,-5,-2,-1,0]:
  q=translate(nut,0,0,dz);poses.append(dict(nut_shift_z_mm=dz,bottom_mm=bounds(q)[2],floor_clearance_mm=bounds(q)[2]-floor,hits=hits(q,absent)))
 # Removable annular pusher: bore clears actual final protruding M5, outside fits8.2AFpocket.
 # Constantposition while driver tightens; not an actual measured tool/sourcepart.
 tube=cut(cyl(3.9,(x,y,-162.7),20),cyl(2.8,(x,y,-162.8),20.2));export(tube,out/('ANNULAR_NUT_PUSHER_'+str(i)));ar=common(nut,translate(tube,0,0,.01))/.01
 pusher_hits=hits(tube);approach=[]
 for dz in [-7,-5,-2,0]:
  q=translate(tube,0,0,dz);approach.append(dict(shift_z_mm=dz,floor_clearance_mm=bounds(q)[2]-floor,hits=hits(q)))
 # Hex4 socket needs tool clearance;3.9AF is explicit insertion gauge rather than supplier tool.
 key=hexz(x,y,-121.35,3.9,62.);export(key,out/('M5_DRIVER_ACCESS_'+str(i)));top_absent=[n for n in parts if n.startswith(('BENCH_THROUGH_SOCKET_KEY','BENCH_THROUGH_SPLIT_PIN'))]
 top=[]
 for dz in [0,1,5,15,30]:
  q=translate(key,0,0,dz);top.append(dict(shift_z_mm=dz,hits=hits(q,top_absent)))
 # Keepers must really be removed for access. Check intended actual obstruction separately.
 installed_hits=hits(key);rows.append(dict(station=i,nut_path=poses,pusher_contact_area_probe_mm2=ar,pusher_final_hits=pusher_hits,pusher_approach=approach,top_driver_path=top,driver_hits_when_keys_installed=installed_hits,tool_minimum_strength=None,measured_tightening_torque=None))
 gauges.extend([dict(kind='proposed_removable_nut_pusher',STEP=ref(out/('ANNULAR_NUT_PUSHER_'+str(i)+'.step')),STL=ref(out/('ANNULAR_NUT_PUSHER_'+str(i)+'.stl'))),dict(kind='hex_socket_access_gauge_NOT_supplier_driver',STEP=ref(out/('M5_DRIVER_ACCESS_'+str(i)+'.step')),STL=ref(out/('M5_DRIVER_ACCESS_'+str(i)+'.stl')))])
checks=dict(all83_identity=True,all_nut_paths_clear_before_bolt_installation=all(not p['hits'] and p['floor_clearance_mm']>0 for r in rows for p in r['nut_path']),annular_pusher_clear_actual_final_bolts=all(not r['pusher_final_hits'] for r in rows),pusher_has_actual_annular_nut_contact=all(r['pusher_contact_area_probe_mm2']>1 for r in rows),annular_pusher_approach_above_floor_clear=all(not p['hits'] and p['floor_clearance_mm']>0 for r in rows for p in r['pusher_approach']),top_driver_path_before_keeper_clear=all(not p['hits'] for r in rows for p in r['top_driver_path']),installed_keeper_obstruction_control_rejects=all(any(p['part_ID'].startswith('BENCH_THROUGH_SOCKET_KEY') for p in r['driver_hits_when_keys_installed']) for r in rows))
result=dict(status='SAME_P1_LOWER_M5_NUT_SUPPORT_AND_TOOL_GAUGE_CLEAR_NOT_THREAD_PROCESS' if all(checks.values()) else 'SAME_P1_LOWER_M5_TOOL_OR_NUT_SUPPORT_GEOMETRY_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),checks=checks,rows=rows,temporary_assembly_gauges=gauges,gauges_are_product_parts=False,product_part_count=83,actual_ground_floor_z_mm=floor,minimum_existing_product_floor_clearance_mm=min(b[2]-floor for n,b in bb.items() if n!='EXTERNAL_BENCH_PLATE'),newly_qualified_system_gate_ids=[],whole_system_release=False,hardware='NOT_MEASURED',limitations=['Sampled finite wholetool/nut paths,notCCD. Removable pusher isreal proposedCADtool with nominal contactprobe; notmanufactured/certifiedsuppliertoolorhandgrip.','Nut isexplicitlysupported byannularpusher beforeboltengagement; no frictionhold/floatingnut fixation assumed. Nutrotation/pocketplay/finitehelicalthreadcontact and actual tighteningtorque/preload unsolved.','Driver3.9AF insertiongauge isnot exact4mmAFtooltolerance orhandle/torqueminimum; keepers must beinstalledAFTER tightening. No physicalprocessrelease.','Source-minimum material/strength,floorfriction/flatness,upperkeepercontact and83bodyoperatingequilibrium remainUNQUALIFIED.'])
dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
