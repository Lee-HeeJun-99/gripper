"""Finite wire-cross-section sphere on actual root groove;NOT a complete wire/pulley."""
import argparse,csv,json,math,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_finite_guard import finite_guard

def vec(value):return np.fromstring(value,sep=' ')
def flat(value):return ' '.join(format(float(x),'.17g') for x in np.array(value).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--tangent-speed',type=float,default=.002);a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/product_root_bearing832/scene.scn';tree=ET.parse(source);root=tree.getroot()
 root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
 wheel=root.find("./Node[@name='wheel']");wheel.find('MechanicalObject').set('velocity','0 0 0 0 0 0');wheel.remove(wheel.find('PartialFixedProjectiveConstraint'));ET.SubElement(wheel,'FixedProjectiveConstraint',indices='0')
 theta=math.pi/64;normal=np.array([math.cos(theta),math.sin(theta),0]);tangent=np.array([-math.sin(theta),math.cos(theta),0]);initial_q=.002005*normal;initial_v=a.tangent_speed*tangent;force=-1e-5*normal;mass=1e-5;radius=.00025;inertia_per_mass=.4*radius**2
 node=ET.SubElement(root,'Node',name='wire_section');ET.SubElement(node,'MechanicalObject',name='frames',template='Rigid3d',position=flat([*initial_q,0,0,0,1]),velocity=flat([*initial_v,0,0,0]));ET.SubElement(node,'UniformMass',template='Rigid3d',vertexMass=flat([mass,4*math.pi*radius**3/3,inertia_per_mass,0,0,0,inertia_per_mass,0,0,0,inertia_per_mass]));ET.SubElement(node,'ConstantForceField',template='Rigid3d',forces=flat([*force,0,0,0]));ET.SubElement(node,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass='1',filename=str(out/'wire.csv'))
 col=ET.SubElement(node,'Node',name='cross_section');ET.SubElement(col,'MechanicalObject',name='points',template='Vec3d',position='0 0 0');ET.SubElement(col,'SphereCollisionModel',radius=str(radius),group='3');ET.SubElement(col,'RigidMapping',input='@../frames',output='@points')
 for item in root.iter():
  if item.get('filename'):item.set('filename',str(out/Path(item.get('filename')).name))
 for tag in ('NativePairRows','NativeResponseRows'):root.find(tag).set('body','@wire_section/frames')
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());steps=60;dt=float(root.get('dt'))
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];start=time.monotonic();process=finite_guard(command,out/'process',420,state_file=out/'wire.csv')
 rows=list(csv.DictReader((out/'wire.csv').open())) if (out/'wire.csv').exists() else [];positions=np.array([vec(r['rigid_q'])[:3] for r in rows]);velocities=np.array([vec(r['rigid_v'])[:3] for r in rows]);impulses=np.array([vec(r['object_impulse_Ns_Nms'])[:3] for r in rows]);finite=bool(len(rows) and np.isfinite(positions).all() and np.isfinite(velocities).all() and np.isfinite(impulses).all())
 topology=wheel.find('./Node/MeshTopology');mesh=trimesh.Trimesh(vertices=vec(topology.get('position')).reshape(-1,3),faces=vec(topology.get('triangles')).astype(int).reshape(-1,3),process=False)
 points=np.vstack([initial_q,positions]) if finite else initial_q[None,:];_,dist,_=trimesh.proximity.closest_point_naive(mesh,points);gaps=dist-radius
 residual=None;sliding=None;nonzero=0
 if finite:
  residual=float(np.max(abs(mass*(velocities-np.vstack([initial_v,velocities[:-1]]))-force*dt-impulses)));sliding=float((positions[-1]-initial_q)@tangent);nonzero=int(np.count_nonzero(np.linalg.norm(impulses,axis=1)>0))
 logs=''.join((out/'process'/x).read_text(errors='replace') for x in ('stdout.log','stderr.log'));complete=process['exit_code']==0 and '[ERROR]' not in logs and finite and len(rows)==steps
 inputs=[Path(__file__),source,BASE/'sofa/native_finite_guard.py'];binaries=[Path(x.get('pluginName')) for x in root.findall('RequiredPlugin') if Path(x.get('pluginName')).is_file()]+[Path(command[0])]
 result=dict(status='NATIVE_FINITE_WIRE_SECTION_COMPLETED_NOT_QUALIFIED' if complete else 'FAIL_NATIVE_WIRE_SECTION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in inputs},binary_hashes={str(x):sha(x) for x in binaries},scene_sha256=sha(out/'scene.scn'),command=command,process=process,runtime_s=time.monotonic()-start,dt_s=dt,steps=len(rows),mass_kg=mass,wire_radius_m=radius,initial_q_m=initial_q.tolist(),initial_v_m_s=initial_v.tolist(),external_force_N=force.tolist(),initial_mesh_gap_m=float(gaps[0]),minimum_accepted_mesh_gap_m=float(min(gaps[1:])) if len(gaps)>1 else None,maximum_linear_momentum_residual_Ns=residual,tangent_travel_m=sliding,nonzero_impulse_steps=nonzero,actual_material=None,scope='Newresearchmodel:onefree spherical wire-cross-section proxy against ACTUAL finite V39 root groove triangles underconstant radialpreload,mu0. WheelallDOFs ideallyfixed;ALL oldwheel/landcollisions retained. SphereisNOT a continuous wire,hasNO CableConstraint,axialstiffness,bending,endpointtension,wraplaw or equalizer. Not matched to839idealwire orB3. No time/mesh/energy/friction/fabrication/holdingqualification.',physical_wire_qualified=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
