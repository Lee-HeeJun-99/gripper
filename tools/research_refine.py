from concurrent.futures import ThreadPoolExecutor,as_completed
from autonomous_trial import run
from research_common import OUT,write_json
def main():
    plan=[('fine_n21',dict(nodes=21,history=.0025)),('fine_repeat',dict(history=.0025,duration=24)),('profile_n41',dict(nodes=41,history=.0025,profile=True)),('profile_halfdt',dict(dt=.00025,history=.0025,profile=True))];results={}
    write_json(OUT/'refinement_plan.json',dict(cases=plan,reason='same model and refined history.0025; coarse history failures retained; separate Beam/time errors',limit=480,memory=4294967296,max_children=4))
    with ThreadPoolExecutor(4)as pool:
        pending={pool.submit(run,name,**kw):name for name,kw in plan}
        while pending:
            future=next(as_completed(pending));name=pending.pop(future)
            try:r=future.result();results[name]=dict(status=r['status'],process=r['process'])
            except Exception as e:r={};results[name]=dict(status='FAIL',reason=repr(e))
            if name in('profile_n41','profile_halfdt')and r.get('status')=='EXPERIMENTAL':
                target,params=('fine_n41',dict(nodes=41,history=.0025))if name=='profile_n41'else('fine_halfdt',dict(dt=.00025,history=.0025));prediction=r['process']['runtime_s']*4.5
                if prediction*1.1>900:results[target]=dict(status='BLOCKED',reason='profile plus10percent exceeds900s',prediction=prediction)
                else:
                    limit=900 if prediction*1.1>480 else 480
                    write_json(OUT/(target+'_execution_plan.json'),dict(profile=name,predicted_18s=prediction,margin=1.1,limit=limit,attempts=1,reason='new fixed-material-point model; actual profile determines single bounded exception; no rerun of old failed binary'));pending[pool.submit(run,target,**params,wall=limit)]=target
            write_json(OUT/'refinement_completed.json',results)
    print(results)
if __name__=='__main__':main()
