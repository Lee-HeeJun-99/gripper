"""Same physics after AD1/AD2 equivalence; retry only documented cost/zero-mu bugs."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from grasp_common import OUT,write_json
from grasp_trial import Config,run

def main():
    c=replace(Config(),rayleigh_mass=2.)
    cases=[('fast_repeat',c,240),('mu_zero_fixed',replace(c,mu=0),240),('fast_n21q32',replace(c,nodes=21,samples=32),360),('fast_n41q16',replace(c,nodes=41,samples=16),480),('fast_n41q32',replace(c,nodes=41,samples=32),480)]
    rows={}
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,name,config,wall):name for name,config,wall in cases}
        for task in as_completed(tasks):
            name=tasks[task]
            try:rows[name]=task.result()
            except Exception as e:rows[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'fast_campaign.json',rows)

if __name__=='__main__':main()
