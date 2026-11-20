"""Execute INSIDE FreeCAD Python only. No fake STEP or legacy flat fallback.

Shared neutral CSG recipe includes exact faceted B3 reference. Triangulated B3
shells become faceted BRep solids,NOT smooth manufactured-surface certification.
This source is syntax-checked here;kernel execution remains BLOCKED if absent.
"""
import argparse,json
from pathlib import Path

def main():
 import FreeCAD as App
 import Part
 p=argparse.ArgumentParser();p.add_argument('--recipe',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();data=json.loads(a.recipe.read_text());a.out.mkdir(parents=True,exist_ok=False);doc=App.newDocument('ReGripManufacturingCandidate');V=App.Vector
 def shape(op):
  kind=op['op']
  if kind=='box':
   lo,hi=op['lo'],op['hi'];s=Part.makeBox(*[hi[i]-lo[i] for i in range(3)],V(*lo))
  elif kind=='cylinder':
   z0,z1=op['z'];xy=op['xy']
   if op['sections']==6:
    import math
    points=[V(xy[0]+op['radius']*math.cos(k*math.pi/3),xy[1]+op['radius']*math.sin(k*math.pi/3),z0) for k in range(6)];s=Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,z1-z0))
   else:s=Part.makeCylinder(op['radius'],z1-z0,V(*xy,z0))
  elif kind=='polyhedron':
   vertices=op['vertices'];faces=[]
   for tri in op['faces']:
    points=[V(*vertices[i]) for i in tri];faces.append(Part.Face(Part.makePolygon(points+[points[0]])))
   s=Part.makeSolid(Part.makeShell(faces))
  elif kind=='transform':
   s=shape(op['shape']);m=App.Matrix()
   for row in range(4):
    for col in range(4):setattr(m,f'A{row+1}{col+1}',op['matrix'][row][col])
   s=s.transformGeometry(m)
  elif kind in ('union','difference'):
   items=[shape(x) for x in op['items']];s=items[0]
   for item in items[1:]:s=s.fuse(item) if kind=='union' else s.cut(item)
  else:raise ValueError('unsupported shared CAD operation '+kind)
  if not s.isValid() or s.Volume<=0:raise ValueError('invalid BRep solid '+kind)
  return s
 objects=[]
 for part in data['parts']:
  obj=doc.addObject('PartDesign::Feature',part['name']);obj.Label=part['name'];obj.Shape=shape(part['shape']);obj.addProperty('App::PropertyString','Qualification').Qualification=part['role'];obj.Shape.exportStep(str(a.out/(part['name']+'.step')));objects.append(obj)
 doc.recompute();Part.export(objects,str(a.out/'assembly.step'));doc.saveAs(str(a.out/'assembly.FCStd'))
 (a.out/'status.json').write_text(json.dumps(dict(status='BREP_EXPORT_EXECUTED_NOT_FABRICATION_QUALIFIED',parts=len(objects),faceted_B3_reference=True,interference_and_strength_verified=False),indent=2))
if __name__=='__main__':main()
