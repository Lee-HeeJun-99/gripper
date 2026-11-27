"""Eight real socket keepers and nonthreaded split-pin cages on current P1.
Cotter is a nominal custom formed representation within reviewed BN687 envelope;
forming, tolerance, fatigue and minimum material are not qualified.
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
TAG='primaryP1_socketcage47'
STATIONS=[('BENCH_MOUNT',i,x,y,74.,'BENCH_ANCHOR_RAIL') for i,(x,y) in enumerate([(-59,-58),(101,-58),(-59,39),(101,39)])]+[('BENCH_THROUGH',i,x,y,-124.,'BENCH_SUPPORT') for i,(x,y) in enumerate([(-65,-35),(107,-35),(-65,15),(107,15)])]
def rod(a,b,r):
 d=[b[i]-a[i] for i in range(3)];L=sum(v*v for v in d)**.5
 return cyl(r,a,L,tuple(v/L for v in d))
def cotter(x,y,z,deployed=True):
 # 1.8mm bounding diameter,20mm nominal under-eye length,3.6mm eye.
 # Half-round split legs have .10mm gap; bends are explicit custom nominal geometry.
 sh=cyl(.9,(x-7,y,z),14.2,(1,0,0));sh=cut(sh,box(x-7.1,y-.05,z-1,14.4,.1,2))
 eye=cut(cyl(1.8,(x-8.7,y,z-.9),1.8),cyl(.85,(x-8.7,y,z-1),2))
 sh=fuse(sh,eye)
 for sign in [-1,1]:
  # Half-round tails continue beyond right cheek,then splay in +/-y.
  tail=cyl(.9,(x+7.1,y,z),5.9,(1,0,0))
  tail=cut(tail,box(x+7,y+(.05 if sign<0 else -2),z-1,6.2,2-.05,2))
  if deployed:
   # Bent legs replaced by smaller equivalent nominal circular wire branches.
   tail=rod((x+7.1,y+sign*.45,z),(x+12,y+sign*3,z),.4)
  sh=fuse(sh,tail)
 return canonical(sh)
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_nutseat46b/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};new={n:parts[n] for n in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT']}
 for prefix,i,x,y,seat,parent in STATIONS:
  z=seat+8.2
  for dx in [-7,4.1]:
   cheek=box(x+dx,y-5,seat,2.9,10,12)
   cheek=cut(cheek,cyl(1.05,(x-7.1,y,z),14.2,(1,0,0)))
   cheek=cut(cheek,cyl(4.4,(x,y,seat-.1),5.2))
   new[parent]=fuse(new[parent],cheek)
  k=fuse(box(x-4,y-4,seat+5.2,8,8,6),hex_axis((x,y,seat+2.6),(0,0,1),3.9,2.7))
  k=cut(k,cyl(1.05,(x-4.1,y,z),8.2,(1,0,0)))
  new[f'{prefix}_SOCKET_KEY_{i}']=canonical(k)
  new[f'{prefix}_SPLIT_PIN_{i}']=cotter(x,y,z)
 changed=[]
 for n,s in new.items():
  s=canonical(s);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changed.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'].get(n)))
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
  row.update(STEP=refs[n],material='UNQUALIFIED minimum;custom keeper/cage or nominal BN687-inspired formed pin',interface='Positive socket/key torque reaction;transverse split-pin axial retention;forming and capacity unqualified')
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),stations=STATIONS,socket_AF_mm=4,keeper_AF_mm=3.9,cross_hole_diameter_mm=2.1,pin_max_diameter_mm=1.8,source=ref(ROOT/'models/standard_drive/primary_cotter_sources47/reviewed.json'),effective_thread_engagement_mm=None,external_ground_attachment=None))
 good=not hits and all(r['valid'] and r['solids']==1 for r in changed)
 d=dict(old);d.update(revision=TAG,status='ACTUAL_EIGHT_SOCKET_CAGES_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_EIGHT_SOCKET_CAGES_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same P1:8 socket keys,8 nonthreaded formed retaining pins and integral cheeks on actual receiver/stand.',not_qualified=old['not_qualified']+['New cages/keys/cotters nominal only;split-pinforming/removal/ductility/material/strength/threadfit/ultimateexternalground unqualified;changedreceiver/stand physicalfieldsinvalid.'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],parts=len(parts),hits=hits,invalid=[r for r in changed if not r['valid'] or r['solids']!=1])));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
