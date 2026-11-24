"""One finite same-finger terminal rung, not an inter-finger support.
Opposed guide frames5/11 become one COM body bonded to the original six feet.
Actual added solid, parallel-axis inertia and every collision feature retained.
Rigid ideal bond and density1000kg/m3 are explicit research assumptions.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from finite_hardware_grasp_pilot import flat
from finite_support_sat import sat

def bar(a,b,w):
 d=b-a;T=trimesh.geometry.align_vectors([1,0,0],d/np.linalg.norm(d));T[:3,3]=(a+b)/2
 return trimesh.creation.box([np.linalg.norm(d)+w,w,w],transform=T)

def capsule_separation(mesh,a,b,r):
 hull=mesh.convex_hull;tri=hull.triangles;n=hull.face_normals;edges=hull.vertices[hull.edges_unique[:,1]]-hull.vertices[hull.edges_unique[:,0]];cross=np.cross(edges,b-a);axes=np.vstack([n,cross,np.eye(3)]);length=np.linalg.norm(axes,axis=1);axes=axes[length>1e-14]/length[length>1e-14,None]
 va=hull.vertices@axes.T;vb=np.vstack([a,b])@axes.T
 return float(np.maximum(vb.min(0)-r-va.max(0),va.min(0)-vb.max(0)-r).max())

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/capillary_hold1700';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 assert json.loads((BASE/'results/indexed_mass1720/summary.json').read_text())['status']=='PASS_INDEXED_NATIVE_MASS_TRANSLATION_ROTATION_ONLY'
 root=ET.parse(src/'scene.scn').getroot();object_c=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3]
 pre=json.loads((src/'preflight.json').read_text());meta=[];bridges=[];hardware=[];routes=[];w=.0008;density=1000.;buffer=.0002;gap=1.;wiregap=1.;foreigngap=1.;geometry_ok=True
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");frames=parent.find('MechanicalObject');q=np.fromstring(frames.get('position'),sep=' ').reshape(-1,7);assert np.all(q[:,3:]==[0,0,0,1])
  an=parent.find("Node[@name='anchors']");aq=np.fromstring(an.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);ao=np.fromstring(an.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
  ends=[aq[ao==k].mean(0) for k in (5,11)];er=np.array([np.cos(np.deg2rad(i*120)),np.sin(np.deg2rad(i*120)),0])
  # Existing0.8mm pad section; dorsal centreline offset=one section+contactbuffer.
  path=np.array([ends[0],ends[0]+er*(w+buffer),ends[1]+er*(w+buffer),ends[1]])
  boxes=[bar(x,y,w) for x,y in zip(path[:-1],path[1:])];bridge=trimesh.boolean.union(boxes,engine='manifold');assert bridge.is_watertight and bridge.volume>0 and bridge.body_count==1
  bridge.density=density;mp=bridge.mass_properties;mb=float(mp.mass);m0=1e-5;mass=2*m0+mb;com=(m0*q[5,:3]+m0*q[11,:3]+mb*mp.center_mass)/mass
  inertia=np.asarray(mp.inertia).copy()
  for m,c,I in [(m0,q[5,:3],np.eye(3)*1e-11),(m0,q[11,:3],np.eye(3)*1e-11),(mb,mp.center_mass,np.zeros((3,3)))]:
   d=c-com;inertia+=I+m*((d@d)*np.eye(3)-np.outer(d,d))
  assert np.linalg.eigvalsh(inertia).min()>0
  newq=q[:11].copy();newq[5,:3]=com;frames.set('position',flat(newq))
  parent.remove(parent.find('UniformMass'))
  ET.SubElement(parent,'UniformMass',template='Rigid3d',name='unmodifiedMass',indices='0 1 2 3 4 6 7 8 9 10',vertexMass='.00001 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6')
  ET.SubElement(parent,'UniformMass',template='Rigid3d',name='yokeMass',indices='5',vertexMass=flat([mass,2e-8+bridge.volume,*((inertia/mass).ravel())]))
  for mapping in parent.iter('RigidMapping'):
   if 'rigidIndexPerPoint' in mapping.attrib:
    ids=np.fromstring(mapping.get('rigidIndexPerPoint'),sep=' ',dtype=int);mapping.set('rigidIndexPerPoint',' '.join(map(str,np.where(ids==11,5,ids))))
  node=ET.SubElement(parent,'Node',name='dorsalYoke');ET.SubElement(node,'MechanicalObject',template='Vec3d',name='surface',position=flat(bridge.vertices));ET.SubElement(node,'MeshTopology',position=flat(bridge.vertices),triangles=' '.join(map(str,bridge.faces.ravel())))
  ET.SubElement(node,'RigidMapping',input='@../frames',output='@surface',globalToLocalCoords='1',rigidIndexPerPoint=' '.join(['5']*len(bridge.vertices)),mapMatrices='1')
  group=parent.find("Node[@name='cable0']/Node[@name='eyelet0']/TriangleCollisionModel").get('group')
  for feature in ('Triangle','Line','Point'):ET.SubElement(node,feature+'CollisionModel',group=group)
  bridge.export(out/f'finger{i}_dorsal_yoke_m.stl');bridges.append((i,bridge,boxes))
  near=trimesh.triangles.closest_point(bridge.triangles,np.repeat(object_c[None],len(bridge.faces),axis=0));objectgap=float(np.linalg.norm(near-object_c,axis=1).min()-.03);gap=min(gap,objectgap);geometry_ok &= objectgap>buffer
  meta.append(dict(finger=i,part='dorsalYoke',rigid_body=5,original_owners=[5,11],original_attachment_points=aq[np.isin(ao,[5,11])].tolist(),volume_mm3=float(bridge.volume)*1e9,added_mass_kg=mb,total_yoke_and_two_guides_mass_kg=mass,COM_m=com.tolist(),inertia_kg_m2=inertia.tolist(),initial_object_gap_mm=objectgap*1000,section_mm=w*1000,dorsal_offset_mm=(w+buffer)*1000))
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']");origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');route=np.vstack([origin,np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)]);routes.append(route)
   for child in cable.findall('Node'):
    if child.get('name','').startswith(('eyelet','support')):
     v=np.fromstring(child.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);f=np.fromstring(child.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);hardware.append((i,trimesh.Trimesh(v,f,process=False)))
 # Sufficient convex separation proof for each actual rectangular bar component.
 for i,bridge,boxes in bridges:
  for box in boxes:
   for route in routes:
    for a0,b0 in zip(route[:-1],route[1:]):wiregap=min(wiregap,capsule_separation(box,a0,b0,.00025))
   for j,other in hardware:
    if i==j:continue
    h=other.convex_hull;foreigngap=min(foreigngap,sat(box.vertices,h.vertices,box.faces,h.faces,box.edges_unique,h.edges_unique)[0])
  for j,other,_ in bridges:
   if i>=j:continue
   for b0 in boxes:
    for b1 in [x for x in bridges if x[0]==j][0][2]:foreigngap=min(foreigngap,sat(b0.vertices,b1.vertices,b0.faces,b1.faces,b0.edges_unique,b1.edges_unique)[0])
 geometry_ok &= wiregap>0 and foreigngap>buffer
 # Same initial FEM, same actual attachment coordinates and idealCable path.
 for i in range(3):
  for name in ('finger','free'):
   old=ET.parse(src/'scene.scn').getroot().find(f"Node[@name='{name}{i}']/MechanicalObject").get('position');assert old==root.find(f"Node[@name='{name}{i}']/MechanicalObject").get('position')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn')
 for f in ('config.json','mesh.json','holding_protocol.json'):(out/f).write_bytes((src/f).read_bytes())
 d=dict(status='READY_DORSAL_YOKE_NATIVE_PILOT' if geometry_ok else 'FAIL_INITIAL_YOKE_GEOMETRY',all_parts=pre['parts']+meta,added_parts=meta,minimum_initial_yoke_object_gap_mm=gap*1000,minimum_wire_capsule_separating_axis_gap_mm=wiregap*1000,minimum_foreign_hardware_separating_axis_gap_mm=foreigngap*1000,density_kg_m3=density,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='One shared terminal rigid body per finger, finite dorsal0.8mm rung. All original guide/support/skin/rail collisions preserved plus real rung collisions. Six original feet rigidly bonded; NO inter-finger joint. Added density1000kg/m3 and rigid perfect bond are declared assumptions, NOT measured hardware. Original guide inertia inherited; actual yoke COM/inertia from closed-solid integration+parallel-axis. Initial geometry ONLY, no swept/full grasp or real finite-wire sliding qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('all_parts','added_parts')},indent=2))
if __name__=='__main__':main()
