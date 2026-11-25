"""Finite registered load lever/surface anchors and derived input direction, actual Finger."""
import argparse,csv,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from scipy.optimize import brentq
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'cad'))
from analyse import sha
from finite_csg64 import register
from bellcrank_link_geometry import shapes,cylinder
from finite_hardware_grasp_pilot import flat
from native_bending_coupon import guarded
from winch_transfer_assess import unique_row,read

def lever_geometry():
 register();lever=shapes()[0];T=np.eye(4);T[:3,:3]=np.array([[0,0,1],[1,0,0],[0,1,0]]);lever.apply_transform(T);bosses=[]
 for y in (-10,0,10):
  m=cylinder(.6,2.,[0,0,0]);T=np.eye(4);T[:3,:3]=Rotation.from_euler('y',90,degrees=True).as_matrix();T[:3,3]=[-.5,y,0];m.apply_transform(T);bosses.append(m)
 lever=trimesh.boolean.union([lever,*bosses],engine='manifold64');assert lever.is_volume and len(lever.split(only_watertight=False))==1
 ai=np.array([-.001,.010,-.0006]);ao=np.array([-.001,-.010,-.0006]);goal=brentq(lambda t:Rotation.from_rotvec([t,0,0]).apply(ao)[2]-ao[2]-.004,-.8,0);mid=Rotation.from_rotvec([goal/2,0,0]).apply(ai);direction=-np.cross([1,0,0],mid);direction/=np.linalg.norm(direction);pull=mid+.020*direction;stroke=np.linalg.norm(pull-ai)-np.linalg.norm(pull-Rotation.from_rotvec([goal,0,0]).apply(ai));return lever,ai,ao,pull,goal,stroke

