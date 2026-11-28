"""Same actual P1: integral ground feet on existing external bench plate.
Ground is an environmental unilateral plane, never a hidden fixed DOF.
Custom stock/process/minimum material and measured ground friction remain unknown.
"""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,fuse,canonical,export,bounds,common,overlap,volume,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
out=ROOT/'cad/exports'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
cp=ROOT/'cad/exports/primaryP1_round64c/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),old['assembly'],old['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};n='EXTERNAL_BENCH_PLATE';parent=refs[n];s=parts[n];v0=volume(s);feet=[]
for x,y in itertools.product([-115.,137.],[-90.,60.]):
 # 20x20 lower pads. 8mm overlap into the original plate (bottom -138).
 # Remaining original pockets, seats and all standard bolts/nuts unchanged.
 s=fuse(s,box(x,y,-170.,20.,20.,40.));feet.append(dict(id='foot_'+str(len(feet)),bounds_mm=[x,y,-170.,x+20,y+20,-130.],contact_bounds_mm=[x,y,-170.,x+20,y+20,-170.],bottom_area_mm2=400.,custom_process='Machine integral feet from thick blank; source-minimum/process/tolerance NOT qualified'))
s=canonical(s);export(s,out/n);s=read(out/(n+'.step'));parts[n]=s;refs[n]=ref(out/(n+'.step'));row=dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=parent,valid=bool(BRepCheck_Analyzer(s).IsValid()),solids=solid_count(s),volume_mm3=volume(s),volume_change_mm3=volume(s)-v0,geometry_credit=True)
bb={n:bounds(s) for n,s in parts.items()};queries=[]
for n,m in itertools.combinations(parts,2):
 if 'EXTERNAL_BENCH_PLATE' not in [n,m] or not overlap(bb[n],bb[m]):continue
 assert not(ROOT/'runtime/STOP').exists();queries.append(dict(pair=[n,m],intersection_mm3=common(parts[n],parts[m])))
hits=[q for q in queries if q['intersection_mm3']>1e-8]
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=out.name
for q in bom['parts']:
 if q['part_ID']=='EXTERNAL_BENCH_PLATE':q.update(STEP=refs[q['part_ID']],interface='Original four M5 nutpockets/seats and keys plus FOUR integral20x20 ground feet at z-170mm. External ground normal/friction contact; no fixed DOF.',material='Custom same-stock continuation; density/strength/process and ground friction UNQUALIFIED')
dump(out/'BOM.json',bom);dump(out/'ground.json',dict(feet=feet,environment_plane_z_mm=-170.,old_lowest_bolt_z_mm=min(bb['BENCH_THROUGH_BOLT_'+str(i)][2] for i in range(4)),assembly_order='Tighten/retain all M5 joints with assembly supported off ground or on its side; only then lower complete specimen onto ground. No in-situ underside tool access through ground claimed.',hardware_measured=False,friction_coefficient=None,material_minimum_MPa=None,process_qualified=False))
d=dict(old);d.update(status='ACTUAL_SAME_P1_GROUND_FEET_CAD_CLEAR_NOT_RELEASE' if not hits and row['valid'] and row['solids']==1 else 'ACTUAL_SAME_P1_GROUND_FEET_CAD_FAIL',revision=out.name,parent=ref(cp),producer=ref(out/'producer.py'),part_references=refs,part_bounds_mm=bb,changed=[row],unchanged_part_STEP_count=82,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),ground=ref(out/'ground.json'),interferences=hits,changed_pair_queries=queries,design_change='Same P1 external plate gains four real integral feet; original83partIDs and82STEPs retained. No other CAD or installed setting changed.',load_path=[*old['load_path'][:-1],'integral four external plate feet','unilateral finite floor contact with UNKNOWN friction'],newly_qualified_system_gate_ids=[],capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=row,hits=hits)));raise SystemExit(0 if not hits and row['valid'] and row['solids']==1 else 2)
