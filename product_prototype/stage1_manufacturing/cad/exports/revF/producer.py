"""Stage1 revA: executable OCC design, not a load/grasp qualification.

Run with PYTHONPATH=/tmp/regrip_stage1_ocp and the robot_ws Python.
Each output must be new; millimetres. Purchased parts are interface envelopes,
not vendor manufacturing models. No threads or ball races are synthesized.
"""
import argparse, csv, hashlib, json, math, subprocess, shutil
from pathlib import Path
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Ax1, gp_Trsf, gp_Vec
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs, STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID

ROOT=Path(__file__).resolve().parents[1]
def box(x,y,z,dx,dy,dz):return BRepPrimAPI_MakeBox(gp_Pnt(x,y,z),dx,dy,dz).Shape()
def cyl(r,p,h,d=(0,0,1)):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*p),gp_Dir(*d)),r,h).Shape()
def cut(a,*tools):
 for b in tools:a=BRepAlgoAPI_Cut(a,b).Shape()
 return a
def fuse(a,b):return BRepAlgoAPI_Fuse(a,b).Shape()
def volume(a):
 g=GProp_GProps();BRepGProp.VolumeProperties_s(a,g);return g.Mass()
def rotate(s,a):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),math.radians(a));return BRepBuilderAPI_Transform(s,t,True).Shape()
def translate(s,x,y,z):
 t=gp_Trsf();t.SetTranslation(gp_Vec(x,y,z));return BRepBuilderAPI_Transform(s,t,True).Shape()
def solid_count(s):
 it=TopExp_Explorer(s,TopAbs_SOLID);n=0
 while it.More():n+=1;it.Next()
 return n
def compound(shapes):
 c=TopoDS_Compound();b=BRep_Builder();b.MakeCompound(c)
 for s in shapes:b.Add(c,s)
 return c
def export(s,path):
 w=STEPControl_Writer();w.Transfer(s,STEPControl_AsIs)
 if w.Write(str(path.with_suffix('.step')))!=IFSelect_RetDone:raise RuntimeError('STEP write')
 BRepMesh_IncrementalMesh(s,0.08,False,0.15,False).Perform()
 w=StlAPI_Writer();w.ASCIIMode=False
 if not w.Write(s,str(path.with_suffix('.stl'))):raise RuntimeError('STL write')

