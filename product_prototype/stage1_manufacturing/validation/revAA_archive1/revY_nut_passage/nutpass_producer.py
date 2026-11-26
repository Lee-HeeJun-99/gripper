"""Plain passage before threaded boss, matched stepped coupling, real runouts.

This constructs NEW billet-machined jaws, not a bonded-in repair ring.
Female thread major-hole CAD is not used as a plain nut passage certificate.
"""
from build_stage1 import box,cyl,cut,fuse
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def limit_band(s,y,length,allowed):return cut(s,cut(box(70,y,10,20,length,20),allowed))
def passage_delta(old):
 s=old['F0_SHAFT']
 s=limit_band(s,-18.01,5.61,cyl(2.2,(80,-18.02,20),5.63,(0,1,0)))
 s=limit_band(s,-12.4,.3,BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(80,-12.4,20),gp_Dir(0,1,0)),2.2,2.493,.3).Shape())
 for y in (-9,14):s=limit_band(s,y,.5,cyl(2.15,(80,y-.01,20),.52,(0,1,0)))
 s=limit_band(s,18.2,.3,BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(80,18.2,20),gp_Dir(0,1,0)),2.493,2.2,.3).Shape())
 s=cut(s,box(70,-18.01,15,8,5.51,10),box(82,-18.01,15,8,5.51,10))
 new={'SHAFT':s};notes={'SHAFT':'303 NEW shaft: outboard plain passage/grip4.400/-0.010 Y-18..-12.4, AF4flatsY-18..-12.5; M5lead0.30 at-12.4..-12.1, fully formed-12.1..-9 and14.5..18.2; root4.30runouts under washersY-9..-8.5/14..14.5; right lead18.2..18.5. 5f6 bearing seats/8shoulder/crosspin unchanged. Thread-gauge overrides nominal major cylinders.'}
 ring=cut(cyl(2.526,(80,-18.5,20),6,(0,1,0)),cyl(2.225,(80,-18.51,20),6.02,(0,1,0)))
 for name,z,h in [('COUPLING_LOWER',14,5.85),('COUPLING_UPPER',20.15,5.85)]:
  body=cut(old['F0_'+name],box(60,-12.5,0,40,3,40));fill=BRepAlgoAPI_Common(ring,box(70,-18.5,z,20,6,h)).Shape();body=fuse(body,fill);new[name]=body;notes[name]='NEW6061 billet stepped split jaw, NOT bonded liner. Inputbore5.050+0.020/-0 Y-32..-18.5, output4.450+0.020/-0 Y-18.5..-12.5, same axis80/20,0.30gap. Pilot small bore first, counterbore input; step transition<=0.20 axial in shaft air gap. Gripoutput5.5 nominal; round+/-Zlands preserved, torque capacity Stage2.'
 return new,notes,[]
CONFIG=dict(shaft_counterhold_AF_mm=4,shaft_counterhold_Y_mm=[-18,-12.5],shaft_plain_passage_D_mm=[4.390,4.400],shaft_plain_passage_Y_mm=[-18,-12.4],nut_plain_GO_mm=4.42,nut_plain_NOGO_mm=4.70,nut_gauge_scope='Additional DESIGN acceptance, NOT reported manufacturer minor-diameter measurement. Also require actual M5x0.5-6H thread gauge.',fully_formed_M5_Y_mm=[[-12.1,-9],[14.5,18.2]],M5_underwasher_runouts_Y_mm=[[-9,-8.5],[14,14.5]],coupling_step_Y_mm=-18.5,coupling_output_face_Y_mm=-12.5,coupling_bores_mm=[5.05,4.45],coupling_output_grip_mm=5.5)
