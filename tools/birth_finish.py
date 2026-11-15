"""Bounded final half-dt and controlled events after the profiled queue fills.

Use once in the documented canonical campaign, not concurrently with a new
campaign launch. Already-running supervisor has only four non-profile cases
left and no unexpanded profiling jobs at this point.
"""
import time
from birth_common import ROOT,OUT,write_json
def active():
    return [p for p in (ROOT/'results/birth_20261115').rglob('process.json')if p.parent.parent.name=='grasp' and not(p.parent/'metrics.json').exists()]
def wait_for(limit,seconds):
    start=time.monotonic()
    while len(active())>=limit:
        if time.monotonic()-start>seconds:raise TimeoutError('bounded wait for physics slot; no child launched')
        time.sleep(2)
def main():
    write_json(OUT/'finish_plan.json',dict(wait_budget_s=1200,maximum_physics_children=4,half_dt_wall_s=480,reason='same v8_clean model; fill missing half-dt pair without pooling v7',one_invocation=True))
    wait_for(4,1200)
    import birth_events,birth_trial
    birth_events.main()
    birth_trial.run('dt_half',dt=.00025,duration=18)
    wait_for(1,1200)
    import birth_energy_audit,birth_memory,birth_assess,birth_plot
    for m in (birth_energy_audit,birth_memory,birth_assess,birth_plot):m.main()
    write_json(OUT/'finish_complete.json',dict(status='completed bounded execution and analysis; not a full physics PASS'))
if __name__=='__main__':main()
