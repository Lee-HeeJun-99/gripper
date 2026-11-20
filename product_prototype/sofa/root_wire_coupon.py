"""Native cable-on-rigid anchors diagnostic; explicitly NOT a sliding pulley."""
import argparse,csv,json,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_finite_guard import finite_guard

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--balanced',action='store_true');p.add_argument('--free-axle',action='store_true');a=p.parse_args()
 if a.free_axle and not a.balanced:p.error('free-axle diagnostic requires balanced anchors')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 source=BASE/'results/product_root_bearing832/scene.scn';tree=ET.parse(source);root=tree.getroot();wheel=root.find("./Node[@name='wheel']")
 wheel.find('MechanicalObject').set('velocity','0 0 0 0 0 0')
 if a.free_axle:wheel.find('PartialFixedProjectiveConstraint').set('fixedDirections','0 0 1 1 1 0')
 root.insert(0,ET.Element('RequiredPlugin',pluginName='/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'))
 radius=.002;tension=.00001;dt=float(root.get('dt'));steps=10
 anchors=[([radius,0,0],[radius,.01,0])]
 if a.balanced:anchors.append(([0,radius,0],[.01,radius,0]))
 for i,(point,pull) in enumerate(anchors):
  child=ET.SubElement(wheel,'Node',name=f'wire{i}')
  ET.SubElement(child,'MechanicalObject',name='point',template='Vec3d',position=' '.join(map(str,point)))
  ET.SubElement(child,'CableConstraint',name='cable',indices='0',pullPoint=' '.join(map(str,pull)),value=str(tension*dt),valueType='force')
  ET.SubElement(child,'RigidMapping',input='@../frames',output='@point',index='0')
 for item in root.iter():
  if item.get('filename'):item.set('filename',str(out/Path(item.get('filename')).name))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
 start=time.monotonic();proc=finite_guard(command,out/'process',420,state_file=out/'wheel.csv')
 rows=list(csv.DictReader((out/'wheel.csv').open())) if (out/'wheel.csv').exists() else []
 v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);finite=bool(len(rows) and np.isfinite(v).all() and np.isfinite(q).all())
 logs=''.join((out/'process'/x).read_text(errors='replace') for x in ('stdout.log','stderr.log'))
 first=list(csv.DictReader((out/'direct.csv').open())) if (out/'direct.csv').exists() else []
 first=[r for r in first if float(r['time_s'])==dt]
 torque_impulse=sum(float(r['lambda_Ns'])*np.fromstring(r['J'],sep=' ')[5] for r in first)
 mass=np.fromstring(wheel.find('UniformMass').get('vertexMass'),sep=' ');iz=mass[0]*mass[-1]
 ref=0 if a.balanced else radius*tension*dt
 actual=iz*v[0,5] if finite else None
 linear=sum((float(r['lambda_Ns'])*np.fromstring(r['J'],sep=' ')[:3] for r in first),np.zeros(3))
 linear_ref=np.array([tension*dt,tension*dt,0]) if a.free_axle else np.zeros(3)
 linear_actual=mass[0]*v[0,:3] if finite else None
 passed=proc['exit_code']==0 and '[ERROR]' not in logs and finite and len(rows)==steps and abs(torque_impulse-ref)<1e-18 and abs(actual-ref)<1e-18 and (not a.free_axle or (np.max(abs(linear-linear_ref))<1e-18 and np.max(abs(linear_actual-linear_ref))<1e-18))
 inputs=[Path(__file__),source,BASE/'sofa/native_finite_guard.py',Path('/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/include/SoftRobots/component/constraint/model/CableModel.inl')]
 binaries=[Path(x.get('pluginName')) for x in root.findall('RequiredPlugin') if Path(x.get('pluginName')).is_file()]
 d=dict(status='PASS_NATIVE_ANCHORED_CABLE_CONTRACT_ONLY' if passed else 'FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in inputs},binary_hashes={str(x):sha(x) for x in binaries},scene_sha256=sha(out/'scene.scn'),command=command,process=proc,runtime_s=time.monotonic()-start,steps=len(rows),dt_s=dt,balanced=a.balanced,tension_N=tension,radius_m=radius,first_reference_angular_impulse_Nms=ref,first_native_J_lambda_Nms=float(torque_impulse),first_angular_momentum_Nms=actual,final_velocity=v[-1].tolist() if finite else None,scope='Rigidly attached anchors,not cable sliding. Balanced case has TWO independently prescribed equal forces,not mechanical equalization. Existing finite wheel/land collision geometry stays enabled. Ideal bearing reactions/work NOT MEASURED. No wire collision,arc constraint,friction,time/energy/3finger qualification.',physical_sliding_qualified=False)
 d.update(free_axle=a.free_axle,first_projected_linear_J_lambda_Ns=linear.tolist(),first_reference_free_linear_impulse_Ns=linear_ref.tolist() if a.free_axle else None,first_linear_momentum_Ns=linear_actual.tolist() if finite else None)
 if a.free_axle:d['scope']+=' NEWfree-in-planeaxlediagnostic:locksaxialz/tilt,allowsxy/spin;notphysicalbearing. Compareinitiallinearimpulseonly;latergeometrychanges. Noaxlereactionclaim.'
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
