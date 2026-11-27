"""Continue SAME P1 anchor: third axial station removes single-line prying.
One locating key+one relieved slot retained; no third lateral locator added.
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
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_anchor36b';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_anchor36/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 base=cut(fuse(parts['TEST_BASE'],box(11,-64,60,20,24,6)),cyl(2.75,(21,-53,59.9),6.2))
 rail=fuse(parts['BENCH_ANCHOR_RAIL'],box(-54,-63,66,150,20,8))
 rail=fuse(fuse(rail,box(-64,-63,66,10.01,107,8)),box(95.99,-63,66,10.01,107,8))
 rail=cut(rail,cyl(2.75,(21,-53,65.9),8.2))
 bolt=cut(fuse(cyl(2.5,(21,-53,60),20),cyl(4.25,(21,-53,55),5)),hex_axis((21,-53,54.99),(0,0,1),4,2.51))
 nut=cut(hex_axis((21,-53,74),(0,0,1),8,4.7),cyl(2.5,(21,-53,73.9),4.9))
 changed=[]
 for n,s in [('TEST_BASE',base),('BENCH_ANCHOR_RAIL',rail),('ANCHOR_BOLT_2',bolt),('ANCHOR_NUT_2',nut)]:
  s=canonical(s);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'].get(n),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_anchor36b'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 for n in ('ANCHOR_BOLT_2','ANCHOR_NUT_2'):bom['parts'].append(dict(part_ID=n,STEP=refs[n],material='ExistingISO4762/ISO4032 dimensional source;minimum/preload unknown',interface='smooth major-thread envelope;not a physical tie'))
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),motivation=ref(ROOT/'validation/integrated/primaryP1_anchor36_audit_inward/summary.json'),design='SAME P1: add ONLY one opposing6mm ear andone M5x20pair at21,-53. Extend the existing receiver into ONE closed8mm-thick frame with central150x67 opening. Three axial stations straddle actualCOM;two original positive-side keys retained,thirdboreclearance only,no redundant locator. External frame-to-bench remainsunqualified.',criteria=dict(intersection_mm3_max=1e-8)))
 r=dict(old);r.update(revision='primaryP1_anchor36b',parts=len(parts),status='PRIMARY_TRIANGULAR_ANCHOR_NOMINAL_GEOMETRY_PASS' if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 'PRIMARY_TRIANGULAR_ANCHOR_GEOMETRY_FAIL',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Continue ONEP1: third axial station at opposite side and one receiverframe;no additional lateral locator. Addresses measured conditional singleline prying amplification,not oldroot numericalconditioning.',not_qualified=old['not_qualified']+['Three-station actual geometry/assembly/force and mass must be rechecked. No carryover of83part equilibrium. Receiverframe bending and external support remainunknown.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),pairs=pairs,hits=hits)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
