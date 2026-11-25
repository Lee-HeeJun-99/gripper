"""Documented alternative to the undimensioned SOYO pilot projection.

Manufacturer17HS15-1504S1/A0648(2025-07-30) supplies pilot2 and general
integer tolerance+-0.5. Conservative envelope:42.3max x40max body,
25max shaft,22max x2.5max pilot. Own CAD, NOT vendor STEP (login-gated).
"""
from build_stage1 import box,cyl,fuse,cut
MOTOR_SPEC=dict(model='STEPPERONLINE17HS15-1504S1',drawing='A0648/2025-07-30',source='https://files.omc-stepperonline.com/17HS15-1504S1_Full_Datasheet.pdf',body_nominal_mm=39,body_limits_mm=[38,40],body_width_max_mm=42.3,flange_Y_mm=-44,shaft_length_mm=[23,25],shaft_diameter_mm=[4.988,5],pilot_diameter_mm=[21.95,22],pilot_height_nominal_mm=2,pilot_height_limits_mm=[1.5,2.5],pilot_height_tolerance_basis='Integer X+-0.5 general tolerance in manufacturer drawing',mount_pitch_mm=[30.8,31.2],mount_thread='4M3 depth4.5MIN',D_flat_across_mm=[4.4,4.6],D_flat_length_mm=[14.75,15.25],wire_connection='A+black/A-green/B+red/B-blue;4leads UL1007AWG26,1000+-15,remoteM20-1060400',actual_hardware_measured=False,CAD_scope='Conservative external mechanical envelope, not internal rotor/inertia or measured thermal/torque model. STEP download requires login; not fetched. No purchase or energizing.')
def motor_delta(old):
 s=box(58.85,-84,-1.15,42.3,40,42.3)
 s=fuse(s,cyl(11,(80,-44,20),2.5,(0,1,0)));s=fuse(s,cyl(2.5,(80,-44,20),25,(0,1,0)))
 # Guaranteed D-flat region for the maximum-length material envelope.
 # Clock flat toward+X; split jaws contact the round +/-Z sides.
 s=cut(s,box(82.11,-34.25,16,3,15.35,8))
 for x in (64.5,95.5):
  for z in (4.5,35.5):s=cut(s,cyl(1.5,(x,-48.5,z),4.6,(0,1,0)))
 return {'MOTOR':s},{'MOTOR':'Purchase17HS15-1504S1 to A0648; conservative maxbody40/maxshaft25/maxpilot2.5; Dflat clock+X; manufacturer pilot height now dimensioned; material/internal dynamics not modelled'},[]
