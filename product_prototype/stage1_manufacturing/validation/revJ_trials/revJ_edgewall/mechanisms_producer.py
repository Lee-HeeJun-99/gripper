"""Tapered fingers, flush terminal bolts, factory-nipple swivel and drum cup.

All end sockets open laterally for factory-finished tendons; there is no
pretence that a2.5-3.8mm nipple passes a0.8mm wire hole. No swage strength claim.
"""
import math
from build_stage1 import box,cyl,cut,fuse,translate,compound,rotate
from incremental_stage1 import hex_y
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCP.Geom import Geom_BezierCurve
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire
from OCP.gp import gp_Circ
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeCone
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf,gp_Ax1,gp_Dir,gp_Ax2
def common(a,b):return BRepAlgoAPI_Common(a,b).Shape()
def prism_x(x,width,yz):
 w=BRepBuilderAPI_MakePolygon()
 for y,z in yz:w.Add(gp_Pnt(x,y,z))
 w.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(width,0,0)).Shape()
def pitch_at(s,beta,p):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(*p),gp_Dir(0,1,0)),beta);return BRepBuilderAPI_Transform(s,t,True).Shape()
def swivel_beta(px,pz):
 vx,vz=44-px,25-pz;phi=math.atan2(vz,vx);return -(phi-math.acos(4.75/math.hypot(vx,vz)))
def hex_x(af,x,length,y,z):
 r=af/math.sqrt(3);w=BRepBuilderAPI_MakePolygon()
 for i in range(6):w.Add(gp_Pnt(x,y+r*math.cos(i*math.pi/3),z+r*math.sin(i*math.pi/3)))
 w.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(length,0,0)).Shape()
def bolt_m2_y(x,y,z,L):
 s=fuse(cyl(1,(x,y,z),L,(0,1,0)),cyl(1.9,(x,y-2,z),2,(0,1,0)))
 return cut(s,hex_y(1.5,y-2,1.0,x,z))
