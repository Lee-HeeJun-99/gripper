"""Actual partial force-mode trial inventory;never a full Holding verdict."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;run=json.loads((src/'summary.json').read_text());root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);index={x:i for i,x in enumerate(t)};q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);parts={k:np.zeros_like(total) for k in ('skin','rail','guide','support','other')};byfinger={str(i):np.zeros_like(total) for i in range(3)};seen=set()
 for r in read(src/'response_rows.csv'):
  names=(r['model0'],r['model1'])
  if not any('/object/'in x for x in names):continue
  key=(float(r['time_s']),int(r['row_id']));assert key not in seen;seen.add(key);k=index[key[0]];other=names[1] if '/object/'in names[0] else names[0];kind='skin' if '/skinCollision/'in other else 'rail' if '/railCollision/'in other else 'guide' if '/guides'in other else 'support' if '/floor/'in other else 'other';impulse=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');parts[kind][k]+=impulse
  if kind=='skin':
   for i in range(3):
    if f'/finger{i}/'in other:byfinger[str(i)][k]+=impulse
 mass=float(root.find("Node[@name='object']/UniformMass").get('vertexMass').split()[0]);g=np.fromstring(root.get('gravity'),sep=' ');momentum=mass*(v[:,:3]-np.vstack([np.zeros((1,3)),v[:-1,:3]]))-total[:,:3]-mass*g*dt;reference=int(np.argmin(abs(t-1.)));samples=[]
 for requested in (.25,.6,.8,1.,1.1,1.2):
  if requested>t[-1]+1e-12:continue
  k=int(np.argmin(abs(t-requested)));samples.append(dict(time_s=float(t[k]),position_mm=(q[k,:3]*1000).tolist(),speed_mm_s=float(np.linalg.norm(v[k,:3])*1000),vertical_velocity_mm_s=float(v[k,2]*1000),downward_from_1s_mm=float((q[reference,2]-q[k,2])*1000) if t[-1]>=1.-1e-12 else None,forces_N={n:(x[k,:3]/dt).tolist() for n,x in parts.items()},skin_force_each_finger_N={n:(x[k,:3]/dt).tolist() for n,x in byfinger.items()}))
 command_error=0.;peak=0.
 for i in range(3):
  for r in read(src/f'finger{i}.csv'):
   for j in range(2):value=float(r[f'cable{j}_force_raw']);peak=max(peak,abs(value)/dt);command_error=max(command_error,abs(value-float(r['command_Ns'])))
 d=dict(status='PARTIAL_NATIVE_INVENTORY_NOT_HOLDING_VERDICT',case=a.case,process=run['process'],duration_s=run['duration_s'],quality=run['qualities'],samples=samples,maximum_force_command_error_Ns=command_error,maximum_cable_force_N=peak,maximum_partition_error_Ns_Nms=float(abs(total-sum(parts.values())).max()),maximum_translational_momentum_residual_Ns=float(abs(momentum).max()),weight_N=float(-mass*g[2]),full_holding='NOT MEASURED',physical_validation='NOT QUALIFIED',input_hashes={f:sha(src/f) for f in ('scene.scn','summary.json','object.csv','response_rows.csv')},source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
