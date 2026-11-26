"""Local heel relief at independently measured60deg closest points.

Not a radius/angle scan: keep all bores, seats and wire pocket; remove the
nonfunctional lateral heel corners at canonicalX37/Y+-3/Z-91.
"""
from build_stage1 import box,cyl,cut,fuse
from mechanisms_stage1 import pitch_at
from receiver_fillet_stage1 import beta
def heel_delta(old):
 result={};notes={}
 for n,y in [('SWIVEL_LOWER',-3.01),('SWIVEL_UPPER',2.5)]:
  q=pitch_at(old['F0_'+n],-beta(),(43,0,-92));tool=fuse(box(30,y,-100,8.5,.51,11),box(30,y,-100,9,.51,10.5),cyl(.5,(38.5,y,-89.5),.51,(0,1,0)));q=cut(q,tool);result[n]=pitch_at(q,beta(),(43,0,-92));notes[n]='Local outside heel side pocket depth0.500, canonicalX<=39/Z<=-89, rounded inner cornerR0.5 (1mm endmill from outerY face); retain axle bore minX41.48 and bolt bore bottomZ-87.6. Closest-point failure at60deg independently identified; no bore/seat/wire pocket moved. Actual strength Stage2.'
 return result,notes,[]
CONFIG=dict(heel_relief_depth_mm=.5,heel_relief_X_max_mm=39,heel_relief_Z_max_mm=-89,heel_relief_corner_mm=.5,heel_to_pivot_bore_min_web_mm=2.48,heel_to_bolt_bore_min_web_mm=1.4)
