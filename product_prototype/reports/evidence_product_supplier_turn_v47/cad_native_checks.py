"""Publish shared native-guide rest CAD inputs and limited static interference checks."""
import argparse,json,shutil,hashlib,math
from pathlib import Path
import numpy as np
import trimesh
from generate import world,width
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--mesh',required=True);p.add_argument('--name',required=True);a=p.parse_args();src=BASE/'meshes'/a.mesh;out=BASE/'drawings'/a.name;out.mkdir(exist_ok=False);c=json.loads((src/'config.json').read_text());mesh=json.loads((src/'mesh.json').read_text());td=c['tendon'];centres=[];wires=[]
 for angle in c['palm']['angles_deg']:
  group=[]
  for side in (-1,1):
   points=np.array([world(c,[x,side*(width(c,x)/2+td['outboard']),td['normal_offset']],angle) for x in [0]+td['guide_stations']]);wires.append(points);group.extend(points[1:])
  centres.append(np.array(group))
 body=np.array(c['simulation']['sphere_center_mm']);R=c['simulation']['sphere_radius_mm'];gR=math.hypot(td['guide_outer_radius'],1);guide_object=min(float(np.linalg.norm(group-body,axis=1).min()-R-gR) for group in centres);between=min(float(np.linalg.norm(centres[i][:,None]-centres[j][None,:],axis=2).min()-2*gR) for i,j in ((0,1),(1,2),(0,2)));wire=1e9
 for points in wires:
  start=points[:-1];d=np.diff(points,axis=0);u=np.clip(np.sum((body-start)*d,axis=1)/np.sum(d*d,axis=1),0,1);wire=min(wire,float(np.linalg.norm(start+u[:,None]*d-body,axis=1).min()-R-td['wire_radius']))
 parts={}
 for name in ('skin','rail_left','rail_right','finger_bonded'):
  m=trimesh.load_mesh(src/(name+'.stl'));parts[name]=dict(watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),volume_mm3=float(m.volume))
 for name in ('assembly.scad','orthographic.svg','config.json'):shutil.copy2(src/name,out/name)
 shutil.copy2(src/'BOM.csv',out/'REGRIP_BOM.csv')
 result=dict(status='STATIC_INPUT_CHECKS_ONLY_NOT_ASSEMBLY_VERIFIED',geometry_config_sha256=sha(src/'config.json'),source_sha256=sha(Path(__file__)),STL=parts,initial_finite_wire_object_gap_mm=wire,initial_enclosing_guide_sphere_object_gap_mm=guide_object,initial_guide_finger_pair_gap_mm=between,guide_hole_radial_wire_clearance_mm=td['guide_hole_radius']-td['wire_radius'],guide_support='three-point foot geometry matches native rigidification subset pattern;material/compliance/solid Boolean NOT verified',guide_mass='10mg/frame research assumption;not measured bracket+eyelet mass',anchor='terminal eyelet at same centre as native last cable point;no duplicate displaced anchor;end-stop strength unverified',moving_clearance='NOT VERIFIED by rest checks;use actual state audit separately',bend_radius='NOT MEASURED:ideal polyline and guide hole radius are NOT physical wire bend radius',STEP='NOT GENERATED:FreeCAD/OpenSCAD/OCC absent',physical_fabrication_ready=False)
 (out/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
