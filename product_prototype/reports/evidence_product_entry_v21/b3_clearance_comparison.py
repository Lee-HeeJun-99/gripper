"""Read-only B3 one-factor/detection comparison;keeps failed physical gates."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def differences(x,y,prefix=''):
 if isinstance(x,dict) and isinstance(y,dict):return sum((differences(x.get(k),y.get(k),prefix+'.'+k if prefix else k) for k in sorted(set(x)|set(y))),[])
 return [] if x==y else [dict(path=prefix,old=x,new=y)]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);baseline=BASE/'results/force_release_clear_support375';sector=BASE/'results/b3_sector_margin1_474';window=BASE/'results/b3_alarm_window485';meta=json.loads((window/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('full window run required;partial output not accepted')
 diff=differences(json.loads((baseline/'config.json').read_text()),json.loads((sector/'config.json').read_text()));prefix=[]
 for name,fields in [(f'finger{i}.csv',('q_m','v_m_s','cable0_force_raw','cable1_force_raw')) for i in range(3)]+[(f'guide_frames{i}.csv',('rigid_q','rigid_v')) for i in range(3)]+[('object.csv',('rigid_q','rigid_v'))]:
  x=list(csv.DictReader((baseline/name).open()));y=list(csv.DictReader((window/name).open()));error={k:0. for k in fields};count=0
  for u,v in zip(x,y):
   if float(v['time_s'])>=2.386:break
   if u['time_s']!=v['time_s']:raise ValueError('clock mismatch')
   count+=1
   for k in fields:error[k]=max(error[k],float(np.max(abs(np.fromstring(u[k],sep=' ')-np.fromstring(v[k],sep=' ')))))
  prefix.append(dict(file=name,frames=count,error=error,status='PASS' if all(e<=1e-12 for e in error.values()) else 'FAIL'))
 applied=list(csv.DictReader((window/'alarm_applied.csv').open()));actual=list(csv.DictReader((window/'object.csv').open()));alarm_ok=len(applied)==len(actual)==1200 and all(float(x['applied_end_clock_s'])==float(y['time_s']) and float(x['actual_contact_distance'])==.0002 and float(x['actual_alarm_m'])==(.005 if 2.386<=float(x['applied_end_clock_s'])<=2.396 else .001) for x,y in zip(applied,actual))
 result=dict(status='DIAGNOSTIC_COMPARISON_NOT_PRODUCT_PASS',producer_sha256=sha(Path(__file__)),sector_config_differences=diff,window_geometry_config_bytes_identical=(window/'config.json').read_bytes()==(baseline/'config.json').read_bytes(),window_alarm_journal_exact=alarm_ok,window_wide_frames=sum(float(r['actual_alarm_m'])==.005 for r in applied),prefix_state_api=prefix,all_prefix_states_pass=all(r['status']=='PASS' for r in prefix),unchanged_gates='Full mesh/time/energy,solid supports,swept CCD,100g,Lift and fabrication remain unqualified. Frozen-motion screen is not a dynamic result.',input_hashes={str(p.relative_to(BASE)):sha(p) for p in (baseline/'summary.json',sector/'summary.json',window/'summary.json',window/'alarm_applied.csv')})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
