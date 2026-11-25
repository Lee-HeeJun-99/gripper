"""Incremental STEP engineering. Never regenerate or modify revA-H.

Purchased bearings/threads remain interface models. Force capacity belongs to
Stage2. Design changes are fresh solids against ALL retained actual hardware.
"""
import argparse,csv,hashlib,json,math,shutil,subprocess,time
from pathlib import Path
from build_stage1 import box,cyl,cut,fuse,volume,rotate,translate,compound,export,solid_count
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pnt,gp_Vec
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 r=STEPControl_Reader();assert r.ReadFile(str(p))==IFSelect_RetDone;r.TransferRoots();return r.OneShape()
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b);return list(b.Get())
def overlap(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-8 for i in range(3))
def common(a,b):return volume(BRepAlgoAPI_Common(a,b).Shape())
def hex_y(af,y,length,x=80,z=20):
 r=af/math.sqrt(3);w=BRepBuilderAPI_MakePolygon()
 for i in range(6):w.Add(gp_Pnt(x+r*math.cos(i*math.pi/3),y,z+r*math.sin(i*math.pi/3)))
 w.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(0,length,0)).Shape()
def bolt_y(x,y,z,length,direction):
 # head bearing face at y; head points direction, shank opposite
 s=fuse(cyl(1.5,(x,y-length*direction,z),length,(0,direction,0)),cyl(2.75,(x,y,z),3,(0,direction,0)))
 return s

def drive_delta(old):
 new={};notes={}
 def add(n,s,process):new[n]=s;notes[n]=process
 # One locating bearing; second outer race is deliberately floating axially.
 # Main bearing/radial bolt datums retained, not scanned by random offsets.
 for label,b0,b1,inside,outside in [('L',-2.5,2.5,2.5,-3),('R',13.5,18.5,13.2,19)]:
  bearing=translate(old[f'F0_BEARING_{label}'],0,-.5 if label=='L' else .5,0)
  add('BEARING_'+label,bearing,'SKF625-Z interface5x16x5; revised axial datum')
  h=old[f'F0_PEDESTAL_{label}']
  # New H6 seat: reconstruct material in old clearance pocket, preserving
  # all actual vertical mount holes through the union.
  y0,y1=(-3,3) if label=='L' else (13,19)
  h=fuse(h,cut(cyl(8.025,(80,y0,20),y1-y0,(0,1,0)),cyl(8.003,(80,y0-1,20),y1-y0+2,(0,1,0))))
  shoulder=cut(cyl(8.003,(80,2.5 if label=='L' else 13,20),.5 if label=='L' else .2,(0,1,0)),cyl(6.5,(80,2 if label=='L' else 12.5,20),2,(0,1,0)))
  # Extend shoulder to bore wall with0.02radial overlap, no face-only fusion.
  shoulder=fuse(shoulder,cut(cyl(8.025,(80,2.5 if label=='L' else 13,20),.5 if label=='L' else .2,(0,1,0)),cyl(6.5,(80,2 if label=='L' else 12.5,20),2,(0,1,0))))
  h=fuse(h,shoulder)
  cap_y=-4 if label=='L' else 19
  cap=cut(cyl(15,(80,cap_y,20),1,(0,1,0)),cyl(6.5,(80,cap_y-1,20),3,(0,1,0)))
  lip_y=-3 if label=='L' else 18.8;lip_len=.5 if label=='L' else .2
  cap=fuse(cap,cut(cyl(7.98,(80,lip_y-.02 if label=='R' else lip_y,20),lip_len+.02,(0,1,0)),cyl(6.5,(80,lip_y-1,20),3,(0,1,0))))
  # Right lip penetrates carrier from outside; left projects into seat.
  # L lip end=-2.48: provide nominal0.02 outer-ring end clearance by trimming.
  if label=='L':cap=cut(cap,box(60,-2.52,0,40,1,40))
  if label=='R':cap=cut(cap,box(60,18,0,40,.8,40))
  for x in (74,86):
   h=cut(h,cyl(1.5,(x,-3 if label=='L' else 16,10),3,(0,1,0)))
   cap=cut(cap,cyl(1.7,(x,cap_y-1,10),3,(0,1,0)))
   add(f'CAP_{label}_BOLT_{x}',bolt_y(x,-4 if label=='L' else 20,10,4,-1 if label=='L' else 1),'ISO4762M3x4;2.5AF recess to supplier drawing')
  add('PEDESTAL_'+label,h,'CNC6061;16H6 radial seat, integral13mm abutment; M3 nominal thread interfaces')
  add('CAP_'+label,cap,'steel1mm ring OD30 ID13 + integral locating lip15.96; M3 clearance')
 # Shaft continuous central8mm shoulder, 5mm journals and M5 nut interfaces.
 shaft=cyl(2.494,(80,-12,20),35,(0,1,0))
 shaft=fuse(shaft,cyl(4,(80,2.5,20),11,(0,1,0)))
 shaft=cut(shaft,cyl(.75,(71,8.5,20),18,(1,0,0)))
 add('SHAFT',shaft,'steel ground5g6 journals; integral8mm central shoulder2.5..13.5; M5x0.5 ends; crosspin1.5H7')
 for label,y in [('L',-3),('R',18.5)]:
  add('INNER_WASHER_'+label,cut(cyl(4,(80,y,20),.5,(0,1,0)),cyl(2.55,(80,y-1,20),3,(0,1,0))),'steel OD8/ID5.1/t0.5; da7.4..8.3 SKF')
 for label,y in [('L',-5.7),('R',19)]:
  add('SHAFT_NUT_'+label,cut(hex_y(8,y,2.7),cyl(2.5,(80,y-1,20),5,(0,1,0))),'M5x0.5 thin nut AF8/t2.7; helical threads omitted; locking compound perTDS')
 # One active channel; stronger middle flange provides real pin-plug threads.
 drum=cyl(8,(80,4,20),8,(0,1,0))
 for y,r,h in [(3.5,10,1),(7,12,3),(11.5,10,1)]:drum=fuse(drum,cyl(r,(80,y,20),h,(0,1,0)))
 drum=cut(drum,cyl(4.05,(80,3,20),11,(0,1,0)),cyl(.75,(71.9,8.5,20),16.2,(1,0,0)))
 for x in (67.8,88):drum=cut(drum,cyl(1,(x,8.5,20),4.2,(1,0,0)))
 drum=cut(drum,cyl(.4,(80,6,10),20))
 add('DRUM',drum,'CNC6061 one active grooveR8; 8.10bore; transverse1.5H7 pin; twoM2 end plugs')
 add('DRUM_PIN',cyl(.7475,(72,8.5,20),16,(1,0,0)),'custom ground steel pin1.49..1.50x16; slip hole1.50..1.51; no unsupported ISO8734 size claim')
 for label,x in [('L',68),('R',88)]:add('DRUM_PIN_PLUG_'+label,cyl(1,(x,8.5,20),4,(1,0,0)),'ISO4026 M2x4 socket set screw; nominal major thread envelope')
 # Real two-jaw split rigid coupling, no missing screw placeholders.
 for label,z,h in [('LOWER',14,5.85),('UPPER',20.15,5.85)]:
  s=cut(box(71,-26,z,18,19.8,h),cyl(2.525,(80,-27,20),22,(0,1,0)))
  for x in (74,86):
   for y in (-21,-9.8):s=cut(s,cyl(1.7 if label=='UPPER' else 1.5,(x,y,13),17))
  add('COUPLING_'+label,s,'CNC6061 split jaw;0.30gap;5.05bore; upper3.4 clearance/lowerM3 thread')
 for x in (74,86):
  for y in (-21,-9.8):
   s=fuse(cyl(1.5,(x,y,16),10),cyl(2.75,(x,y,26),3))
   add(f'COUPLING_BOLT_{x}_{y}',s,'ISO4762M3x10; supplier recess/washer release required')
 return new,notes,['F0_COUPLING']

