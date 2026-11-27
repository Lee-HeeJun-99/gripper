"""Root-only widened spring-strip tabs; no material, capacity or adoption claim."""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,export,common,bounds,overlap,solid_count,volume,rotate,canonical
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt,gp_Vec
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAX_wide_root1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()};changed=[]
for suffix,sgn in [('RAIL_L',-1),('RAIL_R',1)]:
 # New single-sheet blank: width3 at z=-7, linear shoulder to width6 at z=-3.
 # Existing outer pin center y=+/-10, z=1. Preserve thickness and all z<=-7.
 poly=BRepBuilderAPI_MakePolygon()
 for y,z in [(8.5,-7),(11.5,-7),(13,-3),(13,10),(7,10),(7,-3)]:poly.Add(gp_Pnt(50.3,sgn*y,z))
 poly.Close();tab=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(),gp_Vec(.2,0,0)).Shape()
 s=fuse(parts['F0_'+suffix],tab);s=cut(s,cyl(1.05,(48.4,sgn*10,1),2.2,(1,0,0)));s=canonical(s)
 for i in range(3):
  n=f'F{i}_{suffix}';q=rotate(s,120*i)
  assert BRepCheck_Analyzer(q).IsValid() and solid_count(q)==1 and volume(q)>0,n
  export(q,out/n);parts[n]=q;refs[n]=ref(out/(n+'.step'));changed.append(n)
bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
manufacture='Six replacement one-piece .2mm spring-strip blanks; root tab width6mm about existing +/-10mm pin axes, linear shoulder z=-7..-3; original diameter2.1mm root holes. No added piece, adhesive, weld or second distal restraint. Cut/deburr/process/material unqualified.'
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in changed,material_status='UNQUALIFIED') for n,r in sorted(refs.items())],manufacture=manufacture,part_count_delta=0,custom_parts_removed=0,custom_processes_removed=0))
r=dict(status='WIDE_ROOT_NOMINAL_GEOMETRY_PASS' if not hits else 'WIDE_ROOT_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,exact_intersection_pairs=count,manufacture=manufacture,outer_hole_ligament_mm=1.95,old_outer_hole_ligament_mm=.45,distal_change_limit_z_mm=-7,actual_capacity_qualified=False,whole_system_release=False,adopted=False,invalidated=['Changed Rail blank manufacturing/notch/strain and root load transfer','Full ordered assembly, tolerances, flexible swept geometry','Same-revision Stage1 and Stage2 release'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits,parts=len(parts))));raise SystemExit(2 if hits else 0)
