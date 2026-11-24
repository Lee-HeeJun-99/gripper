"""Conservative initial new-layer clearance against ALL existing Native parts.

AABB distance is a rigorous lower bound,not sampled point clearance. Positive
values certify separation for these modeled parts only,not absent CAD supports.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def boxgap(a,b):return float(np.linalg.norm(np.maximum(0,np.maximum(a.min(axis=0)-b.max(axis=0),b.min(axis=0)-a.max(axis=0)))))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';geom=BASE/'results/b3_contact_layer_geometry1336';g=json.loads((geom/'mesh.json').read_text());root=ET.parse(src/'scene.scn').getroot();records=[]
 for i,q in enumerate(np.array(g['world_reference_m'])):
  guides=[];wires=[];others=[]
  for j in range(3):
   if i!=j:
    film=np.fromstring(root.find(f"Node[@name='finger{j}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);others.append(boxgap(q,film));others.append(boxgap(q,np.array(g['world_reference_m'][j])))
   for cable in range(2):
    n=root.find(f"Node[@name='guides{j}']/Node[@name='cable{cable}']");guide=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ')
    for point in guide:
     near=trimesh.triangles.closest_point(q[np.array(g['triangles'])],np.repeat(point[None],len(g['triangles']),axis=0));guides.append(float(np.linalg.norm(near-point,axis=1).min()-np.hypot(.0015,.001)))
    path=np.vstack([pull,guide])
    for k in range(len(path)-1):wires.append(boxgap(q,path[k:k+2])-.00025)
  records.append(dict(finger=i,minimum_other_finger_or_layer_AABB_lower_bound_m=min(others),minimum_all_guide_proxy_gap_m=min(guides),minimum_all_wire_segment_AABB_capsule_lower_bound_m=min(wires)))
 safe=all(min(r[k] for k in r if k!='finger')>0 for r in records)
 d=dict(status='PASS_MODELED_INITIAL_NEW_PART_SEPARATION' if safe else 'BLOCKED_AABB_BOUND_INCONCLUSIVE_OR_COLLISION',records=records,input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','config.json')},geometry_sha256=sha(geom/'mesh.json'),scope='All three existing Native fingers/layers,all36guide spheres and all36finite wire segments. Same-Skin layer bond is intentional shared interface. Missing CAD support/palm/clamp solids and swept/dynamic clearance NOT QUALIFIED.',physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
