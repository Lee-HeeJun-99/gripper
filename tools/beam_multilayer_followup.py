"""Finite structural follow-up, not an extension of the old 45 gates."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from beam_common import OUT,write_json
from beam_multilayer import run
from integrated_trial import Config
def main():
    target=OUT/'multilayer_followup.json'
    if target.exists():raise FileExistsError(target)
    cases=[('L8_comp_halfdt',Config(layers=8,k=100,load=1e-6,duration=12.,dt=.00025),True),('L8_comp_n21',Config(layers=8,nodes=21,k=100,load=1e-6,duration=12.),True),('L8_comp_extended',Config(layers=8,k=100,load=1e-6,duration=18.),True),('L4_equal_total',Config(layers=4,k=100,load=1e-6,duration=12.,equal_total_material=True),False)]
    results={}
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,n,c,compensated=a):n for n,c,a in cases}
        for f in as_completed(tasks):
            n=tasks[f]
            try:results[n]=f.result()
            except Exception as e:results[n]=dict(status='FAIL',failure_reason=repr(e))
            write_json(target,results)
if __name__=='__main__':main()
