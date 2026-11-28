"""Same primary77parts: source-dimensioned real socket drive in six retained M3 heads."""
import sys,json,shutil,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cut,canonical,export,bounds,volume,solid_count
from build_stage1 import compound
from primary_captive59b import hexz
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
out=ROOT/'cad/exports/primaryP1_captive59c';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_captive59b/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};spec=json.loads((REPO/old['cages']['path']).read_text())['specifications'];rows=[]
for q in spec:
 assert not(ROOT/'runtime/STOP').exists();n=q['bolt'];bb=bounds(parts[n]);ztop=bb[5];parts[n]=canonical(cut(parts[n],hexz(q['x'],q['y'],ztop-1.3,2.5,1.4)));export(parts[n],out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'][n],valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),socket_AF_mm=2.5,socket_depth_mm=1.3,head_remaining_floor_mm=1.7))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_captive59c'
for q in bom['parts']:
 q['STEP']=refs[q['part_ID']]
 if q['part_ID'] in [s['bolt'] for s in spec]:q['interface']='ISO4762 M3 retainedshanklength12Root/22Cap, nominalheadD5.5H3 real2.5AFx1.3deep socket. Threadflanks/chamfer/runout/tolerances/grade/minimumstrength/preload NOTqualified. Geometrydimensions only; no materialrating transferred from dimensioncatalogue.'
dump(out/'BOM.json',bom);inputs=dict(parent=ref(cp),original_primary=old['parent'],producer=ref(out/'producer.py'),source=ref(ROOT/'models/standard_drive/primary_captive_sources59/socket_reviewed.json'),cages=old['cages'],mechanism='Continue SAME77part P1: retained6M3 bolts now have realnominal2.5AF/1.3mmdeep socket drive, plus prior new6integralcages/fourstandardhexnuts. All shank/head bearing datums unchanged. No actualthread/preload/lock orgradecertification.',dependencies=[ref(ROOT/'scripts/primary_captive59b.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],criteria_unchanged=True,material_minimum_MPa=None,hardware_status='NOT_MEASURED');dump(out/'inputs.json',inputs)
d=dict(old);d.update(revision='primaryP1_captive59c',parent=ref(cp),part_references=refs,part_bounds_mm={n:bounds(s) for n,s in parts.items()},assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),changed=old['changed']+rows,unchanged_part_STEP_count=66,status='ACTUAL_P1_CAGE_AND_SOCKET11_SOLID_CHANGES_NOT_RELEASE',interferences=None,exact_pairs=None,design_change='ONE77partP1:6open-bottomintegralnutcages+4actualstandarddimensionhexnutsolids+6actualstandarddimensionsocketbolts. Freshsame-revisionassembly/load/auditrequired. OriginalfailedAO preserved.');dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],sockets=rows)));raise SystemExit(0 if all(r['valid'] and r['solids']==1 for r in rows) else 2)
