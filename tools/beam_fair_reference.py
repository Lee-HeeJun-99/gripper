"""Matched numerical/section OFF references, not mixed-condition stiffness ratios."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from beam_common import OUT,write_json
from beam_multilayer import run
from integrated_trial import Config
def main():
    target=OUT/'fair_reference.json'
    if target.exists():raise FileExistsError(target)
    cases=[('L8_free_compensated',Config(layers=8,k=0,load=1e-6,duration=12.),True),('L4_equal_total_free',Config(layers=4,k=0,load=1e-6,duration=12.,equal_total_material=True),False)];results={}
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,n,c,compensated=a):n for n,c,a in cases}
        for f in as_completed(tasks):
            n=tasks[f]
            try:results[n]=f.result()
            except Exception as e:results[n]=dict(status='FAIL',failure_reason=repr(e))
            write_json(target,results)
if __name__=='__main__':main()
