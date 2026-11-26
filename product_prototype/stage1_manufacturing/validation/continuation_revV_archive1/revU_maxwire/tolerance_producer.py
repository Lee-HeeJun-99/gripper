"""Removal-only groove relief for declared0.52mm maximum cable envelope."""
from build_stage1 import cut,cyl
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def tolerance_delta(old):
 out={};notes={}
 for name,x,z in [('DRUM',80,20),('IDLER',44,25)]:
  tor=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),11.28,.30).Shape()
  opening=cut(cyl(19,(x,-.30,z),.60,(0,1,0)),cyl(11.28,(x,-.31,z),.62,(0,1,0)))
  out[name]=cut(old['F0_'+name],tor,opening)
  notes[name]='CNC U groove majorR11.28/profileR0.300+0.010/-0; actual rootD21.960+0/-0.020. Planar0.52 cable outer envelope clear at nominal centreR11.25. No sliding/fatigue certification.'
 return out,notes,[]
