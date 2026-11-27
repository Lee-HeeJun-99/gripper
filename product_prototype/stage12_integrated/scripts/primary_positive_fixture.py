"""Same P1: finite keyed Ground/test-base joint, separate standard through bolts.
Nominal geometry only; keys carry shear without claiming friction or bolt-hole ties.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'cad/exports/primaryP1_fixture11';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_clamp10/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references'])
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 parts={n:read(REPO/r['path']) for n,r in refs.items()}
 # Preserve original frame, service window and shared M5 interfaces. Widen ONLY Ground.
 ground=fuse(parts['GROUND_PLATE'],box(-54,-42,40,22.01,65,6))
 ground=fuse(ground,box(73.99,-42,40,22.01,65,6))
 # One integral rectangular key; roof clearance prevents a hidden vertical support.
 ground=fuse(ground,box(-48,-16,46,8,12,3))
 base=fuse(box(-54,-42,56,150,65,10),box(-54,-42,46,20,65,10.01))
 base=fuse(base,box(76,-42,46,20,65,10.01))
 base=cut(base,box(-48,-16,45.9,8,12,3.3))
 # Open service and root-driver passages continue THROUGH the finite base.
 base=cut(base,box(-18,-36.7,55.9,36,44.7,10.2))
 for y in (-16,16):base=cut(base,cyl(3,(64,y,55.9),10.2))
 new={};centres=[(-44,-30),(-44,10),(86,-30),(86,10)]
 for j,(x,y) in enumerate(centres):
  ground=cut(ground,cyl(2.75,(x,y,39.9),6.2));base=cut(base,cyl(2.75,(x,y,45.9),20.2))
  # ISO4762 M5x35: actual4AF socket2.5deep. Nominal major thread envelope,
  # max unthreaded length13mm; nut z66..70.7 lies within distal22mm thread zone53..75.
  bolt=fuse(cyl(2.5,(x,y,40),35),cyl(4.25,(x,y,35),5))
  bolt=cut(bolt,hex_axis((x,y,34.99),(0,0,1),4,2.51))
  nut=cut(hex_axis((x,y,66),(0,0,1),8,4.7),cyl(2.5,(x,y,65.9),4.9))
  new[f'FIXTURE_BOLT_{j}']=canonical(bolt);new[f'FIXTURE_NUT_{j}']=canonical(nut)
 new.update(GROUND_PLATE=canonical(ground),TEST_BASE=canonical(base))
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/mechanisms_stage1.py'),ref(S1/'scripts/build_stage1.py')],standard_sources=ref(ROOT/'models/standard_drive/fixture_sources1/reviewed.json'),bolt_centres_mm=centres,design='Finite keyed Ground to separate machined test base. One8x12x3mm integral key; pocket roof0.2mm clear. Four separate M5x35 bolts and ISO4032M5 nominal hex nuts. No fixing shared original M5 holes. All same P1 drive/finger/frame retained.',criteria=dict(intersection_mm3_max=1e-8),materials='Ground and TEST_BASE6061-T6 intended machined stock; guaranteed allowables/certificates unassigned. Fastener material/class procurement unselected; no load capacity from geometry.'))
 changed=[]
 for n,s in new.items():
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'))
  changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   count+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_fixture11'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 for n in new:
  if n!='GROUND_PLATE':bom['parts'].append(dict(part_ID=n,STEP=refs[n],material='6061-T6 intended,minimum unknown' if n=='TEST_BASE' else 'Standard dimension; class/material/source-minimum not selected',interface='finite machined keyed base' if n=='TEST_BASE' else 'ISO4762M5x35 socket4AF or ISO4032M5 hex8AF; nominal6g/6H thread envelope,not thread capacity'))
 dump(out/'BOM.json',bom)
 result=dict(old);result.update(revision='primaryP1_fixture11',parts=len(parts),part_references=refs,changed=changed,parent=ref(src),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=count,status='PRIMARY_POSITIVE_FIXTURE_GEOMETRY_FAIL' if hits or not all(x['valid'] and x['solids']==1 for x in changed) else 'PRIMARY_POSITIVE_FIXTURE_NOMINAL_GEOMETRY_PASS',design_change='Ground wings and integral shear key; separate finite bridge test base/four standard through bolt-nut pairs. Same P1,78actual parts. No friction-only shear or hidden fixing of original shared M5.',not_qualified=old['not_qualified']+['New key face nominal zero gap is not a tolerance/fit qualification; no friction needed in local necessary static balance','Finite test base is a specimen boundary with explicit external grip wrench; physical laboratory anchoring and compliant base response NOT qualified','Machined key root notch,thread flank/core/engagement,preload/loosening and plate stress remain unqualified'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),exact_pairs=count,hits=hits)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
