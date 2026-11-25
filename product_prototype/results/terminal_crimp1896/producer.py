"""Closed terminal fitting replaces only a needless last pass-through eyelet.
Endpoint stays fixed; real bridge to existing support and density-difference mass.
"""
import argparse,itertools,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_csg64 import register
from finite_hardware_grasp_pilot import flat
from winch_transfer_assess import read
from parallel_winch_bank import separating_bound

def mesh_node(node):
 v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;f=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);m=trimesh.Trimesh(v,f,process=False);assert m.is_volume;return m
def parallel(m,r):return m*((r@r)*np.eye(3)-np.outer(r,r))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register();src=BASE/'results/parallel_contact1894';root=ET.parse(src/'scene.scn').getroot();parts=[];mass_records=[];rho=1000.;failures=[]
 for i in range(3):
  guides=root.find(f"Node[@name='guides{i}']");frames=np.fromstring(guides.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);original_frames=frames.copy();updates=[]
  for j in range(2):
   cable=guides.find(f"Node[@name='cable{j}']");points=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);centre=points[-1]*1000;axis=points[-1]-points[-2];axis/=np.linalg.norm(axis);node=cable.find("Node[@name='eyelet5']");old=mesh_node(node);support=mesh_node(cable.find("Node[@name='support5']"));near=trimesh.triangles.closest_point(support.triangles,np.repeat(centre[None],len(support.faces),axis=0));near=near[np.linalg.norm(near-centre,axis=1).argmin()];back=near-centre;back-=axis*(axis@back);back/=np.linalg.norm(back);width=np.cross(back,axis);R=np.stack([axis,width,back],axis=1);assert np.linalg.det(R)>.999999999
   block=trimesh.creation.box([2.,1.,.7]);T=np.eye(4);T[:3,:3]=R;T[:3,3]=centre;block.apply_transform(T);base=np.array(list(itertools.product((-.5,.5),(-.25,.25),(.25,))))@R.T+centre;tip=near+.05*back+np.array(list(itertools.product((-.1,.1),repeat=3)));bridge=trimesh.convex.convex_hull(np.vstack([base,tip]));outer=trimesh.boolean.union([block,bridge],engine='manifold64');bore=trimesh.creation.cylinder(radius=.25,segment=np.stack([centre-1.1*axis,centre]),sections=32);new=trimesh.boolean.difference([outer,bore],engine='manifold64');assert new.is_volume and len(new.split(only_watertight=False))==1;bond=trimesh.boolean.intersection([new,support],engine='manifold64');assert bond.volume>0,'Force path needs real support overlap'
   add=trimesh.boolean.difference([new,support],engine='manifold64');remove=trimesh.boolean.difference([old,support],engine='manifold64');assert add.is_volume and remove.is_volume
   for sign,m in [(1,add),(-1,remove)]:updates.append((sign,rho*m.volume*1e-9,m.center_mass*.001,rho*m.moment_inertia*1e-15,m.volume*1e-9))
   owner=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);assert set(owner)=={5};p0=original_frames[5,:3];r0=Rotation.from_quat(original_frames[5,3:]);local=r0.inv().apply(new.vertices*.001-p0);parts.append(dict(finger=i,tendon=j,mesh=new,local=local,initial_parent_q=original_frames[5].copy(),centre_m=points[-1].copy()));new.export(out/f'crimp_f{i}_t{j}_rest_mm.stl')
   for element in (node.find('MechanicalObject'),node.find('MeshTopology')):element.set('position',flat(new.vertices*.001))
   node.find('MeshTopology').set('triangles',flat(new.faces));node.find('RigidMapping').set('rigidIndexPerPoint',' '.join(['5']*len(new.vertices)))
   # Blind bore and connector are a different end-termination topology,
   # not a shrinking through-ring. All three collision feature models stay.
   tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);q=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;cells=q[tet];mask=np.all(cells.max(1)>=add.bounds[0],axis=1)&np.all(cells.min(1)<=add.bounds[1],axis=1)
   for index in np.flatnonzero(mask):
    t=trimesh.convex.convex_hull(cells[index]);value=trimesh.boolean.intersection([add,t],engine='manifold64');v=float(value.volume) if len(value.faces) else 0
    if v!=0:failures.append(dict(kind='initial_new_material_FEM',finger=i,tendon=j,tet=int(index),intersection_mm3=v))
  field=guides.find("UniformMass[@name='yokeMass']");values=np.fromstring(field.get('vertexMass'),sep=' ');oldmass=values[0];oldcentre=frames[5,:3].copy();oldI=values[2:].reshape(3,3)*oldmass;newmass=oldmass+sum(s*m for s,m,c,I,V in updates);newcentre=(oldmass*oldcentre+sum((s*m*c for s,m,c,I,V in updates),np.zeros(3)))/newmass;newI=oldI+parallel(oldmass,oldcentre-newcentre)
  for sign,m,c,I,V in updates:newI+=sign*(I+parallel(m,c-newcentre))
  eig=np.linalg.eigvalsh(newI);assert newmass>0 and eig.min()>0;frames[5,:3]=newcentre;guides.find('MechanicalObject').set('position',flat(frames));newV=values[1]+sum(s*V for s,m,c,I,V in updates);assert newV>0;field.set('vertexMass',flat([newmass,newV,*(newI/newmass).ravel()]));mass_records.append(dict(finger=i,old_mass_kg=oldmass,new_mass_kg=newmass,old_COM_m=oldcentre.tolist(),new_COM_m=newcentre.tolist(),new_inertia_COM_kg_m2=newI.tolist(),minimum_inertia_eigenvalue=float(eig.min()),delta_density_assumed_kg_m3=rho))
 # Necessary replay of NEW fittings on OLD accepted parent poses. It does not
 # prescribe or predict new dynamics and is not a checkpoint initialization.
 history=[read(src/f'guide_frames{i}.csv') for i in range(3)];objects=read(src/'object.csv');min_pair=1.;min_obj=1.;bad=[]
 for k in range(len(objects)):
  moved=[]
  for part in parts:
   q=np.fromstring(history[part['finger']][k]['rigid_q'],sep=' ').reshape(-1,7)[5];v=Rotation.from_quat(q[3:]).apply(part['local'])+q[:3];moved.append(v);centre=np.fromstring(objects[k]['rigid_q'],sep=' ')[:3];tri=v[part['mesh'].faces];near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));gap=float(np.linalg.norm(near-centre,axis=1).min()-.03);min_obj=min(min_obj,gap)
   if gap<=.0002:bad.append(dict(step=k,kind='new_fitting_object_gap',finger=part['finger'],tendon=part['tendon'],gap_m=gap))
  for l in range(6):
   for r in range(l+1,6):
    if parts[l]['finger']==parts[r]['finger']:continue
    gap=separating_bound(moved[l],moved[r]);min_pair=min(min_pair,gap)
    if gap<=.0002:bad.append(dict(step=k,kind='new_fitting_pair_insufficient_gap',pair=[l,r],gap_m=gap))
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');d=dict(status='PASS_TERMINAL_CRIMP_NECESSARY_GEOMETRY_ONLY' if not failures and not bad else 'REJECT_TERMINAL_CRIMP_PREFLIGHT',mass_changes=mass_records,initial_material_failures=failures,replay_failures=bad,minimum_replayed_new_fitting_pair_separating_gap_m=min_pair,minimum_replayed_fitting_object_surface_gap_m=min_obj,configuration=dict(wire_diameter_mm=.5,blind_fitting_outer_mm=[2,1,.7],blind_bore_radius_mm=.25,blind_bore_length_mm=1.,wire_endpoint_unchanged=True,real_support_bridge=True,delta_density_assumed_kg_m3=rho),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='New terminal non-sliding blind crimp fittings, not a ring chamfer/offset scan. Existing last Native cable point has no outgoing span, so a real termination replaces pass-through geometry. Finite bridge overlaps actual support, allCollisionfeatures retained; input/control/Skin/rail/endpoint unchanged. Material mass differences exclude existing support overlap; applied to existing uncalibrated Guide mass budget at inherited researchrho1000, new COM/tensor SPD. Not actual material calibration or rigidJoint strength. Replay uses old accepted Guide poses solely as necessary geometry; not new equilibrated motion or full swept proof. Initial new-material check covers ownFEM; other hardware and fullobject dynamics still require next guarded trial. Crimp retention/friction/fatigue/finite-wire bending NOT MEASURED. No100g PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='replay_failures'},indent=2))
if __name__=='__main__':main()
