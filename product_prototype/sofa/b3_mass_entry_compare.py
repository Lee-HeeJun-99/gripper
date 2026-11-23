"""Same physical geometry/control,three masses,actual short contact-entry traces."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from b3_exploration_contract import normalized
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];hashes={};baseline=BASE/'results/b3_alarm_window485';reference=normalized(baseline/'scene.scn',baseline);old=reference.find("./Node[@name='object']/UniformMass").get('vertexMass');binary=set()
 for name in ('b3_alarm_window485','b3_mass75_entry1084','b3_mass100_explore1059'):
  src=BASE/'results'/name;meta=json.loads((src/'summary.json').read_text());binary.add(meta['binary_sha256']);root=normalized(src/'scene.scn',src);body=root.find("./Node[@name='object']/UniformMass");mass=float(body.get('vertexMass').split()[0]);body.set('vertexMass',old)
  if ET.tostring(root)!=ET.tostring(reference):raise ValueError('unexpected non-mass Scene difference')
  rows=[r for r in csv.DictReader((src/'object.csv').open()) if float(r['time_s'])<=.3+1e-12];t=np.array([float(r['time_s']) for r in rows]);iters=np.array([int(r['solver_iterations']) for r in rows]);err=np.array([float(r['solver_error']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in rows]);skin=np.zeros(len(t));support=np.zeros(len(t));index={x:k for k,x in enumerate(t)};first_skin=None
  for r in csv.DictReader((src/'response_rows.csv').open()):
   time=float(r['time_s'])
   if time>.3+1e-12:break
   paths=[r['model0'],r['model1']]
   if not any('/object/' in x for x in paths):continue
   z=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[2]/meta['dt_s']
   if any('/skinCollision/' in x for x in paths):
    skin[index[time]]+=z
    if abs(z)>0 and first_skin is None:first_skin=time
   elif any('/floor/' in x for x in paths):support[index[time]]+=z
  records.append(dict(case=name,mass_kg=mass,outputs=len(rows),first_nonzero_skin_vertical_s=first_skin,first_iteration_limit_s=float(t[iters>=1000][0]) if any(iters>=1000) else None,iteration_limited_outputs=int(sum(iters>=1000)),maximum_solver_error=float(err.max()),last_object_position_m=q[-1].tolist(),last_skin_vertical_N=float(skin[-1]),last_support_vertical_N=float(support[-1]),holding='NOT ASSESSED_SHORT_ENTRY_WINDOW'))
  with (out/(name+'.csv')).open('w') as f:w=csv.writer(f);w.writerow(['time_s','solver_iterations','solver_error','object_z_m','skin_z_N','support_z_N']);w.writerows(zip(t,iters,err,q[:,2],skin,support))
  for path in [src/'summary.json',src/'object.csv',src/'response_rows.csv',src/'scene.scn']:hashes[str(path.relative_to(BASE))]=sha(path)
 if len(binary)!=1:raise ValueError('compiled physical binary mismatch')
 d=dict(status='MASS_ONLY_ENTRY_DIAGNOSTIC_NOT_CAPACITY_OR_CONVERGENCE',records=records,compiled_physical_binary_sha256=list(binary)[0],hypothesis='Mass dependence of coupled contact/cable iteration saturation,not a changed cable command. Entry trace may motivate bounded linearized-row consistency study;does not identify a unique cause.',physical_validation='NOT QUALIFIED',input_hashes=hashes,producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
