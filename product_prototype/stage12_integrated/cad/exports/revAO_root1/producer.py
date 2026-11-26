"""AN descendant: integral back-clamp dowels capture each layer at root only.
Rigid geometry candidate; no thread, loaded elastic contact or capacity claim.
"""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,export,common,bounds,overlap,solid_count,volume,rotate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAO_root1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAN_palm2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
module={n:parts['F0_'+n] for n in ['SKIN','RAIL_L','RAIL_R','ROOT_FRONT','ROOT_BACK']}
for y in (-7,7):
 # Integral pins: no invented thread load path. Blind front sockets retain support.
 module['ROOT_BACK']=fuse(module['ROOT_BACK'],cyl(1,(48.5,y,1),3,(1,0,0)))
 for name in ('SKIN','RAIL_L','RAIL_R','ROOT_FRONT'):
  module[name]=cut(module[name],cyl(1.05,(48.4,y,1),2.2,(1,0,0)))
changed=[]
for i in range(3):
 for suffix,s in module.items():
  n=f'F{i}_{suffix}';s=rotate(s,120*i)
  assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
  export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in changed,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],manufacture='Back clamp two integral diameter2mm pins at local y=+/-7,z=1; diameter2.1mm layer holes/front blind sockets. Existing clamp bolts retained; thread and assembly-tool qualification missing.'))
r=dict(status='ROOT_CAPTURE_GEOMETRY_PASS' if not hits else 'ROOT_CAPTURE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,exact_intersection_pairs=count,mechanism='Two integral back-clamp pins per Finger, each Rail gets one, PET gets two. Root-only holes; distal parts unchanged. Existing clamp bolts retain normal assembly.',radial_clearance_mm=.05,invalidated=['Root manufacture/assembly','PET notch/bearing/creep and Rail hole strength','Pin shear/bending, front socket and back clamp compliance','Existing bolt threads, separation and Palm load path','Same-revision Stage1/Stage2 release'],actual_capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits,parts=len(parts))));raise SystemExit(2 if hits else 0)
