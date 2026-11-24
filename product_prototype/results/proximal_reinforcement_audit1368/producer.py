"""Read-only original-graph and added-material audit;not hardware qualification."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 old=BASE/'results/b3_railback_grasp1001298';new=BASE/'results/proximal_reinforcement_damped_pilot1367';roots=[ET.parse(x/'scene.scn').getroot() for x in (old,new)]
 for root in roots:
  for n in list(root):
   if (n.tag=='Node' and n.get('name','').startswith(('layerFree','contactLayer'))) or n.tag=='NativeContactRows':root.remove(n)
  for i in range(3):
   f=root.find(f"Node[@name='finger{i}']")
   for n in list(f):
    if n.tag=='Node' and n.get('name') in ('skinCollision','railCollision'):f.remove(n)
  for n in root.iter():
   n.text=None;n.tail=None
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(new),str(old)))
 assert ET.tostring(roots[0])==ET.tostring(roots[1]),'Original physical graph changed'
 g=json.loads((new/'pad_mesh.json').read_text());q=[np.array(x) for x in g['world_reference_m']];gaps=[]
 for i,j in ((0,1),(0,2),(1,2)):gaps.append(float(np.linalg.norm(np.maximum(0,np.maximum(q[i].min(0)-q[j].max(0),q[j].min(0)-q[i].max(0))))))
 assert min(gaps)>0
 root=ET.parse(new/'scene.scn').getroot();damping=[]
 for i in range(3):
  f=root.find(f"Node[@name='finger{i}']");r=root.find(f"Node[@name='contactLayer{i}']")
  for tag,key in [('UniformMass','rayleighMass'),('TetrahedronFEMForceField','rayleighStiffness')]:
   assert f.find(tag).get(key)==r.find(tag).get(key);damping.append(float(r.find(tag).get(key)))
 local=np.array(g['local_positions_mm']);assert g['root_free_fixed_indices']==np.flatnonzero(local[1::2,0]<=5).tolist()
 d=dict(status='PASS_LIMITED_GRAPH_AND_INITIAL_GEOMETRY_AUDIT',original_physical_graph_equal_after_declared_collision_and_observer_changes=True,extension_pair_AABB_lower_bounds_m=gaps,matched_rayleigh_values=damping,original_guide_mapping_preserved=True,scope='Initial geometry and XML contract only. No dynamic clearance, clamp strength, mass-property measurement or convergence certification.',input_hashes={str(x.relative_to(BASE)):sha(x) for x in (old/'scene.scn',new/'scene.scn',new/'pad_mesh.json')})
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
