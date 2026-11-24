"""Source-resolved actual finite hardware impulses; not a causal bracing proof."""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 assert json.loads((src/'summary.json').read_text())['status']=='PASS_READONLY_FINITE_HOLD_OBSERVER'
 dt=float(ET.parse(src/'scene.scn').getroot().get('dt'));pairs={}
 for r in csv.DictReader((src/'response_rows.csv').open()):
  m=[re.match(r'/guides(\d+)/cable(\d+)/(eyelet\d+|support\d+)/',r[k]) for k in ('model0','model1')]
  if all(m) and m[0][1]!=m[1][1] and float(r['lambda_Ns'])!=0:pairs[float(r['time_s']),int(r['row_id'])]=r
 aggregate={};rowforces={};sources={};counts=0
 for i in range(3):
  for r in csv.DictReader((src/f'direct{i}.csv').open()):
   t=float(r['time_s']);key=t,int(r['row_id'])
   if key not in pairs:continue
   J=np.fromstring(r['J'],sep=' ');imp=J*float(r['lambda_Ns']);owner=int(r['column_id']);qfree=np.fromstring(r['free_q'],sep=' ');assert len(imp)==6
   aggregate.setdefault((t,i,owner),np.zeros(6))[:] += imp
   rowforces.setdefault(key,[]).append(dict(finger=i,owner=owner,impulse=imp,centre=qfree[:3]))
   pair=' | '.join(sorted([pairs[key]['model0'],pairs[key]['model1']]))
   sources[pair]=sources.get(pair,0)+1;counts+=1
 action=[];globalmom=[]
 for key,rr in rowforces.items():
  assert len(rr)==2 and rr[0]['finger']!=rr[1]['finger'],'missing actual pair side'
  action.append(np.linalg.norm(sum((x['impulse'][:3] for x in rr),np.zeros(3))))
  globalmom.append(np.linalg.norm(sum((x['impulse'][3:]+np.cross(x['centre'],x['impulse'][:3]) for x in rr),np.zeros(3))))
 records=[]
 for (t,i,o),v in sorted(aggregate.items()):records.append(dict(time_s=t,finger=i,owner=o,force_N=(v[:3]/dt).tolist(),moment_at_native_reference_Nm=(v[3:]/dt).tolist()))
 per=[]
 for i in range(3):
  hold=[r for r in records if r['finger']==i and 1.6-1e-12<=r['time_s']<=2+1e-12]
  # Include zero-contact outputs in window means, not just active times.
  n=sum(1 for r in csv.DictReader((src/'object.csv').open()) if 1.6-1e-12<=float(r['time_s'])<=2+1e-12)
  per.append(dict(finger=i,hold_samples=n,mean_internal_hardware_force_N=(sum((np.array(r['force_N']) for r in hold),np.zeros(3))/n).tolist(),maximum_per_body_contact_force_N=max([float(np.linalg.norm(r['force_N'])) for r in hold],default=0),maximum_per_body_contact_moment_Nm=max([float(np.linalg.norm(r['moment_at_native_reference_Nm'])) for r in hold],default=0)))
 (out/'wrenches.json').write_text(json.dumps(records));d=dict(status='ACTUAL_INTERNAL_HARDWARE_WRENCH_INVENTORY_NOT_UNBRACED_PASS',case=a.case,source_resolved_body_rows=counts,active_constraint_rows=len(pairs),maximum_pair_linear_impulse_imbalance_Ns=max(action,default=None),maximum_pair_origin_angular_impulse_sum_Nms=max(globalmom,default=None),hold=per,source_pairs=sources,scope='Actual parent J^T lambda/dt, summed by body and timestep. Forces can brace fingers although sum across fingers cancels. Moments at Native free/reference centre; parent projection/other loads not whole attachment reaction. Nonzero pair moment may reflect distinct contact points/linearization. No work/energy closure or causal support-removal proof.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn','summary.json','response_rows.csv','object.csv']+[f'direct{i}.csv' for i in range(3)]});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
