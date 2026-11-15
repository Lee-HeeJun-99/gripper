"""Causal controller-clock contrast with bounded actual SDK runs."""
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
from curve_common import ROOT,OUT,write_json
from curve_fixed_clock import run
from trial_validation import read_states


def equivalence(new,old):
    a=read_states(new/'state.txt');b=read_states(old/'state.txt')
    if len(a)!=len(b):raise ValueError('actual equivalence frame count')
    errors={k:float(np.max(np.abs(np.array([r[k]for r in a])-np.array([r[k]for r in b]))))for k in('X','V','R')}
    return dict(status='PASS'if not any(errors.values())else'FAIL',physical_errors=errors,clock_difference=max(abs(u['time']-v['time'])for u,v in zip(a,b)),scope='physical state/force bit-equivalence;clock representation differences deliberately separate')


def main():
    old=ROOT/'results/autonomous_20261116_beam_compensation_a01'
    proof=equivalence(OUT/'grasp/profile_base',old/'grasp/profile_base')
    path=OUT/'profile_physical_equivalence.json'
    if path.exists():raise ValueError('refuse repeated fixed-clock campaign')
    write_json(path,proof)
    if proof['status']!='PASS':return
    profile=json.loads((OUT/'grasp/profile_base/metrics.json').read_text())
    if profile['status']!='EXPERIMENTAL'or profile['process']['runtime_s']*6*1.1>480:raise ValueError('actual base24profile prerequisite')
    write_json(OUT/'campaign_plan.json',dict(max_internal_physics=3,memory=4294967296,default_wall=480,half24_wall=900,quarter18_wall=1320,attempts_per_case=1,scope='same SDK DefaultAnimationLoop mechanics,same schedule thresholds/materials;integer-index clock fixes observed one-step input shifts;quarter is18s not unexecuted24s recovery'))
    records={};profiles={};ready=False;launched=set()
    with ThreadPoolExecutor(3)as pool:
        pending={pool.submit(run,'base24',duration=24):('full','base24',.0005,24),pool.submit(run,'profile_halfdt',dt=.00025,profile=True):('profile','half24',.00025,24),pool.submit(run,'profile_quarterdt',dt=.000125,profile=True):('profile','quarter18',.000125,18)}
        while pending:
            f=next(as_completed(pending));stage,name,dt,duration=pending.pop(f)
            try:
                r=f.result();records[stage+'_'+name]={k:r.get(k)for k in('status','process','bounded_hold_pass','global_moment_residual','recovery_pass')}
                if stage=='profile':profiles[name]=r
                elif name=='base24':
                    eq=equivalence(OUT/'grasp/base24',old/'grasp/repeat24');write_json(OUT/'base24_physical_equivalence.json',eq);ready=r.get('bounded_hold_pass')and r.get('recovery_pass')and eq['status']=='PASS'
            except Exception as error:records[stage+'_'+name]=dict(status='FAIL',reason=repr(error))
            if ready:
                for n,p in profiles.items():
                    if n in launched:continue
                    launched.add(n)
                    d=24 if n=='half24' else 18
                    wall=900 if n=='half24' else 1320
                    h=.00025 if n=='half24' else .000125
                    prediction=p['process']['runtime_s']*d/4
                    if p['status']!='EXPERIMENTAL'or prediction*1.1>wall:records['full_'+n]=dict(status='BLOCKED',prediction=prediction,reason='actual profile exceeds unchanged bounded exception');continue
                    write_json(OUT/(n+'_decision.json'),dict(prediction=prediction,margin=1.1,wall=wall,attempts=1,memory=4294967296))
                    pending[pool.submit(run,n,dt=h,duration=d,wall=wall)]=('full',n,h,d)
            write_json(OUT/'campaign_status.json',records)
    print(records)


if __name__=='__main__':main()
