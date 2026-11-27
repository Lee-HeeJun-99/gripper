"""Same P1, constant half-round retaining legs with finite-radius bends.
Custom geometry, NOT certified ISO1234/supplier geometry or forming capacity.
"""
import json,sys,shutil,itertools,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound,translate
from primary_socketcage47d import STATIONS
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeRevol
from OCP.GC import GC_MakeArcOfCircle
from OCP.gp import gp_Pnt,gp_Vec,gp_Ax1,gp_Dir,gp_Trsf
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
TAG=sys.argv[1] if len(sys.argv)>1 else 'primaryP1_profilepin48'
R=.85;GAP=.1;BEND_R=3.;LEG=5.8;ANGLE=math.pi/4

def section(x,y,z,sign):
 a=gp_Pnt(x,y,z-R);b=gp_Pnt(x,y+sign*R,z);c=gp_Pnt(x,y,z+R)
 w=BRepBuilderAPI_MakeWire();w.Add(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(a,b,c).Value()).Edge());w.Add(BRepBuilderAPI_MakeEdge(c,a).Edge())
 return BRepBuilderAPI_MakeFace(w.Wire()).Face()
def tail(x,y,z,sign,angle):
 # Initial flat face at y+/-gap/2; same material section along whole tail.
 f=section(x,y+sign*GAP/2,z,sign)
 if angle==0:return BRepPrimAPI_MakePrism(f,gp_Vec(LEG,0,0)).Shape()
 axis=gp_Ax1(gp_Pnt(x,y+sign*(GAP/2+BEND_R),z),gp_Dir(0,0,sign))
 arc=BRepPrimAPI_MakeRevol(f,axis,angle).Shape()
 tr=gp_Trsf();tr.SetRotation(axis,angle);end=BRepBuilderAPI_Transform(f,tr,True).Shape()
 rem=LEG-BEND_R*angle
 line=BRepPrimAPI_MakePrism(end,gp_Vec(rem*math.cos(angle),sign*rem*math.sin(angle),0)).Shape()
 return canonical(fuse(arc,line))
def cotter(x,y,z,angle=ANGLE):
 halves=[]
 for sign in [-1,1]:
  f=section(x-7.2,y+sign*GAP/2,z,sign)
  sh=BRepPrimAPI_MakePrism(f,gp_Vec(14.4,0,0)).Shape()
  halves.append(fuse(sh,tail(x+7.2,y,z,sign,angle)))
 # Head kept as explicit custom ring, NOT re-labelled supplier full-profile.
 eye=cut(cyl(1.8,(x-8.9,y,z-.85),1.7),cyl(.85,(x-8.9,y,z-1),2))
 return canonical(fuse(fuse(halves[0],halves[1]),eye))
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'cad/exports'/TAG;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_socketcage47d/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};changes=[]
 for pre,i,x,y,seat,parent in STATIONS:
  n=f'{pre}_SPLIT_PIN_{i}';s=cotter(x,y,seat+8.2);export(s,out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));changes.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n]),parent=old['part_references'][n]))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=TAG
 for c in changes:
  row=next(r for r in bom['parts'] if r['part_ID']==c['part_ID']);row.update(STEP=c['STEP'],material='UNQUALIFIED A2 minimum; custom constant half-round bent pin',interface='1.8mm split shaft;0.1mm split gap;3mm flat-reference bend radius;45deg deployed;custom eye retained;NOT ISO conformity')
 dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),stations=STATIONS,section_radius_mm=R,gap_mm=GAP,flat_reference_bend_radius_mm=BEND_R,flat_reference_tail_length_mm=LEG,angle_rad=ANGLE,eye='Custom ring retained;source envelope only;not supplier CAD',forming_minimum=None,installed_capacity_N=None))
 good=not hits and all(c['valid'] and c['solids']==1 for c in changes)
 d=dict(old);d.update(revision=TAG,status='ACTUAL_CONSTANT_PROFILE_PIN_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_CONSTANT_PROFILE_PIN_GEOMETRY_FAIL',parent=ref(cp),parts=len(parts),part_references=refs,changed=changes,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same P1: replace8reduced circular bent tips by constant half-round swept legs;no parent support/keys/drivetrain changes',not_qualified=old['not_qualified']+['Custom pin eye/full supplier profile,forming/ductility/minimum material and installed capacity unqualified;not ISO1234 conformity'])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],hits=hits,changed=changes)));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
