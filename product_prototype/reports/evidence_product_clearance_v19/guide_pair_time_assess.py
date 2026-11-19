"""All-pair common-output Native free-guide coupon sensitivity;no error floor."""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);names=['b3_guide_pair483','b3_guide_pair_half496','b3_guide_pair_quarter497'];records=[]
 for alarm in ('1','5'):
  for body in (0,1):
   data=[list(csv.DictReader((BASE/'results'/name/alarm/f'guide{body}.csv').open())) for name in names]
   for i,j in itertools.combinations(range(3),2):
    ratio=2**(j-i);initial=np.fromstring(__import__('xml.etree.ElementTree',fromlist=['parse']).parse(BASE/'results'/names[i]/alarm/'scene.scn').getroot().find(f"./Node[@name='guide{body}']/MechanicalObject").get('position'),sep=' ')[:3]
    for k,x in enumerate(data[i]):
     y=data[j][(k+1)*ratio-1];clock=abs(float(x['time_s'])-float(y['time_s']));assert clock<=1e-12
     for key,cols,label in [('rigid_q',slice(0,3),'translation_from_initial_m'),('rigid_v',slice(0,3),'linear_velocity_m_s'),('rigid_v',slice(3,6),'angular_velocity_rad_s')]:
      u=np.fromstring(x[key],sep=' ')[cols];v=np.fromstring(y[key],sep=' ')[cols]
      if key=='rigid_q':u=u-initial;v=v-initial
      absolute=float(np.linalg.norm(u-v));den=max(float(np.linalg.norm(u)),float(np.linalg.norm(v)));relative=absolute/den if den else 0
      records.append(dict(alarm_mm=int(alarm),body=body,pair=f'{i}_{j}',time_s=float(x['time_s']),quantity=label,absolute_error=absolute,relative_error=relative,status='PASS' if relative<=.001 else 'FAIL'))
 with (out/'errors.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 result=dict(scope='Independent two FREE guide collision coupon only;NOT attached B3/time/energy/grasp certification',gate=.001,absolute_floor=None,status='FAIL' if any(r['status']=='FAIL' for r in records) else 'PASS_SELECTED_COUPON_OUTPUTS_ONLY',worst_by_alarm={alarm:max([r for r in records if r['alarm_mm']==int(alarm)],key=lambda r:r['relative_error']) for alarm in ('1','5')},source_sha256=sha(Path(__file__)),source_summaries={name:sha(BASE/'results'/name/'summary.json') for name in names})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
