"""Same P1: positive keyed stand to finite external bench plate, reviewed M5 stacks.
Bench plate is an external-support interface, never a hidden fixed ground.
"""
import json,sys,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume,translate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
TAG='primaryP1_benchattachment45'
PORTS=[(-65,-35),(107,-35),(-65,15),(107,15)]
KEYS=[(-25,-5),(65,-5)]
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_benchstand44d/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 stand=parts['BENCH_SUPPORT'];plate=box(-125,-100,-138,292,190,8);new={}
 for x,y in KEYS:
  stand=fuse(stand,box(x-6,y-8,-134,12,16,4.01))
  plate=cut(plate,box(x-6.1,y-8.1,-134.1,12.2,16.2,4.2))
 for i,(x,y) in enumerate(PORTS):
  stand=cut(stand,cyl(2.75,(x,y,-130.1),20.2))
  stand=cut(stand,cyl(4.75,(x,y,-124),14.1))
  plate=cut(plate,cyl(2.75,(x,y,-138.1),8.2))
  new[f'BENCH_THROUGH_BOLT_{i}']=canonical(translate(parts['BENCH_MOUNT_BOLT_0'],x+59,y+58,-198))
  new[f'BENCH_THROUGH_NUT_{i}']=canonical(translate(parts['BENCH_MOUNT_NUT_0'],x+59,y+58,-198))
 new['BENCH_SUPPORT']=canonical(stand);new['EXTERNAL_BENCH_PLATE']=canonical(plate);changed=[]
 for n,s in new.items():
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'].get(n)))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for n in new:
  row=next((r for r in bom['parts'] if r['part_ID']==n),None)
  if row is None:row=dict(part_ID=n);bom['parts'].append(row)
  row.update(STEP=refs[n],material='UNQUALIFIED custom support/bench plate or reviewed ISO4762/4032 envelope',interface='Integral two-key shear/yaw stop with finite clearance;four through-bolt stacks for conditional uplift;external plate is NOT grounded')
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),ports_xy_mm=PORTS,keys_xy_mm=KEYS,key_dimensions_mm=[12,16,4],pocket_dimensions_mm=[12.2,16.2,4.1],head_seat_z_mm=-124,plate_top_z_mm=-130,plate_bottom_z_mm=-138,grip_mm=14,nominal_overlap_mm=4.7,tip_projection_mm=1.3,standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),physical_external_ground_attachment=None))
 good=not hits and all(r['valid'] and r['solids']==1 for r in changed)
 d=dict(old);d.update(revision=TAG,status='ACTUAL_KEYED_BENCH_INTERFACE_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_KEYED_BENCH_INTERFACE_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same P1 stand: two integral underside shear/yaw keys,two finite bench pockets,four counterbored reviewed through stacks;finite external bench plate.',not_qualified=old['not_qualified']+['New bench-interface material/process/strength/mass/thread/preload/locking/ultimate ground unsupported. No external plate fixation is adopted.'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],parts=len(parts),hits=hits)));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