def module(revised=False,fastened=False,offset=False,outward=False,service=False):
 p=[]
 def add(id,s,material,process,role='made',note=''):
  p.append(dict(id=id,shape=s,material=material,process=process,role=role,note=note))
 # Tangential Y axis, nominal centre X35/Z20. Shaft isolated from motor by
 # 1mm axial gap inside independently clamped coupling.
 add('SHAFT',cyl(2.5,(35,-12,20),35,(0,1,0)),'steel','turn/grind; h6 seats; end faces deburred')
 for label,y in [('L',-2),('R',13)]:
  add('BEARING_'+label,cut(cyl(8,(35,y,20),5,(0,1,0)),cyl(2.5,(35,y-1,20),7,(0,1,0))), 'SKF 625 candidate','purchase; boundary envelope only','purchased_envelope')
  h=box(20 if fastened else 23,y if label=='R' else y-1,-7 if revised else -1,30 if fastened else 24,6 if revised else 7,39 if revised else 33)
  h=cut(h,cyl(8.025,(35,y-2,20),9,(0,1,0)))
  for x in ((24.5,45.5) if fastened else (26,44)):h=cut(h,cyl(1.7,(x,y+2.5,-13),48))
  add('PEDESTAL_'+label,h,'6061-T6 candidate','CNC; bearing pocket final bore16.05 +0.02/-0 mm')
 # Two independent channels, integral flanges; real cross holes for wire
 # exist but final positive terminal clamp is intentionally a release gate.
 drum=cyl(8,(35,4,20),8,(0,1,0))
 for y in (3.5,7.5,11.5):drum=fuse(drum,cyl(10,(35,y,20),1,(0,1,0)))
 drum=cut(drum,cyl(2.55,(35,3,20),11,(0,1,0)))
 for y in (6,10):drum=cut(drum,cyl(.4,(35,y,10),20))
 add('DRUM',drum,'POM candidate','CNC turn + drill; bore5.10; two0.8 wire holes',note='shaft torque lock and captive tendon clamps unfinished')
 coupling=cut(cyl(6,(35,-22,20),19,(0,1,0)),cyl(2.55,(35,-23,20),21,(0,1,0)))
 for y in (-18,-7):coupling=cut(coupling,cyl(1.25,(35,y,20),7))
 add('COUPLING',coupling,'6061-T6 candidate','turn/drill/tap M3 radial holes; set screws separately required',note='clamp torque/pullout unmeasured')
 motor=box(13.85,-75, -1.15,42.3,38,42.3)
 motor=fuse(motor,cyl(11,(35,-37,20),2,(0,1,0)))
 motor=fuse(motor,cyl(2.5,(35,-37,20),24,(0,1,0)))
 if fastened:
  for x in (19.5,50.5):
   for z in (4.5,35.5):motor=cut(motor,cyl(1.5,(x,-41.5,z),4.5,(0,1,0)))
 add('MOTOR',motor,'SOYO SY42STH38-1684A','purchase; nominal boundary envelope','purchased_envelope', 'Pololu2267 drawing; no stock/price/loaded-speed qualification')
 plate=cut(box(11,-37,-7 if revised else -5,48,3,52 if revised else 50),cyl(11.25,(35,-38,20),5,(0,1,0)))
 for x in (19.5,50.5):
  for z in (4.5,35.5):plate=cut(plate,cyl(1.8,(x,-38,z),5,(0,1,0)))
 if fastened:
  plate=fuse(plate,box(11,-37,-7,48,12,4))
  for x in (18,52):plate=cut(plate,cyl(1.7,(x,-29.5,-8),6))
 add('MOTOR_PLATE',plate,'6061-T6 candidate','CNC; 31mm square4x3.6 clearance',note='base angle/fastening not yet complete')
 # Flat, stress-free sheet reference: intentionally NOT B3 manufactured
 # distal precurve. Root overlap retained inside clamp contact planes.
 add('SKIN',box(50,-12,-100,.3,24,110),'PET candidate','knife/laser cut100 free +10 root; deburr',note='flat reference; not validated B3 geometry')
 for label,y in [('L',-9),('R',6)]:
  add('RAIL_'+label,box(50.3,y,-100,.2,3,110),'spring strip candidate','cut/deburr; joining process not qualified')
 for label,x,depth in [('FRONT',47,3),('BACK',50.5,3)]:
  h=box(x,-20,-7 if revised else 0,depth,40,17 if revised else 10)
  for y in (-16,16):h=cut(h,cyl(1.7,(x-1,y,5),depth+2,(1,0,0)))
  if fastened and label=='BACK':
   h=fuse(h,box(53,-20,-7,10,40,4))
   for hy in (-16,16):h=cut(h,cyl(1.7,(59,hy,-8),6))
  add('ROOT_'+label,h,'6061-T6 candidate','CNC; two3.4 transverse through bores',note='root-to-palm fastening still required')
 # Removable distal clamp: open slot captures flat sheet without glue.
 terminal=cut(box(47,-8,-100,7,16,5),box(50,-13,-101,.5,26,7))
 terminal=cut(terminal,cyl(.4,(47,0,-98),8,(1,0,0)))
 if not offset:add('TERMINAL',terminal,'POM candidate','CNC split clamp;0.8 tendon bore',note='clamp screws/positive retention unfinished')
 else:
  for label,x,depth in [('FRONT',47,3),('BACK',50.5,3.5)]:
   s=cut(box(x,-8,-100,depth,16,5),cyl(.4,(46,0,-98),9,(1,0,0)))
   for y in (-4,4):s=cut(s,cyl(1.7,(46,y,-97.5),9,(1,0,0)))
   add('TERMINAL_'+label,s,'POM candidate','CNC; two3.4 bolt bores,0.8 tendon bore',note='terminal clamp preload/wire retention need Stage2 test')
  # Real sheet perforations align with removable terminal clamp; no holes
  # are silently cut in imported/historical B3 meshes.
  skin=next(q for q in p if q['id']=='SKIN')
  for y in (-4,4):skin['shape']=cut(skin['shape'],cyl(1.7,(49,y,-97.5),3,(1,0,0)))
 if revised and not fastened:
  # Finite foot and M3 clearance holes complete a screw path to the Palm.
  # Bolts/threads/engagement still must be added and inspected, not assumed.
  for tag,x,y,dx,dy in [('MOTOR_FOOT',11,-46,48,9),('ROOT_FOOT',53.5,-20,10,40)]:
   foot=box(x,y,-7,dx,dy,4)
   for hx,hy in ([(18,-41.5),(52,-41.5)] if tag=='MOTOR_FOOT' else [(59,-16),(59,16)]):foot=cut(foot,cyl(1.7,(hx,hy,-8),6))
   add(tag,foot,'6061-T6 candidate','CNC; flange bolted to Palm; joint to vertical plate requires brackets')
 if fastened:
  def bolt(id,p,length,d=(0,0,1)):
   # Head bearing face p; shank goes opposite d. Nominal thread MAJOR
   # envelope, not helical threads. Head dimensions from Bossard ISO4762.
   start=tuple(p[k]-length*d[k] for k in range(3))
   s=fuse(cyl(1.5,start,length,d),cyl(2.75,p,3,d))
   add(id,s,'steel ISO4762 M3 candidate',f'purchase M3x{length}; head5.5x3;2.5AF tool','fastener_envelope','threads simplified; purchased lot/torque unqualified')
  def nut(id,x,y):
   s=cut(cyl(3.175,(x,y,-14.4),2.4),cyl(1.5,(x,y,-15),4))
   add(id,s,'steel M3 nut candidate','purchase ISO4032; cylindrical AF circumscribed ENVELOPE','fastener_envelope','hex geometry/washer selection unfinished')
  for label,y in [('L',.5),('R',15.5)]:
   for x in (24.5,45.5):
    bolt(f'PEDESTAL_{label}_BOLT_{x}',(x,y,32),50);nut(f'PEDESTAL_{label}_NUT_{x}',x,y)
  for label,x,y in [('MF0',18,-29.5),('MF1',52,-29.5),('RF0',59,-16),('RF1',59,16)]:
   bolt(label+'_BOLT',(x,y,-3),12);nut(label+'_NUT',x,y)
  for x in (19.5,50.5):
   for z in (4.5,35.5):bolt(f'MOTOR_BOLT_{x}_{z}',(x,-34,z),6,(0,1,0))
  for y in (-16,16):bolt(f'ROOT_BOLT_{y}',(47,y,5),12,(-1,0,0))
  if offset:
   for y in (-4,4):bolt(f'TERMINAL_BOLT_{y}',(47,y,-97.5),12,(-1,0,0))
   # The added shaft-bearing bolt space is resolved by moving the entire
   # drive inward8mm, not shrinking a fastener/bearing/collision model.
   for q in p:
    if not q['id'].startswith(('ROOT','RF','RAIL','SKIN','TERMINAL')):q['shape']=translate(q['shape'],45 if outward else -8,0,0)
   # Actual removable nuts; circumscribed cylindrical envelope is conservative
   # for collision, not a claim that an off-the-shelf hex nut is round.
   for label,ys,z,x in [('ROOT',(-16,16),5,53.5),('TERMINAL',(-4,4),-97.5,54)]:
    for y in ys:add(f'{label}_NUT_{y}',cut(cyl(3.175,(x,y,z),2.4,(1,0,0)),cyl(1.5,(x-1,y,z),5,(1,0,0))),'M3 steel nut candidate','purchase; conservative circumcircle','fastener_envelope')
 if outward:
  # Separate fixed idler supplies the inward route while large real motors
  # and bearing supports remain outside the Root bolt/service envelope.
  bracket=fuse(box(38,1,-7,3,2,35),box(38,1,22,9,2,6))
  bracket=fuse(bracket,box(31,-3,-7,10,10,4) if service else box(36,-1,-7,8,6,4))
  bracket=cut(bracket,cyl(1.7,(44,0,25),4,(0,1,0)))
  bracket=cut(bracket,cyl(1.7,(34.5 if service else 39.5,2,-8),6))
  add('IDLER_BRACKET',bracket,'6061-T6 candidate','CNC integral post/foot; M3 clearance')
  pulley=cyl(4.5,(44,4,25),4,(0,1,0))
  for y in (4,7.5):pulley=fuse(pulley,cyl(5.5,(44,y,25),.5,(0,1,0)))
  pulley=cut(pulley,cyl(1.7,(44,3,25),6,(0,1,0)))
  add('IDLER',pulley,'POM candidate','turn/drill;3.4 plain bore; nominal wire grooveR4.5',note='wire bend/fatigue/friction NOT MEASURED')
  for label,y in [('L',3),('R',8)]:add('IDLER_SPACER_'+label,cut(cyl(2.5,(44,y,25),1,(0,1,0)),cyl(1.55,(44,y-1,25),3,(0,1,0))),'steel candidate','turn ID3.1 OD5 thickness1')
  bolt('IDLER_AXLE',(44,1,25),12,(0,-1,0))
  add('IDLER_NUT',cut(cyl(3.175,(44,9,25),2.4,(0,1,0)),cyl(1.5,(44,8,25),5,(0,1,0))),'M3 steel nut candidate','purchase; conservative circumcircle','fastener_envelope')
  bolt('IDLER_BASE_BOLT',(34.5 if service else 39.5,2,-3),12);nut('IDLER_BASE_NUT',34.5 if service else 39.5,2)
 return p

