"""Matched early-time actuation-topology assessment,not Holding certification."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from b3_contact_direction_history import assess
from b3_skin_centerline import metrics

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in ('b3_railback_grasp1001298','b3_proximal_terminal1326'):
  src=BASE/'results'/name;direction=assess(name,out);local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);stations=np.unique(local[:,0]);masks=[(local[:,0]==s)&(local[:,2]==local[:,2].max()) for s in stations];items=[]
  for i in range(3):
   rows=list(csv.DictReader((src/f'finger{i}.csv').open()));r=next(r for r in rows if abs(float(r['time_s'])-.6)<1e-12);q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);items.append(dict(finger=i,**metrics(np.array([q[m].mean(axis=0) for m in masks]))))
  normals=list(csv.DictReader((out/(name+'.csv')).open()));end=next(r for r in normals if abs(float(r['time_s'])-.6)<1e-12)
  records.append(dict(case=name,actual_time_s=float(end['time_s']),active_skin_normals=int(end['active_normals']),skin_Fz_N=float(end['measured_skin_Fz_N']),min_nz=end['min_nz'],max_nz=end['max_nz'],centerline=items,input_sha256=sha(src/'finger0.csv')))
 result=dict(status='MATCHED_EARLY_TOPOLOGY_DIAGNOSTIC',records=records,scope='0.6s actual accepted state. Different physical actuation topology;not time convergence,distributed Wrapping,Holding or fabricated anchor qualification.',holding='NOT MEASURED',physical_validation='NOT QUALIFIED')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
