"""Frozen accepted-geometry normal-ray diagnostic,not a new deformation model.

Compare rest clearance budget with thickness needed along ACTUAL deformed pad
directions. Changing a profile will change mechanics;these rays do not predict it.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def ray(p,n,c,R):
 b=float(np.dot(p-c,n));disc=b*b-float(np.dot(p-c,p-c))+R*R
 if disc<0:return None
 roots=[v for v in (-b-np.sqrt(disc),-b+np.sqrt(disc)) if v>=0]
 return min(roots) if roots else None
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_contact_layer_union_withdraw1352';g=json.loads((src/'pad_mesh.json').read_text());local=np.array(g['local_positions_mm'])[::2];q0=np.array(g['world_reference_m'][0]);center0=np.array([0.,0.,-.065]);budget=[]
 for b,t in zip(q0[::2],q0[1::2]):n=(t-b)/np.linalg.norm(t-b);budget.append(ray(b,n,center0,.0302))
 pad=read(src/'contact_layer0.csv');body=read(src/'object.csv');records=[]
 for wanted in (.6,1.2):
  k=next(k for k,r in enumerate(body) if abs(float(r['time_s'])-wanted)<1e-12);assert pad[k]['time_s']==body[k]['time_s'];q=np.fromstring(pad[k]['q'],sep=' ').reshape(-1,3);center=np.fromstring(body[k]['rigid_q'],sep=' ')[:3]
  for j,(bottom,top) in enumerate(zip(q[::2],q[1::2])):
   length=float(np.linalg.norm(top-bottom));n=(top-bottom)/length;needed=ray(bottom,n,center,.03);required_rest=None if needed is None else needed*.0005/length;point=None if needed is None else bottom+n*needed
   records.append(dict(actual_time_s=float(body[k]['time_s']),material_station_mm=float(local[j,0]),material_width_mm=float(local[j,1]),actual_top_gap_m=float(np.linalg.norm(top-center)-.03),actual_thickness_m=length,initial_normal_ray_budget_to_contact_margin_m=budget[j],deformed_ray_first_sphere_intersection_m=needed,frozen_stretch_equivalent_rest_thickness_m=required_rest,frozen_profile_within_initial_budget=None if needed is None or budget[j] is None else bool(required_rest<=budget[j]),hypothetical_intersection_force_normal_z=None if point is None else float((center-point)[2]/.03)))
 with (out/'profile_rays.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 d=dict(status='FROZEN_GEOMETRY_PROFILE_DIAGNOSTIC_ONLY',records=records,scope='Actual width-node coordinates and actual object center;first positive sphere-ray intersection along observed pad thickness. Rest-equivalent scaling freezes measured kinematics. NOT contact,force capacity,a manufactured profile solution or global impossibility proof. NULL ray can miss sphere;no artificial floor.',material='assumedE1MPa,nu.3,rho1000;no measured material selection',physical_validation='NOT QUALIFIED',input_hashes={f:sha(src/f) for f in ('pad_mesh.json','contact_layer0.csv','object.csv')});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));valid=[r for r in records if r['frozen_profile_within_initial_budget'] is not None];print(json.dumps(dict(status=d['status'],rays=len(records),misses=sum(r['deformed_ray_first_sphere_intersection_m'] is None for r in records),outside_initial_budget=sum(not r['frozen_profile_within_initial_budget'] for r in valid))))
if __name__=='__main__':main()
