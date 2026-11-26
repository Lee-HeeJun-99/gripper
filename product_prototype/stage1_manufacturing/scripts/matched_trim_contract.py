"""Interval design closure plus BLANK physical inspection sheet; no measurements."""
import argparse,csv,json,math,shutil
from manufacturing_packet import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 body=[2.99,3.01];recess=[.59,.61];nut=[1.35,1.60];exposure=[.50,.65]
 grip=[2*body[0]-2*recess[1],2*body[1]-2*recess[0]]
 length=[grip[0]+nut[0]+exposure[0],grip[1]+nut[1]+exposure[1]]
 upper_seat=[body[0]-recess[1],body[1]-recess[0]];positive_tip=upper_seat[1]+nut[1]+exposure[1];negative_head=-(body[1]-recess[0])-2
 insert_margin=4.08-4;stop_margin=3.82/math.cos(math.pi/6)-4.12
 checks=dict(stock8_trim_allowance_min_mm=8-length[1],bolt_positive_extra_mm=positive_tip-4.6,bolt_negative_extra_mm=-4.4-negative_head,nut_negative_extra_mm=2.4-upper_seat[0],nut_positive_extra_mm=upper_seat[1]+nut[1]-4,nut_AF_insertion_margin_mm=insert_margin,nut_30deg_stop_margin_mm=stop_margin)
 passed=checks['stock8_trim_allowance_min_mm']>0 and checks['bolt_positive_extra_mm']<=.10 and checks['bolt_negative_extra_mm']<=.03 and checks['nut_negative_extra_mm']<=.020000000001 and checks['nut_positive_extra_mm']<=.10 and insert_margin>0 and stop_margin>0
 result=dict(status='MATCHED_TRIM_DESIGN_CONTRACT_PASS' if passed else 'FAIL',body_half_thickness_mm=body,recess_mm=recess,nut_acceptance_thickness_mm=nut,nut_AF_acceptance_mm=[3.82,4.00],captive_pocket_AF_mm=[4.08,4.12],finished_exposed_tip_acceptance_mm=exposure,grip_interval_mm=grip,matched_underhead_length_design_interval_mm=length,checks=checks,method='Measure actual closed-half grip and actual selected nut; trim each stockM2x8 to L=grip+nut_height+0.55, rechamfer/deburr/gauge6g; final inspect exposed tip0.50..0.65 and full nut engagement. Match/label screw to receiver location. Do NOT blindly cut every screw to7mm.',scope='Analytic manufacturing acceptance/design closure only; all hardware readings remain blank/NOT MEASURED. Full stated convex stack-motion envelope separately required.',stage1_release=False)
 with (out/'ACTUAL_TRIM_INSPECTION_TEMPLATE.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['part_ID','actual_grip_mm','actual_nut_height_mm','target_underhead_length_mm','actual_finished_underhead_mm','actual_exposed_tip_mm','thread_gauge','operator','state']);w.writeheader()
  for i in range(3):
   for x in (39,47):
    for z in (-86.5,-74.5):w.writerow(dict(part_ID=f'F{i}_SWIVEL_BOLT_{x}_{z}',state='NOT MEASURED'))
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
