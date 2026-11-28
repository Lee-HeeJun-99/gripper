"""Same P1 installed split-pin prototype: source-sized eye, split D shaft, bent legs.
The selected 45degree leg form is a manufacturing proposal, not supplier certified geometry.
"""
import sys,json,math,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,bounds,common,overlap,volume,solid_count,translate
from build_stage1 import compound
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Elips,gp_Circ,gp_Ax1,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def transform(s,t):return BRepBuilderAPI_Transform(s,t,True).Shape()
def pin_local(angle):
 # Local X is insertion axis, Z separates the two half-round legs. Source shaft OD .9.
 # Eye outer dimensions 3x1.8: ellipse centreline 2.5x1.3 plus .5round section.
 path=BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Elips(gp_Ax2(gp_Pnt(-6.25,0,0),gp_Dir(0,1,0),gp_Dir(1,0,0)),1.25,.65)).Edge()).Wire()
 profile=BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(gp_Pnt(-5,0,0),gp_Dir(0,0,1)),.25)).Edge()).Wire()
 eye=BRepOffsetAPI_MakePipe(path,BRepBuilderAPI_MakeFace(profile).Face()).Shape()
 halves=[]
 for sign in [-1,1]:
  shaft=cut(cyl(.45,(-5,0,0),8.6,(1,0,0)),box(-5.1,-1,-1 if sign==1 else .02,8.9,2,1.02 if sign==1 else 1))
  leg=cut(cyl(.45,(3.4,0,0),1.6,(1,0,0)),box(3.3,-1,-1 if sign==1 else .02,1.9,2,1.02 if sign==1 else 1))
  t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(3.4,0,0),gp_Dir(0,1,0)),-sign*math.radians(angle));halves.append(fuse(shaft,transform(leg,t)))
 return canonical(cut(fuse(fuse(eye,halves[0]),halves[1]),box(-4.5,-1,-.02,10,2,.04)))
def world(s,g):
 t=gp_Trsf()
 if g['name'].startswith('ROOT'):t.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),math.pi/2)
 elif g['name']=='CAP_SOCKET_KEEPER_7':t.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),math.pi)
 s=transform(s,t);roll=gp_Trsf();roll.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(*g['pin_axis'])),math.pi/2);s=transform(s,roll);return translate(s,g.get('anchor_x',g['x']),g['anchor_y_mm'],g['top']+1)
def main():
 tag=sys.argv[1];out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_keeper60c/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references'])
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 groups=json.loads((REPO/old['anchors']['path']).read_text())['groups'];parts={n:read(REPO/r['path']) for n,r in refs.items()};rows=[]
 for g in groups:
  assert not(ROOT/'runtime/STOP').exists();oldn=g['pin'];n=g['name']+'_INSTALLED_SPLIT_PIN';parts.pop(oldn);refs.pop(oldn);s=world(pin_local(45),g);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));g.update(pin=n,old_shaft_proxy=oldn,axial_retention='Actual nominal eye and two45degree splayed half-round legs; strength/forming/tolerance NOT qualified',installed_bend_deg=45)
  rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),bounds_mm=bounds(parts[n]),source_size=ref(ROOT/'models/standard_drive/primary_keeper_sources60/reviewed.json'),manufacturing_status='Source-size design proposal. Exact supplier forming/radii/leg length tolerances and minimum strength unknown.'))
 # Real tool window leaves X62..66mm continuous bridge strip and original tongue.
 n='ROOT_SOCKET_KEEPER';parent=refs[n];parts[n]=canonical(cut(parts[n],box(58,2.9,1.9,4,2.7,2)))
 export(parts[n],out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'))
 rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=parent,valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),bounds_mm=bounds(parts[n]),design='Top-access notch for actual Root split-pin legs, nominal continuous X62..66 strip remains; no stiffness/capacity certificate.'))
 bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for n,m in itertools.combinations(parts,2):
  if not any(n==q['part_ID'] or m==q['part_ID'] for q in rows) or not overlap(bb[n],bb[m]):continue
  assert not(ROOT/'runtime/STOP').exists();queries.append(dict(pair=[n,m],intersection_mm3=common(parts[n],parts[m])))
 hits=[q for q in queries if q['intersection_mm3']>1e-8]
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
 for q in bom['parts']:q['STEP']=refs.get(q['part_ID'],q['STEP'])
 for g in groups:
  row=next(q for q in bom['parts'] if q['part_ID']==g['old_shaft_proxy']);row.update(part_ID=g['pin'],STEP=refs[g['pin']],interface='Nominal installed split-pin eye, separated D shaft,45degree splayed legs; proposed formed geometry',material='A2 size reference only; minimum strength/process UNQUALIFIED')
 dump(out/'BOM.json',bom);dump(out/'anchors.json',dict(groups=groups,parent=old['anchors'],supplier_shape_certified=False,source_size=ref(ROOT/'models/standard_drive/primary_keeper_sources60/reviewed.json')))
 d=dict(old);d.update(revision=tag,parent=ref(cp),producer=ref(out/'producer.py'),part_references=refs,part_bounds_mm=bb,parts=len(parts),changed=rows,unchanged_part_STEP_count=79,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),anchors=ref(out/'anchors.json'),interferences=hits,pin_pair_queries=queries,status='ACTUAL_P1_INSTALLED_SPLIT_PIN_DESIGN_CLEAR_NOT_RELEASE' if not hits else 'ACTUAL_P1_INSTALLED_SPLIT_PIN_DESIGN_FAIL',design_change='Same P1: three source-sized installed-pin solids with actual .04mm slit and one real Root keeper tool window; 79partSTEPs retained. Custom nominal forming proposal using reviewed1x10 size; not supplier exact CAD or strength certificate.',newly_qualified_system_gate_ids=[],capacity_qualified=False,whole_system_release=False)
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=rows,hits=hits)));return 0 if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 2
if __name__=='__main__':sys.exit(main())
