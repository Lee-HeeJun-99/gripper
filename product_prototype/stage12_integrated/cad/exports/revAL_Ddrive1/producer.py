"""Finite descendant D-drive; partial implementation, no axial/strength release."""
import json,sys,shutil,itertools,math
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,export,volume,bounds,overlap,common,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
out=ROOT/'cad/exports/revAL_Ddrive1';out.mkdir(parents=True,exist_ok=False)
shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
for r in refs.values():assert sha(REPO/r['path'])==r['SHA256']
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),spec=ref(S1/'scripts/sourced_motor_stage1.py')))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
# Maximum flat coordinate 4.6-4.988/2=2.106; twenty-four micron proposed clearance.
# Guaranteed flat starts no later than Y=1.75; hub starts Y=4.8.
bore=cut(cyl(2.52,(110,4.7,20),11.4,(0,1,0)),box(112.13,4.6,16,3,11.6,8))
hub=cut(fuse(cyl(4,(110,4.8,20),11.2,(0,1,0)),cyl(7,(110,9.8,20),6.2,(0,1,0))),bore)
removed=[];changed=[]
for i in range(3):
 n=f'F{i}_CLUTCH_INPUT_HUB';s=rotate(hub,120*i)
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
 n=f'F{i}_CLUTCH_CLAMP_BOLT';removed.append(n);parts.pop(n);refs.pop(n)
bb={n:bounds(s) for n,s in parts.items()};hits=[]
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 if overlap(bb[n],bb[m]):
  v=common(parts[n],parts[m])
  if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
# JSON BOM instead of raw CSV: immutable references for all compatible descendant parts.
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,material_status='UNQUALIFIED',changed=n in changed) for n,r in sorted(refs.items())]))
dump(out/'summary.json',dict(status='D_DRIVE_NOMINAL_GEOMETRY_PASS' if not hits else 'D_DRIVE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),part_references=refs,parts=len(parts),changed=changed,removed_design_parts=removed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,flat_bore_x_from_axis_mm=2.13,bore_radius_mm=2.52,shaft_modified=False,axial_retention_qualified=False,actual_capacity_qualified=False,whole_system_release=False,invalidated=['Hub torque/axial contact and strength','Motor orientation and assembly fit','Clutch preload/drag/transient maximum','Affected full Stage1 and Stage2 releases'],remaining=['Independent positive axial/thrust capture into ground','Loaded elastic contact and supplier orientation verification','Material/allowables/safety2 and mesh1%','Overload and global energy qualification']))
print(json.dumps(dict(parts=len(parts),hits=hits)))
