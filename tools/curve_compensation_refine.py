"""Revalidate new summation model at one production-candidate dt,not old gates."""
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
from curve_common import OUT,write_json
from curve_compensation import run


def main():
    if not json.loads((OUT/'grasp/halfdt/metrics.json').read_text()).get('bounded_hold_pass'):
        raise ValueError('actual half-step physical baseline prerequisite')
    plan=OUT/'refinement_plan.json'
    if plan.exists():raise ValueError('refuse repeated refinement campaign')
    cases=[('mesh41_half',dict(nodes=41)),('history_fine_half',dict(history=.00125)),('mesh11_half',dict(nodes=11))]
    write_json(plan,dict(dt=.00025,cases=cases,profiles_sequential=True,full_children_at_most=2,full_wall_cap=1320,attempts_per_case=1,memory=4294967296,scope='new integration arithmetic needs independent mesh/history gates;coarse11FAILpreserved;no optimizer or force change'))
    records={};qualified=[]
    # Run sequential profiles first. Start only when other campaigns leave a
    # physical-child slot;the caller is responsible for the global <=4 budget.
    for name,kw in cases:
        r=run('profile_'+name,dt=.00025,profile=True,**kw)
        prediction=r['process']['runtime_s']*4.5;wall=480 if prediction*1.1<=480 else 900 if prediction*1.1<=900 else 1080 if prediction*1.1<=1080 else 1320
        records['profile_'+name]=dict(status=r['status'],process=r['process'])
        if r['status']=='EXPERIMENTAL'and prediction*1.1<=1320:
            write_json(OUT/(name+'_decision.json'),dict(prediction=prediction,margin=1.1,wall=wall,attempts=1,scope='profile-justified bounded mesh/history requalification,unchanged physics thresholds'))
            qualified.append((name,kw,wall))
        else:records['full_'+name]=dict(status='BLOCKED',prediction=prediction,reason='actual profile exceeds finite allowance')
        write_json(OUT/'refinement_status.json',records)
    with ThreadPoolExecutor(2)as pool:
        futures={pool.submit(run,name,dt=.00025,wall=wall,**kw):name for name,kw,wall in qualified}
        for f in as_completed(futures):
            name=futures[f]
            try:r=f.result();records['full_'+name]={k:r.get(k)for k in('status','process','bounded_hold_pass','global_moment_residual')}
            except Exception as error:records['full_'+name]=dict(status='FAIL',reason=repr(error))
            write_json(OUT/'refinement_status.json',records)
    print(records)


if __name__=='__main__':main()
