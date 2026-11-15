"""Bounded one-factor test of the observed fine-dt equilibrium floor."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from curve_common import OUT, write_json
from curve_compensation import run


def main():
    decision=OUT/'campaign_plan.json'
    if decision.exists():raise ValueError('refuse duplicated compensation campaign')
    scope=json.loads((OUT/'scope_test_v1/summary.json').read_text())
    base_profile=json.loads((OUT/'grasp/profile_base/metrics.json').read_text())
    if scope['status']!='PASS'or base_profile['status']!='EXPERIMENTAL':raise ValueError('actual scope/profile prerequisites')
    write_json(decision,dict(reason='Actual standard-Euler quarter result fails global moment1e-3;test lost structural translation increments,not added force. Object/quaternion/root remain untouched.',max_internal_children=3,default_wall=480,half_exception_wall=900,quarter_exception_wall=1320,memory_per_child=4294967296,attempts_per_case=1,prerequisite='higher-resolution full runs launch only after base hold passes and actual own profile fits margin'))
    records={};profiles={};base_ready=False;launched=set()
    with ThreadPoolExecutor(3)as pool:
        pending={pool.submit(run,'base',wall=480):('full','base',.0005),
                 pool.submit(run,'profile_halfdt',dt=.00025,profile=True):('profile','halfdt',.00025),
                 pool.submit(run,'profile_quarterdt',dt=.000125,profile=True):('profile','quarterdt',.000125)}
        while pending:
            future=next(as_completed(pending));stage,name,dt=pending.pop(future)
            try:
                r=future.result();records[stage+'_'+name]={k:r.get(k)for k in('status','process','bounded_hold_pass','global_moment_residual')}
                if stage=='profile':profiles[name]=r
                elif name=='base':base_ready=r.get('bounded_hold_pass',False)
            except Exception as error:records[stage+'_'+name]=dict(status='FAIL',reason=repr(error))
            if base_ready:
                for n,p in profiles.items():
                    if n in launched:continue
                    launched.add(n);wall=900 if n=='halfdt' else 1320
                    prediction=p['process']['runtime_s']*4.5
                    if p['status']!='EXPERIMENTAL'or prediction*1.1>wall:
                        records['full_'+n]=dict(status='BLOCKED',prediction=prediction,wall=wall,reason='own profile does not fit bounded allowance');continue
                    write_json(OUT/(n+'_decision.json'),dict(prediction=prediction,margin=1.1,wall=wall,attempts=1,scope='one independent structural-compensation contrast;previous standard-EulerFAILpreserved'))
                    pending[pool.submit(run,n,dt=.00025 if n=='halfdt'else .000125,wall=wall)]=('full',n,dt)
            write_json(OUT/'campaign_status.json',records)
    print(records)


if __name__=='__main__':main()
