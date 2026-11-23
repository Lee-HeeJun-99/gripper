"""Conditional CAD tolerance/endplay budget,not measured manufacturing capability."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def stack(shim,span_error=0.,wheel_error=0.,shim_error=0.,groove_error=0.,wire_error=0.):
 if min(shim,span_error,wheel_error,shim_error,groove_error,wire_error)<0 or shim_error>shim:raise ValueError('invalid explicit stack bounds')
 minimum=2.8-span_error-(1.8+wheel_error)-2*(shim+shim_error);maximum=2.8+span_error-(1.8-wheel_error)-2*(shim-shim_error);wire_side=(.8-groove_error-(.5+wire_error))/2;wander=maximum/2
 return dict(shim_thickness_mm_each=shim,minimum_total_axial_clearance_mm=minimum,maximum_total_axial_clearance_mm=maximum,maximum_centered_wheel_wander_mm=wander,available_centered_wire_side_gap_mm=wire_side,alignment_margin_mm=wire_side-wander,strict_nonbinding_and_alignment=minimum>0 and wire_side-wander>0)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results/product_bridge_service768/summary.json';records=[dict(case='current_nominal_no_shims',**stack(0.)),dict(case='proposed_0p4_shims_nominal',**stack(.4)),dict(case='ASSUMED_tolerance_example_NOT_process_capability',**stack(.4,.05,.05,.02))];radial=[dict(assumed_symmetric_diameter_errors_mm=t,assumed_coaxial_offset_mm=t,minimum_radial_margin_mm=(1.2-t-(1.+t))/2-t) for t in (0.,.01,.05,.1)]
 result=dict(status='CONDITIONAL_STACK_BUDGET_NOT_TOLERANCE_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),service_evidence_sha256=sha(source),records=records,radial_scenarios=radial,actual_manufacturing_tolerances_mm=None,measured_endplay_mm=None,scope='Nominal existing fork inner span2.8,wheelwidth1.8,groove0.8,wireD0.5,pinD1,bore1.2mm. Geometric centered-wire/wheel assumptions only. Axisfreeplay can invalidate nominal route alignment. Example symmetric error bounds are ASSUMPTIONS,not shop capability,ISO fit or supplier specs. Neither positive nominalmargin nor service-screen clearance certifies friction,wear or dynamic alignment.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
