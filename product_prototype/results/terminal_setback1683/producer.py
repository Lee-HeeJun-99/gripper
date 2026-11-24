"""One physical axial terminal-guide setback; saved-motion screen,not dynamics.
Ring OD/ID/length unchanged; actual Cable path and finite support both move.
No chamfer/force/dt/collision-model scan. Never treat convex-envelope overlap as
proven ring-solid overlap, or absence at saved poses as swept clearance.
"""
import argparse,csv,itertools,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from finite_hardware_grasp_pilot import flat
from finite_support_sat import sat

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/dispatch_finite_holding1586';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 root=ET.parse(src/'scene.scn').getroot();parts=[];shifts={};changed=[];times=None;wiregap=1.;initialgap=1.;R=.03
 obj=list(csv.DictReader((src/'object.csv').open()));centres=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in obj])
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
  rows=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows]);rot=Rotation.from_quat(q[:,:,3:].reshape(-1,4)).as_matrix().reshape(len(q),-1,3,3)
  if times is None:times=t
  else:assert np.array_equal(times,t)
  film=list(csv.DictReader((src/f'finger{i}.csv').open()));assert [float(r['time_s']) for r in film]==list(times)
  anchors=parent.find("Node[@name='anchors']");feet=np.fromstring(anchors.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owners=np.fromstring(anchors.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']");ring=cable.find("Node[@name='eyelet5']");v=np.fromstring(ring.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);n=len(v)//4;c=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis);shift=-.002*axis
   owner=int(ring.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);shifts[i,j]=shift
   ey=v[0]-c;ey-=axis*(ey@axis);ey/=np.linalg.norm(ey);ez=np.cross(axis,ey);newv=v+shift
   ring.find('MechanicalObject').set('position',flat(newv));ring.find('MeshTopology').set('position',flat(newv))
   support=cable.find("Node[@name='support5']");oldsv=np.fromstring(support.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);oldsf=np.fromstring(support.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)
   cube=np.array(list(itertools.product((-.0004,.0004),repeat=3)));ff=feet[owners==owner];assert len(ff)==3
   points=np.concatenate([ff[:,None,:]+cube[None],(c+shift-.0012*ez)[None,None,:]+cube[None]],axis=0).reshape(-1,3);hull=trimesh.convex.convex_hull(points)
   for tag in ('MechanicalObject','MeshTopology'):support.find(tag).set('position',flat(hull.vertices))
   support.find('MeshTopology').set('triangles',flat(hull.faces));support.find('RigidMapping').set('rigidIndexPerPoint',' '.join([str(owner)]*len(hull.vertices)))
   cq=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);cq[5]+=shift;cable.find('MechanicalObject').set('position',flat(cq))
   assert {x.tag for x in ring if x.tag.endswith('CollisionModel')}=={'TriangleCollisionModel','LineCollisionModel','PointCollisionModel'}
   assert {x.tag for x in support if x.tag.endswith('CollisionModel')}=={'TriangleCollisionModel','LineCollisionModel','PointCollisionModel'}
   changed.append(dict(finger=i,cable=j,shift_world_m=shift.tolist(),ring_dimensions_mm=dict(OD=3,ID=1.2,length=2),support_old_volume_mm3=float(trimesh.Trimesh(oldsv,oldsf,process=False).volume)*1e9,support_new_volume_mm3=float(hull.volume)*1e9,assumption='Rigid support extends from ORIGINAL 3 bonded feet to set-back ring. Mass/inertia/strength uncalibrated; this is not same-material hardware qualification.'))
   localshift=Rotation.from_quat(q0[owner,3:]).inv().apply(shift);actualshift=np.einsum('tij,j->ti',rot[:,owner],localshift)
   paths=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in film]);paths[:,5]+=actualshift
   origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');paths=np.concatenate([np.repeat(origin[None,None],len(times),axis=0),paths],axis=1);edge=np.diff(paths,axis=1);den=(edge*edge).sum(2);assert np.all(den>0)
   u=np.clip(((centres[:,None]-paths[:,:-1])*edge).sum(2)/den,0,1);g=np.linalg.norm(paths[:,:-1]+u[:,:,None]*edge-centres[:,None],axis=2)-R-.00025;wiregap=min(wiregap,float(g.min()))
   for node in cable.findall('Node'):
    if not node.get('name','').startswith(('eyelet','support')):continue
    vertices=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);o=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);local=Rotation.from_quat(q0[o,3:]).inv().apply(vertices-q0[o,:3]);mapped=np.einsum('tij,vj->tvi',rot[:,o],local)+q[:,o,None,:3]
    # Convex envelope only for conservative separation. For a ring, overlap is inconclusive.
    convex=trimesh.convex.convex_hull(local);item=dict(finger=i,cable=j,name=node.get('name'),moved=node.get('name') in ('eyelet5','support5'),vertices=mapped,faces=convex.faces,local=convex.vertices,owner=o,lo=mapped.min(1),hi=mapped.max(1))
    item['envelope']=np.einsum('tij,vj->tvi',rot[:,o],convex.vertices)+q[:,o,None,:3];item['edges']=convex.edges_unique;parts.append(item)
    if item['moved']:
     mesh=trimesh.Trimesh(vertices,faces,process=False);mesh.export(out/f'f{i}c{j}_{node.get("name")}_metres.stl');tri=vertices[faces];near=trimesh.triangles.closest_point(tri,np.repeat(centres[:1],len(tri),axis=0));initialgap=min(initialgap,float(np.linalg.norm(near-centres[0],axis=1).min()-R))
 records=[];narrow=0;checks=0
 for left,right in itertools.combinations(parts,2):
  if left['finger']==right['finger'] or not(left['moved'] or right['moved']):continue
  checks+=len(times);mask=np.all(left['hi']+.0002>=right['lo'],axis=1)&np.all(right['hi']+.0002>=left['lo'],axis=1)
  for k in np.flatnonzero(mask):
   narrow+=1;gap,status=sat(left['envelope'][k],right['envelope'][k],left['faces'],right['faces'],left['edges'],right['edges'])
   if gap<=.0002:records.append(dict(time_s=float(times[k]),left=[left['finger'],left['cable'],left['name']],right=[right['finger'],right['cable'],right['name']],envelope_axis_gap_mm=gap*1000,classification='ACTUAL_SUPPORT_CONVEX_OVERLAP' if status=='STRICT_CONVEX_OVERLAP' and left['name'].startswith('support') and right['name'].startswith('support') else 'NOT_CERTIFIED_CLEAR_OF_0.2mm_BUFFER'))
 for node in root.iter():
  for key,value in list(node.attrib.items()):node.set(key,value.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'candidate_scene_NOT_RUN.scn')
 ok=not records and wiregap>=0 and initialgap>=.0002
 d=dict(status='READY_FOR_BOUNDED_NATIVE_PILOT' if ok else 'REJECT_OR_BLOCK_SETBACK_BEFORE_NATIVE',source_case=src.name,actual_new_Native_run=False,geometry_change='ONE terminal ring axial setback2mm with cablepoint and finite support reconstruction; not chamfer scan or collision removal',changed_parts=changed,initial_saved_object_hardware_gap_mm=initialgap*1000,minimum_replayed_wire_object_gap_mm=wiregap*1000,interfinger_pair_frames=checks,narrow_pair_frames=narrow,uncleared_pair_frames=len(records),first_uncleared=records[:10],scope='Actual OLD1586 saved poses, not changed candidate equilibrium/holding or swept CCD. Envelope overlap is NOT proof of ring-solid contact. Cable remains ideal Native constraint,not qualified finite wire-eyelet contact; material/mass/strength unknown. No old functional result transferred.',input_hashes={f:sha(src/f) for f in ['scene.scn','object.csv']+[f'guide_frames{i}.csv' for i in range(3)]+[f'finger{i}.csv' for i in range(3)]},source_sha256=sha(Path(__file__)))
 (out/'uncleared.json').write_text(json.dumps(records));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
