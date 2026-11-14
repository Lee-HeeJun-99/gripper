"""Cold-start structural Euler regression with compensated v*dt accumulation.

No grasp object is present; no target/force feedback or tolerance changes.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from integrated_trial import Config
from stabilization_trials import run
from stabilization_common import OUT,write_json

def main():
    cases=[('L8_base',Config(layers=8,k=100)),('L8_halfdt',Config(layers=8,k=100,dt=.00025)),
           ('L8_mesh',Config(layers=8,k=100,nodes=21,connectors=tuple(range(2,21,2)))),('L8_extended',Config(layers=8,k=100,duration=18)),
           ('small',Config(k=0,load=0,normal_k=.001,cable_tension=1e-6,duration=18)),('length',Config(k=0,load=0,normal_k=.001,cable_k=.01,shortening=.0001,duration=18)),
           ('wire_pressure',Config(k=1,mode=1,load=0,normal_k=.001,cable_tension=1e-5,pressure=1e-8,duration=18)),
           ('L2_regression',Config(k=100)),('L4_regression',Config(layers=4,k=100))]
    rows={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        tasks={pool.submit(run,'compensated_cold/'+name,c,compensated=True):name for name,c in cases}
        for task in as_completed(tasks):
            name=tasks[task]
            try:rows[name]=task.result()
            except Exception as e:rows[name]=dict(status='FAIL',reason=repr(e))
            write_json(OUT/'compensated_cold/summary.json',dict(records=rows,scope='structural compensated Euler, cold start; original standard-Euler failures preserved'))

if __name__=='__main__':main()
