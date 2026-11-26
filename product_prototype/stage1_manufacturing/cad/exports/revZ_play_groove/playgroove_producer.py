"""Broad U floor accommodates declared bearing play, not a radius scan.

Actual flat-bottom annular cut; physical pulley flanges retained. This is a
clearance/manufacture candidate, NOT qualified tracking/friction/dynamics.
"""
from build_stage1 import cut,cyl
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def play_delta(old):
 result={};notes={}
 for n,x,z in [('DRUM',80,20),('IDLER',44,25)]:
  ring=cut(cyl(19,(x,-.45,z),.90,(0,1,0)),cyl(10.93,(x,-.46,z),.92,(0,1,0)))
  opening=cut(cyl(19,(x,-.55,z),1.10,(0,1,0)),cyl(11.03,(x,-.56,z),1.12,(0,1,0)))
  corner=[BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(0,1,0)),11.03,.10).Shape() for y in (-.45,.45)]
  result[n]=cut(old['F0_'+n],ring,opening,*corner)
  notes[n]='NEW broad U: actual floorR10.930 (rootD21.860+0/-0.010), flat regionY+-0.450MIN,0.10internal corner to sideY+-0.550. Rounded support flanges retained. Accommodates declared radial/axial play geometrically; wire tracking/friction/working radius under load NOT MEASURED. Turn/inspect at20+-1C.'
 return result,notes,[]
CONFIG=dict(broad_groove_floor_radius_mm=10.930,broad_groove_root_limits_mm=[21.850,21.860],broad_groove_flat_halfwidth_mm=.450,broad_groove_side_halfwidth_mm=.550,broad_groove_corner_mm=.10,groove_combined_radial_offset_bound_mm=.045,groove_combined_axial_offset_bound_mm=.155)
