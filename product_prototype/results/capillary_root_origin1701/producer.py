"""All-three-root/six-origin fixture on current finite hardware;not a Lift test."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def install(root,out,begin,end,height):
 meta=json.loads((BASE/'results/b3_origin_observer1075/summary.json').read_text());binary=Path(meta['binary']);assert sha(binary)==meta['binary_sha256'];root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));dt=float(root.get('dt'))
 for i in range(3):
  free=root.find(f"Node[@name='free{i}']");fixed=free.find('FixedProjectiveConstraint');ids=fixed.get('indices');free.remove(fixed);times=[0,begin-dt,end-dt,10.] if begin>0 else [-dt,end-dt,10.];mov=[0,0,height,height] if begin>0 else [0,height,height];ET.SubElement(free,'LinearMovementProjectiveConstraint',indices=ids,keyTimes=' '.join(map(str,times)),movements=' '.join(f'0 0 {z}' for z in mov))
  # Append after NativeCableSequence so its origin reset cannot overwrite this.
  finger=root.find(f"Node[@name='finger{i}']")
  for j in range(2):ET.SubElement(finger,'NativeCableOrigin',target=f'@../guides{i}/cable{j}/actuator',filename=str(out/f'origin{i}_{j}.csv'),drive='1',begin=str(begin),end=str(end),height=str(height))
 return dict(binary_sha256=sha(binary),compiled_source_sha256=meta['compiled_source_sha256'])
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='dispatch_finite_holding1586');a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();identity=install(root,out,0,.01,.0001)
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',str(out/'scene.scn')],out/'process',60);local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);mask=local[:,0]<=5;position=velocity=origin=0.;counts=[]
 for i in range(3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open()));counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
  for r in rows:
   t=float(r['time_s']);q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);v=np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3);position=max(position,float(abs(q[mask]-q0[mask]-[0,0,.0001*min(t/.01,1)]).max()))
   if t<.01-1e-12:velocity=max(velocity,float(abs(v[mask]-[0,0,.01]).max()))
  for j in range(2):
   for r in csv.DictReader((out/f'origin{i}_{j}.csv').open()):
    t=float(r['accepted_time_s']);delta=np.fromstring(r['actual_pullPoint_m'],sep=' ')-np.fromstring(r['initial_pullPoint_m'],sep=' ');origin=max(origin,float(abs(delta-[0,0,.0001*min(t/.01,1)]).max()))
 logs=''.join((out/'process'/x).read_text(errors='replace') for x in ('stdout.log','stderr.log'));ok=proc['exit_code']==0 and '[ERROR]'not in logs and counts==[4]*3 and max(position,velocity,origin)<=1e-12;d=dict(status='PASS_ALL_ROOTS_AND_ORIGINS_API_ONLY' if ok else 'FAIL_ROOT_ORIGIN_API',process=proc,outputs=counts,maximum_root_position_error_m=position,maximum_interior_root_velocity_error_m_s=velocity,maximum_origin_error_m=origin,origin_plugin=identity,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='Current finite3finger ALLcollisions/freeobject retained,rootexternalfixture only. No objectstate prescribed. 100micrometre/10ms inputAPI test,NOTHolding/Lift or work/physical qualification.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
