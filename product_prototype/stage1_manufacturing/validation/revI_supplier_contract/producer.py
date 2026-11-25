"""Actual nominal axial stops and independent worst-case fit/load references."""
import argparse,json,shutil,math
from pathlib import Path
from incremental_stage1 import ROOT,read,common,translate,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 src=ROOT/'cad/exports'/a.case;index=json.loads((src/'summary.json').read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 parts={n:read(ROOT/v['path']) for n,v in index['parts'].items() if n.startswith('F0_')}
 stops=[]
 for label,shifts in [('L',[-.03,-.02,0,.01]),('R',[-.31,-.3,0,.3,.31])]:
  for dy in shifts:
   b=translate(parts['F0_BEARING_'+label],0,dy,0)
   stops.append(dict(bearing=label,shift_mm=dy,cap_intersection_mm3=common(b,parts['F0_CAP_'+label]),housing_intersection_mm3=common(b,parts['F0_PEDESTAL_'+label])))
 # Vendor P6 bounds from SKF table, conservatively not assuming a special
 # narrower width grade. Machining fits are explicit procurement limits.
 fits=dict(bearing_mean_bore_mm=[4.993,5.000],shaft_f6_mm=[4.982,4.990],journal_MEAN_diametral_clearance_mm=[.003,.018],bearing_mean_OD_mm=[15.993,16.000],housing_H6_mm=[16,16.011],housing_MEAN_diametral_clearance_mm=[0,.018],bearing_width_mm=[4.88,5],left_cavity_mm=[5.01,5.03],left_endplay_mm=[.01,.15],right_cavity_mm=[5.58,5.62],right_endplay_mm=[.58,.74],shaft_abutment_D_mm=8,SKF_da_range_mm=[7.4,8.3],housing_abutment_D_mm=13,SKF_Da_max_mm=13.6,abutment_fillet_max_mm=.2,SKF_fillet_max_mm=.3,fit_scope='Manufacturer P6 MEAN limits; single-plane variation/envelope/gauge inspection must additionally be met. Deliberately clamped slip journal for unpowered prototype, NOT a conventional rotating-load fit/creep/life approval.',correction='revI_fit prior numerical shaft range was wrongly labelled g6; superseded by actual manufacturer f6 -10/-18um table. Old result preserved, not silently overwritten.')
 gap=.3;required=5.05-4.982
 torque=dict(reference_tendon_N=1.5,winding_centre_radius_mm=8.25,reference_torque_Nmm=12.375,pin_radius_mm=.7475,double_shear_area_mm2=2*math.pi*.7475**2,nominal_reference_pin_force_N=12.375/4,approximate_reference_shear_MPa=(12.375/4)/(2*math.pi*.7475**2),allowable_MPa=None,capacity_pass=False,shaft_drum_positive_path='drum transverse hole -> captured pin -> shaft cross hole; M2 plugs retain pin ends, not transmit torque',coupler_bore_mm=5.05,minimum_shaft_mm=4.982,required_jaw_closure_mm=required,available_jaw_gap_mm=gap,jaw_gap_margin_mm=gap-required,actual_clamping_force_N=None)
 assert fits['journal_MEAN_diametral_clearance_mm'][0]>0 and fits['left_endplay_mm'][0]>0
 assert 7.4<=8<=8.3 and 13<=13.6 and .2<=.3
 assert next(s for s in stops if s['bearing']=='L' and s['shift_mm']==-.03)['cap_intersection_mm3']>0
 assert next(s for s in stops if s['bearing']=='L' and s['shift_mm']==.01)['housing_intersection_mm3']>0
 assert next(s for s in stops if s['bearing']=='R' and s['shift_mm']==-.31)['housing_intersection_mm3']>0
 assert next(s for s in stops if s['bearing']=='R' and s['shift_mm']==.31)['cap_intersection_mm3']>0
 result=dict(status='AXIAL_AND_POSITIVE_TORQUE_GEOMETRY_CONTRACT_PASS',axial_stops=stops,fit_limits=fits,reference_only_torque=torque,nominal_assembly_collisions=index['collisions'],scope='Design geometry and specified tolerance ranges only. No force, locknut cure, fit inspection, material allowable or powered hardware test.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');(out/'input_sha256.json').write_text(json.dumps({str(src/'summary.json'):sha(src/'summary.json')},indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
