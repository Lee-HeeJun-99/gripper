"""Actual single B3 Finger driven by two mass-bearing winches and C2 tendons."""
import argparse,copy,csv,json,sys,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'cad'))
from analyse import sha
from finite_hardware_grasp_pilot import flat
from native_bending_coupon import guarded
from bellcrank_link_geometry import shapes
from finite_csg64 import register

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--outward-handed',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/yoke_hold_diagnostic1741';root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));removed=['object','floor','finger1','finger2','free1','free2','guides1','guides2']
 for e in list(root):
  if (e.tag=='Node' and e.get('name') in removed) or e.tag in ('NativeResponseRows','NativeDetectionPairs','NativeContactRows'):root.remove(e)
 finger=root.find("Node[@name='finger0']");finger.remove(finger.find('NativeCableSequence'));ET.SubElement(finger,'NativePointJournal',body='@dofs',filename=str(out/'skin.csv'));q0=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);assert np.all(np.isfinite(d0)) and np.all(d0!=0)
 prototype=ET.parse(BASE/'results/bearing_stroke1876/scene.scn').getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Mapping.Linear'));probe=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so';assert sha(probe)=='9140d6a0be5283118412fa86df18a88a06dcba875602f3c9cba783b50f8cde96';root.insert(0,ET.Element('RequiredPlugin',pluginName=str(probe)));register();rotor=shapes()[0];rotor.apply_scale(.001);T=np.eye(4);T[:3,:3]=Rotation.from_euler('y',90,degrees=True).as_matrix();rotor.apply_transform(T);rotor.apply_translation([.0045,0,0]);preflight=[];rotorbounds=[]
 for j in range(2):
  old=root.find(f"Node[@name='guides0']/Node[@name='cable{j}']");oldact=old.find('CableConstraint');origin=np.fromstring(oldact.get('pullPoint'),sep=' ');old.remove(oldact);route=np.fromstring(old.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);mount=Rotation.from_euler('z',180 if a.outward_handed and j==1 else 0,degrees=True);Rmount=mount.as_matrix();shift=origin-mount.apply([.0035,-.01,0]);drive=copy.deepcopy(prototype.find("Node[@name='shaft']"));drive.set('name',f'winch{j}');driveports=drive.find("Node[@name='ports']");driveports.remove(driveports.find('ConstantForceField'))
  for e in drive.iter():
   if e.tag in ('MechanicalObject','MeshTopology') and e.get('position'):
    width=7 if e.get('template')=='Rigid3d' else 3;q=np.fromstring(e.get('position'),sep=' ').reshape(-1,width);q[:,:3]=mount.apply(q[:,:3])+shift
    if width==7:q[:,3:]=(mount*Rotation.from_quat(q[:,3:])).as_quat()
    e.set('position',flat(q))
   if e.tag=='UniformMass':
    values=np.fromstring(e.get('vertexMass'),sep=' ');values[2:]=(Rmount@values[2:].reshape(3,3)@Rmount.T).ravel();e.set('vertexMass',flat(values))
   if e.tag=='CableConstraint':e.set('pullPoint',flat(mount.apply(np.fromstring(e.get('pullPoint'),sep=' '))+shift));e.set('maxForce',str(1.5*dt))
   if e.get('filename'):e.set('filename',str(out/f'winch{j}_{Path(e.get("filename")).name}'))
  root.append(drive);controller=copy.deepcopy(prototype.find('NativeCableSequence'))
  for key in ('body','cable0','cable1'):controller.set(key,controller.get(key).replace('@shaft/',f'@winch{j}/'))
  controller.set('filename',str(out/f'winch{j}_commands.csv'));root.append(controller)
  mesh=rotor.copy();transform=np.eye(4);transform[:3,:3]=Rmount;transform[:3,3]=shift;mesh.apply_transform(transform);rotorbounds.append(mesh.bounds);clearances=[]
  # AABB separation is a sufficient initial proof when positive. It is not
  # used as a distance estimate for overlapping boxes or swept motion.
  obstacles=[('actualFEM',q0,None)]
  for n in root.find("Node[@name='guides0']").iter('Node'):
   mo=n.find('MechanicalObject');top=n.find('MeshTopology')
   if mo is not None and top is not None and top.get('triangles'):obstacles.append((n.get('name'),np.fromstring(mo.get('position'),sep=' ').reshape(-1,3),np.fromstring(top.get('triangles'),sep=' ',dtype=int).reshape(-1,3)))
  for name,points,faces in obstacles:
   lower,upper=points.min(0),points.max(0);sep=float(np.maximum(lower-mesh.bounds[1],mesh.bounds[0]-upper).max());record=dict(obstacle=name,positive_separating_axis_gap_m=sep)
   if sep<=0:
    assert faces is not None,'No sufficient FEM clearance';x=mesh.copy();x.apply_scale(1000);y=trimesh.Trimesh(points*1000,faces,process=False);assert x.is_volume and y.is_volume,(j,name,'invalid preflight solid');intersection=trimesh.boolean.intersection([x,y],engine='manifold64');volume=float(intersection.volume) if len(intersection.faces) else 0;record['exact_CSG_intersection_mm3']=volume
    if volume!=0 or len(intersection.faces):
     (out/'preflight_collision.json').write_text(json.dumps(dict(winch=j,obstacle=name,intersection_mm3=volume,intersection_faces=len(intersection.faces),scope='Actual finite solid witness, no geometry or collision removal'),indent=2));intersection.export(out/'preflight_intersection_mm.stl');raise AssertionError((j,name,volume,'exact initial intersection or unresolved topology'))
   if a.outward_handed:assert sep>.0002,(j,name,sep,'Insufficient initial contact-buffer separation')
   clearances.append(record)
  surface=ET.SubElement(drive,'Node',name='finiteRotor');ET.SubElement(surface,'MechanicalObject',template='Vec3d',name='surface',position=flat(mesh.vertices));ET.SubElement(surface,'MeshTopology',position=flat(mesh.vertices),triangles=flat(mesh.faces));ET.SubElement(surface,'RigidMapping',input='@../frames',output='@surface',globalToLocalCoords='1',rigidIndexPerPoint=' '.join(['2']*len(mesh.vertices)))
  for kind in ('Triangle','Line','Point'):ET.SubElement(surface,kind+'CollisionModel',group=str(20+j))
  cable=ET.SubElement(root,'Node',name=f'fingerTendon{j}');ET.SubElement(cable,'MechanicalObject',template='Vec3d',name='points',position=flat(np.vstack([origin,route])));ET.SubElement(cable,'SubsetMultiMapping',template='Vec3d,Vec3d',input=f'@../winch{j}/ports/points @../guides0/cable{j}/points',output='@points',indexPairs='0 1 '+' '.join(f'1 {k}' for k in range(len(route))),mapMatrices='1');ET.SubElement(cable,'CableConstraint',template='Vec3d',name='output',indices=' '.join(map(str,range(len(route)+1))),hasPullPoint='0',valueType='displacement',value='0',minForce='0');ET.SubElement(root,'NativeCablePhase',body=f'@fingerTendon{j}/points',solver='@constraints',cable=f'@fingerTendon{j}/output',filename=str(out/f'tendon{j}_phases.csv'));preflight.append(dict(cable=j,unchanged_initial_origin_m=origin.tolist(),new_winch_shift_m=shift.tolist(),mount_rotation_matrix=Rmount.tolist(),initial_clearances=clearances))
  if a.outward_handed:ET.SubElement(root,'NativeCablePhase',body=f'@winch{j}/ports/points',rigidBody=f'@winch{j}/frames',solver='@constraints',cable=f'@winch{j}/ports/input',filename=str(out/f'winch{j}_input_phases.csv'))
 if a.outward_handed:
  ET.SubElement(root,'NativeResponseRows',manager='@nativeResponses',body='@guides0/frames',solver='@constraints',filename=str(out/'contact_provenance.csv'));ET.SubElement(root,'NativeDetectionPairs',narrow='@nativeNarrow',filename=str(out/'detector.csv'))
 pairgap=float(np.maximum(rotorbounds[0][0]-rotorbounds[1][1],rotorbounds[1][0]-rotorbounds[0][1]).max());assert pairgap>0
 for e in root.iter():
  for k,v in list(e.attrib.items()):e.set(k,v.replace(str(src),str(out)))
 for name in ('config.json','mesh.json'):(out/name).write_bytes((src/name).read_bytes())
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),dt_s=dt,steps=100,duration_s=.25,initial_rotor_pair_separating_gap_m=pairgap,rotor_to_wire_initial_slab_gap_m=.00025,per_winch=preflight,removed=removed,initial_minimum_abs_tet_determinant=float(abs(d0).min()),binary_sha256={e.get('pluginName'):sha(Path(e.get('pluginName'))) for e in root.iter('RequiredPlugin') if e.get('pluginName','').startswith('/')},scope='Initial actual FEM/finiteGuide separation plus added finiteRotor collisions; same1741Skin/Rail/Guide mapping and material. Two ideal-bearing winches replace two world force sources with actual C2 endpoint coupling. Existing hardware collisions retained. Removing other fingers/object/support is declared no-object singleFinger isolation, not Holding. Winch ideal bearing/return bond/anchor unqualified; new1873hub NOT adopted.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'skin.csv').open())) if (out/'skin.csv').exists() else [];qualities=[];displacements=[]
 for r in rows:
  q=np.fromstring(r['q'],sep=' ').reshape(-1,3);qualities.append(float((det(q)/d0).min()));displacements.append(float(np.linalg.norm(q-q0,axis=1).max()))
 ok=process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==100 and min(qualities,default=-1)>0 and max(displacements,default=0)>1e-6
 d=dict(status='VALID_SINGLE_FINGER_SUPPORTED_WINCH_PREFIX_ONLY' if ok else 'FAIL_SINGLE_FINGER_SUPPORTED_WINCH',process=process,saved_steps=len(rows),minimum_saved_volume_ratio=min(qualities,default=None),maximum_skin_nodal_displacement_m=max(displacements,default=None),source_sha256=sha(Path(__file__)),preflight_sha256=sha(out/'preflight.json'),errors=[s for s in logs.splitlines() if '[ERROR]'in s],scope=pre['scope']+' No grip/object/contact/time/mesh/material PASS; row/force analysis still required before expansion. Skin displacement is not automatically tendon contribution; gravity remains active.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':
 try:main()
 except Exception as error:
  import traceback
  tag=sys.argv[sys.argv.index('--tag')+1];out=BASE/'results'/tag
  if out.exists() and not (out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_SINGLE_FINGER_INTEGRATION_PIPELINE',exception=repr(error),native_scene_generated=(out/'scene.scn').exists(),traceback=traceback.format_exc(),scope='Failure retained, no component/grasp promotion. Inspect preflight witness and actual process if present.'),indent=2))
  raise
