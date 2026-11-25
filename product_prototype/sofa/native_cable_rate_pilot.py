"""Four-step read-only Native cable observer; exact preserved-prefix purity."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three,flat

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.01,.6),default=.01);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);steps=round(a.duration/.0025)
 src=BASE/'results/yoke_hold_diagnostic1741';root=ET.parse(src/'scene.scn').getroot();pre=json.loads((src/'preflight.json').read_text());binary=BASE/'cad/build_cable_rate1819/libReGripCableRate.so';assert binary.exists()
 ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));geometry=[]
 for i in range(3):
  node=root.find(f"Node[@name='guides{i}']");q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
  for j in range(2):
   c=node.find(f"Node[@name='cable{j}']");ids=np.fromstring(c.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);x=np.fromstring(c.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);local=Rotation.from_quat(q[ids,3:]).inv().apply(x-q[ids,:3]);origin=np.fromstring(c.find('CableConstraint').get('pullPoint'),sep=' ');geometry.append((i,j,ids,local,origin))
   ET.SubElement(root,'NativeCableRate',body=f'@guides{i}/frames',local=flat(local),owners=' '.join(map(str,ids)),origin=flat(origin),filename=str(out/f'rate{i}_{j}.csv'))
 for e in root.iter():
  for k,v in list(e.attrib.items()):e.set(k,v.replace(str(src),str(out)))
 run_three(root,out,src,pre['eyelet'],pre['parts'],steps,a.duration,249.3*a.duration/2)
 purity=0.;error=0.
 for name,fields in [('object.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms'))]+[(f'guide_frames{i}.csv',('rigid_q','rigid_v')) for i in range(3)]+[(f'finger{i}.csv',('q_m','v_m_s')) for i in range(3)]:
  old=list(csv.DictReader((src/name).open()));new=list(csv.DictReader((out/name).open()));assert len(new)==steps
  for x,y in zip(new,old):
   assert float(x['time_s'])==float(y['time_s'])
   for field in fields:purity=max(purity,float(abs(np.fromstring(x[field],sep=' ')-np.fromstring(y[field],sep=' ')).max()))
 for i,j,ids,local,origin in geometry:
  frames=list(csv.DictReader((out/f'guide_frames{i}.csv').open()));sensor=list(csv.DictReader((out/f'rate{i}_{j}.csv').open()));assert len(sensor)==steps
  for fr,se in zip(frames,sensor):
   assert float(fr['time_s'])==float(se['time_s'])
   q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7)[ids];v=np.fromstring(fr['rigid_v'],sep=' ').reshape(-1,6)[ids];arm=Rotation.from_quat(q[:,3:]).apply(local);x=np.vstack([origin,q[:,:3]+arm]);vel=np.vstack([np.zeros(3),v[:,:3]+np.cross(v[:,3:],arm)]);dx=np.diff(x,axis=0);length=np.linalg.norm(dx,axis=1).sum();rate=float((dx/np.linalg.norm(dx,axis=1)[:,None]*np.diff(vel,axis=0)).sum());error=max(error,abs(rate-float(se['rate_m_s'])),abs(length-float(se['length_m'])))
 result=dict(status='PASS_READ_ONLY_NATIVE_RATE_PREFIX' if purity==0 and error<=1e-12 else 'FAIL_RATE_OR_OBSERVER_PURITY',passive_q_v_impulse_maximum_difference=purity,maximum_sensor_length_rate_error=error,actual_steps=steps,actual_duration_s=a.duration,source_sha256=sha(Path(__file__)),observer_source_sha256=sha(BASE/'sofa/native_cable_rate/Observer.cpp'),binary_sha256=sha(binary),scope='Accepted AnimateEnd only; no force, state, contact or solver writes. Bounded prefix purity, not full Hold purity, force-phase/work, feedback efficacy, convergence or grasp PASS.')
 (out/'observer_assessment.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'Observer.cpp').write_bytes((BASE/'sofa/native_cable_rate/Observer.cpp').read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
