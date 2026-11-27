"""Direct external mating plate replacing the stepped adapter; capacity unqualified."""
import sys,json,math,itertools,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,export,common,bounds,overlap,solid_count,volume,box,rotate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAY_direct_plate1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
# One flat annular plate is the declared finite external mating component.
# It replaces the product adapter; lower annular face is machine interface,
# whose compliance and fastening remain explicitly unspecified.
plate=cut(cyl(44,(0,0,-20),8),cyl(20,(0,0,-21),10))
for a in (0,120,240):plate=cut(plate,rotate(box(31.5,-1,-21,14,2,10),a))
module={};centers=[]
for i,a in enumerate((60,180,300)):
 x,y=25*math.cos(math.radians(a)),25*math.sin(math.radians(a));centers.append([x,y])
 plate=cut(plate,cyl(2.2,(x,y,-21),10))
 module[f'PALM_BOLT_{i}']=fuse(cyl(1.99,(x,y,-24),17.1),cyl(3.5,(x,y,-6.9),4))
 module[f'PALM_NUT_{i}']=cut(cyl(4,(x,y,-23.2),3.2),cyl(2,(x,y,-23.3),3.4))
for a in (45,135,225,315):
 x,y=38*math.cos(math.radians(a)),38*math.sin(math.radians(a));plate=cut(plate,cyl(2.75,(x,y,-21),10))
module['PALM_BASE_ADAPTER']=plate
for n,s in module.items():
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'))
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in module and m not in module:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
note='Single flat8mm annular external mating plate replaces16mm stepped adapter; three shorter nominal M4 connectors. Round head/nut/shank envelopes only, actual thread/core/grade/preload/tooling unqualified. Four5.5mm machine holes at radius38, lower face z=-20; machine stiffness/fasteners absent. Material/cost unknown.'
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in module,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],note=note,custom_parts_removed=0,part_count_delta=0,custom_processes_removed=0))
r=dict(status='DIRECT_PLATE_GEOMETRY_PASS' if not hits else 'DIRECT_PLATE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=list(module),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,exact_intersection_pairs=count,bolt_centers_mm=centers,note=note,actual_capacity_qualified=False,whole_system_release=False,adopted=False,invalidated=['Plate and Palm stress, six-axis load demand, bearing and bolt/thread/preload','Machine mounting stiffness and fasteners','Full installed assembly and tendon motion/service','Same-revision Stage1 Stage2 release'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits,parts=len(parts))));raise SystemExit(2 if hits else 0)
