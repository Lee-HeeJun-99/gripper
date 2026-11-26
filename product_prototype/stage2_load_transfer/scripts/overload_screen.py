"""Motor holding-torque JAM reference, not measured stall or safe upper bound.
Expose unmitigated overload; nominal reference torque must not masquerade as
the actual protected maximum load. No existing FAIL is reclassified.
"""
import argparse,json,math
from pathlib import Path
from load_requirements import ROOT,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/worst_case'/a.tag;out.mkdir(parents=True,exist_ok=False)
    tau=.45;r=.011165;T=tau/r
    R=2*T # necessary triangle upper bound, equal input/output tension scenario
    moment=R*.00275;stress=32*moment/(math.pi*.00155**3)
    pinforce=tau/(2*.00405);pin_shear=pinforce/(math.pi*.00149**2/4)
    result=dict(status='OVERLOAD_PROTECTION_NOT_QUALIFIED',scope='STATIC JAM/OBSTRUCTION HAZARD REFERENCE; NOT MEASURED CAPACITY OR MOTOR SAFETY MAXIMUM',
        motor_nominal_holding_torque_Nm=tau,minimum_seated_radius_m=r,ideal_reference_tension_N=T,
        idler_radial_triangle_upper_reference_N=R,idler_runout_bending_reference_Pa=stress,
        required_yield_for_factor2_without_notch_Pa=2*stress,
        shaft_pin_nominal_shear_reference_Pa=pin_shear,
        nominal_303_yield_typical_Pa=241e6,
        warning='Typical yield is NOT certified allowable; notch/preload/fatigue unresolved. Holding torque is NOT a rated upper torque bound. Frictional slip is NOT a qualified safety torque limiter.',
        required_correction='A validated independent torque/tension limiter or certified drive force cap is required before adopting a low-N load envelope; a stroke stop alone cannot protect an earlier jam.',
        source_SHA256=sha(Path(__file__)),material_evidence_SHA256=sha(ROOT/'models/materials/evidence.json'),
        motor_source='https://files.omc-stepperonline.com/17HS15-1504S1_Full_Datasheet.pdf',
        command='python scripts/overload_screen.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
