"""Actual0.5mm free tendon solid in REST installation pose, not heat-set wire.
Factory-metal outlet to outlet; wire inside swaged terminals is not invented.
"""
import math
import numpy as np
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCP.gp import gp_Pnt,gp_Circ,gp_Ax2,gp_Dir
from build_stage1 import volume
import wire_motion as wm
REPORT={}
def curved(c,r,lo,hi):
 def p(t):return gp_Pnt(c[0]+r*math.cos(t),0,c[1]+r*math.sin(t))
 return BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(p(lo),p((lo+hi)/2),p(hi)).Value()).Edge()
def wire_delta(index):
 wm.setup(index);assert wm.MODEL=='planar_tangent_nipple'
 g=wm.path(0);start=[80,0,8.75];t=np.array([math.sin(g['beta']),0,math.cos(g['beta'])]);end=g['P']+16*t
 w=BRepBuilderAPI_MakeWire();w.Add(curved((80,20),wm.DRUM_R,wm.START_PHI,g['phi']));w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*g['A']),gp_Pnt(*g['B'])).Edge());w.Add(curved((44,25),wm.IDLER_R,g['phi'],g['end']));w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*g['Q']),gp_Pnt(*end)).Edge())
 profile=BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(gp_Pnt(*start),gp_Dir(1,0,0)),.25)).Edge()).Wire()).Face()
 s=BRepOffsetAPI_MakePipe(w.Wire(),profile).Shape();L=g['free']+wm.DRUM_R*(g['phi']-wm.START_PHI)+4;expected=math.pi*.25**2*L
 assert abs(volume(s)-expected)<expected*1e-6,(volume(s),expected)
 REPORT.update(dict(free_length_between_metal_stem_outlets_mm=L,diameter_mm=.5,volume_mm3=volume(s),expected_volume_mm3=expected,length_procurement_mm=[L-.25,L+.25],inspection_reference_tension_N=.1,scope='Finished free-wire length design requirement, NOT a measured supplier product. REST installed curve is NOT stress-free manufacture or a heat-set coil. Three completed tendon purchases include six NI000032 ends, not six loose terminals.'))
 return {'TENDON_WIRE':s},{'TENDON_WIRE':f'Factory-finished0.50mm7x7 stainless cable with NI000032 both ends; free stem-outlet length{L:.5f}+-0.25mm at0.1N inspection reference; CAD installation pose only; no preforming or measured strength'},[]
