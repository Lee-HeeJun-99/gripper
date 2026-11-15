from curve_trial import run
from curve_common import OUT,write_json
def main():
    profile=run('profile_halfdt',dt=.00025,profile=True);prediction=profile['process']['runtime_s']*4.5
    if profile['status']!='EXPERIMENTAL'or prediction*1.1>900:
        write_json(OUT/'halfdt_decision.json',dict(status='BLOCKED',prediction=prediction,reason='profile margin exceeds900s or physical loading failure'));return
    limit=900 if prediction*1.1>480 else 480
    write_json(OUT/'halfdt_decision.json',dict(prediction=prediction,wall=limit,attempts=1,reason='new objective curve map independent time diagnostic;prior linear base-to-quarter failure retained'))
    run('halfdt',dt=.00025,wall=limit)
if __name__=='__main__':main()
