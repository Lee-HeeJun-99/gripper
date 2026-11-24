"""Next-step actuation contract and actual cross-finger rows, not a full Hold gate."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from mechanism_contact_inventory import identify

def read(folder,name):return list(csv.DictReader((folder/name).open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;old=BASE/'results/capillary_hold1700';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 controls=[];first=[];err=0.;pair_count=0;pair_first=None
 for i in range(3):
  c=read(src,f'clutch{i}.csv');f=read(src,f'finger{i}.csv');baseline=read(old,f'finger{i}.csv');trigger=next((k for k,r in enumerate(c) if r['latched']=='1'),None);first.append(None if trigger is None else float(c[trigger]['time_s']))
  for k in range(1,len(f)):
   # Existing sequence runs at BEGIN; clutch latches at previous END.
   assert float(f[k]['time_s'])==float(baseline[k]['time_s'])
   expected=float(c[k-1]['next_maximumForce_N'])*float(baseline[k]['command_N'])/1.5
   err=max(err,abs(float(f[k]['command_N'])-expected))
  controls.append(dict(finger=i,trigger_time_s=first[-1],first_zero_force_time_s=next((float(r['time_s']) for k,r in enumerate(f) if k>0 and float(c[k-1]['next_maximumForce_N'])==0 and float(r['command_N'])==0),None),minimum_sector_gap_mm=min(float(r['accepted_sector_gap_m']) for r in c)*1000))
 for r in csv.DictReader((src/'response_rows.csv').open()):
  ids=[identify(r[k]) for k in ('model0','model1')]
  if all(x is not None for x in ids) and ids[0][0]!=ids[1][0] and float(r['lambda_Ns'])!=0:
   pair_count+=1;pair_first=float(r['time_s']) if pair_first is None else pair_first
 times=[x for x in first if x is not None];cut=min(times) if times else float('inf');purity=0.
 for name,fields in [('object.csv',('rigid_q','rigid_v'))]+[(f'finger{i}.csv',('q_m','v_m_s')) for i in range(3)]:
  for x,y in zip(read(src,name),read(old,name)):
   if float(x['time_s'])>cut+1e-12:break
   assert float(x['time_s'])==float(y['time_s'])
   for k in fields:purity=max(purity,float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()))
 obj=read(src,'object.csv');q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in obj]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in obj]);t=np.array([float(r['time_s']) for r in obj]);late=t>=1.;assert err<=1e-12 and purity==0
 d=dict(status='PASS_ACTUATION_CONTRACT_ONLY_PREFIX_REJECTED_FOR_EXPANSION',case=a.case,controls=controls,next_step_force_error_N=err,pre_intervention_qv_difference=purity,cross_finger_nonzero_rows=pair_count,first_cross_finger_response_s=pair_first,last_object_position_m=q[-1,:3].tolist(),last_object_velocity_mm_s=(v[-1,:3]*1000).tolist(),max_post_1s_speed_mm_s=float(np.linalg.norm(v[late,:3],axis=1).max()*1000),last_horizontal_displacement_mm=float(np.linalg.norm(q[-1,:2]-q[0,:2])*1000),hold_window='NOT RUN: prefix ends1.2s, not a formal1.6–2.0s verdict',scope='One latching release at original half-buffer. No threshold scan. Establishes actual command timing, not an invariant barrier or proof that every feedback/physical clutch fails. Prefix loses symmetric approach; no full-Hold/Lift expansion without a new mechanism.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','summary.json','clutch_assessment.json','object.csv','response_rows.csv')})
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
