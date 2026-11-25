"""Common GLOBAL-axis Palm winches: independent of Finger yaw, no radial module copying."""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from registered_winch_drive import lever_geometry

def separating_bound(vertices,points):
 x=np.asarray(vertices)*1000;y=np.asarray(points)*1000
 gap=float(np.maximum(y.min(0)-x.max(0),x.min(0)-y.max(0)).max())
 if gap>.2:return gap/1000
 hx=trimesh.convex.convex_hull(x);hy=trimesh.convex.convex_hull(y);axes=np.vstack([np.eye(3),hx.face_normals,hy.face_normals]);px=x@axes.T;py=y@axes.T;return float(np.maximum(py.min(0)-px.max(0),px.min(0)-py.max(0)).max())/1000

def modules(root,lever,ai,ao,pull):
 data=[]
 for i in range(3):
  for j in range(2):
   origin=np.fromstring(root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/CableConstraint").get('pullPoint'),sep=' ');mount=Rotation.from_euler('z',0 if origin[1]>0 else 180,degrees=True);centre=origin-mount.apply(ao);vertices=mount.apply(lever.vertices*.001)+centre;data.append(dict(finger=i,tendon=j,origin=origin,mount=mount,centre=centre,vertices=vertices,pull=centre+mount.apply(pull)))
 return data

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/yoke_hold_diagnostic1741/scene.scn';root=ET.parse(src).getroot();lever,ai,ao,pull,goal,stroke=lever_geometry();parts=modules(root,lever,ai,ao,pull);obstacles=[]
 for i in range(3):
  q=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);obstacles.append((f'FEM{i}',q))
  for n in root.find(f"Node[@name='guides{i}']").iter('Node'):
   mo=n.find('MechanicalObject');top=n.find('MeshTopology')
   if mo is not None and top is not None and top.get('triangles'):obstacles.append((f'guide{i}/{n.get("name")}',np.fromstring(mo.get('position'),sep=' ').reshape(-1,3)))
 initial=[];swept=[];wire=[];radius=float(np.linalg.norm(lever.vertices[:,1:],axis=1).max())*.001;anchor_radius=float(np.linalg.norm(ai[1:]));swept_bounds=[];wire_bounds=[]
 for d in parts:
  centre=d['centre'];v=d['vertices'];lo=v.min(0);hi=v.max(0);lo[1:]=centre[1:]-radius;hi[1:]=centre[1:]+radius;swept_bounds.append((lo,hi));wx=d['origin'][0];wlo=np.array([wx-.00025,centre[1]-anchor_radius-.00025,min(centre[2]-anchor_radius,d['pull'][2])-.00025]);whi=np.array([wx+.00025,centre[1]+anchor_radius+.00025,max(centre[2]+anchor_radius,d['pull'][2])+.00025]);wire_bounds.append((wlo,whi));gaps=[(name,separating_bound(v,q)) for name,q in obstacles];initial.append(dict(finger=d['finger'],tendon=d['tendon'],origin_m=d['origin'].tolist(),logical_centre_m=centre.tolist(),world_axis= d['mount'].apply([1,0,0]).tolist(),minimum_initial_finite_body_separating_gap_m=min(g for _,g in gaps),limiting_obstacle=min(gaps,key=lambda x:x[1])[0]));mesh=trimesh.Trimesh(v*1000,lever.faces,process=False);mesh.export(out/f'bank_f{d["finger"]}_t{d["tendon"]}_rest_mm.stl')
 for i in range(6):
  for j in range(i+1,6):
   l,h=swept_bounds[i];l2,h2=swept_bounds[j];gap=float(np.maximum(l2-h,l-h2).max());swept.append(dict(pair=[i,j],full_rotation_envelope_separating_gap_m=gap))
  for j in range(6):
   if i==j:continue
   l,h=wire_bounds[i];l2,h2=swept_bounds[j];gap=float(np.maximum(l2-h,l-h2).max());wire.append(dict(wire=i,other_rotor=j,full_rotation_envelope_separating_gap_m=gap))
 ok=all(d['minimum_initial_finite_body_separating_gap_m']>.0002 for d in initial) and all(d['full_rotation_envelope_separating_gap_m']>.0002 for d in swept+wire)
 d=dict(status='PASS_COMMON_AXIS_BANK_NECESSARY_GEOMETRY_ONLY' if ok else 'REJECT_COMMON_AXIS_BANK_GEOMETRY',initial=initial,rotor_rotor_swept=swept,input_wire_other_rotor_swept=wire,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src),lever_source_sha256=sha(BASE/'sofa/registered_winch_drive.py'),scope='Different Palm architecture: six parallel GLOBAL X axes, not radial copies. Original tendon origins retained, handedness chosen by worldYsign. Vertical output direction works independently of Finger yaw; lateral output motion differs, so new Native test required. Sufficient convex separating planes certify initial rotor/FEM/Guide clearance when bound>200um; no CSG tolerance floor. Full360degree rotor envelopes and input-wire envelopes conservatively prove all intermodule gaps, independent of relative phases. Own input-wire3pose proof is1891/92 only; output full-guide wire motion, palm/housing, actual bearing/anchor and strength NOT qualified. No actual gripping/object/dynamic collision/time/mesh PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k not in ('rotor_rotor_swept','input_wire_other_rotor_swept')},indent=2))
if __name__=='__main__':main()
