"""Only balance/repeat and convergence diagnostics, not optimized grasp scores."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from beam_common import OUT,write_json
from beam_grasp_trial import run
def main():
    cases=[('Tz_repeat',dict()),('Tz_q16',dict(samples=16,duration=18.)),('Tz_q32',dict(samples=32,duration=18.)),('Tz_n21q32',dict(nodes=21,samples=32,duration=18.)),('Tz_halfdt',dict(dt=.00025,duration=18.)),('Tz_historyhalf',dict(history=.005,duration=18.))]
    write_json(OUT/'grasp_convergence_plan.json',dict(cases=cases,criteria=dict(spatial=0.01,dt=.001,history=.01,repeat=1e-6),scope='same Tz5e-6 law/loads/materials, no performance objective, profile before41-node full run',maximum_children=2,wall_per_child=480));results={}
    with ThreadPoolExecutor(2) as pool:
        futures={pool.submit(run,name,**cfg):name for name,cfg in cases}
        for f in as_completed(futures):
            name=futures[f]
            try:results[name]=f.result()
            except Exception as e:results[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'grasp_convergence.json',results)
if __name__=='__main__':main()
