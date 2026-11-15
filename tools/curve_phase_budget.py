"""Refine runtime prediction using measured full-path and phase cost,not a larger cap."""
import json
import numpy as np
from curve_common import ROOT,OUT,write_json
from curve_trial import run
from trial_validation import read_states
def main():
    baseline=run('baseline18');generic=ROOT/'results/autonomous_20261116_curve_a01/grasp/n11';a=read_states(generic/'state.txt');b=read_states(OUT/'grasp/baseline18/state.txt')
    errors={key:float(np.max(np.abs(np.array([r[key]for r in a])-np.array([r[key]for r in b]))))for key in('X','V','R')}
    equivalent=errors['X']<1e-11 and errors['V']<1e-11 and errors['R']<1e-12
    write_json(OUT/'full_path_equivalence.json',dict(status='PASS'if equivalent else'FAIL',maximum_absolute_errors=errors,scope='actual full18s path,generic versus strict-FP native;not a new mesh certificate'))
    if not baseline.get('bounded_hold_pass')or not equivalent:return
    if (OUT/'grasp/quarterdt').exists():write_json(OUT/'phase_budget_decision.json',dict(status='NOT APPLICABLE',reason='one bounded quarter-step attempt already created;do not duplicate'));return
    p=json.loads((OUT/'grasp/profile_quarterdt/metrics.json').read_text());p0=json.loads((OUT/'grasp/profile_equivalence/metrics.json').read_text())
    if p['status']!='EXPERIMENTAL':raise RuntimeError('quarter profile failed')
    ratio=p['process']['runtime_s']/p0['process']['runtime_s'];estimate=ratio*baseline['process']['runtime_s'];eligible=estimate*1.1<=900
    write_json(OUT/'phase_budget_decision.json',dict(status='single qualified attempt'if eligible else'BLOCKED',full_path_seconds=baseline['process']['runtime_s'],matched_profile_dt_cost_ratio=ratio,predicted_seconds=estimate,margin=1.1,wall=900,attempts=1 if eligible else 0,reason='uniform4.5 extrapolation overweights expensive initial phase;actual full18s cost and matched4s per-dt ratio give phase-weighted bound,original profile-only rejection preserved'))
    if eligible:run('quarterdt_phase_budget',dt=.000125,wall=900)
if __name__=='__main__':main()
