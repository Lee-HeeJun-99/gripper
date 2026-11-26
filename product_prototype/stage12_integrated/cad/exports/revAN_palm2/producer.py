"""AM descendant with finite through-bolted Palm adapter; no rated thread capacity."""
import sys,json,math,itertools,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,export,common,bounds,overlap,solid_count,volume,box,rotate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAN_palm2';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAM_axial3/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
palm=parts['PALM'];adapter=cut(fuse(cyl(30,(0,0,-28),16),cyl(44,(0,0,-28),6)),cyl(20,(0,0,-29),18))
# Three explicit radial tendon service slots, not exact copied collision solids.
for a in (0,120,240):adapter=cut(adapter,rotate(box(31.5,-1,-29,14,2,8),a))
module={};centers=[]
for i,a in enumerate((60,180,300)):
 x,y=25*math.cos(math.radians(a)),25*math.sin(math.radians(a));centers.append([x,y])
 tool=cyl(2.2,(x,y,-29),23);palm=cut(palm,tool);adapter=cut(adapter,tool)
 module[f'PALM_BOLT_{i}']=fuse(cyl(1.99,(x,y,-32),25.1),cyl(3.5,(x,y,-6.9),4))
 module[f'PALM_NUT_{i}']=cut(cyl(4,(x,y,-31.2),3.2),cyl(2,(x,y,-31.3),3.4))
for a in (45,135,225,315):
 x,y=38*math.cos(math.radians(a)),38*math.sin(math.radians(a));adapter=cut(adapter,cyl(2.75,(x,y,-29),8))
module.update(PALM=palm,PALM_BASE_ADAPTER=adapter);changed=list(module)
for n,s in module.items():
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'))
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in changed,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],fastener_note='Three nominal M4 through bolts; round nut envelopes require actual standard hex/thread/tool design. No preload/rating assigned.'))
r=dict(status='PALM_ADAPTER_GEOMETRY_PASS' if not hits else 'PALM_ADAPTER_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,exact_intersection_pairs=count,bolt_centers_mm=centers,radial_shank_clearance_mm=.21,head_clearance_mm=.1,external_interface='Four diameter5.5 through holes at radius38mm, angles45/135/225/315, flange z=-28..-22. External machine/fasteners not modeled or qualified; no fixed Palm FE nodes.',invalidated=['Palm manufacture/section strength','Assembly and tool paths','Adapter bending, bolt/nut threads and preload','Ground mounting and6DOF capacity','Same-revision Stage1/Stage2 release'],actual_capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits,parts=len(parts))));raise SystemExit(2 if hits else 0)
