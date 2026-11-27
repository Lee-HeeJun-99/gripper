"""Same P1 fixture: centre the shear key after off-axis finite-face failure.
Keep fixture11 and its execution/failed uniform-face reference immutable.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_fixture12';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_fixture11/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 parts={n:read(REPO/r['path']) for n,r in refs.items()}
 ground=cut(parts['GROUND_PLATE'],box(-48,-16,46,8,12,3.1));ground=canonical(fuse(ground,box(-48,-6,46,8,12,3)))
 base=fuse(parts['TEST_BASE'],box(-48,-16,46,8,12,3.2));base=canonical(cut(base,box(-48,-6,45.9,8,12,3.3)))
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),failure_evidence=ref(ROOT/'validation/integrated/primaryP1_fixture_verify1/summary.json'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],mechanism='Move integral key from y=-10 to y=0mm; uniform key shear now has zero yaw wrench without opposing-side bearing couples. Same8x12x3mm key,0.2mm roof gap,same78parts and all original drive/finger/frame/bolt datums. Off-axis coarse reference failure preserved,not relaxed.',criteria=dict(intersection_mm3_max=1e-8)))
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
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_fixture12'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom)
 r=dict(old);r.update(revision='primaryP1_fixture12',status='PRIMARY_CENTERED_FIXTURE_GEOMETRY_FAIL' if hits or not all(x['valid'] and x['solids']==1 for x in changed) else 'PRIMARY_CENTERED_FIXTURE_NOMINAL_GEOMETRY_PASS',part_references=refs,changed=changed,parent=ref(src),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=count,design_change='Same P1 finite keyed Ground/test-base joint with key centred at y=0. Eight separate standard bolt/nut solids reused fromfixture11; Ground/Base revised,not a different product.')
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),exact_pairs=count,hits=hits)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
