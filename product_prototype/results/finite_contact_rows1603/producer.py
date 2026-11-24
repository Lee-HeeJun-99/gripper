"""Actual Native Coulomb multiplier and sphere-normal torque inventory only."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def audit(case):
 src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));cfg=json.loads((src/'config.json').read_text());mu=cfg['simulation']['friction'];blocks={};normal_torque=0.;groups=0;negative=0;excess=0.;records=[]
 for r in csv.DictReader((src/'response_rows.csv').open()):
  t=float(r['time_s']);paths=(r['model0'],r['model1'])
  if not 1.6-1e-12<=t<=2+1e-12 or not any('/object/'in s for s in paths) or not any('/skinCollision/'in s for s in paths):continue
  offset=int(r['row_id'])-int(r['first_row']);key=(t,r['constraint_path'],int(r['first_row']),offset//3);component=offset%3;g=blocks.setdefault(key,{});assert component not in g;g[component]=(float(r['lambda_Ns']),np.fromstring(r['object_impulse_Ns_Nms'],sep=' '))
 for key,g in blocks.items():
  assert set(g)=={0,1,2};lam=np.array([g[k][0] for k in range(3)]);negative+=int(lam[0]<0);defect=max(0.,float(np.linalg.norm(lam[1:])-mu*lam[0]));excess=max(excess,defect);normal_torque=max(normal_torque,float(np.linalg.norm(g[0][1][3:]))/dt);groups+=1
  if lam[0]>0:records.append(dict(time_s=key[0],normal_force_N=float(lam[0]/dt),tangential_force_N=float(np.linalg.norm(lam[1:])/dt),cone_excess_Ns=defect))
 return dict(case=case,complete_hold_skin_contact_groups=groups,active_groups=len(records),negative_normal_multipliers=negative,maximum_Coulomb_cone_excess_Ns=excess,maximum_normal_row_object_torque_Nm=normal_torque,friction_assumed=mu,input_hashes={f:sha(src/f) for f in ('scene.scn','response_rows.csv','config.json')},scope='Actual complete3row multipliers. Sphere normal torque should vanish for radial contact. This is NOT full complementarity/W-matrix residual,contactwork,stability or time/mesh qualification. Tangential object power alone cannot be called frictional dissipation.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[audit(x) for x in ('dispatch_finite_holding1586','chamfer_eyelet_holding1594')];d=dict(status='ACTUAL_HOLD_CONTACT_ROW_INVENTORY_ONLY',records=records,source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
