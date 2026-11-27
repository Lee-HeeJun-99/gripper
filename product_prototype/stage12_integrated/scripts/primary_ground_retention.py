"""Same primary P1: source dimensional M5 socket/hex retention, not thread capacity."""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports/primaryP1_retention20';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_framekey19/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 source=ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json';sources=json.loads(source.read_text());assert sources['bolt']['dimensions_mm']['L']==20
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),source=ref(source),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/mechanisms_stage1.py'),ref(S1/'scripts/build_stage1.py')],design='ONLY four internal Ground M5 pairs changed. ISO4762 M5x20 full thread nominal major envelope,8.5dia x5 head,4AF x2.5 socket; ISO4032 M5 8AF x4.7 nuts. Grip34..46,tip54,projection3.3mm. ExistingFrame/Groundkey and all70otherparts unchanged. No threadflank/preload/strength certificate.',criteria=dict(intersection_mm3_max=1e-8)))
 changed=[]
 for i,(x,y) in enumerate([(-25,-28),(-25,14),(60,-28),(60,0)]):
  bolt=cut(fuse(cyl(2.5,(x,y,34),20),cyl(4.25,(x,y,29),5)),hex_axis((x,y,28.99),(0,0,1),4,2.51))
  nut=cut(hex_axis((x,y,46),(0,0,1),8,4.7),cyl(2.5,(x,y,45.9),4.9))
  for n,s in [(f'GROUND_BOLT_{i}',bolt),(f'GROUND_NUT_{i}',nut)]:
   s=canonical(s);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'][n],valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']='primaryP1_retention20'
 for row in bom['parts']:
  row['STEP']=refs[row['part_ID']]
  if row['part_ID'].startswith('GROUND_BOLT'):row.update(material='A2 stainless dimension reference; class/minimum unassigned',interface='ISO4762 M5x20 fullthread,4AFsocket2.5deep. Major envelope,not thread capacity.')
  if row['part_ID'].startswith('GROUND_NUT'):row.update(material='ISO4032 A4-70 source dimension reference; no certificate',interface='8AFx4.7 nominal hex,0.8pitch,major bore. Not flank/engagement strength.')
 dump(out/'BOM.json',bom);r=dict(old);r.update(revision='primaryP1_retention20',status='PRIMARY_INTERNAL_RETENTION_GEOMETRY_FAIL' if hits or not all(c['valid'] and c['solids']==1 for c in changed) else 'PRIMARY_INTERNAL_RETENTION_NOMINAL_GEOMETRY_PASS',parent=ref(src),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same78part P1,ONLY8internalM5hardware solids: real4AFsocketheads/M5x20projection and8AFhexnuts.70partrefsunchanged; frame/groundkey retained.',not_qualified=old['not_qualified']+['New internal hardware dimensional/access/footprint/mass verification pending; smooth major thread envelopes cannot certify flank contact,engagement,torque/preload/locking/material capacity.'])
 dump(out/'summary.json',r);print(dict(status=r['status'],parts=len(parts),pairs=pairs,hits=hits));raise SystemExit(2 if hits else 0)
if __name__=='__main__':main()
