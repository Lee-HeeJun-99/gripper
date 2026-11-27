"""Same primary P1: actual removable keyed external anchor interface.

Extends TEST_BASE, not a replacement Finger or an adopted laboratory bench.
Two outboard M5x20 pairs reuse existing reviewed standard dimensions. One
square locator and one X-relieved slot avoid two fully locating square keys.
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

TAG='primaryP1_anchor36'
STATIONS=[-44.,86.]
def main():
 assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'cad/exports'/TAG;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references'])
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 parts={n:read(REPO/r['path']) for n,r in refs.items()};base=parts['TEST_BASE'];rail=box(-54,24,66,150,20,8)
 for i,x in enumerate(STATIONS):
  # Integral ears,6mm stock thickness; continuous2mm overlap with old body.
  base=fuse(base,box(x-10,21,60,20,24,6))
  base=fuse(base,box(x-6,28,65.99,12,12,3.01))
  base=cut(base,cyl(2.75,(x,34,59.9),10))
  half=6 if i==0 else 6.2
  rail=cut(rail,box(x-half,28,65.9,2*half,12,3.3),cyl(2.75,(x,34,65.9),8.2))
  # R1 blind corner reliefs permit nominal2mm cutter access from below.
  for xx in (x-half,x+half):
   for yy in (28,40):rail=cut(rail,cyl(1,(xx,yy,65.9),3.3))
 new={'TEST_BASE':canonical(base),'BENCH_ANCHOR_RAIL':canonical(rail)}
 for i,x in enumerate(STATIONS):
  new[f'ANCHOR_BOLT_{i}']=canonical(cut(fuse(cyl(2.5,(x,34,60),20),cyl(4.25,(x,34,55),5)),hex_axis((x,34,54.99),(0,0,1),4,2.51)))
  new[f'ANCHOR_NUT_{i}']=canonical(cut(hex_axis((x,34,74),(0,0,1),8,4.7),cyl(2.5,(x,34,73.9),4.9)))
 changed=[]
 for n,s in new.items():
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'))
  changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'].get(n)))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 for n in new:
  if n=='TEST_BASE':continue
  bom['parts'].append(dict(part_ID=n,STEP=refs[n],material='6061-T6 design intent,minimum unqualified' if n=='BENCH_ANCHOR_RAIL' else 'Existing ISO4762/ISO4032 source dimensions;minimum/preload unqualified',interface='finite CAD; smooth major-thread envelope is NOT load-bearing thread'))
 dump(out/'BOM.json',bom)
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/mechanisms_stage1.py'),ref(S1/'scripts/build_stage1.py')],design='Same ONE P1; retain all77otherparts. TEST_BASE gets two6mm outboard ears and3mm integral keys. One12mm square pocket,one12.4mm X-relieved slot; bothR1blind dogbones,0.2mm roofgap. Finite150x20x8 anchorrail,two existing-source M5x20 socket/hex pairs. Bolt grip14mm,nut4.7,tipprojection1.3mm nominal. Rail external attachment NOT defined or fixed.',criteria=dict(intersection_mm3_max=1e-8),assembly='Rail lowered in Z over2keys; two bolts inserted upward from below; nuts lowered from above,held8AF while4AFsocket rotates below. Existing Finger/root/cartridge/tendon path untouched.'))
 r=dict(old);r.update(revision=TAG,parts=len(parts),status='PRIMARY_KEYED_ANCHOR_NOMINAL_GEOMETRY_PASS' if not hits and all(c['valid'] and c['solids']==1 for c in changed) else 'PRIMARY_KEYED_ANCHOR_GEOMETRY_FAIL',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Actual independent external-base attachment mechanism on SAME P1: one square key plus relieved slot,finite ears/receiver and two standard M5 pairs. No AO,drive,Finger,Root or distalPET geometry changed.',load_path=old['load_path']+['TEST_BASE -> two integral ears -> actual planar key bearing and M5 axial retention -> BENCH_ANCHOR_RAIL -> external support NOT QUALIFIED'],whole_system_release=False,capacity_qualified=False,newly_qualified_system_gate_ids=[],not_qualified=old['not_qualified']+['New TEST_BASE/anchorrail mass,stiffness,local notch/ear strength,tolerance/source minima,thread flank/core/preload and external rail-to-laboratory attachment unqualified. Prior78part equilibria not transferable.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),changed=changed,exact_pairs=pairs,interferences=hits)));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
