"""Manufacturing alternative:22mm groove roots, planar tangent factory end.

Addresses manufacturer bend recommendation and removes the small-radius3D
Bezier transfer entirely. Uses actual latest assembly STEP, not RevH rebuild.
"""
import math
from incremental_stage1 import bounds
from mechanisms_stage1 import hex_axis,pitch_at
from build_stage1 import box,cyl,cut,fuse
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
CONFIG=dict(wire_model='planar_tangent_nipple',drum_wire_radius_mm=11.25,idler_wire_radius_mm=11.25,groove_root_radius_mm=11,groove_profile_radius_mm=.28,wire_nominal_diameter_mm=.5,wire_acceptance_diameter_mm=[.48,.52],drum_start_phi=-math.pi/2,drum_centre_mm=[80,0,20],idler_centre_mm=[44,0,25],nipple_outlet_mm=[80,0,8.75],supplier_basis='CarlStahl6x7-WSC recommended groove diameter42*d;22>=42*.52=21.84. Recommendation, not tested fatigue/life.',housing_seat_mm=[16.010,16.021],housing_nominal_mm=16.016,captive_swivel_nuts=True)
def groove(s,x,z):
 tor=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),11.28,.28).Shape()
 opening=cut(cyl(19,(x,-.28,z),.56,(0,1,0)),cyl(11.28,(x,-.29,z),.58,(0,1,0)))
 return cut(s,tor,opening)