def upgrade(root,lever,ai,ao,pull,stroke,out):
 records=[];rho=1000.;vol=lever.volume*1e-9;mass=rho*vol;Ilocal=rho*lever.moment_inertia*1e-15
 for j in range(2):
  drive=root.find(f"Node[@name='winch{j}']");frames=np.fromstring(drive.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);mount=Rotation.from_quat(frames[0,3:]);R=mount.as_matrix();ports=drive.find("Node[@name='ports']");oldports=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);origin=oldports[1].copy();oldcentre=np.fromstring(drive.find("Node[@name='body3']/MechanicalObject").get('position'),sep=' ')[:3];centre=origin-mount.apply(ao);delta=centre-oldcentre
  for e in drive.iter():
   if e.tag in ('MechanicalObject','MeshTopology') and e.get('position'):
    width=7 if e.get('template')=='Rigid3d' else 3;q=np.fromstring(e.get('position'),sep=' ').reshape(-1,width);q[:,:3]+=delta;e.set('position',flat(q))
  ports.find('MechanicalObject').set('position',flat(mount.apply([ai,ao])+centre));ports.find('CableConstraint').set('pullPoint',flat(mount.apply(pull)+centre));body=drive.find("Node[@name='body3']");q=np.fromstring(body.find('MechanicalObject').get('position'),sep=' ');q[:3]=centre+mount.apply(lever.center_mass*.001);body.find('MechanicalObject').set('position',flat(q));body.find('UniformMass').set('vertexMass',flat([mass,vol,*(R@Ilocal@R.T/mass).ravel()]));surface=drive.find("Node[@name='finiteRotor']");v=mount.apply(lever.vertices*.001)+centre
  for e in (surface.find('MechanicalObject'),surface.find('MeshTopology')):e.set('position',flat(v))
  surface.find('MeshTopology').set('triangles',flat(lever.faces))
  for controller in root.findall('NativeCableSequence'):
   if controller.get('body')==f'@winch{j}/ports/points':controller.set('stroke',str(stroke))
  assert abs(np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[1]-origin).max()<1e-12
  obstacles=[('FEM',np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3))]
  for n in root.find("Node[@name='guides0']").iter('Node'):
   mo=n.find('MechanicalObject');top=n.find('MeshTopology')
   if mo is not None and top is not None and top.get('triangles'):obstacles.append((n.get('name'),np.fromstring(mo.get('position'),sep=' ').reshape(-1,3)))
  gaps=[]
  for name,points in obstacles:
   gap=float(np.maximum(points.min(0)-v.max(0),v.min(0)-points.max(0)).max());assert gap>.0002,(j,name,gap);gaps.append(gap)
  records.append(dict(winch=j,minimum_initial_separating_axis_gap_m=min(gaps),original_output_origin_m=origin.tolist(),logical_lever_centre_m=centre.tolist(),rotor_mass_kg=mass,rotor_COM_m=q[:3].tolist(),axial_inertia_kg_m2=float(Ilocal[0,0])))
 return records

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--full',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());lever,ai,ao,pull,goal,stroke=lever_geometry();lever.export(out/'registered_integral_lever_mm.stl');wirechecks=[]
 for t in (0,goal/2,goal):
  R=Rotation.from_rotvec([t,0,0]);m=lever.copy();T=np.eye(4);T[:3,:3]=R.as_matrix();m.apply_transform(T);end=R.apply(ai);trim=end-.0007*(end-pull)/np.linalg.norm(end-pull);wire=trimesh.creation.cylinder(radius=.25,segment=np.stack([pull,trim])*1000,sections=32);overlap=trimesh.boolean.intersection([m,wire],engine='manifold64');volume=float(overlap.volume) if len(overlap.faces) else 0;assert volume==0 and len(overlap.faces)==0,(t,volume,'finite input wire preflight');wirechecks.append(dict(angle_rad=float(t),input_wire_intersection_mm3=volume))
 src=BASE/'results/winch_outward1886';root=ET.parse(src/'scene.scn').getroot();records=upgrade(root,lever,ai,ao,pull,stroke,out)
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 steps=240 if a.full else 100;ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),root_modules=records,local_input_anchor_m=ai.tolist(),local_output_anchor_m=ao.tolist(),local_derived_midstroke_tangent_pullpoint_m=pull.tolist(),target_output_displacement_m=.004,target_angle_rad=goal,derived_input_stroke_m=stroke,wirechecks=wirechecks,source_hypothesis='New physical candidate: registered lever+integral stand-off bosses/surface anchors+derived midpoint-tangent idler. Multiple necessary changes, not single-variable superiority claim. Same Skin/Rail/material/rootdt/inputcap. New mass/COM/tensor explicit.',scope='Rigid integral lever and ideal coaxial bearing/return bond/terminated wire clamp research assumptions; central boss meets return shaft at its endface, actual socket/bond strength and manufacture NOT MEASURED. No finite-wire sliding or bearingcontact validation. All existing Finger/new lever collisions retained.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));ok=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
 if ok:
  rows=read(out/'skin.csv');assert len(rows)==steps;tet=np.array(json.loads((BASE/'results/winch_finger1882/mesh.json').read_text())['tetrahedra']);q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);ratios=[float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows];contacts=[r for r in read(out/'contact_provenance.csv') if float(r['lambda_Ns'])!=0];dt=float(root.get('dt'));tendons=[]
  for j in range(2):
   phase=[r for r in read(out/f'winch{j}_input_phases.csv') if r['phase']=='accepted_end'];op=[r for r in read(out/f'tendon{j}_phases.csv') if r['phase']=='accepted_end'];commands=read(out/f'winch{j}_commands.csv');node=root.find(f"Node[@name='winch{j}']/Node[@name='ports']");P=np.fromstring(node.find('CableConstraint').get('pullPoint'),sep=' ');a0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[0];L0=np.linalg.norm(P-a0);forces=[];errors=[];outputs=[]
   for p,c,o in zip(phase,commands,op):
    lam=np.fromstring(p['lambda_Ns'],sep=' ');forces.append(float(lam[unique_row(p['J'],0)]/dt));q=np.fromstring(p['q'],sep=' ').reshape(-1,3);errors.append(abs(L0-np.linalg.norm(P-q[0])-float(c['command_m'])));outputs.append(float(lam[unique_row(o['J'])]/dt))
   tendons.append(dict(tendon=j,maximum_input_tension_N=max(forces),final_input_tension_N=forces[-1],maximum_output_tension_N=max(outputs),final_output_tension_N=outputs[-1],maximum_input_geometric_error_m=max(errors),late_input_geometric_error_m=max(errors[-20:]),force_cap_samples=sum(f>=1.5-1e-9 for f in forces)))
  metrics=dict(saved_steps=steps,minimum_saved_volume_ratio=min(ratios),nonzero_contact_rows=len(contacts),tendons=tendons);ok=min(ratios)>0 and not contacts and all(t['maximum_input_tension_N']<=1.5+1e-12 and (not a.full or t['late_input_geometric_error_m']<=1e-6) for t in tendons)
 d=dict(status='PASS_REGISTERED_LEVER_FULL_SINGLE_CLOSING_ONLY' if ok and a.full else 'PASS_REGISTERED_LEVER_PREFIX_ONLY' if ok else 'FAIL_REGISTERED_LEVER_SINGLE_FINGER',process=process,metrics=metrics,preflight_sha256=sha(out/'preflight.json'),source_sha256=sha(Path(__file__)),scope=pre['scope']+' Actual no-object Finger only; not3Finger or100ggrasp, no time/mesh/material/physical joint qualification.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
