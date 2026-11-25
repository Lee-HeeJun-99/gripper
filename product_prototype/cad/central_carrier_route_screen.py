"""Necessary clearance gate for a new single central transverse-carrier drive."""
import argparse,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/capillary_hold1700/scene.scn';root=ET.parse(source).getroot();sphere=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];records=[]
 for i in range(3):
  node=root.find(f"Node[@name='guides{i}']");routes=[]
  for j in range(2):
   c=node.find(f"Node[@name='cable{j}']");routes.append(np.vstack([np.fromstring(c.find('CableConstraint').get('pullPoint'),sep=' '),np.fromstring(c.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)]))
  points=(routes[0]+routes[1])/2;pieces=[];gaps=[]
  for k,(x,y) in enumerate(zip(points[:-1],points[1:])):
   delta=y-x;u=float(np.clip((sphere-x)@delta/(delta@delta),0,1));distance=np.linalg.norm(x+u*delta-sphere);gaps.append(dict(segment=k,projection_fraction=u,centreline_sphere_gap_mm=float((distance-.03)*1000),capsule_sphere_gap_mm=float((distance-.03-.00025)*1000)));pieces.append(trimesh.creation.cylinder(radius=.00025,segment=np.stack([x,y]),sections=16))
  trimesh.util.concatenate(pieces).export(out/f'finger{i}_central_wire_m.stl');records.append(dict(finger=i,route_m=points.tolist(),segments=gaps))
 inside=sum(r['centreline_sphere_gap_mm']<0 for f in records for r in f['segments']);d=dict(status='REJECTED_CENTRAL_CARRIER_ROUTE' if inside else 'NECESSARY_WIRE_GATE_ONLY_NOT_ASSEMBLY_PASS',centreline_inside_object_segments=inside,minimum_capsule_gap_mm=min(r['capsule_sphere_gap_mm'] for f in records for r in f['segments']),records=records,source_sha256=sha(Path(__file__)),input_scene_sha256=sha(source),native_run=False,scope='New one-central-tendon/six transverse-carrier mechanism necessary gate. Same mean normal moment arm, wire radius0.25mm and sphere R30. Centreline intersection itself proves obstruction, not only a bounding-ball estimate. No old collision model disabled or Native scene modified. Carrier/anchor/mass/assembly NOT IMPLEMENTED because routing failed; not all reroutings ruled out.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
