"""Parametric laminated pressure-pocket concept,NOT fabricated/sealed gripper.
Finite port bore is meshed explicitly; no unavailable boolean/STEP kernel claim.
All dimensions mm. Flexible seam/frame manufacture and materials TBD.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1]

def bored_end():
 corner=np.arctan(.7/6);angles=sorted(set(np.linspace(0,2*np.pi,48,endpoint=False).tolist()+[corner,np.pi-corner,np.pi+corner,2*np.pi-corner]));n=len(angles);vertices=[]
 for x in (22,25):
  for inner in (False,True):
   for t in angles:
    c,s=np.cos(t),np.sin(t);r=.4 if inner else min(6/abs(c) if abs(c)>1e-15 else np.inf,.7/abs(s) if abs(s)>1e-15 else np.inf);vertices.append([x,r*c,r*s])
 faces=[]
 for i in range(n):
  j=(i+1)%n
  for a,b,c,d in [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]:faces.extend([[a,b,c],[a,c,d]])
 m=trimesh.Trimesh(vertices=vertices,faces=faces,process=True);m.fix_normals();return m,float(min(.4*np.cos((angles[(i+1)%n]-angles[i])%(2*np.pi)/2) for i in range(n))-.39)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);parts={}
 def box(name,dims,centre):
  m=trimesh.creation.box(extents=dims);m.apply_translation(centre);parts[name]=m
 for i in range(8):box(f'PET_layer_{i+1}',[40,10,.1],[0,0,-.575+.05+i*.15])
 box('upper_membrane',[50,18,.1],[0,0,.75]);box('lower_membrane',[50,18,.1],[0,0,-.75]);box('seal_band_y_minus',[50,3,1.4],[0,-7.5,0]);box('seal_band_y_plus',[50,3,1.4],[0,7.5,0]);box('seal_band_x_minus',[3,12,1.4],[-23.5,0,0]);end,portgap=bored_end();parts['seal_band_port_end']=end;tube=trimesh.creation.annulus(r_min=.2,r_max=.39,height=7.1,sections=48);tube.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]));tube.apply_translation([25.45,0,0]);parts['port_tube_concept']=tube
 for name,m in parts.items():m.export(out/(name+'.stl'))
 trimesh.util.concatenate(list(parts.values())).export(out/'assembly.stl')
 params=dict(units='mm',layers=8,layer_length=40,layer_width=10,layer_thickness=.1,layer_air_gap=.05,pocket_inner=[44,12,1.4],outer=[50,18,1.6],membrane_thickness=.1,port_bore_radius=.4,port_tube_outer_radius=.39,port_tube_inner_radius=.2,materials='NOT SELECTED/PET proxy;no measured moduli/friction/seal strength',operating_pressure_Pa=None,seal_process='TBD;flexible seal bands are geometric envelopes,not validated manufacturing joints');(out/'parameters.json').write_text(json.dumps(params,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 scad=['// Concept pressure pocket ONLY,not Native result or fabrication release. Dimensions mm.']
 scad.extend(f'import("{name}.stl");' for name in parts);(out/'assembly.scad').write_text('\n'.join(scad))
 with (out/'BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['part','quantity','material','qualification']);w.writerows([[name,1,'UNKNOWN;PET proxy for layers','GEOMETRY ONLY;seal,bond,pressure,fatigue NOT MEASURED'] for name in parts])
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="440"><rect width="900" height="440" fill="white"/><g fill="none" stroke="black"><rect x="80" y="80" width="500" height="180"/><rect x="110" y="110" width="440" height="120"/><rect x="130" y="120" width="400" height="100"/><rect x="550" y="166" width="70" height="8"/></g><g font-family="sans-serif" font-size="16"><text x="30" y="30">LAMINATED PRESSURE POCKET — CONCEPT CAD, NOT SIMULATION</text><text x="80" y="65">Outer 50 x 18 mm / inner 44 x 12 mm / stack 40 x 10 mm</text><text x="80" y="300">8 x 0.10 mm layers; 0.05 mm air gaps; pocket H1.4 mm</text><text x="80" y="330">Membranes0.10 mm; port ID0.40 / OD0.78 mm; bore0.80 mm</text><text x="80" y="360">Seal/bond/material/pressure/moving clearance NOT VALIDATED</text><text x="80" y="390">Not integrated with B3; STEP and fabrication readiness BLOCKED</text></g></svg>';(out/'dimensions.svg').write_text(svg)
 d=dict(status='PARAMETRIC_POCKET_GEOMETRY_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),parts=len(parts),all_parts_watertight=all(m.is_watertight for m in parts.values()),minimum_interlayer_gap_mm=.05,stack_membrane_gap_mm=.125,stack_end_clearance_mm=2,stack_width_clearance_mm=1,port_finite_mesh_radial_clearance_mm=portgap,minimum_endwall_thickness_mm=.3,pressure_seal='NOT VALIDATED;nominal port clearance requires real sealed joint',dynamic_interference='NOT MEASURED',Native_jamming='NOT VALIDATED',STEP='NOT GENERATED',fabrication_ready=False);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
