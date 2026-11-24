"""Actual composite exterior/support load and sphere momentum inventory."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_contact_layer_union_entry1351');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);index={v:k for k,v in enumerate(t)};parts={k:np.zeros((len(rows),6)) for k in ('composite','guide','support','other')};seen=set()
 for r in read(src/'response_rows.csv'):
  paths=(r['model0'],r['model1'])
  if not any('/object/'in x for x in paths):continue
  key=(float(r['time_s']),int(r['row_id']));assert key not in seen;seen.add(key);other=paths[1] if '/object/'in paths[0] else paths[0];kind='composite' if '/exterior/'in other else 'guide' if '/guides'in other else 'support' if '/floor/'in other else 'other';parts[kind][index[key[0]]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
 tree=ET.parse(src/'scene.scn');root=tree.getroot();dt=float(root.get('dt'));gravity=np.fromstring(root.get('gravity'),sep=' ');massdata=root.find("Node[@name='object']/UniformMass");vertex=np.fromstring(massdata.get('vertexMass',''),sep=' ');mass=float(vertex[0]) if len(vertex) else float(massdata.get('totalMass'));R=float(root.find("Node[@name='object']/Node/SphereCollisionModel").get('radius'))
 if len(vertex):assert np.max(abs(vertex[2:].reshape(3,3)-np.eye(3)*.4*R*R))<1e-15
 v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);I=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);dv=np.diff(np.vstack([np.zeros(6),v]),axis=0);linear=mass*dv[:,:3]-mass*gravity*dt-I[:,:3];angular=.4*mass*R*R*dv[:,3:]-I[:,3:];partition=float(abs(I-sum(parts.values())).max());history=[]
 for k,time in enumerate(t):history.append(dict(time_s=float(time),object_z_m=float(q[k,2]),object_speed_m_s=float(np.linalg.norm(v[k,:3])),solver_iterations=int(rows[k]['solver_iterations']),**{n+'_Fz_N':float(f[k,2]/dt) for n,f in parts.items()}))
 with (out/'history.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
 d=dict(status='ACTUAL_COMPOSITE_LOAD_INVENTORY_ONLY',case=a.case,outputs=len(t),endpoint=history[-1],sphere_mass_kg=mass,gravity_m_s2=gravity.tolist(),weight_N=float(-mass*gravity[2]),linear_momentum_max_residual_Ns=float(abs(linear).max()),angular_momentum_max_residual_Nms=float(abs(angular).max()),response_partition_max_error_Ns_Nms=partition,max_solver_iterations=max(r['solver_iterations'] for r in history),bare_Skin_load='NOT_SEPARATED_BY_MODEL_PAIR_COMPOSITE_SURFACE',contact_area=None,pressure=None,whole_energy=None,physical_validation='NOT QUALIFIED',scope='Actual response rows grouped by collision model path. Composite includes Skin/Rail/pad;not bareSkin force or Holding verdict. Spherical momentum inventory only,not time/mesh/energy or hardware qualification.',input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv')});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
