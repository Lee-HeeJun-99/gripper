"""RevAH finite shared-register interval contract, not total motor alignment.
Unknown pilot-to-shaft runout and elastic deflection are NOT assigned zero.
"""
import argparse,json,shutil,sys
from baseline_registry import ROOT,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from sourced_motor_stage1 import MOTOR_SPEC
def calculate(r):
    bore=r['common_bore_mm'];mp=r['motor_pilot_mm'];sp=r['spindle_pilot_mm']
    H=r['plate_thickness_mm'];S=r['spacer_length_mm'];L=r['spindle_boss_length_mm']
    gap=H[0]+S[0]-L[1]-MOTOR_SPEC['pilot_height_limits_mm'][1]
    engagement=[L[0]-S[1],L[1]-S[0]]
    float_bound=(bore[1]-mp[0]+bore[1]-sp[0])/2
    shaft_clearance=(5.29-MOTOR_SPEC['shaft_diameter_mm'][1])/2
    return dict(min_motor_pilot_diametral_clearance_mm=bore[0]-mp[1],min_spindle_pilot_diametral_clearance_mm=bore[0]-sp[1],minimum_pilot_tip_to_boss_axial_gap_mm=gap,pilot_engagement_mm=engagement,interface_center_float_bound_mm=float_bound,minimum_spindle_shaft_radial_clearance_mm=shaft_clearance,remaining_unallocated_coaxiality_deflection_budget_mm=shaft_clearance-float_bound)
def valid(x):return x['min_motor_pilot_diametral_clearance_mm']>0 and x['min_spindle_pilot_diametral_clearance_mm']>0 and x['minimum_pilot_tip_to_boss_axial_gap_mm']>0 and x['pilot_engagement_mm'][0]>0 and x['remaining_unallocated_coaxiality_deflection_budget_mm']>0
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/alignment'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());assert d['shared_register'];r=d['register_requirement'];x=calculate(r)
    # These are independent design-control failures, not fabricated measurements.
    wrong=dict(r,motor_pilot_mm=[22.1,22.2]);assert not valid(calculate(wrong))
    wrong=dict(r,spindle_boss_length_mm=[5.6,5.7]);assert not valid(calculate(wrong))
    result=dict(status='SHARED_REGISTER_INTERFACE_BOUNDS_PASS' if valid(x) else 'FAIL',scope='Nominal CAD and declared interface tolerance requirements only; total alignment/reaction NOT qualified',candidate=ref(src),producer=ref(out/'producer.py'),motor_drawing_model=ref(S1/'scripts/sourced_motor_stage1.py'),intervals=r,derived=x,
        actual_motor_shaft_engagement_mm=[4.2,6.2],drawing_nominal_engagement_mm=5.2,warning='Older candidate field motor_shaft_available_nominal_engagement_mm=6.2 describes maximum-length CAD envelope, NOT the drawing nominal or minimum. This supplier-range calculation supersedes that label.',
        additional_design_requirement=dict(spindle_shaft_bore_mm=[5.29,5.31],qualification='Proposed machining interval, not measured process capability'),
        unresolved=['Actual manufacturer pilot-to-shaft runout','Spindle journal-to-pilot machining coaxiality and loaded deformation','Front collet has only4.2mm minimum shaft engagement; clamp bolt is ahead of shaft tip, actual closure/torque/axial holding needs validation','Actual motor axial bearing limit and friction/spring calibration','Assembly/inspection process capability and qualified materials'],
        controls=['oversized motor pilot rejected','long boss colliding with maximum motor pilot rejected'],whole_motor_alignment_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
