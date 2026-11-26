"""Positive metal preload bypass and thread runout, not a loose-nut trick.

Old nominal rotating stacks had zero axial running clearance. Idler now
uses inverted stepped3/M2 axle clamped to bracket through shoulder washers;
receiver rotates on a clamped3mm sleeve. Matched thrust shims set0.03gap.
"""
from build_stage1 import cyl,cut,fuse,translate
from mechanisms_stage1 import hex_axis
def ring(x,y,z,od,id_,length):return cut(cyl(od/2,(x,y,z),length,(0,1,0)),cyl(id_/2,(x,y-.01,z),length+.02,(0,1,0)))
def preload_delta(old):
 new={};notes={}
 def add(n,s,note):new[n]=s;notes[n]=note
 # Idler axle head is at free +Y end.3mm shoulder seats through an ID2.1
 # washer on bracket, so nut preload no longer passes through rotating POM.
 axle=fuse(cyl(1.5,(44,-2.5,25),5.5,(0,1,0)),cyl(2.75,(44,3,25),3,(0,1,0)))
 axle=fuse(axle,cyl(1,(44,-7.6,25),5.1,(0,1,0)))
 axle=cut(axle,ring(44,-3,25,2.2,1.55,.5),hex_axis((44,6,25),(0,-1,0),2.5,1.5))
 add('IDLER_AXLE',axle,'Custom303 stepped3mm shoulderY-2.5..3; M2x0.4-6g fully formedY-7.6..-3; root1.55 runoutY-3..-2.5; head5.5x3/socket2.5AF atY6')
 add('IDLER_SHOULDER_WASHER',ring(44,-3,25,5,2.1,.5),'Steel shoulder washerOD5/ID2.1/t0.5 between bracket innerfaceY-3 and3mm shaft shoulderY-2.5; positive metal preload path')
 add('IDLER_CLAMP_WASHER',ring(44,-5.5,25,5,2.1,.5),'SteelOD5/ID2.1/t0.5 on outer bracket faceY-5; M2nut clamps bracket, NOT POM')
 add('IDLER_NUT',cut(hex_axis((44,-7.1,25),(0,1,0),4,1.6),cyl(1,(44,-7.2,25),1.8,(0,1,0))),'PurchasedM2/AF4/t1.6 nominal,6H; axis-Y service,0.5 nominal screw protrusion; actual nut grade/locking inspection Stage2')
 add('IDLER_SPACER_L',ring(44,-2.5,25,5,3.1,.485),'Matched303 thrust shimOD5/ID3.1/nominal0.485; centre Idler grooveY0+-0.005, combined running gap0.025..0.035 after actual measurement')
 add('IDLER_SPACER_R',ring(44,2.015,25,5,3.1,.985),'Matched303 thrust shimOD5/ID3.1/nominal0.985; head stopsY3, not POM preload; inspect running gap0.025..0.035')
 # Receiver nut keeps its previous external position: counterbore the
 # fork ear and fit a REAL washer over the0.5mm thread runout.
 add('TERMINAL_FRONT',cut(old['F0_TERMINAL_FRONT'],cyl(2.1,(43,5,-92),.6,(0,1,0))),'Retained inner relief/clamp; right fork actual4.20counterboreY5..5.5 forOD4x0.5 washer; remaining journal land1.5, nominal radial web0.9')
 for n in ('SWIVEL_LOWER','SWIVEL_UPPER'):add(n,cut(old['F0_'+n],cyl(1.52,(43,-4,-92),8,(0,1,0))),'RetainedR0.35 pocket; actual3.040+-0.010 pivot bore over stationary3mm sleeve, NOT clamped rotating body')
 add('SWIVEL_SLEEVE',ring(43,-3.5,-92,3,2.02,7),'Stationary303 compression sleeveOD3.000/-0.005,ID2.020+0.010/-0; nominalL7, MATCH actual fork gap; nut preload bypasses receiver')
 add('SWIVEL_SPACER_L',ring(43,-3.5,-92,4,3.1,.485),'Matched303 thrust shimOD4/ID3.1/nom0.485; actual sleeve minus receiver minus both shims =0.025..0.035 running gap')
 add('SWIVEL_SPACER_R',ring(43,3.015,-92,4,3.1,.485),'Matched303 thrust shimOD4/ID3.1/nom0.485; centre receiver and inspect free rotation after nut locking')
 add('SWIVEL_SPACER_OUT',ring(43,5,-92,4,2.1,.5),'Real303 outer washerOD4/ID2.1/t0.5 within fork counterbore, externalY ends5.5 unchanged; covers thread runout')
 add('SWIVEL_AXLE',cut(old['F0_SWIVEL_AXLE'],ring(43,5,-92,2.2,1.55,.5)),'Custom303 smooth2mmY-5.5..5.0, under-washer runoutroot1.55/Y5..5.5; fully formedM2x0.4-6g Y5.5..8.5, original head/nut external positions retained')
 return new,notes,[]
CONFIG=dict(idler_shoulder_variant=True,receiver_preload_sleeve=True,running_gap_acceptance_mm=[.025,.035],matched_centreplane_acceptance_mm=[-.005,.005],nominal_running_gap_mm=.03)
