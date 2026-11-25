"""Actual finite lever vs force-port registration and necessary six-module assembly gate."""
import argparse,itertools,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_csg64 import register

def intersection(x,y):
 m=trimesh.boolean.intersection([x,y],engine='manifold64');v=float(m.volume) if len(m.faces) else 0;assert v>=0;return v
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register();src=BASE/'results/winch_outward1886/scene.scn';root=ET.parse(src).getroot();b3src=BASE/'results/yoke_hold_diagnostic1741/scene.scn';b3=ET.parse(b3src).getroot();records=[];corrected=[];wires=[]
 for j in range(2):
  drive=root.find(f"Node[@name='winch{j}']");q=np.fromstring(drive.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);mount=Rotation.from_quat(q[0,3:]);body=drive.find("Node[@name='body3']");centre=np.fromstring(body.find('MechanicalObject').get('position'),sep=' ')[:3];ports=drive.find("Node[@name='ports']");points=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);surface=drive.find("Node[@name='finiteRotor']");vertices=np.fromstring(surface.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(surface.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);local=mount.inv().apply(vertices-centre)*1000;portlocal=mount.inv().apply(points-centre)*1000;bounds=np.array([local.min(0),local.max(0)]);dist=np.linalg.norm(np.maximum(np.maximum(bounds[0]-portlocal,portlocal-bounds[1]),0),axis=1)
  # Proper registration change: rotate the finite lever around its own axle,
  # not the actuated points or Finger. Source had long axisZ but ports alongY.
  correction=mount*Rotation.from_euler('x',90,degrees=True)*mount.inv();newvertices=correction.apply(vertices-centre)+centre;mesh=trimesh.Trimesh(newvertices*1000,faces,process=False);assert mesh.is_volume;mesh.export(out/f'registered_rotor{j}_candidate_mm.stl');corrected.append(mesh);pull=np.fromstring(ports.find('CableConstraint').get('pullPoint'),sep=' ');trim=points[0]-.0007*(points[0]-pull)/np.linalg.norm(points[0]-pull);wire=trimesh.creation.cylinder(radius=.25,segment=np.stack([pull,trim])*1000,sections=32);assert wire.is_volume;wires.append(wire);wire.export(out/f'input_wire{j}_before_termination_mm.stl');hit=intersection(mesh,wire)
  records.append(dict(winch=j,actual_local_body_bounds_mm=bounds.tolist(),actual_local_force_ports_mm=portlocal.tolist(),port_to_original_body_AABB_distance_lower_bound_mm=dist.tolist(),proper_registration='Finite lever Rx90about own axle, end holes alignYplus/minus10; not applied to old Native',corrected_input_wire_intersection_mm3=hit))
 parts={}
 for i,angle in enumerate((0,120,240)):
  R=Rotation.from_euler('z',angle,degrees=True);T=np.eye(4);T[:3,:3]=R.as_matrix()
  for j in range(2):
   original=np.fromstring(root.find(f"Node[@name='fingerTendon{j}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)[0];origin=np.fromstring(b3.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/CableConstraint").get('pullPoint'),sep=' ');assert abs(R.apply(original)-origin).max()<1e-12;m=corrected[j].copy();m.apply_transform(T);parts[f'finger{i}_winch{j}']=m
 hits=[]
 for (left,x),(right,y) in itertools.combinations(parts.items(),2):
  if np.any(x.bounds[1]<y.bounds[0]) or np.any(y.bounds[1]<x.bounds[0]):continue
  v=intersection(x,y)
  if v>0:hits.append(dict(pair=[left,right],intersection_mm3=v))
 d=dict(status='REJECT_THREE_FINGER_PACKING_OR_INPUT_WIRE' if hits or any(r['corrected_input_wire_intersection_mm3']>0 for r in records) else 'NECESSARY_REGISTERED_GEOMETRY_GATE_ONLY',original_registration_status='FAIL_OFF_BODY_FORCE_PORTS' if any(min(r['port_to_original_body_AABB_distance_lower_bound_mm'])>0 for r in records) else 'CHECK',records=records,six_module_intersections=hits,source_sha256=sha(Path(__file__)),inputs_sha256={str(p):sha(p) for p in [src,b3src]},scope='New read-only registration audit: actual1886finite collider long axisZ while physical end portsY, lower-bound9mm gap proves missing force-bearing arm geometry; Native scalar force-port results remain historical idealized results, not hardware qualification. Rx90solid candidate corrects registration while preserving volume/COM/axial inertia but changes full tensor/collider and was NOT run Native. Actual0.5mm input wire includes all except declared last0.7mm termination domain; any positive intersection rejects. Six registered modules copied only for initial geometry, not equilibrated motion. No part removed, no size/force/tolerance scan, no old verdict changed. Need actual registered lever/input anchor and real Palm layout before3Finger Native.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
