from autonomous_trial import run
from research_common import OUT,write_json
def main():
    profile=run('profile_quarterdt',history=.0025,dt=.000125,profile=True)
    prediction=profile['process']['runtime_s']*4.5
    if profile['status']!='EXPERIMENTAL'or prediction*1.1>900:
        write_json(OUT/'quarterdt_decision.json',dict(status='BLOCKED',prediction=prediction,reason='profile plus10percent exceeds single900s bound or profile fails'));return
    limit=900 if prediction*1.1>480 else 480
    write_json(OUT/'quarterdt_decision.json',dict(status='profile-qualified single attempt',profile_wall_s=profile['process']['runtime_s'],prediction=prediction,margin=1.1,limit=limit,memory=4294967296,reason='half-dt friction-loss difference0.0999735percent is near0.1percent threshold; quarter-step provides new information, same fine history, no old-result reuse',attempts=1))
    run('fine_quarterdt',history=.0025,dt=.000125,wall=limit)
if __name__=='__main__':main()
