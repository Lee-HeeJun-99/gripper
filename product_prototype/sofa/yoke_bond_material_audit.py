"""Independent solid audit: intended old support welds vs NEW FEM intrusion.
Exact solid operations on stored faceted geometry (Manifold finite precision),
not a physical strength/tolerance result or non-faceted universal proof.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha

def surface(node):
 return trimesh.Trimesh(np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3),np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3),process=False)

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();records=[]
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");y=surface(parent.find("Node[@name='dorsalYoke']"));supports=[surface(parent.find(f"Node[@name='cable{j}']/Node[@name='support5']")) for j in range(2)]
  added=trimesh.boolean.difference([y,*supports],engine='manifold');assert added.is_watertight and added.volume>0 and added.body_count==1;added.density=1000.;mp=added.mass_properties
  film=root.find(f"Node[@name='finger{i}']");q=np.fromstring(film.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);tet=np.fromstring(film.find('MeshTopology').get('tetrahedra'),sep=' ',dtype=int).reshape(-1,4);mask=np.all(q[tet].max(1)>=added.bounds[0],axis=1)&np.all(q[tet].min(1)<=added.bounds[1],axis=1);bad=[]
  for k in np.flatnonzero(mask):
   cell=trimesh.convex.convex_hull(q[tet[k]]);hit=trimesh.boolean.intersection([added,cell],engine='manifold')
   if len(hit.faces) and hit.volume>0:bad.append(dict(tetrahedron=int(k),new_overlap_mm3=float(hit.volume)*1e9))
  added.export(out/f'finger{i}_new_material_only_m.stl');records.append(dict(finger=i,complete_yoke_volume_mm3=float(y.volume)*1e9,added_material_volume_mm3=float(added.volume)*1e9,intended_original_support_union_overlap_mm3=float(y.volume-added.volume)*1e9,added_mass_kg=float(mp.mass),added_COM_m=mp.center_mass.tolist(),added_inertia_COM_kg_m2=mp.inertia.tolist(),tested_FEM_cells=int(mask.sum()),new_material_FEM_overlap=bad))
 d=dict(status='PASS_NEW_YOKE_MATERIAL_FEM_SEPARATION_ONLY' if all(not x['new_material_FEM_overlap'] for x in records) else 'FAIL_NEW_YOKE_MATERIAL_FEM_OVERLAP',case=a.case,records=records,source_sha256=sha(Path(__file__)),input_scene_sha256=sha(src/'scene.scn'),scope='Original two terminal supports are the declared intended weld domains, not arbitrary same-finger collision omissions. Subtract those actual solids before checking newly introduced material against EVERY broad-phase tetrahedron. Manifold faceted CSG, no modified Skin or old result. Material duplicated inside old support must NOT be counted twice in added mass. Density1000kg/m3 is a research assumption, real bond rigidity/strength NOT MEASURED. No dynamic/swept claim.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
