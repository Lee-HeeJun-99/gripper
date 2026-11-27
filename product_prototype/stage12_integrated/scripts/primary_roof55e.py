"""Same77part P1: remove obsolete stacked-fixture seams from integral support.
Actual single-billet intent with open driver/motor corridors, no interface ties.
"""
import json,sys,shutil,os,time
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,volume,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
out=ROOT/'cad/exports/primaryP1_integral55e';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_integral55c/summary.json';old=json.loads(cp.read_text());rootp=ROOT/'cad/exports/primaryP1_guide53/summary.json';root=json.loads(rootp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};stand=read(REPO/root['part_references']['BENCH_SUPPORT']['path']);stand=cut(stand,box(-200,-200,40,500,500,200))
# Four existing outboard columns remain; actual new arms overlap each by1mm.
for cx in [-84,126]:
 for y in [-58,39]:
  x0,x1=(-89,-48) if cx<0 else (90,131);stand=fuse(stand,box(x0,y-10,39,x1-x0,20,10))
for x in [-54,90]:stand=fuse(stand,box(x,-68,40,6,117,9))
stand=fuse(stand,box(-54,-42,40,150,65,9));frame=read(REPO/root['part_references']['OPEN_FRAME']['path']);stand=fuse(stand,frame)
# Existing actualdrive group XY[-17,17]x[-35.1,7.5],capminY-36.4.
# Open rectangular36x46mm access;R2dogbonereliefs permit nominal endmill access.
stand=cut(stand,box(-18,-37,30,36,46,30))
for x in [-18,18]:
 for y in [-37,9]:stand=cut(stand,cyl(2,(x,y,30),30))
for y in [-16,16]:stand=cut(stand,cyl(2,(64,y,30),30))
stand=canonical(stand);export(stand,out/'BENCH_SUPPORT');parts['BENCH_SUPPORT']=read(out/'BENCH_SUPPORT.step');refs['BENCH_SUPPORT']=ref(out/'BENCH_SUPPORT.step');bb={n:bounds(s) for n,s in parts.items()};queries=[]
for n,s in parts.items():
 if n=='BENCH_SUPPORT' or not overlap(bb[n],bb['BENCH_SUPPORT']):continue
 assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',pair=['BENCH_SUPPORT',n]))+'\n');f.flush();os.fsync(f.fileno())
 v=common(s,parts['BENCH_SUPPORT']);r=dict(state='COMPLETE',pair=['BENCH_SUPPORT',n],intersection_mm3=v,elapsed_s=time.monotonic()-t);queries.append(r)
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
hits=[r for r in queries if abs(r['intersection_mm3'])>1e-8];valid=bool(BRepCheck_Analyzer(parts['BENCH_SUPPORT']).IsValid());solids=solid_count(parts['BENCH_SUPPORT']);w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_integral55e'
for r in bom['parts']:
 r['STEP']=refs[r['part_ID']]
 if r['part_ID']=='BENCH_SUPPORT':r.update(interface='ONEintegralRoot/Motorframe,9mmroofplate,4outboardarms10mmthick,4existingcolumns/base/hostdatums;36x46mmR2dogboneMotoraccess;two4mmRFdriverholes. No historicalGroundPlate/TEST_BASE/receiver interfaces.',material='6061-T6 single-billetdesignintent with source typicalelasticpropertiesONLY;replaceshistoricalmixedsteelGroundPlate;stockminimum/process/toolsetup/strength NOTqualified')
dump(out/'BOM.json',bom);dump(out/'identity_BOM55e.json',dict(parts=refs,parts_count=len(parts)));inputs=dict(parent=ref(cp),original_datums=ref(rootp),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],mechanism='SAME77partP1. Replace obsolete groundedstack/key/keeper/nut pockets by simplecontinuousroofand4arms after actualh8meshsliverFAIL;not meshtolerancerelaxation. Rootseat/wall/Motorlands/hostall retained at originalcoordinates.',roof_mm=dict(x=[-54,96],y=[-42,23],z=[40,49]),arms_mm=dict(x=[[-89,-48],[90,131]],y=[[-68,-48],[29,49]],z=[39,49]),sidebeams_mm=dict(x=[[-54,-48],[90,96]],y=[-68,49],z=[40,49]),drive_access_mm=dict(x=[-18,18],y=[-37,9],z=[30,60],dogbone_R_mm=2),RF_driver_holes_mm=dict(x=64,y=[-16,16],d=4,z=[30,60]),lowerstand_cut_z_mm=40,source_nominal_material=ref(ROOT/'models/materials/primary_joint_sources1/reviewed.json'),minimum_material_MPa=None,actual_100g_operating_field=None,whole_system_release=False,criteria_unchanged=True)
dump(out/'inputs.json',inputs);d=dict(old);d.update(revision='primaryP1_integral55e',status='ACTUAL_P1_SIMPLIFIED_INTEGRAL_ROOF77PART_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if valid and solids==1 and not hits else 'ACTUAL_P1_SIMPLIFIED_INTEGRAL_ROOF_GEOMETRY_FAIL',parent=ref(cp),part_references=refs,part_bounds_mm=bb,parts=77,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),identity_BOM=ref(out/'identity_BOM55e.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),changed=[dict(part_ID='BENCH_SUPPORT',STEP=refs['BENCH_SUPPORT'],STL=ref(out/'BENCH_SUPPORT.stl'),valid=valid,solids=solids,volume_mm3=volume(parts['BENCH_SUPPORT']),parent=old['part_references']['BENCH_SUPPORT'])],unchanged_part_STEP_count=76,interferences=hits,exact_pairs=len(queries),design_change='Same77partP1simpler ONEcontinuousroof/arms/groundframe;obsoleteupperstackremoved;actualRoot/Motor/benchthrough/sourcepartsdatumsretained',load_path=['Motor','Drum','Tendon','Finger','replaceableRoot','integralRoot/Motorframe-roof-arms-columns-base','retainedfourBENCH_THROUGHjoints','EXTERNAL_BENCH_PLATE','UNQUALIFIED ultimatehost'],not_qualified=old['not_qualified']+['55e newroof/arms/material/process/strength/newfullFE/assembly/mesh notyetqualified;old55cFEpoorquality/SuperLUmemoryFAIL preserved'])
dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],valid=valid,solids=solids,hits=hits,queries=len(queries),volume=d['changed'][0]['volume_mm3'])));raise SystemExit(0 if valid and solids==1 and not hits else 2)
