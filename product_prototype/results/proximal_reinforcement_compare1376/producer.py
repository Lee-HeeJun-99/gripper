"""Matched-time accepted-response comparison,not an equal-volume stiffness test."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/proximal_reinforcement_rotation1373/summary.json';rot=json.loads(src.read_text())['records'];records=[]
 for i in range(3):
  r=[r for r in rot if r['finger']==i and not r['reference']];old=[x for x in r if x['case']=='b3_railback_grasp1001298'];new=[x for x in r if x['case']=='proximal_reinforcement_mid1370']
  for b,c in zip(old,new):
   assert b['actual_time_s']==c['actual_time_s'];records.append(dict(finger=i,time_s=b['actual_time_s'],baseline_tip_deg=b['tip_segment_angle_deg'],candidate_tip_deg=c['tip_segment_angle_deg'],candidate_minus_baseline_tip_deg=c['tip_segment_angle_deg']-b['tip_segment_angle_deg'],candidate_minus_baseline_proximal_turn_deg=c['proximal_signed_turn_deg']-b['proximal_signed_turn_deg']))
 endpoint=[r for r in records if r['time_s']>1];d=dict(status='ACTUAL_THREE_FINGER_COMPARISON_ONLY',records=records,all_three_endpoint_tip_angles_worse=all(r['candidate_minus_baseline_tip_deg']<0 for r in endpoint),all_three_endpoint_tip_angles_better=all(r['candidate_minus_baseline_tip_deg']>0 for r in endpoint),scope='Same original geometry/material/control,added85.354939mg/finger and finite backing. Actual coupled transient;not equal-volume or static stiffness comparison. No global statement that all reinforcements fail. No full Holding verdict.',source_sha256=sha(Path(__file__)),input_sha256=sha(src),physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
