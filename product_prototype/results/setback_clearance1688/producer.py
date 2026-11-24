"""Independent actual accepted-pose finite hardware clearance, not contact counts.
Convex-envelope separation is sufficient; overlap is not necessarily annular
solid overlap. Report uncertainty rather than invent a clearance PASS.
"""
import argparse,csv,itertools,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from finite_support_sat import sat

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();parts=[];times=None;objectrows=list(csv.DictReader((src/'object.csv').open()));centres=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in objectrows]);R=.03;objectgap=1.;objectworst=None
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);rr=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));t=np.array([float(r['time_s']) for r in rr]);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rr]);rot=Rotation.from_quat(q[:,:,3:].reshape(-1,4)).as_matrix().reshape(len(q),-1,3,3)
  if times is None:times=t
  else:assert np.array_equal(times,t)
  for j in range(2):
   for node in parent.find(f"Node[@name='cable{j}']").findall('Node'):
    if not node.get('name','').startswith(('eyelet','support')):continue
    v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);f=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);o=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);local=Rotation.from_quat(q0[o,3:]).inv().apply(v-q0[o,:3]);hull=trimesh.convex.convex_hull(local);mapped=np.einsum('tij,vj->tvi',rot[:,o],hull.vertices)+q[:,o,None,:3]
    parts.append(dict(finger=i,cable=j,name=node.get('name'),vertices=mapped,faces=hull.faces,edges=hull.edges_unique,lo=mapped.min(1),hi=mapped.max(1)))
    # Exact triangle/sphere nearest surface distance. Body-local centres avoid
    # re-transforming every hardware triangle for every saved output.
    lc=np.einsum('tji,tj->ti',rot[:,o],centres-q[:,o,:3]);tri=local[f]
    for k,c in enumerate(lc):
     near=trimesh.triangles.closest_point(tri,np.repeat(c[None],len(tri),axis=0));gap=float(np.linalg.norm(near-c,axis=1).min()-R)
     # If centre lies inside a convex SUPPORT, distance must be signed negative.
     if node.get('name').startswith('support'):
      normals=hull.face_normals;inside=np.all(np.einsum('ij,ij->i',c-hull.triangles[:,0],normals)<=0)
      if inside:gap=-float(np.linalg.norm(near-c,axis=1).min())-R
     if gap<objectgap:objectgap=gap;objectworst=dict(time_s=float(times[k]),finger=i,cable=j,part=node.get('name'))
 records=[];broad=0;narrow=0
 for left,right in itertools.combinations(parts,2):
  if left['finger']==right['finger']:continue
  broad+=len(times);mask=np.all(left['hi']+.0002>=right['lo'],axis=1)&np.all(right['hi']+.0002>=left['lo'],axis=1)
  for k in np.flatnonzero(mask):
   narrow+=1;gap,status=sat(left['vertices'][k],right['vertices'][k],left['faces'],right['faces'],left['edges'],right['edges'])
   if gap<=.0002:records.append(dict(time_s=float(times[k]),left=[left['finger'],left['cable'],left['name']],right=[right['finger'],right['cable'],right['name']],axis_gap_mm=gap*1000,status=status))
 d=dict(status='PASS_SAVED_INTERFINGER_ENVELOPE_CLEARANCE_ONLY' if not records and objectgap>=.0002 else 'FAIL_OR_UNRESOLVED_SAVED_HARDWARE_CLEARANCE',case=a.case,accepted_outputs=len(times),actual_parts=len(parts),pair_frames=broad,narrow_pair_frames=narrow,uncleared_pair_frames=len(records),minimum_hardware_object_triangle_gap_mm=objectgap*1000,worst_object_gap=objectworst,first_uncleared=records[:10],scope='Actual candidate accepted Rigid3 poses; all eyelet/support convex envelopes across DIFFERENT fingers. Positive separation certifies finite facets outside existing0.2mm buffer at saved outputs only. Envelope overlap is NOT proof of ring-solid penetration. Same-finger/joints/skin/wire and swept intervals NOT certified. Not time/mesh/energy/physical qualification.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn','object.csv']+[f'guide_frames{i}.csv' for i in range(3)]});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'uncleared.json').write_text(json.dumps(records));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
