"""Executable OpenSCAD source from SAME neutral CSG. Not kernel execution."""
import argparse,json
from pathlib import Path

def emit(op):
 kind=op['op']
 if kind=='box':
  lo,hi=op['lo'],op['hi'];return 'translate('+json.dumps(lo)+') cube('+json.dumps([hi[i]-lo[i] for i in range(3)])+');'
 if kind=='cylinder':
  z0,z1=op['z'];return f'translate({json.dumps([*op["xy"],z0])}) cylinder(h={z1-z0},r={op["radius"]},$fn={op["sections"]});'
 if kind=='polyhedron':return 'polyhedron(points='+json.dumps(op['vertices'])+',faces='+json.dumps(op['faces'])+',convexity=20);'
 if kind=='transform':return 'multmatrix('+json.dumps(op['matrix'])+') {'+emit(op['shape'])+'}'
 if kind in ('union','difference'):return kind+'(){'+''.join(emit(s) for s in op['items'])+'}'
 raise ValueError('unsupported shared CAD operation')

def main():
 p=argparse.ArgumentParser();p.add_argument('--recipe',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();data=json.loads(a.recipe.read_text());a.out.parent.mkdir(parents=True,exist_ok=True)
 with a.out.open('x') as stream:
  stream.write('// ReGrip PARAMETRIC DESIGN,NOT SOFA motion or fabrication qualification.\n// CSG regeneration source is manufacturing_assembly.py + shared config.\npart="assembly";\n')
  for i,part in enumerate(data['parts']):stream.write(f'module part_{i}(){{'+emit(part['shape'])+'}\n')
  stream.write('if(part=="assembly"){'+''.join(f'part_{i}();' for i in range(len(data['parts'])))+'}\n')
  for i,part in enumerate(data['parts']):stream.write(f'if(part=={json.dumps(part["name"])}) part_{i}();\n')
 print('SCAD source written;OpenSCAD kernel NOT executed')
if __name__=='__main__':main()
