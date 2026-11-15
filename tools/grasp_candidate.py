"""Extra dt/extended-duration validation of the actual planar Optuna Pareto point."""
import json,concurrent.futures
from grasp_common import OUT,write_json
from run_trial import run_trial
from optimize import objective_values
def main():
    out=OUT/'candidate_extra';out.mkdir(exist_ok=False);candidate=json.loads((OUT/'optuna_v2/actual/pareto_candidates.json').read_text())[0]
    def one(label):
        dt,T=(.00025,3.) if label=='halfdt' else (.0005,9.)
        off=run_trial(out/(label+'_off'),dt=dt,duration=T,timeout=120)
        on=run_trial(out/(label+'_on'),k=candidate['k'],connectors=candidate['connector_indices'],dt=dt,duration=T,timeout=120)
        r=dict(off_status=off['status'],on_status=on['status'],status='FAIL',dt=dt,duration=T)
        if off['status']=='complete' and on['status']=='complete':
            ratio,slip=objective_values(off,on);r.update(stiffness_ratio=ratio,normalized_slip=slip,relative_ratio_change=abs(ratio/candidate['stiffness_ratio']-1),relative_slip_change=abs(slip/candidate['normalized_slip']-1));r['status']='PASS' if max(r['relative_ratio_change'],r['relative_slip_change'])<.005 else 'FAIL'
        return label,r
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=dict(pool.map(one,('halfdt','plus6s')))
    write_json(out/'summary.json',dict(candidate=candidate,checks=results,tolerance=.005,scope='validated planar30mm model only; dt fixed within each OFF/ON pair; no grasp objective'))
    print(results)
if __name__=='__main__':main()
