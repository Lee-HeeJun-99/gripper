"""Actual removable socket keeper and keyed base cheeks on SAME P1.
Nominal custom parts; material/threads/strength are unqualified.
"""
import json,sys,shutil,itertools,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
TAG='primaryP1_socketkeeper44b'
def rot(s,x,y):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(x,y,0),gp_Dir(0,1,0)),math.pi/2);return BRepBuilderAPI_Transform(s,t,True).Shape()
def main():
 assert not(ROOT/'runtime/STOP').exists()
 out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports/primaryP1_nutcapture43b/summary.json';old=json.loads(src.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};base=parts['TEST_BASE'];new={}
 for i,(x,y) in enumerate([(-44,34),(86,34),(21,-53)]):
  # Cheeks connect to original underside ear at z60, rectangular key reacts torque.
  for a in (-7,4.1):
   leg=box(x+a,y-8,46,2.9,16,14.01)
   leg=cut(leg,cyl(2.75,(x-7.1,y,50),14.2,(1,0,0)))
   base=fuse(base,leg)
  keeper=fuse(box(x-4,y-5,47,8,10,6),hex_axis((x,y,52.99),(0,0,1),3.9,4.41))
  keeper=cut(keeper,cyl(2.55,(x-4.1,y,50),8.2,(1,0,0)))
  new[f'SOCKET_KEEPER_{i}']=canonical(keeper)
  # Existing reviewed M5x20 ISO4762 / ISO4032 dimensions, horizontal cross pin.
  bolt=cut(fuse(cyl(2.5,(x-7,y,50),20,(1,0,0)),cyl(4.25,(x-12,y,50),5,(1,0,0))),hex_axis((x-12.01,y,50),(1,0,0),4,2.51))
  nut=cut(hex_axis((x+7,y,50),(1,0,0),8,4.7),cyl(2.5,(x+6.9,y,50),4.9,(1,0,0)))
  new[f'KEEPER_PIN_{i}']=canonical(bolt);new[f'KEEPER_NUT_{i}']=canonical(nut)
 new['TEST_BASE']=canonical(base);changed=[]
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
 for row in bom['parts']:row['STEP']=refs[row['part_ID']]
 for n in new:
  if n!='TEST_BASE':bom['parts'].append(dict(part_ID=n,STEP=refs[n],material='UNQUALIFIED minimum;custom keeper or reviewed M5 envelope',interface='Keyed socket keeper/cross pin; smooth threads not axial qualification'))
 dump(out/'BOM.json',bom)
 dump(out/'inputs.json',dict(parent=ref(src),producer=ref(out/'producer.py'),standard_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),socket_AF_mm=4,keeper_AF_mm=3.9,engagement_z_mm=[55,57.4],key_clearance_per_side_mm=.1,retention='transverse removable M5x20 and ISO4032 nut;nut locking/preload not qualified',criteria=dict(intersection_mm3_max=1e-8)))
 good=not hits and all(c['valid'] and c['solids']==1 for c in changed)
 r=dict(old);r.update(revision=TAG,status='ACTUAL_SOCKET_KEEPER_LOCAL_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_SOCKET_KEEPER_GEOMETRY_FAIL',parent=ref(src),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same P1 actual removable socket keepers,transverse M5 retention and base key cheeks;external support remains unresolved.',not_qualified=old['not_qualified']+['Changed TEST_BASE requires new FE/mass/contact binding;keeper material,source tolerances,pin nut locking,thread transfer,external fixture unqualified.'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),hits=hits,changed=changed)));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
