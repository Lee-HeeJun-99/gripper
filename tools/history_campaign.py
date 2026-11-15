"""Finite homogeneous-build convergence campaign, no grasp optimization."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from history_common import OUT,write_json
from history_trial import run
def main():
    target=OUT/'campaign_v3.json'
    if target.exists():raise FileExistsError(target)
    cases=[('base',dict()),('normal_q32',dict(samples=32,duration=18.)),('history_half',dict(history=.005,duration=18.)),('dt_half',dict(dt=.00025,duration=18.))]
    write_json(OUT/'campaign_v3_plan.json',dict(cases=cases,max_children=4,wall_limit=480,memory_limit_gib=4,scope='normal quadrature order differs from cellOrder; tangential material-cell Gauss2 separately validated against analytic/extra cell-order tests; existing acceptance limits unchanged'))
    results={}
    with ThreadPoolExecutor(4) as pool:
        futures={pool.submit(run,n,**c):n for n,c in cases}
        for f in as_completed(futures):
            n=futures[f]
            try:results[n]=f.result()
            except Exception as e:results[n]=dict(status='FAIL',failure_reason=repr(e))
            write_json(target,results)
if __name__=='__main__':main()
