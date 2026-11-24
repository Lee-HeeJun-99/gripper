"""Stored Native new-rung material vs actual deforming FEM; no state writes.
Sampled solid CSG at declared accepted times. Not a swept collision certificate.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from yoke_bond_material_audit import surface

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();records=[];tests=0
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);raw=surface(parent.find("Node[@name='dorsalYoke']"));supports=[surface(parent.find(f"Node[@name='cable{j}']/Node[@name='support5']")) for j in range(2)];new=trimesh.boolean.difference([raw,*supports],engine='manifold');local=Rotation.from_quat(q0[5,3:]).inv().apply(new.vertices-q0[5,:3]);frames=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));film=list(csv.DictReader((src/f'finger{i}.csv').open()));tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);assert len(frames)==len(film)
  # Initial state and eight uniformly indexed saved states, including final.
  initial=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
  samples=[(0.,q0,initial)]+[(float(frames[k]['time_s']),np.fromstring(frames[k]['rigid_q'],sep=' ').reshape(-1,7),np.fromstring(film[k]['q_m'],sep=' ').reshape(-1,3)) for k in np.unique(np.linspace(0,len(film)-1,8,dtype=int))]
  for time,q,positions in samples:
   moved=trimesh.Trimesh(Rotation.from_quat(q[5,3:]).apply(local)+q[5,:3],new.faces,process=False);vertices=positions[tet];mask=np.all(vertices.max(1)>=moved.bounds[0],axis=1)&np.all(vertices.min(1)<=moved.bounds[1],axis=1);hits=[]
   for k in np.flatnonzero(mask):
    cell=trimesh.convex.convex_hull(vertices[k]);hit=trimesh.boolean.intersection([moved,cell],engine='manifold');tests+=1
    if len(hit.faces) and hit.volume>0:hits.append(dict(tetrahedron=int(k),overlap_mm3=float(hit.volume)*1e9))
   records.append(dict(time_s=time,finger=i,positive_solid_intersections=hits))
 d=dict(status='POSITIVE_SAMPLED_NEW_MATERIAL_FEM_INTERSECTION' if any(r['positive_solid_intersections'] for r in records) else 'NO_POSITIVE_SAMPLED_NEW_MATERIAL_FEM_INTERSECTION',case=a.case,records=records,cell_tests=tests,source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn','mesh.json']+[f'guide_frames{i}.csv' for i in range(3)]+[f'finger{i}.csv' for i in range(3)]},scope='Manifold finite precision on stored actual candidate geometry and accepted FEM; original support/rung weld volumes explicitly removed. Initial+8saved states per finger ONLY, not every step/swept. Positive tiny volumes require numerical scale diagnosis, not an arbitrary ignored-volume floor. No Native contact-response claim because intentional bonded same-finger group is inherited.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
