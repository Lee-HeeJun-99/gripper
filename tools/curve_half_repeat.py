import json
from curve_common import OUT,write_json
from curve_compensation import run


def main():
    old=json.loads((OUT/'grasp/halfdt/metrics.json').read_text())
    profile=json.loads((OUT/'grasp/profile_halfdt/metrics.json').read_text())
    if not old.get('bounded_hold_pass')or profile['status']!='EXPERIMENTAL':raise ValueError('actual baseline/profile prerequisites')
    decision=OUT/'half_repeat24_decision.json'
    if decision.exists():raise ValueError('refuse duplicate repeat decision')
    prediction=profile['process']['runtime_s']*6
    if prediction*1.1>900:raise ValueError('profile exceeds bounded repeat allowance')
    write_json(decision,dict(profile_runtime=profile['process']['runtime_s'],prediction=prediction,margin=1.1,wall=900,attempts=1,memory=4294967296,scope='uninstantiated selected-half-dt24s reference/recovery for read-only energy journal;no optimizer'))
    run('half_repeat24',dt=.00025,duration=24,wall=900)


if __name__=='__main__':main()
