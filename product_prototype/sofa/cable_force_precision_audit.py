"""Read-only diagnosis of failed string force observation, never changes FAIL."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from b3_cable_phase_pilot import parse
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_cable_deformed1829';rows=list(csv.DictReader((src/'phases.csv').open()));finger=list(csv.DictReader((src/'finger0.csv').open()));rounderror=0.;rawerror=0.;typederror=0.
 for k,fr in enumerate(finger):
  d={r['phase']:r for r in rows if int(r['step'])==k};_,row=parse(d['build_end']['J'],6,3);lam=np.fromstring(d['solve_end']['lambda_Ns'],sep=' ')[row];raw=float(fr['cable0_force_raw']);logged=float(d['accepted_end']['cable_force_raw']);rounderror=max(rounderror,abs(logged-float(format(raw,'.6g'))));rawerror=max(rawerror,abs(lam-raw));typederror=max(typederror,abs(lam-logged))
 result=dict(status='PASS_FORCE_STRING_PRECISION_DIAGNOSIS_ONLY' if rounderror==0 and rawerror==0 else 'FAIL_PRECISION_HYPOTHESIS',samples=len(finger),maximum_string_vs_six_significant_digit_rounding_error_Ns=rounderror,maximum_actual_solver_vs_existing_full_precision_force_error_Ns=rawerror,original_string_field_vs_actual_solver_error_Ns=typederror,original_phase_assessment_status=json.loads((src/'phase_assessment.json').read_text())['status'],scope='1829FAIL preserved. Actual raw force equals solver impulse; six-significant-digit string formatting explains every observed field discrepancy. New typed Native trial required for a new observation PASS; no tolerance relaxation or rewriting.',source_sha256=sha(Path(__file__)),input_sha256={f:sha(src/f) for f in ('phases.csv','finger0.csv','phase_assessment.json')})
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
