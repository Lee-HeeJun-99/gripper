"""Finite-envelope measured-state clutch: new control hypothesis, not a force sweep.
Only the next cable sequence maximum force changes. All q/v, contacts and material
states remain native; disabled mode must reproduce the original state exactly.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three,flat

def hardware_sensor(root,i):
 parent=root.find(f"Node[@name='guides{i}']")
 q=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
 local=[];owners=[]
 for j in range(2):
  cable=parent.find(f"Node[@name='cable{j}']")
  for n in cable.findall('Node'):
   if not n.get('name','').startswith(('eyelet','support')):continue
   v=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
   ids=np.fromstring(n.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
   assert len(ids)==len(v)
   for x,k in zip(v,ids):local.append(Rotation.from_quat(q[k,3:]).inv().apply(x-q[k,:3]));owners.append(k)
 theta=np.deg2rad(i*120);er=np.array([np.cos(theta),np.sin(theta),0]);et=np.array([-er[1],er[0],0])
 normals=np.array([(-np.sqrt(3)*er+side*et)/2 for side in (-1,1)])
 return np.array(local),np.array(owners),normals

def sensed_gap(q,local,owners,normals):
 x=Rotation.from_quat(q[owners,3:]).apply(local)+q[owners,:3]
 return float(-(x@normals.T).max())

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--enabled',action='store_true');p.add_argument('--duration',type=float,choices=(.01,1.2,2.),default=.01);p.add_argument('--control');a=p.parse_args()
 src=BASE/'results/capillary_hold1700';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 root=ET.parse(src/'scene.scn').getroot();pre=json.loads((src/'preflight.json').read_text());threshold=float(root.find('NativeRigidSphereLocalProximity').get('contactDistance'))/2
 binary=BASE/'cad/build_sector_clutch1714/libReGripSectorClutch.so';assert binary.exists()
 if a.enabled:
  assert a.control
  control=json.loads((BASE/'results'/a.control/'clutch_assessment.json').read_text());assert control['passive_purity_maximum']==0 and control['sensor_error_m']<=1e-12
  assert a.duration==1.2,'Expand only after independently assessing this minimal mechanism trial'
 ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));sensors=[];margins=[]
 for i in range(3):
  sequence=root.find(f"Node[@name='finger{i}']/NativeCableSequence");sequence.set('name','sequence')
  local,owners,normals=hardware_sensor(root,i);sensors.append((local,owners,normals))
  q0=np.fromstring(root.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  margins.append(sensed_gap(q0,*sensors[-1]));assert margins[-1]>threshold
  ET.SubElement(root,'NativeSectorClutch',body=f'@guides{i}/frames',sequence=f'@finger{i}/sequence',vertices=flat(local),owners=' '.join(map(str,owners)),normal0=flat(normals[0]),normal1=flat(normals[1]),threshold=str(threshold),enabled=str(int(a.enabled)),filename=str(out/f'clutch{i}.csv'))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 intervention=dict(hypothesis='Accepted finite hardware own-sector limit triggers a latching release of that finger cable pair. Tests whether closure drive sustains bracing; not guaranteed collision avoidance or Holding.',enabled=a.enabled,threshold_m=threshold,initial_sector_gaps_m=margins,command_limit_N=1.5,source_sha256=sha(Path(__file__)),controller_source_sha256=sha(BASE/'sofa/native_sector_clutch/Controller.cpp'),binary_sha256=sha(binary),source_scene_sha256=sha(src/'scene.scn'),unchanged='All geometry, masses, FEM, mapping, initial states, wire path, collision models, contactDistance, friction, dt and solver. Controller changes only next-step cable command; no state or contact writes.',physical_scope='Ideal geometric sensing/zero-delay clutch assumption; real sensor, clutch dynamics and finite-wire sliding NOT QUALIFIED. Original full time/mesh failures preserved.')
 (out/'intervention.json').write_text(json.dumps(intervention,indent=2));(out/'Controller.cpp').write_bytes((BASE/'sofa/native_sector_clutch/Controller.cpp').read_bytes())
 run_three(root,out,src,pre['eyelet'],pre['parts'],round(a.duration/.0025),a.duration,300.)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 purity=0.;sensor_error=0.;triggers=[]
 for i in range(3):
  frames=list(csv.DictReader((out/f'guide_frames{i}.csv').open()));sensor=list(csv.DictReader((out/f'clutch{i}.csv').open()));assert len(frames)==len(sensor)
  for fr,se in zip(frames,sensor):
   assert float(fr['time_s'])==float(se['time_s'])
   q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7);sensor_error=max(sensor_error,abs(sensed_gap(q,*sensors[i])-float(se['accepted_sector_gap_m'])))
  triggers.append(next((float(s['time_s']) for s in sensor if s['latched']=='1'),None))
 if not a.enabled:
  for name,fields in [('object.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms'))]+[(f'guide_frames{i}.csv',('rigid_q','rigid_v')) for i in range(3)]+[(f'finger{i}.csv',('q_m','v_m_s')) for i in range(3)]:
   old=list(csv.DictReader((src/name).open()));new=list(csv.DictReader((out/name).open()));assert len(new)==round(a.duration/.0025)
   for x,y in zip(new,old):
    assert float(x['time_s'])==float(y['time_s'])
    for field in fields:purity=max(purity,float(abs(np.fromstring(x[field],sep=' ')-np.fromstring(y[field],sep=' ')).max()))
 result=dict(status='PASS_PASSIVE_SENSOR_ONLY' if not a.enabled and purity==0 and sensor_error<=1e-12 else 'ACTIVE_CONTROL_REQUIRES_CONTACT_AND_GOAL_ASSESSMENT',passive_purity_maximum=purity if not a.enabled else None,sensor_error_m=sensor_error,trigger_time_s=triggers,scope=intervention['physical_scope'])
 (out/'clutch_assessment.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
