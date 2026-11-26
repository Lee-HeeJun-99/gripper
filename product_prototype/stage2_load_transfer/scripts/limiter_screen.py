"""Manufacturer-data interface screen; no invented torque calibration or CAD."""
import argparse,json
from pathlib import Path
from load_requirements import ROOT,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/motor'/a.tag;out.mkdir(parents=True,exist_ok=False)
    rows=[
      dict(candidate='HPI friction family',published_range_Nm=[.01*.112984829,40*.112984829],published_unit='in-lb',
           envelope_mm=None,bores_mm=None,low_torque_accuracy=None,status='DRAWING_AND_CALIBRATION_REQUIRED',
           source='https://highprecisioninc.com/torque-limiters/'),
      dict(candidate='Huco401.25',outer_diameter_mm=26,minimum_bore_mm=6,current_input_mm=5,current_output_mm=4.4,
           bore_drop_in=False,status='NOT_A_DROP_IN',low_torque_accuracy=None,
           source='https://www.huco.com/shop/couplings/miniature-friction-clutches/401-25'),
      dict(candidate='Dynatect EAS12 adjustable',outer_diameter_mm=19.05,length_mm=31.75,
           current_coupling_length_mm=19.5,extra_length_mm=31.75-19.5,published_capacity_Nm=.96,
           minimum_calibrated_setting_Nm=None,status='NOT_A_DROP_IN_AND_LOW_SETTING_UNVERIFIED',
           source='https://dynatect.com/product/slip-ease-slip-clutches/')]
    result=dict(status='NO_VERIFIED_DROP_IN_LIMITER',scope='PRIMARY MANUFACTURER DATA / INTERFACE SCREEN ONLY',rows=rows,
        operating_torque_lower_required_Nm=None,safe_torque_upper_bound_Nm=None,
        required_next='Derive protected load window from real structure/grasp needs; obtain actual drawing/accuracy or design independently qualified force-cap mechanism; no purchase/contact made',
        source_SHA256=sha(Path(__file__)),command='python scripts/limiter_screen.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
