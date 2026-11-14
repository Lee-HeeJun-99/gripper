"""Verify actual small-load convergence of the new 3D constitutive model to planar."""
from pathlib import Path
import json
from research_trial import run
from verification_common import ROOT,write_json

def main():
    out=ROOT/'results/next_phase/small_load_limit';out.mkdir(parents=True,exist_ok=False)
    legacy=run(out/'planar',length=30,k=1,load=1e-5,duration=3)
    finite=run(out/'finite',length=30,k=1,load=1e-5,duration=3,finite=True)
    old=json.loads((ROOT/'reports/revalidation_evidence/metrics/k1.json').read_text())
    new=json.loads((ROOT/'results/next_phase/sofa/finite_L30/metrics.json').read_text())
    high_error=abs(new['tip_deflection_mm']/old['tip_deflection_mm']-1)
    low_error=abs(finite['tip_deflection_mm']/legacy['tip_deflection_mm']-1)
    write_json(out/'summary.json',dict(status='PASS' if legacy['status']==finite['status']=='PASS' and low_error<high_error and low_error<.001 else 'FAIL',
        high_load=1e-4,low_load=1e-5,high_relative_difference=high_error,low_relative_difference=low_error,
        note='Comparing actual SOFA equilibria; new energy differs nonlinearly, no equality claim at finite strain'))
    print(high_error,low_error)

if __name__=='__main__':main()
