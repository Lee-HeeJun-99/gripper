"""Actual finite support through-relief for one16RW ferrule candidate.
Manifold CSG is a mesh kernel, NOT STEP/OCC/fabrication certification.
Independent triangle/slab radial minimum checks every resulting bore face.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from finite_hardware_grasp_pilot import flat
from capillary_guide_candidate import SPEC

def polygon_radius(poly):
 p=np.asarray(poly)[:,1:];edge=np.roll(p,-1,axis=0)-p;den=(edge*edge).sum(1);valid=den>0
 if not valid.any():return float(np.linalg.norm(p[0]))
 area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1));cross=edge[:,0]*(-p[:,1])-edge[:,1]*(-p[:,0])
 if area!=0 and (np.all(cross>=0) or np.all(cross<=0)):return 0.
 u=np.zeros(len(edge));u[valid]=np.clip(-(p[valid]*edge[valid]).sum(1)/den[valid],0,1)
 return float(np.linalg.norm(p+u[:,None]*edge,axis=1).min())

def bore_surface_min(local,faces,half=.001):
 best=float('inf');count=0
 for face in faces:
  poly=[x for x in local[face]]
  for sign in (-1,1):
   if not poly:break
   result=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    da=sign*a[0]-half;db=sign*b[0]-half
    if da<=0:result.append(a)
    if (da<0 and db>0) or (da>0 and db<0):result.append(a+(b-a)*da/(da-db))
   poly=result
  if poly:best=min(best,polygon_radius(poly));count+=1
 if not count:raise ValueError('no faces in finite bore slab')
 return best,count

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/capillary_guide1692';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();records=[];rimax=(SPEC['ID_in']+SPEC['ID_tolerance_in'])*.0254/2
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");anchors=parent.find("Node[@name='anchors']");feet=np.fromstring(anchors.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owners=np.fromstring(anchors.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']")
   for k in range(6):
    ring=cable.find(f"Node[@name='eyelet{k}']");v=np.fromstring(ring.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);n=len(v)//4;c=v.mean(0);axis=v[2*n:].mean(0)-v[:2*n].mean(0);axis/=np.linalg.norm(axis);ey=v[0]-c;ey-=axis*(ey@axis);ey/=np.linalg.norm(ey);basis=np.stack([axis,ey,np.cross(axis,ey)],axis=1)
    node=cable.find(f"Node[@name='support{k}']");sv=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);sf=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);local=(sv-c)@basis;old=trimesh.Trimesh(local,sf,process=False)
    # Design a1.4mm minimum-inscribed through-relief in SUPPORT,not the metal
    # ring bore. Extend cutter beyond actual support axial bounds; no residual
    # end-cap blocks the finite wire. Radius is an explicit new part dimension.
    low,high=local[:,0].min()-.001,local[:,0].max()+.001;cut=trimesh.creation.cylinder(radius=.0007/np.cos(np.pi/32),height=high-low,sections=32);cut.vertices=cut.vertices[:,[2,0,1]]+[.5*(low+high),0,0]
    new=trimesh.boolean.difference([old,cut],engine='manifold');assert isinstance(new,trimesh.Trimesh) and new.is_watertight and new.volume>0
    minimum,facecount=bore_surface_min(new.vertices,new.faces);axisoutside=not bool(new.contains(np.array([[-.001,0,0],[0,0,0],[.001,0,0]])).any());footlocal=(feet[owners==owner]-c)@basis;assert len(footlocal)==3;footinside=bool(new.contains(footlocal).all());connected=len(new.split())==1
    world=new.vertices@basis.T+c
    for tag in ('MechanicalObject','MeshTopology'):node.find(tag).set('position',flat(world))
    node.find('MeshTopology').set('triangles',flat(new.faces));node.find('RigidMapping').set('rigidIndexPerPoint',' '.join([str(owner)]*len(world)))
    records.append(dict(finger=i,cable=j,station=k,old_volume_mm3=float(old.volume)*1e9,new_volume_mm3=float(new.volume)*1e9,minimum_all_face_radius_in_bore_slab_mm=minimum*1000,manufacturer_MAX_ID_clearance_mm=(minimum-rimax)*1000,clipped_faces=facecount,axis_outside=axisoutside,three_original_feet_inside=footinside,one_connected_solid=connected))
    if k==5:trimesh.Trimesh(world,new.faces,process=False).export(out/f'f{i}c{j}_bored_support_metres.stl')
 for node in root.iter():
  for key,value in list(node.attrib.items()):node.set(key,value.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'supplier_dimensions.json').write_bytes((src/'supplier_dimensions.json').read_bytes())
 ok=all(r['manufacturer_MAX_ID_clearance_mm']>0 and r['axis_outside'] and r['three_original_feet_inside'] and r['one_connected_solid'] for r in records)
 d=dict(status='READY_BOUNDED_CAPILLARY_GEOMETRY_ONLY' if ok else 'FAIL_BORED_SUPPORT_GEOMETRY',actual_Native_execution=False,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),trimesh_version=trimesh.__version__,support_relief_minimum_diameter_mm=1.4,all_parts=records,minimum_bore_support_radial_clearance_mm=min(r['manufacturer_MAX_ID_clearance_mm'] for r in records),removed_support_volume_mm3=sum(r['old_volume_mm3']-r['new_volume_mm3'] for r in records),scope='Actual mesh CSG of all36finite supports; ring OD/ID/length from one supplier16RW, unchanged centres/path. ALLhardware collisionfeatures retained. Independent triangle/slab radial minima plus axis containment checks, same original3feet retained and connected. NOT retention/adhesive/fastener/strength/manufacturing tolerance or STEP. All rigid mass/inertia inherited research assumptions; support volumes changed explicitly. No finite-wire contact/sliding or new Holding qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='all_parts'},indent=2))
if __name__=='__main__':main()
