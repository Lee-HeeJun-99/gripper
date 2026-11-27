"""Same actual P1: finite R0.5 key-root fillet and relieved pocket entrance."""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cut,canonical,export,common,bounds,overlap,solid_count,volume
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

def rect(z,delta):
 p=BRepBuilderAPI_MakePolygon()
 for x,y in [(-48-delta,-6-delta),(-40+delta,-6-delta),(-40+delta,6+delta),(-48-delta,6+delta)]:p.Add(gp_Pnt(x,y,z))
 p.Close();return p.Wire()
def main():
 out=ROOT/'cad/exports/primaryP1_fixture14';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_fixture13/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 ground=parts['GROUND_PLATE'];it=TopExp_Explorer(ground,TopAbs_EDGE);fil=BRepFilletAPI_MakeFillet(ground);edges=[]
 while it.More():
  e=TopoDS.Edge_s(it.Current());bb=bounds(e)
  if abs(bb[2]-46)<1e-6 and abs(bb[5]-46)<1e-6 and bb[0]>=-48-1e-6 and bb[3]<=-40+1e-6 and bb[1]>=-6-1e-6 and bb[4]<=6+1e-6:
   fil.Add(.5,e);edges.append(bb)
  it.Next()
 assert len(edges)==4,edges;fil.Build();assert fil.IsDone();ground=canonical(fil.Shape())
 # A0.6x45degree blind underside chamfer relief,not a lateral fit relaxation.
 loft=BRepOffsetAPI_ThruSections(True,True);loft.AddWire(rect(45.9,.7));loft.AddWire(rect(46.6,0));loft.Build();assert loft.IsDone();base=canonical(cut(parts['TEST_BASE'],loft.Shape()))
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],motivation=ref(ROOT/'validation/integrated/primaryP1_joint35_1/summary.json'),design='Continue SAME P1: fourR0.5concave key-root fillets on Ground. Base underside pocket entrance relieved0.6mmx45deg to clear physical root fillets; existingR1blind corner reliefs and upper zero-nominal-gap key retained. No purchased part or load/criteria change.',filleted_original_edges_mm=edges,criteria=dict(intersection_mm3_max=1e-8),unqualified='Root fillet improves finite geometry,not certified stress reduction; actual tool radius/tolerances/fit/thread/anchorage/full3Finger remain unqualified.'))
 changed=[]
 for n,s in [('GROUND_PLATE',ground),('TEST_BASE',base)]:
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   count+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_fixture14'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom);r=dict(old);r.update(revision='primaryP1_fixture14',status='PRIMARY_KEY_ROOT_RELIEF_GEOMETRY_FAIL' if hits or not all(q['valid'] and q['solids']==1 for q in changed) else 'PRIMARY_KEY_ROOT_RELIEF_NOMINAL_GEOMETRY_PASS',part_references=refs,changed=changed,parent=ref(src),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=count,design_change='Same78partP1: R0.5integral key root plus actual0.6mm45deg entrance pocket relief. No new hardware. No stress/convergence/fit/anchor strength approval from CAD.')
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],changed=changed,interferences=hits,exact_pairs=count)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
