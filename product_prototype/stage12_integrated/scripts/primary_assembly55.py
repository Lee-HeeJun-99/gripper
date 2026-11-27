"""Independent actual111part P1 identity, continuous addedweb and ordered assembly.
Finite wholepart samples distinguished from exact addedmaterial vertical sweep.
"""
import json,sys,shutil,time,os,itertools,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,translate,common,bounds,overlap,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
from primary_motor_bearing_wrenches import faces
from primary_anchor_contact38 import common_faces,surface_moment
out=ROOT/'validation/integrated/primaryP1_assembly55';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_integral55b/summary.json';cad=json.loads(cp.read_text());old=json.loads((REPO/cad['parent']['path']).read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(v) for n,v in s.items()};poses=[];queries=[]
def journal(r):
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
def hits(shape,others,label):
 b=bounds(shape);result=[]
 for n in others:
  if not overlap(b,bb[n]):continue
  assert not(ROOT/'runtime/STOP').exists();t=time.monotonic();journal(dict(state='START',operation=label,other=n));v=common(shape,s[n]);r=dict(state='COMPLETE',operation=label,other=n,intersection_mm3=v,elapsed_s=time.monotonic()-t);journal(r);queries.append(r)
  if abs(v)>1e-8:result.append(r)
 return result
late=[n for n in s if n.startswith(('SOCKET_KEEPER_','KEEPER_PIN_','KEEPER_NUT_'))];upper=[n for n in s if n not in late and n!='BENCH_SUPPORT' and n!='EXTERNAL_BENCH_PLATE' and not n.startswith(('BENCH_THROUGH_','ANCHOR_'))]
# Offbench support lowered OVER already assembled payload, then anchor hardware
# and retained late keepers. Do not lower payload through closedreceiverroof.
for dz in [25.,10.,3.2,1.,.2,0.]:
 label='offbench_integral_support_lowering_'+str(dz);poses.append(dict(operation=label,translation_mm=[0,0,dz],moving=['BENCH_SUPPORT'],stationary=upper,hits=hits(translate(s['BENCH_SUPPORT'],0,0,dz),upper,label)))
# Entire rigid payload+support is only an assembly placement, NEVER a physics tie.
for dz in [20.,10.,5.,1.,.2,0.]:
 for n in [x for x in s if not x.startswith('BENCH_THROUGH_') and x!='EXTERNAL_BENCH_PLATE']:
  label='complete_module_onto_referencehost_'+str(dz)+'_'+n;posed=translate(s[n],0,0,dz)
  if overlap(bounds(posed),bb['EXTERNAL_BENCH_PLATE']):poses.append(dict(operation=label,moving=[n],stationary=['EXTERNAL_BENCH_PLATE'],translation_mm=[0,0,dz],hits=hits(posed,['EXTERNAL_BENCH_PLATE'],label)))
# Retained original anchor fasteners/keepers installed AFTER new support lowering.
for i in range(3):
 for typ,zs in [('BOLT',[-25,-10,-2,0]),('NUT',[25,10,2,0])]:
  n=f'ANCHOR_{typ}_{i}';others=upper+['BENCH_SUPPORT']
  for dz in zs:
   label=f'{n}_axial_approach_without_matinghardware_{dz}';poses.append(dict(operation=label,hits=hits(translate(s[n],0,0,dz),others,label)))
 for typ,axis,amounts in [('SOCKET_KEEPER',2,[-30,-15,-8,-4,-1,0]),('KEEPER_PIN',0,[-20,-17,-10,-4,-1,0]),('KEEPER_NUT',0,[20,10,5,1,0])]:
  n=f'{typ}_{i}';omit={n}
  if typ=='SOCKET_KEEPER':omit|={f'KEEPER_PIN_{i}',f'KEEPER_NUT_{i}'}
  if typ=='KEEPER_PIN':omit|={f'KEEPER_NUT_{i}'}
  others=[x for x in s if x not in omit and not x.startswith('BENCH_THROUGH_') and x!='EXTERNAL_BENCH_PLATE'];
  for amount in amounts:
   d=np.zeros(3);d[axis]=amount;label=f'{n}_late_approach_{amount}';poses.append(dict(operation=label,hits=hits(translate(s[n],*d),others,label)))
