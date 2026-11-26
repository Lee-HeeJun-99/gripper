"""Actual inner-face relief, not collision suppression.

The rigid ears extend to naturalZ-84,11mm above the rigid distal5mm.
At60deg the preceding flexible sheet intrudes0.719mm from the tip tangent.
1mm relief clears it; the M3 cone ends atX48.7, so its bearing seat remains.
"""
import math
from build_stage1 import box,cut
def relief_delta(old):
 s=cut(old['F0_TERMINAL_FRONT'],box(49,-7.3,-95,2,14.6,12))
 return {'TERMINAL_FRONT':s},{'TERMINAL_FRONT':'CNC inner relief1.0deep/X49..50/Y+-7.3/Z-95..-83 for own flexible Skin/Rail; original full DIN7991 coneX47..48.7, boreYmin7.8, and actual distal5mm clamp/index retained'},[]
RELIEF=dict(depth_mm=1,halfwidth_mm=7.3,natural_Z_mm=[-95,-83],maximum_reference_intrusion_mm=88/(math.pi/3)*(1-math.cos((math.pi/3)*11/88)),scope='Prescribed constant-curvature target only, not an observed FEM shape; actual own-material collision test required.')
