"""P1 same product: remove unnecessary detachable receiver/support interface.
One continuous machinable-support intent, NOT a weld, rigid tie or qualified process.
"""
import json,sys,shutil,csv,os,time
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
TAG='primaryP1_integral55c'
def main():
 out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide53/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert not(ROOT/'runtime/STOP').exists();assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),old['assembly'],old['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()}
 removed=[n for n in parts if n.startswith(('BENCH_MOUNT_','ANCHOR_','SOCKET_KEEPER_','KEEPER_PIN_','KEEPER_NUT_','FIXTURE_BOLT_','FIXTURE_NUT_','GROUND_BOLT_','GROUND_NUT_'))];assert len(removed)==47
 merged=['BENCH_ANCHOR_RAIL','TEST_BASE','GROUND_PLATE','OPEN_FRAME']
 # Four annular rectangular webs traverse the actual4mm airgap and overlap
 # both retained bodies by6/4mm. Old clearance bores remain open.
 bridges=[];support=parts['BENCH_SUPPORT']
 for x,y in [(-59,-58),(101,-58),(-59,39),(101,39)]:
  x0,x1=(x-7,x+4.8) if x<0 else (x-4.8,x+7)
  b=cut(box(x0,y-5,60,x1-x0,10,14),cyl(2.75,(x,y,59),16));bridges.append(b);support=fuse(support,b)
 
 for n in merged:support=fuse(support,parts[n])
 support=canonical(support);export(support,out/'BENCH_SUPPORT');support=read(out/'BENCH_SUPPORT.step')
 for n in removed+merged:del parts[n];del refs[n]
 parts['BENCH_SUPPORT']=support;refs['BENCH_SUPPORT']=ref(out/'BENCH_SUPPORT.step');bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for n,s in parts.items():
  if n=='BENCH_SUPPORT' or not overlap(bb[n],bb['BENCH_SUPPORT']):continue
  assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',pair=['BENCH_SUPPORT',n],operation='changed_actual_solid_intersection'))+'\n');f.flush();os.fsync(f.fileno())
  v=common(s,support);row=dict(state='COMPLETE',pair=['BENCH_SUPPORT',n],intersection_mm3=v,elapsed_s=time.monotonic()-t);queries.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 hits=[r for r in queries if abs(r['intersection_mm3'])>1e-8];valid=bool(BRepCheck_Analyzer(support).IsValid());solids=solid_count(support)
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG;bom['parts']=[r for r in bom['parts'] if r['part_ID'] in parts]
 for r in bom['parts']:
  r['STEP']=refs[r['part_ID']]
  if r['part_ID']=='BENCH_SUPPORT':r.update(interface='Single continuous OPEN_FRAME+GROUND_PLATE+TEST_BASE+receiver+stand, four11.8x10mm annular webs around retained5.5mm bores; no detachable mount thread/contact. CNC from ONE billet intent, NOT weld or bonded/tied assembly.',material='6061-T6 CONDITIONAL typical elastic reference only; material minimum, stock size, access, residual stress/process/tolerances UNQUALIFIED')
 dump(out/'BOM.json',bom)
 with (out/'identity_BOM55.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['part_ID','STEP_path','STEP_SHA256']);writer.writerows((n,r['path'],r['SHA256']) for n,r in sorted(refs.items()))
 inputs=dict(parent=ref(cp),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],mechanism='Same P1 product; integrate all fixed groundstack bodies into one continuous actual solid after actual stagedassembly failed; retain removableMotorcap andRootcartridge; source-reviewed upstream drive/cartridge and lowerbenchthroughstandardparts unchanged',removed_parts={n:old['part_references'][n] for n in removed},merged_parts={n:old['part_references'][n] for n in merged},bridge_centres_mm=[[-59,-58],[101,-58],[-59,39],[101,39]],bridge_outer_xy_mm=[11.8,10],minimum_TEST_BASE_X_clearance_mm=.2,bridge_z_mm=[60,74],bore_d_mm=5.5,gap_z_mm=[66,70],minimum_added_axial_section_each_mm2=118-3.141592653589793*2.75**2,process='ONE machined billet intent; no weld/printed material/ideal ties assumed; actual manufacture access and certified minimum remain gates',material_minimum_MPa=None,operating_load_N=None,ultimate_host_boundary=None,standard_sources_preserved=[ref(ROOT/'models/materials/primary_joint_sources1/reviewed.json'),ref(ROOT/'models/standard_drive/primary_thread_sources49/reviewed.json')],criteria_unchanged=True)
 dump(out/'inputs.json',inputs)
 d={k:v for k,v in old.items() if k not in ['changed','interferences','exact_pairs','unchanged_part_STEP_count','part_bounds_mm','part_references','assembly','BOM','inputs','producer']};d.update(revision=TAG,status='ACTUAL_P1_INTEGRAL_SUPPORT_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if valid and solids==1 and not hits else 'ACTUAL_P1_INTEGRAL_SUPPORT_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,part_bounds_mm=bb,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),identity_BOM=ref(out/'identity_BOM55.csv'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),changed=[dict(part_ID='BENCH_SUPPORT',STEP=refs['BENCH_SUPPORT'],STL=ref(out/'BENCH_SUPPORT.stl'),valid=valid,solids=solids,volume_mm3=volume(support),parent=old['part_references']['BENCH_SUPPORT'])],removed_part_IDs=removed+merged,unchanged_part_STEP_count=76,exact_pairs=len(queries),interferences=hits,design_change='SameP1 receiver/stand integrated intoONEcontinuous solid throughfourannularwebs;47 unnecessary grounded-interface fasteners removed;all76retainedpartsidentical',load_path=['Motor','Drum','Tendon','Finger','replaceableRoot/cartridge','continuousBENCH_SUPPORT including actualRoot/Motor frame interfaces','fourexistingBENCH_THROUGH joints','EXTERNAL_BENCH_PLATE','UNQUALIFIED ultimatehost'],whole_system_release=False,newly_qualified_system_gate_ids=[],not_qualified=old['not_qualified']+['Newintegralsupport manufacturing,notch/ligament/elasticity/mass/mesh/currentoperatingfield andultimatehost NOTqualified. Removedinterface functions provided bycontinuousmaterial geometry,not capacitycertificate. All22criteria unchanged.'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],parts=len(parts),valid=valid,solids=solids,queries=len(queries),hits=hits)));raise SystemExit(0 if valid and solids==1 and not hits else 2)
if __name__=='__main__':main()
