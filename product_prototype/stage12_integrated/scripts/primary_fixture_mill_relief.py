"""Same P1 fixture: make the underside key pocket cuttable by a2mm end mill.
Four blind corner reliefs; preserve exact straight load faces and roof clearance.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_fixture13';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_fixture12/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 base=parts['TEST_BASE']
 for x in (-48,-40):
  for y in (-6,6):base=cut(base,cyl(1,(x,y,45.9),3.3))
 base=canonical(base);export(base,out/'TEST_BASE');parts['TEST_BASE']=read(out/'TEST_BASE.step');refs['TEST_BASE']=ref(out/'TEST_BASE.step')
 changed=[dict(part_ID='TEST_BASE',STEP=refs['TEST_BASE'],STL=ref(out/'TEST_BASE.stl'),valid=bool(BRepCheck_Analyzer(parts['TEST_BASE']).IsValid()),solids=solid_count(parts['TEST_BASE']),volume_mm3=volume(parts['TEST_BASE']))]
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],design='Same P1 centered key. Add four R1blind dogbone reliefs to base pocket,depth3.2mm from underside46 to49.2. A2mm flat end mill can enter from underside before fixture assembly. Nominal straight keyx contact length10mm,y length6mm; actual area must be re-extracted. No sharp internal rectangular pocket manufacturing claim.',process_unqualified=['Tool radius/runout,burrs,corner root fillets,surface finish,fit/tolerance and minimum material remain unqualified'],criteria=dict(intersection_mm3_max=1e-8)))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];count=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   count+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_fixture13'
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 dump(out/'BOM.json',bom)
 r=dict(old);r.update(revision='primaryP1_fixture13',status='PRIMARY_MILL_RELIEVED_FIXTURE_GEOMETRY_FAIL' if hits or not changed[0]['valid'] or changed[0]['solids']!=1 else 'PRIMARY_MILL_RELIEVED_FIXTURE_NOMINAL_GEOMETRY_PASS',part_references=refs,changed=changed,parent=ref(src),assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=count,design_change='Continue same P1: four R1 pocket corner reliefs permit nominal2mm-endmill underside machining. No hardware change,78parts; full assembly/load contacts must be reverified.')
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),exact_pairs=count,hits=hits)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
