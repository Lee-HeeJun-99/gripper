"""Finite beam validation campaign, no grasp optimization or tolerance changes."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from beam_trial import run
from beam_common import OUT,write_json
def main():
    cases=[('force'+str(n),dict(nodes=n,duration=12.)) for n in (11,21,41)]
    cases += [('force_repeat',dict(duration=12.)),('force_halfdt',dict(duration=12.,dt=.00025)),('axial',dict(duration=12.,axis=0,load=1e-6)),('moment',dict(duration=12.,axis=4,load=1e-5)),('torsion',dict(duration=12.,axis=3,load=1e-5)),('rotated',dict(duration=12.,rotation=2.1)),('inherited',dict(duration=12.,inherited=True))]
    OUT.mkdir(parents=True,exist_ok=True);write_json(OUT/'single_plan.json',dict(cases=cases,maximum_children=2,wall_cap_s=480,reason='initial3s atmassdamping.2 is transient; declared massdamping2 matchesgrasp benchmark, all qualification cases use same damping and12s',criteria=dict(relative_residual=1e-3,speed=1e-5,relative_drift=1e-4)))
    results={}
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,name,**cfg):name for name,cfg in cases}
        for future in as_completed(tasks):
            name=tasks[future]
            try:results[name]=future.result()
            except Exception as e:results[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'single_campaign.json',results)
if __name__=='__main__':main()