def main():
 a=argparse.ArgumentParser();a.add_argument('--revision',required=True);arg=a.parse_args()
 out=ROOT/'cad'/'exports'/arg.revision;out.mkdir(parents=True,exist_ok=False)
 parts=[]
 revised=arg.revision!='revA'
 fastened=arg.revision not in ('revA','revB')
 offset=arg.revision not in ('revA','revB','revC')
 outward=arg.revision not in ('revA','revB','revC','revD')
 service=arg.revision not in ('revA','revB','revC','revD','revE')
 if outward:palm=cut(cyl(135,(0,0,-12),5),cyl(20,(0,0,-13),7))
 palm=cut(cyl(115,(0,0,-12 if revised else -6),5),cyl(20,(0,0,-13 if revised else -7),7))
 if revised:
  for angle in (0,120,240):
   # Sheet slot permits insertion along Z; tendon slots use actual declared
   # straight REST route across Palm rather than deleting its collision.
   for tool in [box(49.7,-13,-13,1.1,26,7),box(38 if outward else 25 if offset else 33,-1,-13,8 if outward else 15 if offset else 7,13,7)]:palm=cut(palm,rotate(tool,angle))
   holes=([(x,y) for x in (24.5,45.5) for y in (.5,15.5)]+[(18,-29.5),(52,-29.5),(59,-16),(59,16)]) if fastened else [(26,.5),(44,.5),(26,15.5),(44,15.5),(18,-41.5),(52,-41.5),(59,-16),(59,16)]
   for x,y in holes:palm=cut(palm,rotate(cyl(1.7,(x+(45 if outward else -8) if offset and x!=59 else x,y,-13),7),angle))
   if outward:palm=cut(palm,rotate(cyl(1.7,(34.5 if service else 39.5,2,-13),7),angle))
 # Motor envelopes extend below proposed palm. Full audit must detect this,
 # not remove motor collision geometry or white-list the contact.
 parts.append(dict(id='PALM',shape=palm,material='6061-T6 candidate',process='CNC plate',role='made',note='mount holes incomplete'))
 for i,angle in enumerate((0,120,240)):
  for p in module(revised,fastened,offset,outward,service):parts.append(dict(p,id=f'F{i}_{p["id"]}',shape=rotate(p['shape'],angle)))
 rows=[]
 for p in parts:
  s=p['shape'];v=volume(s);valid=BRepCheck_Analyzer(s).IsValid()
  if not valid or v<=0:raise RuntimeError('invalid '+p['id'])
  export(s,out/p['id']);rows.append(dict(**{k:v for k,v in p.items() if k!='shape'},volume_mm3=v,brep_valid=valid,solid_count=solid_count(s)))
 export(compound([p['shape'] for p in parts]),out/'ASSEMBLY')
 # Actual STEP round trip, not a filename-presence check.
 r=STEPControl_Reader();assert r.ReadFile(str(out/'ASSEMBLY.step'))==IFSelect_RetDone;r.TransferRoots()
 actual=volume(r.OneShape());expected=sum(p['volume_mm3'] for p in rows)
 assert abs(actual-expected)<1e-6*expected
 collisions=[]
 for i,p in enumerate(parts):
  for q in parts[i+1:]:
   # OCC common solid volumes; touching bearing/shaft interfaces have zero
   # bulk volume. No blanket assembly mate suppression.
   v=volume(BRepAlgoAPI_Common(p['shape'],q['shape']).Shape())
   if v>1e-7:collisions.append(dict(a=p['id'],b=q['id'],volume_mm3=v))
 result=dict(revision=arg.revision,source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),parts=rows,collisions=collisions,roundtrip_volume_error_mm3=actual-expected,stage1_release=False,scope='nominal solid geometry only; no threads/strength/Native/grasp test')
 (out/'audit.json').write_text(json.dumps(result,indent=2))
 shutil.copyfile(__file__,out/'producer.py')
 (out/'source_sha256.txt').write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()+'\n')
 with (out/'BOM.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['id','material','process','role','note','volume_mm3','brep_valid','solid_count']);w.writeheader();w.writerows(rows)
 print(json.dumps(dict(parts=len(parts),collisions=len(collisions),out=str(out))))
if __name__=='__main__':main()
