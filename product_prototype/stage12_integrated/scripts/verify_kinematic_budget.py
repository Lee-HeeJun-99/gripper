"""Independent saved-state check using SciPy CubicHermiteSpline, no producer import."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
out=ROOT/'validation/finger'/sys.argv[1]
source=ROOT/'validation/finger/flexible_distributed2/summary.json'
original=json.loads(source.read_text());result=json.loads((out/'summary.json').read_text())
inputs=json.loads((out/'inputs.json').read_text())
assert all(hashlib.sha256((REPO/r['path']).read_bytes()).hexdigest()==r['SHA256'] for r in inputs['inputs'])
checks=[]
for row in result['rows']:
    r=next(r for r in original['rows'] if r['n']==row['n'] and r['force_N']==row['force_N'])
    L=.088 if row['body']=='rail' else .0862
    q=np.array(r[row['body']+'_q']);knots=np.linspace(0,L,row['n']+1)
    derivative=CubicHermiteSpline(knots,q[::2],q[1::2]).derivative()
    def density(s):
        v=float(derivative(s));return 2*np.sin(np.arctan(v)/2)**2
    shortening=sum(quad(density,a,b,epsabs=1e-20)[0] for a,b in zip(knots,knots[1:]))
    error=abs(shortening-row['inextensible_tip_x_shortening_m'])
    checks.append(dict(n=r['n'],force_N=r['force_N'],body=row['body'],shortening_m=shortening,error_m=error,passed=error<1e-16))
passed=all(r['passed'] for r in checks) and result['status']=='ANALYSIS_COMPLETE'
record=dict(status='PASS' if passed else 'FAIL',scope='Independent actual saved-state shortening and input-hash verification',checks=checks,all_input_hashes_match=True,producer_copy_matches=hashlib.sha256((out/'producer.py').read_bytes()).hexdigest()==hashlib.sha256((ROOT/'scripts/finite_kinematic_budget.py').read_bytes()).hexdigest())
assert record['producer_copy_matches']
(out/'independent_verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));raise SystemExit(0 if passed else 2)
