"""SAME78part P1 integral lateral capture outside the flexible rails."""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def wedge(sign):
 p=BRepBuilderAPI_MakePolygon()
 for y,z in [(20,-7.01),(20,-6.4),(19.39,-7.01)]:p.Add(gp_Pnt(59.99,sign*y,z))
 p.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Vec(8.02,0,0)).Shape()
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_ycapture23';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_seated22/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],design='Same78partP1 integral two8x2.9x4mm Frame Yshoulders at x60..68,inner y+-20.1,z-7..-3,R0.5 inner roots. Root tabs two0.6x45deg lower edge chamfers. NominalYclearance0.1mm; RF bolts/nuts retain removable cartridge, no additional hardware. Outside flexible rail span. Preserve distalPETsliding and3Finger/jamming extension.',criteria=dict(intersection_mm3_max=1e-8),unqualified='No supported material minimum,fit tolerance,notch strength,preload/thread/elastic/global energy or full system release. Old sourcefield belongs to seated22 and MUST NOT be reused as a new equilibrium.'))
 frame=fuse(parts['OPEN_FRAME'],box(60,-23,-7.01,8,2.9,4.01),box(60,20.1,-7.01,8,2.9,4.01));frame=canonical(frame);fil=BRepFilletAPI_MakeFillet(frame);it=TopExp_Explorer(frame,TopAbs_EDGE);edges=[]
 while it.More():
  e=TopoDS.Edge_s(it.Current());b=bounds(e)
  if abs(b[2]+7)<1e-6 and abs(b[5]+7)<1e-6 and abs(abs(b[1])-20.1)<1e-6 and abs(b[1]-b[4])<1e-6 and abs(b[0]-60)<1e-6 and abs(b[3]-68)<1e-6 and b not in edges:edges.append(b);fil.Add(.5,e)
  it.Next()
 assert len(edges)==2,edges;fil.Build();assert fil.IsDone();frame=canonical(fil.Shape());root=canonical(cut(parts['F0_ROOT_BACK'],wedge(1),wedge(-1)));changed=[]
 for n,shape in [('OPEN_FRAME',frame),('F0_ROOT_BACK',root)]:
  export(shape,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'][n],valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),volume_change_mm3=volume(parts[n])-volume(read(REPO/old['part_references'][n]['path']))))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_ycapture23'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom);r=dict(old);r.update(revision='primaryP1_ycapture23',status='PRIMARY_YCAPTURE_NOMINAL_GEOMETRY_PASS' if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 'PRIMARY_YCAPTURE_GEOMETRY_FAIL',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='IntegralYbearing shoulders plus Root edge machining clearance, same78parts. Existing removableRF keeper bolts unchanged. Geometry replaces reliance on unmodeled threaded shear with finite planar lateral bearing; 0.1mm nominal gap, not fixation.',not_qualified=old['not_qualified']+['NewRoot/Frame remesh and original-unit fullforce/gap/finiteboundary/mesh/time checks required. Prior sourcefield is immutable diagnostic only.','Newshoulder/root notch material/process/tolerances and elastic contact closure unresolved.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],changed=changed,pairs=pairs,hits=hits)));raise SystemExit(0 if not hits else 2)
if __name__=='__main__':main()