def beta(r):return -(math.atan2(117,1)-math.acos(r/math.hypot(117,1)))
def bend_delta(old):
 new={};notes={};removed=[]
 def add(n,s,note):new[n]=s;notes[n]=note
 palm=old['PALM']
 from build_stage1 import rotate
 for angle in (0,120,240):palm=cut(palm,rotate(box(21.5,-.75,-13,19.8,1.5,7),angle))
 add('GLOBAL__PALM',palm,'Retained actual OD230 Palm with expanded physical swept-wire slot; all prior holes preserved')
 add('IDLER_BRACKET',cut(old['F0_IDLER_BRACKET'],box(21.5,-.75,-8,19.8,1.85,7)),'Retained post/bolt with open swept-wire foot relief')
 idler=cyl(11.56,(44,-2,25),4,(0,1,0))
 for yy in (-2,1.5):idler=fuse(idler,cyl(12.5,(44,yy,25),.5,(0,1,0)))
 idler=groove(cut(idler,cyl(1.52,(44,-3,25),6,(0,1,0))),44,25)
 add('IDLER',idler,'POM22mm root,0.28radius U-groove/25mm flanges,3.040+-0.010 bore; manufacturer42*d geometry condition, not fatigue certification')
 drum=cyl(11.56,(80,-2,20),3,(0,1,0))
 drum=fuse(drum,cyl(17,(80,-2.5,20),1,(0,1,0)));drum=fuse(drum,cyl(17,(80,1,20),5.5,(0,1,0)))
 drum=groove(cut(drum,cyl(4.05,(80,-3,20),11,(0,1,0))),80,20)
 drum=cut(drum,cyl(.75,(62.8,2.5,20),34.4,(1,0,0)))
 for x in (62.8,93):drum=cut(drum,cyl(1,(x,2.5,20),4.2,(1,0,0)))
 capregion=box(62.9,4.5,2.9,34.2,2,34.2);cap=BRepAlgoAPI_Common(drum,capregion).Shape();drum=cut(drum,capregion)
 pocket=cyl(2.1,(73.8,0,8.75),6.2,(1,0,0))
 drum=cut(drum,pocket,box(73.8,0,6.65,6.2,8,4.2),cyl(.4,(79.8,0,8.75),2.4,(1,0,0)))
 cap=fuse(cap,cut(cyl(17,(80,6.5,20),1,(0,1,0)),cyl(4.05,(80,6.4,20),1.2,(0,1,0))))
 removed += [n for n in old if n.startswith('F0_DRUM_CAP_BOLT')]
 for x,z in ((69,26),(91,26),(80,6)):
  drum=cut(drum,cyl(1,(x,.5,z),4,(0,1,0)));cap=cut(cap,cyl(1.1,(x,4.4,z),3.2,(0,1,0)),cyl(2,(x,5.5,z),2.1,(0,1,0)))
  screw=fuse(cyl(1,(x,1.5,z),4,(0,1,0)),cyl(1.9,(x,5.5,z),2,(0,1,0)))
  screw=cut(screw,hex_axis((x,7.5,z),(0,-1,0),1.5,1));add(f'DRUM_CAP_BOLT_{x}_{z}',screw,'ISO4762M2x4 with actual1.5AF socket;3mm body engagement')
 add('DRUM',drum,'CNC6061 root22/0.28profile; directly tangent factory nipple atX80/Y0/Z8.75, no small-radius internal transfer')
 add('DRUM_NIPPLE_CAP',cap,'Full annular3mm removable cap OD34/ID8.1;3M2 outside terminal/pin paths')
 add('DRUM_FACTORY_NIPPLE',cut(cyl(1.9,(74,0,8.75),6,(1,0,0)),cyl(.25,(73.8,0,8.75),6.4,(1,0,0))),'NI000032 maximum3.8x6 seated stem-outletX80, tangent to wire coil')
 add('DRUM_PIN',cyl(.7475,(67,2.5,20),26,(1,0,0)),'Custom ground1.49..1.50x26; positive transverse torque path')
 for label,x,d in [('L',63,1),('R',97,-1)]:
  q=cyl(1,(x,2.5,20),4,(d,0,0));q=cut(q,hex_axis((x,2.5,20),(d,0,0),.9,1))
  add('DRUM_PIN_PLUG_'+label,q,'ISO4026M2x4 boundary, actual0.9AF socket; confirm supplier tool/torque before purchase')
 # Rigidly orient the existing receiver, nipple and its four bolt/nut pairs.
 delta=beta(11.25)-beta(4.75)
 for n,s in old.items():
  if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')):add(n[3:],pitch_at(s,delta,(43,0,-92)),'Existing actual receiver reoriented to22mm-root idler tangent; geometry/material retained')
 # New tangent angle exposed a60deg head/nut interFinger contact. Recess
 # both sides0.6mm; actual hex pockets prevent nut rotation. Trim stockM2x8
 # to7mm under-head length (not falsely claiming a confirmed stock SKU).
 for label in ('LOWER','UPPER'):
  body=pitch_at(new['SWIVEL_'+label],-beta(11.25),(43,0,-92))
  for x in (39,47):
   for z in (-86.5,-74.5):
    if label=='LOWER':
     body=cut(body,cyl(2,(x,-3.01,z),.61,(0,1,0)))
     # Counterbore tangent to body X37/49 made a zero-wall STL edge.
     # Open the outboard half as a real machined spotface, not mesh repair.
     body=cut(body,box(36.9 if x==39 else 47,-3.01,z-2,2.1,.61,4))
    else:body=cut(body,hex_axis((x,2.4,z),(0,1,0),4.10,.61))
  add('SWIVEL_'+label,pitch_at(body,beta(11.25),(43,0,-92)),'CNC303;0.6mm head recess or4.10AF captive nut pocket; bore/pocket unchanged; nut anti-rotation geometry, strength Stage2')
 for x in (39,47):
  for z in (-86.5,-74.5):
   screw=fuse(cyl(1,(x,-2.4,z),7,(0,1,0)),cyl(1.9,(x,-4.4,z),2,(0,1,0)));screw=cut(screw,hex_axis((x,-4.4,z),(0,1,0),1.5,1))
   add(f'SWIVEL_BOLT_{x}_{z}',pitch_at(screw,beta(11.25),(43,0,-92)),'Custom M2x7: trim purchased ISO4762M2x8, deburr/rechamfer/gauge6g; actual1.5AF socket;0.6mm end protrusion')
   from build_stage1 import translate
   nut=translate(old[f'F0_SWIVEL_NUT_{x}_{z}'],0,-.6,0)
   add(f'SWIVEL_NUT_{x}_{z}',pitch_at(nut,delta,(43,0,-92)),'M2 AF4/t1.6 recessed0.6 in4.10AF pocket; positive anti-rotation, not measured torque capacity')
 # Leave an actual open5.5AF wrench lane around the Root nuts instead of
 # certifying a spanner through the docking pad. Retain1mm M2 edge web.
 root=old['F0_ROOT_BACK']
 for yy in (-12,10):root=cut(root,box(53.5,yy,5,2.1,2,5.1))
 add('ROOT_BACK',root,'Retained clamp; docking pad narrowed from24to20mm for real5.5AF spanner lane; M2edge ligament1mm')
 # SKF P6 mean OD is not the local maximum: sealed-ring variation9um
 # permits local16.0045mm. Replace former mean-only16H6 with explicit
 #16.010..16.021 clearance requirement, while preserving inner abutments.
 for label,y,h in [('L',-9.001,5.501),('R',8.7,5.801)]:
  add('PEDESTAL_'+label,cut(old['F0_PEDESTAL_'+label],cyl(8.008,(80,y,20),h,(0,1,0))),'CNC seat16.010..16.021 nominal16.016; SKF P6 local OD variation accounted, NOT mislabeled16H6')
 return new,notes,removed