def nipple():return cut(cyl(1.9,(43,0,-87),11),cyl(.25,(43,0,-88),13))
def mechanisms_delta(old):
 new={};notes={};removed=[]
 def add(n,s,p):new[n]=s;notes[n]=p
 # All relocated base fasteners receive REAL matching Palm holes. Existing
 # revH holes remain visible unused holes, not removed from historical CAD.
 palm=old['PALM']
 for angle in (0,120,240):
  for x,y in [(69.5,-5.5),(90.5,-5.5),(69.5,11),(90.5,11),(63,-35.5),(97,-35.5),(34.5,-4)]:palm=cut(palm,rotate(cyl(1.7,(x,y,-13),7),angle))
  palm=cut(palm,rotate(box(49.7,-13,-13,6,26,7),angle))
  for yy in (-24.3,21.7):palm=cut(palm,rotate(box(53.2,yy,-13,2.6,2.6,7),angle))
 add('GLOBAL__PALM',palm,'CNC original OD230 Palm plus planar-drive relocated bolt holes; original unused holes retained')
 # Exact planar alignment requires ALL winch/idler wire centres atY0.
 # This is a rigid6mm translation of the complete drive, not an unphysical
 # lateral bend in an unsupported taut wire. Reuse actual bearing contract.
 for n,s in old.items():
  if not n.startswith('F0_'):continue
  short=n[3:]
  if short.startswith(('ROOT','RF','SKIN','RAIL','TERMINAL')):continue
  extra=1.5 if short.startswith(('PEDESTAL_R','BEARING_R','CAP_R','INNER_WASHER_R','SHAFT_NUT_R')) else 0
  add(short,translate(s,0,-6+extra,0),'retained revI component, rigid Y-6 planar alignment; right bearing package +1.5 for real nipple-cap backer')
 shaft=fuse(cyl(2.493,(80,-12,20),36.5,(0,1,0)),cyl(4,(80,2.5,20),12.5,(0,1,0)))
 shaft=cut(shaft,cyl(.75,(71,8.5,20),18,(1,0,0)))
 add('SHAFT',translate(shaft,0,-6,0),'steel5f6 journals; central8mm shoulder length12.5; right bearing package+1.5 for cap clearance')
 # Correct physical sheet outline, end indexing instead of rail-severing M3
 # holes. End bolt ears now lie OUTSIDE the full tapered laminate outline.
 skin=prism_x(50,.3,[(-12,10),(12,10),(12,0),(6,-100),(-6,-100),(-12,0)])
 skin=cut(skin,cyl(.8,(49,0,-97),3,(1,0,0)));add('SKIN',skin,'PET0.30 tapered24to12 L100+10root; indexing hole1.60 atY0/Z-97')
 for side,sign in [('L',-1),('R',1)]:
  yz=[(sign*y,z) for y,z in [(8.5,10),(11.5,10),(11.5,0),(5.5,-100),(2.5,-100),(8.5,0)]]
  add('RAIL_'+side,prism_x(50.3,.2,yz),'spring strip0.20 x3; tapered-edge position, no severing end bores')
 removed += [n for n in old if n.startswith('F0_TERMINAL')]
 for label,x,depth in [('FRONT',47,3),('BACK',50.5,3.5)]:
  if label=='FRONT':s=fuse(fuse(box(x,-3,-100,depth,6,5),box(x,-5.5,-96,depth,11,6)),box(x,-13.5,-91,depth,27,7))
  else:s=fuse(box(x,-5.5,-100,depth,11,10),box(x,-13.5,-91,depth,27,7))
  for y in (-9.5,9.5):
   s=cut(s,cyl(1.7,(46,y,-88),10,(1,0,0)))
   if label=='FRONT':
    cone=BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(47.2,y,-88),gp_Dir(1,0,0)),3,1.5,1.5).Shape()
    s=cut(s,cyl(3,(47,y,-88),.2,(1,0,0)),cone)
  if label=='FRONT':
   for yy in (-8,4.5):s=fuse(s,box(x,yy,-93,depth,3.5,3))
   s=cut(s,box(40,-5.7,-91,11,11.4,8),box(49,-7,-95,2,14,4))
   s=cut(s,cyl(.8,(49,0,-97),1.1,(1,0,0)))
   # Two real fork ears connect to front tongue through overlapping bridges.
   for y in (-5.5,3.5):
    s=fuse(s,box(40,y,-95,6,2,6));s=fuse(s,box(45,y,-95,4,2,1))
   s=cut(s,cyl(1.1,(43,-7,-92),14,(0,1,0)))
  else:
   s=cut(s,box(50.4,-7,-95,1.1,14,10))
   s=fuse(s,cyl(.75,(49,0,-97),1.5,(1,0,0)))
   s=fuse(s,prism_x(50.3,3.7,[(-5.5,-100),(5.5,-100),(4.5,-101),(-4.5,-101)]))
  # Final machining AFTER the connecting bridges: the first order refilled
  # part of the countersink and created actual screw interference.
  for y in (-9.5,9.5):
   s=cut(s,cyl(1.7,(46,y,-88),10,(1,0,0)))
   if label=='FRONT':s=cut(s,cyl(3,(47,y,-88),.2,(1,0,0)),BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(47.2,y,-88),gp_Dir(1,0,0)),3,1.5,1.5).Shape())
  add('TERMINAL_'+label,s,'CNC6061; narrow tongue, upper ears; front DIN7991M3 countersinks; back integral1.5 indexing boss')
 for y in (-9.5,9.5):
  cone=BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(47.2,y,-88),gp_Dir(1,0,0)),3,1.5,1.5).Shape()
  s=fuse(fuse(cyl(3,(47,y,-88),.2,(1,0,0)),cone),cyl(1.5,(48.7,y,-88),8.3,(1,0,0)))
  s=cut(s,hex_x(2,47,1.2,y,-88));add(f'TERMINAL_FLUSH_BOLT_{y}',s,'Bossard BN20 DIN7991M3x10,6head/1.7height/2AF; NOT substituted ISO10642 larger head')
  add(f'TERMINAL_FLUSH_NUT_{y}',cut(hex_x(5.5,54,2.4,y,-88),cyl(1.5,(53,y,-88),5,(1,0,0))),'M3 thin nut AF5.5/t2.4 interface; locking per chosen product')
 # Split swivel chamber: max envelope includes both possible interpretation
 # of supplier A/B axial dimensions (sum upper bounds11mm); pocket12mm.
 whole=fuse(box(37,-3,-90,12,6,18),box(41,-3,-94,4,6,6))
 whole=cut(whole,cyl(2.1,(43,0,-88),12),cyl(.4,(43,0,-76),5),cyl(1.05,(43,-4,-92),8,(0,1,0)))
 for x in (39,47):
  for z in (-86.5,-74.5):whole=cut(whole,cyl(1.1,(x,-4,z),8,(0,1,0)))
 beta=swivel_beta(43,-92)
 for label,y in [('LOWER',-3),('UPPER',0)]:
  half=common(whole,box(30,y,-100,25,3,35));add('SWIVEL_'+label,pitch_at(half,beta,(43,0,-92)),'CNC steel split receiver; pocket4.2x12, exit0.8; free Y swivel; no fictitious wire clamp')
 add('TIP_FACTORY_NIPPLE',pitch_at(nipple(),beta,(43,0,-92)),'CarlStahl NI000032 factory terminal for0.45..0.63wire; MAX envelope3.8x11, NOT actual crimp internals')
 for x in (39,47):
  for z in (-86.5,-74.5):
   add(f'SWIVEL_BOLT_{x}_{z}',pitch_at(bolt_m2_y(x,-3,z,8),beta,(43,0,-92)),'ISO4762M2x8,head3.8x2,1.5AF socket')
   nut=cut(hex_y(4,3,1.6,x,z),cyl(1,(x,2,z),4,(0,1,0)))
   add(f'SWIVEL_NUT_{x}_{z}',pitch_at(nut,beta,(43,0,-92)),'M2 hex nut AF4/t1.6; specified locking')
 axle=fuse(cyl(1,(43,-5.5,-92),14,(0,1,0)),cyl(1.9,(43,-7.5,-92),2,(0,1,0)))
 axle=cut(axle,hex_y(1.5,-7.5,1,43,-92));add('SWIVEL_AXLE',axle,'custom smooth2mm axle11mm bearing span + M2x0.4end, head3.8x2; NOT fully threaded screw bearing')
 for label,y in [('L',-3.5),('R',3)]:add('SWIVEL_SPACER_'+label,cut(cyl(2,(43,y,-92),.5,(0,1,0)),cyl(1.05,(43,y-.1,-92),.7,(0,1,0))),'steel OD4/ID2.1/t0.5 thrust spacer')
 add('SWIVEL_AXLE_NUT',cut(hex_y(4,5.5,1.6,43,-92),cyl(1,(43,5,-92),3,(0,1,0))),'M2 AF4/t1.6 locking compound; axle clearance not nut preload on swivel')
 # Positive factory-end capture at winch, split loading from+Y face; the
 # prefinished nipple is never pulled through the0.8exit or hidden in a knot.
 drum=fuse(cyl(8,(80,4,20),8,(0,1,0)),cyl(10,(80,3.5,20),1,(0,1,0)))
 drum=fuse(drum,cyl(12,(80,7,20),5.5,(0,1,0)))
 drum=cut(drum,cyl(4.05,(80,3,20),11,(0,1,0)),cyl(.75,(71.9,8.5,20),16.2,(1,0,0)))
 for x in (67.8,88):drum=cut(drum,cyl(1,(x,8.5,20),4.2,(1,0,0)))
 cap_region=box(69,10.5,7,22,2,18);cap=common(drum,cap_region);drum=cut(drum,cap_region)
 pocket=cyl(2.1,(74,9.6,13.5),12,(1,0,0))
 drum=cut(drum,pocket,box(74,9.6,11.4,12,4,4.2));cap=cut(cap,pocket)
 # Cubic lead-out with real finite wire-radius clearance, sampled cutter
 # axes. This is explicit routing geometry, not a Native wire simulation.
 P=[(86,9.6,13.5),(88.0,9.6,13.5),(88.25,6,18),(88.25,6,20)]
 def bez(t):return tuple((1-t)**3*P[0][j]+3*(1-t)**2*t*P[1][j]+3*(1-t)*t*t*P[2][j]+t**3*P[3][j] for j in range(3))
 pts=[bez(k/32) for k in range(33)]
 poles=TColgp_Array1OfPnt(1,4)
 for i,v in enumerate(P,1):poles.SetValue(i,gp_Pnt(*v))
 spine=BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(Geom_BezierCurve(poles)).Edge()).Wire()
 profile=BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(gp_Pnt(*P[0]),gp_Dir(1,0,0)),.65)).Edge()).Wire()).Face()
 lead_tool=BRepOffsetAPI_MakePipe(spine,profile).Shape();drum=cut(drum,lead_tool);cap=cut(cap,lead_tool)
 for u,v in zip(pts,pts[1:]):
  # Open loading slot to the removable face. The cap, not collision
  # suppression, subsequently closes the+Y access opening.
  slot=cyl(.65,(u[0],u[1],u[2]),13-u[1],(0,1,0));drum=cut(drum,slot)
 # Full1mm annular backer connects all cap islands; partial segment alone
 # was actually disconnected in revJ_mount and is preserved as FAIL.
 cap=fuse(cap,cut(cyl(12,(80,12.5,20),1,(0,1,0)),cyl(4.05,(80,12.4,20),1.2,(0,1,0))))
 for x in (72,88):
  for z in (15,22):
   drum=cut(drum,cyl(1,(x,6.5,z),4,(0,1,0)));cap=cut(cap,cyl(1.1,(x,10.4,z),3.2,(0,1,0)),cyl(2,(x,11.5,z),2.1,(0,1,0)))
   screw=fuse(cyl(1,(x,7.5,z),4,(0,1,0)),cyl(1.9,(x,11.5,z),2,(0,1,0)))
   screw=cut(screw,hex_y(1.5,12.5,1.1,x,z));add(f'DRUM_CAP_BOLT_{x}_{z}',translate(screw,0,-6,0),'ISO4762M2x4, recessed head flush with Yface; 3mm thread engagement')
 add('DRUM',translate(drum,0,-6,0),'CNC6061 single grooveR8, factory nipple side pocket, pin retained by twoM2 plugs')
 add('DRUM_NIPPLE_CAP',translate(cap,0,-6,0),'CNC6061 removable face segment; side-load finished nipple and wire,4M2 screws')
 ni=cut(cyl(1.9,(74.5,9.6,13.5),11,(1,0,0)),cyl(.25,(74,9.6,13.5),13,(1,0,0)))
 add('DRUM_FACTORY_NIPPLE',translate(ni,0,-6,0),'CarlStahl NI000032 MAX supplier-end envelope; exact delivered end tested Stage2')
 # Root cassette docking, two independent M2s and keyed registration boss.
 root=fuse(old['F0_ROOT_BACK'],box(53.5,-12,5,2,24,5))
 frame=box(50.5,-25,10,14,50,2);frame=fuse(frame,cyl(1.5,(53,0,9),1))
 for yy in (-24,22):frame=fuse(frame,box(53.5,yy,-18,2,2,30))
 frame=fuse(frame,box(53.5,-24,-18,2,48,4))
 for yy in (-8,8):frame=cut(frame,cyl(1,(53.4,yy,-16),2.2,(1,0,0)))
 root=cut(root,cyl(1.6,(53,0,8.95),1.2))
 frame=cut(frame,cyl(2.75,(59,0,9.9),2.2))
 for y in (-8,8):
  root=cut(root,cyl(1,(53,y,7.5),2.6));frame=cut(frame,cyl(1.1,(53,y,9.9),2.2))
  screw=fuse(cyl(1,(53,y,8),4),cyl(1.9,(53,y,12),2))
  # Z-axis socket, real top access independent of motor/pedestal sequence.
  w=BRepBuilderAPI_MakePolygon()
  for i in range(6):w.Add(gp_Pnt(53+1.5/math.sqrt(3)*math.cos(i*math.pi/3),y+1.5/math.sqrt(3)*math.sin(i*math.pi/3),13))
  w.Close();tool=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(0,0,1.1)).Shape();screw=cut(screw,tool)
  add(f'CASSETTE_BOLT_{y}',screw,'ISO4762M2x4;2mm engagement; top access independent from Root bolts')
 add('ROOT_BACK',root,'existing root updated only with two blindM2 docking holes/key pocket')
 add('JAMMING_DOCK',frame,'CNC keyed docking interface; two M2; future pressure film NOT installed or qualified')
 return new,notes,removed