def main():
 a=argparse.ArgumentParser();a.add_argument('--tag',required=True);args=a.parse_args();start=time.monotonic()
 out=ROOT/'cad/exports'/args.tag;out.mkdir(exist_ok=False)
 src=ROOT/'cad/exports/revH';audit=json.loads((src/'audit.json').read_text())
 allparts={p['id']:read(src/(p['id']+'.step')) for p in audit['parts']}
 changed,notes,removed=drive_delta(allparts)
 provenance={n:dict(path=str((src/(n+'.step')).relative_to(ROOT)),sha256=sha(src/(n+'.step'))) for n in allparts}
 for i in range(3):
  for n in removed:
   name=n.replace('F0_',f'F{i}_',1);del allparts[name];provenance.pop(name)
  for name,s in changed.items():
   n=f'F{i}_{name}';s=rotate(s,i*120)
   assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1,(n,'invalid solid')
   export(s,out/n);allparts[n]=s;provenance[n]=dict(path=str((out/(n+'.step')).relative_to(ROOT)),sha256=sha(out/(n+'.step')),process=notes[name])
 export(compound(list(allparts.values())),out/'ASSEMBLY')
 r=read(out/'ASSEMBLY.step');expected=sum(volume(s) for s in allparts.values());assert abs(volume(r)-expected)<expected*1e-6
 b={n:bounds(s) for n,s in allparts.items()};collisions=[];names=list(allparts)
 for j,n in enumerate(names):
  for m in names[j+1:]:
   if not overlap(b[n],b[m]):continue
   v=common(allparts[n],allparts[m])
   if v>1e-7:collisions.append(dict(a=n,b=m,volume_mm3=v))
 result=dict(tag=args.tag,source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),incremental_base='revH',parts=provenance,part_count=len(allparts),changed_per_finger=list(changed),collisions=collisions,all_BRep_single_valid=True,STEP_roundtrip_volume_error_mm3=volume(r)-expected,runtime_s=time.monotonic()-start,stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py')
 (out/'dependencies_sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'scripts/build_stage1.py',src/'audit.json']},indent=2))
 print(json.dumps(dict(parts=len(allparts),collisions=collisions,runtime_s=result['runtime_s'])))
if __name__=='__main__':main()
