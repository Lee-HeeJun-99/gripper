"""Same P1 integralguide width4.0->4.1mm;earlier positive yawtakeup.
New actual receiver solid,remaining127parts preserved;manufacturing allowance unqualified.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
out=ROOT/'cad/exports/primaryP1_guide53';assert not(ROOT/'runtime/STOP').exists();out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide52/summary_corrected.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),old['assembly'],old['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};rail=parts['BENCH_ANCHOR_RAIL']
for y in [-58.,39.]:rail=fuse(rail,box(-78.05,y-3,50,4.1,6,20))
rail=canonical(rail);export(rail,out/'BENCH_ANCHOR_RAIL');parts['BENCH_ANCHOR_RAIL']=read(out/'BENCH_ANCHOR_RAIL.step');refs['BENCH_ANCHOR_RAIL']=ref(out/'BENCH_ANCHOR_RAIL.step');changed=[dict(part_ID='BENCH_ANCHOR_RAIL',STEP=refs['BENCH_ANCHOR_RAIL'],STL=ref(out/'BENCH_ANCHOR_RAIL.stl'),valid=bool(BRepCheck_Analyzer(parts['BENCH_ANCHOR_RAIL']).IsValid()),solids=solid_count(parts['BENCH_ANCHOR_RAIL']),volume_mm3=volume(parts['BENCH_ANCHOR_RAIL']),parent=old['part_references']['BENCH_ANCHOR_RAIL'])];bb={n:bounds(s) for n,s in parts.items()};hits=[];queries=[]
for n,s in parts.items():
 if n=='BENCH_ANCHOR_RAIL' or not overlap(bb[n],bb['BENCH_ANCHOR_RAIL']):continue
 assert not(ROOT/'runtime/STOP').exists()
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',pair=['BENCH_ANCHOR_RAIL',n]))+'\n')
 v=common(parts['BENCH_ANCHOR_RAIL'],s);row=dict(state='COMPLETE',a='BENCH_ANCHOR_RAIL',b=n,common_mm3=v);queries.append(row)
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 if abs(v)>1e-8:hits.append(row)
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_guide53'
for r in bom['parts']:
 r['STEP']=refs[r['part_ID']]
 if r['part_ID']=='BENCH_ANCHOR_RAIL':r.update(interface='Integral4.1x6mmguidetongues inunchanged4.2x6.2mmopenmortises;nominal.05mmXsidegap,.1mmYsidegap;6mmwalloverlap;actualmachining/tolerancesNOTqualified')
dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),tongue_x_mm=[-78.05,-73.95],tongue_y_centres_mm=[-58,39],tongue_z_mm=[50,70],slot_x_mm=[-78.1,-73.9],actual_vertical_overlap_mm=6,sidegap_X_mm=.05,sidegap_Y_mm=.1,mechanism='Earlier yawbearing before old finitepose pincollision;not strength/tolerance PASS',standardparts_preserved=127,minimum_material_MPa=None,capacity_N=None))
d=dict(old);d.update(revision='primaryP1_guide53',status='ACTUAL_P1_EARLIER_GUIDE_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 'ACTUAL_P1_EARLIER_GUIDE_GEOMETRY_FAIL',parent=ref(cp),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),changed=changed,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),part_bounds_mm=bb,interferences=hits,exact_pairs=len(queries),unchanged_part_STEP_count=127,design_change='SameprimaryP1singleintegralreceiverguidewidth4.0to4.1mm;nominalXsidegap.05mm;noadditionalhardware',not_qualified=old['not_qualified']+['Earlierguide finitecontact/pin/clearance/force/pressure/material/process/tolerance notyetqualified;allphysicalgatesunchanged']);dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=changed,queries=len(queries),hits=hits)),flush=True);raise SystemExit(0 if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 2)
