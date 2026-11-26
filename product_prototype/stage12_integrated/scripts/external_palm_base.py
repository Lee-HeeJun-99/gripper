"""Finite external mounting contrast, no thread capacity or machine certificate."""
import sys,json,math,shutil,itertools
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAR_base2';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
base=cut(cyl(44,(0,0,-36),8),cyl(20,(0,0,-37),10));new={};centers=[]
for i,a in enumerate((45,135,225,315)):
 x,y=38*math.cos(math.radians(a)),38*math.sin(math.radians(a));centers.append([x,y])
 base=cut(base,cyl(2.75,(x,y,-37),10))
 new[f'BASE_BOLT_{i}']=fuse(cyl(2.49,(x,y,-40),18.1),cyl(4.25,(x,y,-21.9),4))
 new[f'BASE_NUT_{i}']=cut(cyl(4.5,(x,y,-39.3),3.2),cyl(2.5,(x,y,-39.4),3.4))
# Explicit service counterbores clear the existing internal M4 nuts and tails.
for i in range(3):
 a=math.radians(60+120*i);x,y=25*math.cos(a),25*math.sin(a)
 base=cut(base,cyl(4.3,(x,y,-32.5),4.6))
new['EXTERNAL_BASE']=base
for n,s in new.items():
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'))
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in new and m not in new:continue
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in new,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],note='External base boundary is its lower annular face; machine fastening/support stiffness absent. Nominal M5 smooth shank and round nut envelopes, no thread engagement/preload/rating.'))
dump(out/'summary.json',dict(status='EXTERNAL_BASE_GEOMETRY_PASS' if not hits else 'EXTERNAL_BASE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=list(new),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),bolt_centers_mm=centers,interferences=hits,exact_intersection_pairs=count,actual_capacity_qualified=False,whole_system_release=False,invalidated=['External ground boundary stiffness','Bolt/nut thread capacity and tooling','Adapter/base contact bending and bearing','Complete assembly paths','Same revision Stage1/Stage2 release']))
print(json.dumps(dict(parts=len(parts),hits=hits)));raise SystemExit(2 if hits else 0)
