"""Actual Native common-axis mechanism state/row assessment, reusable without reruns."""
import csv,json,re,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
from winch_transfer_assess import unique_row,read

def assess(root,out,steps):
 dt=float(root.get('dt'));tet=np.array(json.loads((BASE/'results/parallel_contact1894/mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));qualities=[]
 for i in range(3):
  rows=read(out/f'skin{i}.csv');assert len(rows)==steps;q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);d0=det(q0);qualities.append(min(float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows))
 objects=read(out/'object.csv');assert len(objects)==steps;q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in objects]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in objects]);forces=[];cableforces=[]
 for i in range(3):
  for j in range(2):
   rows=[r for r in read(out/f'drive_{i}_{j}_phases.csv') if r['phase']=='accepted_end'];assert len(rows)==steps;actual=[];output=[]
   for r in rows:
    lam=np.fromstring(r['lambda_Ns'],sep=' ');actual.append(float(lam[unique_row(r['J'],0)]/dt));output.append(float(lam[unique_row(r['J'],1)]/dt))
   forces.extend(actual);cableforces.append(dict(finger=i,tendon=j,maximum_input_N=max(actual),maximum_output_N=max(output)))
 groups={k:np.zeros((steps,6)) for k in ('skin','rail','guide','support','winch','unknown')};time_index={float(r['time_s']):k for k,r in enumerate(objects)};pairs={};skin_fingers=set();internal=0;rootcontact=0;guide_times=[]
 for r in csv.DictReader((out/'response_rows.csv').open()):
  models=[r['model0'],r['model1']];lam=float(r['lambda_Ns']);index=time_index[float(r['time_s'])];imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
  if any(n.startswith('/object/') for n in models):
   other=next(n for n in models if not n.startswith('/object/'));group='skin' if '/skinCollision/'in other else 'rail' if '/railCollision/'in other else 'guide' if other.startswith('/guides') else 'support' if other.startswith('/floor/') else 'winch' if other.startswith('/drive_') else 'unknown';groups[group][index]+=imp
   if group=='skin' and lam!=0:skin_fingers.add(int(re.search(r'/finger(\d+)',other)[1]))
  if lam!=0:
   key=tuple(models);pairs[key]=pairs.get(key,0)+1
   if all(n.startswith('/guides') for n in models):internal+=1;guide_times.append(float(r['time_s']))
   if any(n.startswith('/drive_') for n in models):rootcontact+=1
 total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in objects]);part_error=float(abs(total-sum(groups.values())).max());metrics=dict(minimum_saved_volume_ratios=qualities,actual_skin_contact_fingers=sorted(skin_fingers),nonzero_guide_guide_rows=internal,guide_guide_first_time_s=min(guide_times,default=None),guide_guide_last_time_s=max(guide_times,default=None),nonzero_new_root_contact_rows=rootcontact,contact_pairs=[dict(pair=list(k),nonzero_rows=v) for k,v in pairs.items()],actual_tendon_forces=cableforces,object_final_position_m=q[-1,:3].tolist(),object_final_speed_mm_s=float(np.linalg.norm(v[-1,:3])*1000),object_partition_error_Ns=part_error,mean_object_force_groups_N={k:(f[:,:3]/dt).mean(0).tolist() for k,f in groups.items()});valid=min(qualities)>0 and max(forces)<=1.5+1e-12 and min(forces)>=-1e-12 and part_error<=1e-12 and np.isfinite(q).all() and np.isfinite(v).all();unbraced=valid and internal==0 and rootcontact==0 and skin_fingers=={0,1,2}
 return metrics,bool(valid),bool(unbraced)
