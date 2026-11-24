"""Read-only no-object unload/recovery vs same-time zero-force gravity reference."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/opposed_release1401';ref=BASE/'results/opposed_zero_reference1403';prior=BASE/'results/opposed_nonuniform_mid1398';r=read(src/'finger0.csv');z=read(ref/'finger0.csv');assert len(r)==len(z)==480;root=ET.parse(src/'scene.scn').getroot();q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);history=[]
 for row,zero in zip(r,z):
  assert row['time_s']==zero['time_s'];q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);qz=np.fromstring(zero['q_m'],sep=' ').reshape(-1,3);v=np.fromstring(row['v_m_s'],sep=' ').reshape(-1,3);vz=np.fromstring(zero['v_m_s'],sep=' ').reshape(-1,3);norm=np.linalg.norm(qz-q0);history.append(dict(time_s=float(row['time_s']),command_force_N=float(row['command_N']),max_q_minus_gravity_reference_m=float(abs(q-qz).max()),max_v_minus_gravity_reference_m_s=float(abs(v-vz).max()),max_node_speed_m_s=float(np.linalg.norm(v,axis=1).max()),relative_displacement_vs_gravity_without_floor=None if norm==0 else float(np.linalg.norm(q-qz)/norm)))
 late=[row for row in r if float(row['time_s'])>=.9-1e-12];impulse=max(abs(float(row[f'cable{k}_force_raw'])) for row in late for k in (0,1));command=max(abs(float(row['command_N'])) for row in late);prefix={}
 for file in ('finger0.csv','guide_frames0.csv','skin_points0.csv','rail_points0.csv'):
  previous=read(prior/file);current=read(src/file);prefix[file]=current[:len(previous)]==previous
 d=dict(status='ACTUAL_UNLOAD_AND_REFERENCE_RETURN_INVENTORY_ONLY',endpoint=history[-1],late_after_release_samples=len(late),late_max_cable_impulse_Ns=impulse,late_max_command_N=command,first_240_record_equality=prefix,history=history,scope='Same-time Nativegravity zero-force reference,not manufactured-rest or measuredmaterial recovery certification. No q/vreset or chunkedresume. Exactprefix is reproducibility,not time convergence. No object/contact or Holding. No invented recovery tolerance.',physical_validation='NOT QUALIFIED',input_hashes={str(p.relative_to(BASE)):sha(p) for case in (src,ref,prior) for p in (case/'scene.scn',case/'finger0.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('history','input_hashes')}))
if __name__=='__main__':main()
