"""Same78part P1: positive Frame/Ground shear path, no extra purchased hardware."""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.gp import gp_Pnt
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def rect(z,d):
 p=BRepBuilderAPI_MakePolygon()
 for x,y in [(56-d,5-d),(64+d,5-d),(64+d,11+d),(56-d,11+d)]:p.Add(gp_Pnt(x,y,z))
 p.Close();return p.Wire()
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_framekey19';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_interfaces18/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/primary_key_root_relief.py')],design='SAME78partP1: integral8x6x3mm Frame top shear key at[56,5,40],R0.5concave root. Ground blind underside pocket nominalzero lateral gap,0.2mmroof clearance,fourR1corner tool reliefs and0.6mm45deg entry. Existing fourM5 axial retention unchanged. Ground/Base oldkey unchanged. No friction-only shear,sharedM5fixation,newarchitecture or purchases.',criteria=dict(intersection_mm3_max=1e-8),scope='Machinable geometric intent,not process/tolerance/capacity certification; source-backed motor/hub/standardhardware unchanged.'))
 frame=canonical(fuse(parts['OPEN_FRAME'],box(56,5,39.99,8,6,3.01)));fil=BRepFilletAPI_MakeFillet(frame);it=TopExp_Explorer(frame,TopAbs_EDGE);edges=[]
 while it.More():
  e=TopoDS.Edge_s(it.Current());b=bounds(e)
  if abs(b[2]-40)<1e-6 and abs(b[5]-40)<1e-6 and b[0]>=56-1e-6 and b[3]<=64+1e-6 and b[1]>=5-1e-6 and b[4]<=11+1e-6 and b not in edges:edges.append(b);fil.Add(.5,e)
  it.Next()
 assert len(edges)==4,edges;fil.Build();assert fil.IsDone();frame=canonical(fil.Shape())
 ground=cut(parts['GROUND_PLATE'],box(56,5,39.9,8,6,3.3))
 for x,y in [(56,5),(64,5),(64,11),(56,11)]:ground=cut(ground,cyl(1,(x,y,39.9),3.3))
 loft=BRepOffsetAPI_ThruSections(True,True);loft.AddWire(rect(39.9,.7));loft.AddWire(rect(40.6,0));loft.Build();assert loft.IsDone();ground=canonical(cut(ground,loft.Shape()))
 changed=[]
 for n,s in [('OPEN_FRAME',frame),('GROUND_PLATE',ground)]:
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'][n]))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_framekey19'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom);r=dict(old);r.update(revision='primaryP1_framekey19',status='PRIMARY_FRAME_KEY_NOMINAL_GEOMETRY_PASS' if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 'PRIMARY_FRAME_KEY_GEOMETRY_FAIL',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='SAME78partP1: positive integralFrame/Ground8x6x3key,R0.5root and relievedpocket. OriginalRootwall,motorlands,GroundBasekey/stockparts retained. No strength/process/fit certification.',load_path=['Motor->Drum->Tendon->Finger->Root->Frame->newintegralkey+fouraxialM5->Ground->existingkey+fouraxialM5->Base->UNQUALIFIEDphysicalanchor'],not_qualified=old['not_qualified']+['NewFrame/Groundkey actualload/finitecompliance,assembly,fit/gap/contactconvergence and notchstrength must be checked; oldfrictionlessplanarFx failure preserved.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],changed=changed,pairs=pairs,hits=hits)));raise SystemExit(0 if not hits else 2)
if __name__=='__main__':main()
