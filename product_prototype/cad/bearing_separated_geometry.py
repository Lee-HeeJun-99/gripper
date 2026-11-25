"""Finite supported hollow journal plus separate return shaft; actual saved-angle replay."""
import argparse,csv,itertools,json,sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_csg64 import register
from bellcrank_link_geometry import cylinder

def shaft(angles):
 zs=np.r_[-2.,np.linspace(-1.8,1.2,17),1.45];theta=np.interp(zs,[-2,-1.8,-.3,1.2,1.45],[0,0,angles[0],angles[1],angles[1]]);vertices=[]
 for z,t in zip(zs,theta):
  a=np.arange(32)*2*np.pi/32+t;vertices.extend(np.column_stack([.25*np.cos(a),.25*np.sin(a),np.full(32,z)]))
 faces=[]
 for k in range(len(zs)-1):
  for j in range(32):
   p=k*32+j;q=k*32+(j+1)%32;faces.extend([[p,q,q+32],[p,q+32,p+32]])
 for j in range(1,31):faces.extend([[0,j+1,j],[(len(zs)-1)*32,(len(zs)-1)*32+j,(len(zs)-1)*32+j+1]])
 m=trimesh.Trimesh(vertices=np.asarray(vertices),faces=np.asarray(faces),process=False);assert m.is_volume;return m

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register()
 rotor=trimesh.boolean.union([trimesh.creation.box([24,2,1]),cylinder(2.5,2.7,[0,0,.35])],engine='manifold64');rotor=trimesh.boolean.difference([rotor,cylinder(1.55,2.4,[0,0,0]),cylinder(.25,.25,[0,0,1.325]),*[cylinder(.3,2,[x,0,0]) for x in (-10,10)]],engine='manifold64')
 # Integral housing: sleeve has0.2mm positive overlap into base before union,
 # rather than relying on roundoff-sensitive coincident endfaces.
 housing=trimesh.boolean.union([cylinder(3.5,.8,[0,0,-2.2]),cylinder(1.5,3.,[0,0,-.5])],engine='manifold64');housing=trimesh.boolean.difference([housing,cylinder(.35,2.9,[0,0,-.35]),cylinder(.25,.2,[0,0,-1.9])],engine='manifold64')
 source=BASE/'results/bearing_native1870/states.csv';rows=list(csv.DictReader(source.open()));poses=[np.zeros(2)]+[Rotation.from_quat(np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7)[1:,3:]).as_rotvec()[:,0] for row in rows];records=[];parts_at_rest={}
 for k,angles in enumerate(poses):
  moving=rotor.copy()
  T=np.eye(4);T[:3,:3]=Rotation.from_rotvec([0,0,float(angles[-1])]).as_matrix();moving.apply_transform(T);parts=dict(rotor=moving,housing=housing,return_shaft=shaft(angles));hits=[]
  for name,m in parts.items():
   assert m.is_volume and len(m.split(only_watertight=False))==1,name
   if k==0:m.export(out/f'{name}_rest_mm.stl');parts_at_rest[name]=dict(volume_mm3=float(m.volume),COM_mm=m.center_mass.tolist(),unit_density_inertia_mm5=m.moment_inertia.tolist())
  for (left,x),(right,y) in itertools.combinations(parts.items(),2):
   overlap=trimesh.boolean.intersection([x,y],engine='manifold64');volume=float(overlap.volume) if len(overlap.faces) else 0.
   if volume!=0 or (len(overlap.faces) and not overlap.is_volume):hits.append(dict(pair=[left,right],intersection_mm3=volume,faces=len(overlap.faces),positive_closed_volume=bool(overlap.is_volume),invalid_signed_intersection=bool(volume<0)))
  records.append(dict(sample=k,twist_angles_rad=np.asarray(angles).tolist(),positive_intersections=hits))
 d=dict(status='PASS_SAMPLED_BEARING_SEPARATION_GEOMETRY_ONLY' if not any(r['positive_intersections'] for r in records) else 'REJECTED_FINITE_BEARING_GEOMETRY',records=records,components=parts_at_rest,source_sha256=sha(Path(__file__)),source_angles_sha256=sha(source),configuration=dict(rotor_hub_outer_radius_mm=2.5,radial_bore_radius_mm=1.55,sleeve_outer_radius_mm=1.5,sleeve_inner_radius_mm=.35,return_shaft_radius_mm=.25,free_return_length_mm=3,root_socket_length_mm=.2,rotor_socket_length_mm=.25,radial_bearing_gap_mm=.05),scope='New three finite connected solids and actual1870angles replay only; changed rotor mass/inertia, not same as1870Native assembly. Return shaft socket fits are ideal zero-thickness bonds, retention/material/adhesive/press fit NOT MEASURED. Root and cap bond lengths explicit; ring bore does not erase wire/object collision. Hollow sleeve transfers radial load to fixed housing; return shaft passes inside.50um radial gap remains incompatible with inherited200um contact buffer if actual contact bearings used. Ideal projective bearing is not validated finite bearing friction/contact/compliance. Faceted twist shaft is a kinematic replay, NOT a new Native FEM solution, swept proof or stress test. No Finger/wire route/grasp/STEP qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
