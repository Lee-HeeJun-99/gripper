"""Actual mapped Cartesian mass inventory; detect missing rigid gyroscopic dynamics."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def vec(s):return np.fromstring(s,sep=' ')
def read(p):return list(csv.DictReader(p.open()))
def inventory(q,v,m):
 c=q.mean(axis=0);u=v.mean(axis=0);r=q-c
 return m*u,np.sum(np.cross(r,m/len(q)*(v-u)),axis=0),float(m/(2*len(q))*np.sum((v-u)**2)),m/len(q)*sum(((x@x)*np.eye(3)-np.outer(x,x) for x in r),np.zeros((3,3)))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());records=[]
 if not meta['mapped_mass']:raise ValueError('requires actual mapped point masses')
 m=meta['assumed_mass_kg']
 for variant in (0,1):
  d=src/str(variant);root=ET.parse(d/'scene.scn').getroot()
  for i in (0,1):
   initial=meta['initial'][i];c=np.array(initial['q'])[:3];v=np.array(initial['v']);points=vec(root.find(f"./Node[@name='guide{i}']/Node[@name='massQuadrature']/MechanicalObject").get('position')).reshape(-1,3);vel=v[:3]+np.cross(v[3:],points-c);P,H,E,I=inventory(points,vel,m);P0,H0,E0=P.copy(),H.copy(),E;states=read(d/f'guide{i}.csv');massrows=read(d/f'mass{i}.csv')
   for state,row in zip(states,massrows):
    q=vec(row['q']).reshape(-1,3);u=vec(row['v']).reshape(-1,3);Pn,Hn,En,In=inventory(q,u,m);imp=vec(state['object_impulse_Ns_Nms']);records.append(dict(variant=variant,body=i,time_s=float(row['time_s']),linear_impulse_error_Ns=float(np.linalg.norm(Pn-P-imp[:3])),COM_angular_impulse_defect_Nms=float(np.linalg.norm(Hn-H-imp[3:])),angular_momentum_drift_from_initial_Nms=float(np.linalg.norm(Hn-H0)),angular_momentum_relative_drift=float(np.linalg.norm(Hn-H0)/np.linalg.norm(H0)),rotational_energy_J=En,rotational_energy_change_J=En-E,initial_geometric_inertia_error_kg_m2=float(np.max(abs(I-np.array(initial['world_inertia_kg_m2']))))));P,H,E=Pn,Hn,En
 free=meta['free_reference'];worst=max(r['angular_momentum_relative_drift'] for r in records);result=dict(status=('PASS_FREE_ANGULAR_0.1_PERCENT' if worst<=.001 else 'FAIL_FREE_ANGULAR_0.1_PERCENT') if free else 'CONTACT_ANGULAR_INVENTORY_DIAGNOSTIC',scope='Actual Native mapped Cartesian mass inventory. Defect is numerical/model inconsistency,NOT heat. Free torque-free angular invariant gate0.1%;contact rows and changing inertia separately measured. Not time convergence/B3 qualification.',source_summary_sha256=sha(src/'summary.json'),producer_sha256=sha(Path(__file__)),records=records,maximum_linear_impulse_error_Ns=max(r['linear_impulse_error_Ns'] for r in records),maximum_COM_angular_impulse_defect_Nms=max(r['COM_angular_impulse_defect_Nms'] for r in records),maximum_free_relative_angular_drift=worst if free else None,maximum_initial_geometric_inertia_error_kg_m2=max(r['initial_geometric_inertia_error_kg_m2'] for r in records))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
