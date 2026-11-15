import json
import numpy as np
from curve_common import ROOT,OUT,write_json
from curve_trial import run
from trial_validation import read_states
def main():
    r=run('profile_equivalence',profile=True);old=ROOT/'results/autonomous_20261116_curve_a01/grasp/profile_n11';new=OUT/'grasp/profile_equivalence';a=read_states(old/'state.txt');b=read_states(new/'state.txt');errors={}
    if len(a)!=len(b):raise ValueError('profile state count differs')
    for key in('X','V','R'):errors[key]=float(np.max(np.abs(np.array([x[key]for x in a])-np.array([x[key]for x in b]))))
    valid=r['status']=='EXPERIMENTAL'and errors['X']<1e-11 and errors['V']<1e-11 and errors['R']<1e-12
    write_json(OUT/'equivalence.json',dict(status='PASS'if valid else'FAIL',maximum_absolute_errors=errors,flags='-O3 -march=native -ffp-contract=off,no fast-math',scope='actual4s same-physics raw states;not full dynamic or mesh certificate'))
    if not valid:return
    profile=run('profile_quarterdt',dt=.000125,profile=True);prediction=profile['process']['runtime_s']*4.5
    if profile['status']!='EXPERIMENTAL'or prediction*1.1>900:write_json(OUT/'quarterdt_decision.json',dict(status='BLOCKED',prediction=prediction,reason='strict-FP native profile plus10percent exceeds900s bound or failed'));return
    wall=900 if prediction*1.1>480 else 480;write_json(OUT/'quarterdt_decision.json',dict(prediction=prediction,wall=wall,attempts=1,reason='profile-qualified strict-FP ISA optimization,actual equivalence tested;no physics/tolerance relaxation'));run('quarterdt',dt=.000125,wall=wall)
if __name__=='__main__':main()
