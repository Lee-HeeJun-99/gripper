"""Same P1 finite four-pad support and reviewed M5x20 mounting stacks.
Stand rests on planar ground; no hidden friction or fixed bottom nodes.
"""
import json,sys,shutil,itertools,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume,translate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
TAG='primaryP1_benchstand44c'
def invert(s):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(-44,34,67),gp_Dir(1,0,0)),math.pi);return BRepBuilderAPI_Transform(s,t,True).Shape()
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_socketkeeper44c/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
 stand=box(-95,-75,-130,232,140,20);new={};ports=[(-59,-58),(101,-58),(-59,39),(101,39)]
 for i,(x,y) in enumerate(ports):
  # Continuous machined/welded-shape intent,process and material unqualified.
  left=x<0;cx=x-25 if left else x+25
  stand=fuse(fuse(stand,box(cx-5,y-10,-110.01,10,20,176.01)),box(min(cx-5,x-10),y-10,60,max(cx+5,x+10)-min(cx-5,x-10),20,6))
  stand=cut(stand,cyl(2.75,(x,y,59.9),6.2))
  new[f'BENCH_MOUNT_BOLT_{i}']=canonical(translate(invert(parts['ANCHOR_BOLT_0']),x+44,y-34,0))
  new[f'BENCH_MOUNT_NUT_{i}']=canonical(translate(invert(parts['ANCHOR_NUT_0']),x+44,y-34,0))
 new['BENCH_SUPPORT']=canonical(stand);changed=[]
 for n,s in new.items():
  export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=None))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for n in new:bom['parts'].append(dict(part_ID=n,STEP=refs[n],material='UNQUALIFIED custom support or reviewed ISO4762/4032 envelope',interface='Ground planar normal-only;no friction/preload/strength qualification'))
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),ports_xy_mm=ports,support_top_z_mm=66,ground_plane_z_mm=0,ground_law='Unilateral normal-only;friction coefficient unknown,not silently fixed',standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),mount_grip_mm=14,nut_height_mm=4.7,tip_projection_mm=1.3))
 good=not hits and all(c['valid'] and c['solids']==1 for c in changed);r=dict(old);r.update(revision=TAG,status='ACTUAL_BENCH_SUPPORT_LOCAL_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_BENCH_SUPPORT_GEOMETRY_FAIL',parent=ref(src),parts=len(parts),part_references=refs,changed=old['changed']+changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same P1 socketkeepers plus finite four-pad bench stand attached at actual receiver ports by reviewed M5x20 stacks. Ground is unilateral normal-only.',not_qualified=old['not_qualified']+['New support local strength/mass/process/material and mounting thread/preload/locking unqualified;normal-only floor cannot resist horizontal wrench.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),hits=hits)));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
