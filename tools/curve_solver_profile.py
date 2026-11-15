import json
import numpy as np
from curve_common import ROOT,OUT,write_json
from curve_trial import run
from trial_validation import read_states
def main():
    r=run('scalar_equivalence_profile',profile=True,fixed_layout=True,tributary_mass=True,scalar_solver=True);old=ROOT/'results/autonomous_20261116_full_native_a01/grasp/equivalence_profile';a=read_states(old/'state.txt');b=read_states(OUT/'grasp/scalar_equivalence_profile/state.txt');errors={k:float(np.max(np.abs(np.array([v[k]for v in a])-np.array([v[k]for v in b]))))for k in('X','V','R')};oldr=json.loads((old/'metrics.json').read_text());passed=r['status']=='EXPERIMENTAL'and all(v<1e-11 for v in errors.values())
    write_json(OUT/'solver_profile.json',dict(status='PASS'if passed else'FAIL',maximum_absolute_state_differences=errors,scalar_wall_s=r['process']['runtime_s'],block_wall_s=oldr['process']['runtime_s'],scope='same nonsymmetric EigenSparseLU equations,different supported storage template,actual4s path;not full stability/convergence or a matched-isolated CPU benchmark'))
    print(passed,errors,r['process']['runtime_s'])
if __name__=='__main__':main()
