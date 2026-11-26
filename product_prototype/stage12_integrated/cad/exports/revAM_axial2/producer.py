"""AL descendant: finite integral rear stop and removable through-bolted front stop.
Geometry candidate only; plain thread envelopes explicitly lack flank capacity.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,export,volume,bounds,overlap,common,solid_count,hex_y
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAM_axial2';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAL_Ddrive1/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
hub=fuse(parts['F0_CLUTCH_INPUT_HUB'],cut(cyl(10,(110,12,20),2,(0,1,0)),cyl(2.52,(110,11.9,20),2.2,(0,1,0))))
# Added annulus is outside the existing bore, preserving the D flat.
rear=cut(fuse(cyl(12,(110,10.5,20),1.4,(0,1,0)),box(79,10.5,16,62,1.4,8)),cyl(7.2,(110,10.4,20),1.6,(0,1,0)))
front=cut(fuse(cyl(12,(110,14.1,20),2,(0,1,0)),box(79,14.1,16,62,2,8)),cyl(7.2,(110,14,20),2.2,(0,1,0)))
plate=parts['F0_MOTOR_PLATE']
for extra in (box(79,-8.5,16,62,5,8),box(79,-8.5,16,6,22.6,8),box(135,-8.5,16,6,22.6,8),rear):plate=fuse(plate,extra)
module={'MOTOR_PLATE':plate,'CLUTCH_INPUT_HUB':hub,'AXIAL_FRONT_STOP':front}
for x in (82,138):
 for name in ('MOTOR_PLATE','AXIAL_FRONT_STOP'):module[name]=cut(module[name],cyl(1.7,(x,-9,20),29,(0,1,0)))
 bolt=fuse(cyl(1.49,(x,-13.9,20),30,(0,1,0)),cyl(2.75,(x,16.1,20),3,(0,1,0)))
 nut=cut(hex_y(5.5,-10.9,2.4,x,20),cyl(1.5,(x,-11,20),2.6,(0,1,0)))
 module[f'AXIAL_BOLT_{x}']=bolt;module[f'AXIAL_NUT_{x}']=nut
changed=[]
for i in range(3):
 for suffix,s in module.items():
  n=f'F{i}_{suffix}';s=rotate(s,120*i)
  assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
  export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in changed,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],fastener_note='M3x30 and M3 nuts nominal envelopes; actual ISO thread/engagement/preload/allowables not yet qualified'))
r=dict(status='AXIAL_CAPTURE_GEOMETRY_PASS' if not hits else 'AXIAL_CAPTURE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,exact_intersection_pairs=count,mechanism='Hub annular shoulder trapped with0.1mm each axial clearance between integral grounded rear stop and removable front stop; two M3 through bolts/nuts per sector',invalidated=['Hub D-bore/torque/strength','Plate stiffness, mass, mounting and manufacture','New axial friction/impact/assembly','Fastener thread flank/strength','Stage1/Stage2 same-revision release'],actual_capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits,parts=len(parts))));raise SystemExit(2 if hits else 0)