# Old reviewed tool bounding corridors;exact fulltool/rotation notcertified.
for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
 for label,tool in [('4AF_driver_enclosure',cyl(2.5,(x,y,20),37.5)),('8AF_openhead_enclosure',cyl(9.5,(x,y,74),4.7))]:
  others=[n for n in s if n not in [f'ANCHOR_BOLT_{i}',f'ANCHOR_NUT_{i}']];poses.append(dict(operation=f'anchor{i}_{label}',hits=hits(tool,others,label)))
sections=[];sweeps=[]
for x,y in [(-59,-58),(101,-58),(-59,39),(101,39)]:
 x0,x1=(x-7,x+4.8) if x<0 else (x-4.8,x+7);slab=box(x0-.01,y-5.01,67.9995,x1-x0+.02,10.02,.001);area=common(s['BENCH_SUPPORT'],slab)/.001;sections.append(dict(center_mm=[x,y,68],measured_area_mm2=area,analytic_area_mm2=118-math.pi*2.75**2,minimum_nominal_bore_ligament_mm=2.05))
 # Continuous vertical sweep of entire addedweb from0to25mm. Ancestor material
 # assembly is separatefiniteposes; this exactprism DOES NOT certify allpartsCCD.
 web=cut(box(x0,y-5,60,x1-x0,10,39),cyl(2.75,(x,y,59),41));label=f'continuous_addedweb_sweep_{x}_{y}';sweeps.append(dict(label=label,motion_mm=[0,0,25],hits=hits(web,upper,label)))
# Nonzero volumetric intersections with both parentbodies prove real continuous
# material construction,not merefacecoincidence or declaredrigidtie.
ps=read(REPO/old['part_references']['BENCH_SUPPORT']['path']);pr=read(REPO/old['part_references']['BENCH_ANCHOR_RAIL']['path']);connect=[]
for x,y in [(-59,-58),(101,-58),(-59,39),(101,39)]:
 x0,x1=(x-7,x+4.8) if x<0 else (x-4.8,x+7);web=cut(box(x0,y-5,60,x1-x0,10,14),cyl(2.75,(x,y,59),16));connect.append(dict(center_xy_mm=[x,y],overlap_parent_stand_mm3=common(web,ps),overlap_parent_receiver_mm3=common(web,pr)))
checks=dict(actual111parts=len(s)==111,unchanged110STEP=sum(refs.get(n)==r for n,r in old['part_references'].items())==110,allpartsvalidsingle=all(BRepCheck_Analyzer(sh).IsValid() and solid_count(sh)==1 for sh in s.values()),assembly111solids=solid_count(read(REPO/cad['assembly']['path']))==111,BOMmatches={r['part_ID']:r['STEP'] for r in json.loads((REPO/cad['BOM']['path']).read_text())['parts']}==refs,finite_ordered_assembly=all(not r['hits'] for r in poses),continuous_addedweb_sweeps=all(not r['hits'] for r in sweeps),actual_bridge_sections=all(abs(r['measured_area_mm2']/r['analytic_area_mm2']-1)<1e-7 for r in sections),real_continuous_material=all(r['overlap_parent_stand_mm3']>1 and r['overlap_parent_receiver_mm3']>1 for r in connect))
dump(out/'summary.json',dict(status='ACTUAL_P1_INTEGRAL111PART_ORDERED_ASSEMBLY_AND_CONTINUOUS_ADDEDWEB_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_INTEGRAL111PART_ORDERED_ASSEMBLY_OR_CONTINUOUS_WEB_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks={k:bool(v) for k,v in checks.items()},actual_parts=111,unchanged_part_STEP_count=110,removed_part_IDs=cad['removed_part_IDs'],poses=poses,queries=len(queries),sections=sections,continuous_addedweb_sweeps=sweeps,material_connections=connect,maximum_intersection_mm3=max(abs(r['intersection_mm3']) for r in queries),failed_poses=[r for r in poses if r['hits']],newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Finitewholebody approachsamples plus exact addedwebverticalsweeps,NOT fullcontinuousassemblyCCD','Individualexistinguppermodulebuild/actualtendonoperation/Rootcartridgeprocess notrecertified;retainedgeometryonly','Existinganchor-nut axial approach is pre-engagement toolclearanceONLY;threadedscrew-inlaw/preload/locking notcertified','LowerBENCH_THROUGH sourceparts unchanged;actualhelicalassembly/pinforming/retention/hostloadclosure stillUNQUALIFIED','NewONEbillet manufacturingintent needs stock/toolsetup/tolerance/certifiedmaterial andnotchstrength;all22criteriaunchanged']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},poses=len(poses),queries=len(queries),failed=[r for r in poses if r['hits']],sections=sections)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
