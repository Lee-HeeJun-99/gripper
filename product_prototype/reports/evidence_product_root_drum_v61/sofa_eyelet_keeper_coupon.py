"""Native finite keeper/eyelet axial-stop coupon;not real clamp strength or gripper."""
import argparse,csv,json,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_finite_guard import finite_guard
import sys
sys.path.insert(0,str(BASE/'cad'))
from manufacturing_assembly import evaluate

def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def collision(node,body,group,rigid=False):
 mesh=ET.SubElement(node,'Node',name='surface');ET.SubElement(mesh,'MeshTopology',name='topology',position=flat(body.vertices*.001),triangles=flat(body.faces));ET.SubElement(mesh,'MechanicalObject',name='points',template='Vec3d',position='@topology.position')
 if rigid:ET.SubElement(mesh,'RigidMapping',input='@../frames',output='@points')
 else:ET.SubElement(mesh,'FixedProjectiveConstraint',indices=flat(np.arange(len(body.vertices))))
 for tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):ET.SubElement(mesh,tag,group=str(group),**({} if rigid else dict(moving='0',simulated='0')))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--direction',type=int,choices=(-1,1),default=1);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/product_root_bearing832/scene.scn';recipe=BASE/'results/product_eyelet_keeper894/full_assembly_recipe.json';frame=BASE/'results/product_eyelet_keeper894/keeper_frame.json';parts=json.loads(recipe.read_text())['parts'];H=np.array(json.loads(frame.read_text()));ring=evaluate(next(p['shape'] for p in parts if p['name']=='f0_c1_s0_eyelet'));ring.apply_transform(np.linalg.inv(H));com=ring.center_mass.copy();ring.apply_translation(-com);mass=1e-4;I=ring.moment_inertia/ring.volume*1e-6
 tree=ET.parse(source);root=tree.getroot()
 for node in list(root.findall('Node')):root.remove(node)
 body=ET.SubElement(root,'Node',name='eyelet');initial_v=np.array([0,0,a.direction*.01,0,0,0]);ET.SubElement(body,'MechanicalObject',name='frames',template='Rigid3d',position='0 0 0 0 0 0 1',velocity=flat(initial_v));ET.SubElement(body,'UniformMass',template='Rigid3d',vertexMass=flat([mass,ring.volume*1e-9,*I.ravel()]));ET.SubElement(body,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass='1',filename=str(out/'eyelet.csv'));collision(body,ring,1,True)
 names=['f0_c1_s0_support','f0_c1_s0_keeper_cover',*[f'f0_c1_s0_keeper_screw{k}' for k in (0,1)],*[f'f0_c1_s0_keeper_nut{k}' for k in (0,1)]]
 for name in names:
  mesh=evaluate(next(p['shape'] for p in parts if p['name']==name));mesh.apply_transform(np.linalg.inv(H));mesh.apply_translation(-com);collision(ET.SubElement(root,'Node',name=name),mesh,2)
 for tag in ('NativePairRows','NativeResponseRows'):root.find(tag).set('body','@eyelet/frames')
 for item in root.iter():
  if item.get('filename'):item.set('filename',str(out/Path(item.get('filename')).name))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());steps=80;dt=float(root.get('dt'));command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];start=time.monotonic();process=finite_guard(command,out/'process',420,state_file=out/'eyelet.csv');rows=list(csv.DictReader((out/'eyelet.csv').open())) if (out/'eyelet.csv').exists() else [];q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);imp=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3] for r in rows]);finite=bool(len(rows) and np.isfinite(q).all() and np.isfinite(v).all() and np.isfinite(imp).all());logs=''.join((out/'process'/x).read_text(errors='replace') for x in ('stdout.log','stderr.log'));complete=process['exit_code']==0 and '[ERROR]' not in logs and finite and len(rows)==steps
 binaries=[Path(command[0]),*[Path(x.get('pluginName')) for x in root.findall('RequiredPlugin') if Path(x.get('pluginName')).is_file()]]
 for item in root.findall('RequiredPlugin'):
  lib=Path('/home/ubuntu/SOFA/v26.06.00/lib')/('lib'+item.get('pluginName')+'.so')
  if lib.is_file():binaries.append(lib)
 result=dict(status='NATIVE_KEEPER_COUPON_COMPLETED_NOT_JOINT_QUALIFICATION' if complete else 'FAIL_NATIVE_KEEPER_COUPON',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p):sha(p) for p in (Path(__file__),source,recipe,frame,BASE/'cad/manufacturing_assembly.py',BASE/'sofa/native_finite_guard.py')},binary_hashes={str(p):sha(p) for p in binaries},SDK='/home/ubuntu/SOFA/v26.06.00',scene_sha256=sha(out/'scene.scn'),command=command,process=process,runtime_s=time.monotonic()-start,dt_s=dt,state_rows=len(rows),simulated_time_s=len(rows)*dt,ASSUMED_eyelet_mass_kg=mass,assumed_uniform_inertia_per_mass_m2=I.tolist(),common_frame_COM_shift_mm=com.tolist(),initial_v=initial_v.tolist(),maximum_axial_travel_mm=float(np.max(abs(q[:,2]))*1000) if finite else None,final_velocity=v[-1].tolist() if finite else None,nonzero_impulse_steps=int(np.count_nonzero(np.linalg.norm(imp,axis=1)>0)) if finite else None,maximum_linear_momentum_residual_Ns=float(np.max(abs(mass*(v[:,:3]-np.vstack([initial_v[:3],v[:-1,:3]]))-imp))) if finite else None,actual_material=None,actual_joint_strength_N=None,fabrication_ready=False,scope='NEW finite axial-stop diagnostic:actual keeper6solids ideally fixed,actual Eyelet Rigid3 free,assumed100mg uniformmass,initialaxialspeed10mm/s,gravity0,mu0,20ms. Common rigidframe+COM recenter preservesrelativeCADgeometry. No cable/Skin/fullhardware/realpreload/materialdeformation/retentionstrength/time/mesh/impactlaw/holdingqualification;contact impulses NOT continuousforces.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],rows=len(rows),travel_mm=result['maximum_axial_travel_mm'],impulse_steps=result['nonzero_impulse_steps'],runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
