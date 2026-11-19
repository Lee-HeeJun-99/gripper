"""Run INSIDE FreeCAD Python:parameterized true solids,STEP/STL export.
Not executed in this environment:FreeCAD/OCC unavailable. No fake STEP fallback.
Set REGRIP_CAD_OUT to a new unique destination before FreeCADCmd execution.
"""
import os,json,math
from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path(__file__).resolve().parents[1]
def main():
 c=json.loads((ROOT/'config/design_v1.json').read_text());out=Path(os.environ['REGRIP_CAD_OUT']);out.mkdir(parents=True,exist_ok=False);f=c['finger'];td=c['tendon'];p=c['palm'];V=App.Vector;doc=App.newDocument('ReGripCandidate')
 def poly(points,h):return Part.Face(Part.makePolygon([V(*v) for v in points+[points[0]]])).extrude(V(0,0,h))
 def w(x):return f['root_width']+(f['tip_width']-f['root_width'])*max(0,x-50)/50
 skin=poly([[x,y,0] for x,y in ((0,-12),(50,-12),(100,-6),(100,6),(50,12),(0,12))],f['skin_thickness'])
 rails=[]
 for side in (-1,1):rails.append(poly([[x,y,-f['rail_thickness']] for x,y in ((0,side*12),(50,side*12),(100,side*6),(100,side*(6-f['rail_width'])),(50,side*(12-f['rail_width'])),(0,side*(12-f['rail_width'])))],f['rail_thickness']))
 palm=Part.makeCylinder(p['outer_radius'],8,V(0,0,5)).cut(Part.makeCylinder(p['inner_radius'],10,V(0,0,4)))
 for angle in p['angles_deg']:
  a=math.radians(angle)
  for y in (-14,14):palm=palm.cut(Part.makeCylinder(1.7,10,V(50*math.cos(a)+y*math.sin(a),50*math.sin(a)-y*math.cos(a),4)))
 mount=Part.makeBox(7,36,4+f['skin_thickness'],V(0,-18,-4)).fuse(Part.makeBox(5,36,14,V(-5,-18,-7)))
 clamp=Part.makeBox(5,36,3,V(0,-18,f['skin_thickness']))
 for y in (-14,14):
  mount=mount.cut(Part.makeCylinder(1.7,10,V(2.5,y,-5))).cut(Part.makeCylinder(1.7,7,V(-6,y,0),V(1,0,0)))
  clamp=clamp.cut(Part.makeCylinder(1.7,5,V(2.5,y,-1)))
 mount=mount.cut(Part.makeBox(7,f['root_width'],5,V(0,-f['root_width']/2,-f['rail_thickness'])))
 guide=Part.makeCylinder(td['guide_outer_radius'],2,V(-1,0,0),V(1,0,0)).cut(Part.makeCylinder(td['guide_hole_radius'],4,V(-2,0,0),V(1,0,0)))
 anchor=Part.makeBox(4,4,2,V(-2,-2,-1)).cut(Part.makeCylinder(.6,4,V(0,0,-2)))
 pulley=Part.makeCylinder(8,5).fuse(Part.makeCylinder(10,1)).fuse(Part.makeCylinder(10,1,V(0,0,4))).cut(Part.makeCylinder(3,7,V(0,0,-1)))
 plate=Part.makeBox(50,40,4,V(-25,-20,17))
 for x in (-15,15):plate=plate.cut(Part.makeBox(3.4,24,6,V(x-1.7,-12,16)).fuse(Part.makeCylinder(1.7,6,V(x,-12,16))).fuse(Part.makeCylinder(1.7,6,V(x,12,16))))
 coupling=Part.makeCylinder(8,12).cut(Part.makeCylinder(3,14,V(0,0,-1))).cut(Part.makeBox(9,1,8,V(0,-.5,5))).cut(Part.makeCylinder(1.7,18,V(-9,0,9),V(1,0,0)))
 fastener=Part.makeCylinder(1.5,16).fuse(Part.makeCylinder(2.75,3,V(0,0,16)))
 parts=dict(skin=skin,rail_left=rails[0],rail_right=rails[1],palm=palm,mount=mount,clamp=clamp,guide=guide,anchor=anchor,pulley=pulley,motor_plate=plate,coupling=coupling,fastener_placeholder=fastener)
 for name,shape in parts.items():
  if not shape.isValid() or shape.Volume<=0:raise RuntimeError('invalid solid:'+name)
  shape.exportStep(str(out/(name+'.step')));shape.exportStl(str(out/(name+'.stl')))
 assembly=[palm,plate]
 for angle in p['angles_deg']:
  a=math.radians(angle);R=App.Matrix();R.A11=0;R.A12=math.sin(a);R.A13=-math.cos(a);R.A14=50*math.cos(a);R.A21=0;R.A22=-math.cos(a);R.A23=-math.sin(a);R.A24=50*math.sin(a);R.A31=-1;R.A32=0;R.A33=0
  local=[skin,*rails,mount,clamp]
  for x in td['guide_stations']:
   for side in (-1,1):g=guide.copy();g.translate(V(x,side*(w(x)/2+td['outboard']),td['normal_offset']));local.append(g)
  for s in local:assembly.append(s.transformGeometry(R))
 compound=Part.makeCompound(assembly);compound.exportStep(str(out/'assembly.step'));compound.exportStl(str(out/'assembly.stl'));obj=doc.addObject('PartDesign::Feature','CandidateAssembly');obj.Shape=compound;doc.recompute();doc.saveAs(str(out/'candidate.FCStd'))
 (out/'status.json').write_text(json.dumps(dict(status='CAD_SOLIDS_CREATED_NOT_FABRICATION_READY',parts=list(parts),notes=['guide supports,anchors and drivetrain not integrated in STEP assembly','M3/shaft/motor dimensions provisional','no dynamic interference qualification']),indent=2))
main()
