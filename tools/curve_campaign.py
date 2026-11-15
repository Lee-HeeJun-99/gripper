from concurrent.futures import ThreadPoolExecutor,as_completed
from curve_trial import run
from curve_common import OUT,write_json
def main():
    results={};write_json(OUT/'plan.json',dict(nodes=[11,21,41],history=.0025,dt=.0005,duration=18,max_children=3,memory_per_child=4294967296,default_wall=480,exception='single profiled attempt up to900seconds,no repeated timeouts'))
    with ThreadPoolExecutor(3)as pool:
        pending={pool.submit(run,'profile_n'+str(n),nodes=n,profile=True):('profile',n)for n in(11,21,41)}
        while pending:
            future=next(as_completed(pending));stage,n=pending.pop(future);name=stage+'_n'+str(n)
            try:r=future.result();results[name]=dict(status=r['status'],process=r['process'])
            except Exception as e:r={};results[name]=dict(status='FAIL',reason=repr(e))
            if stage=='profile'and r.get('status')=='EXPERIMENTAL':
                prediction=r['process']['runtime_s']*4.5
                if prediction*1.1>900:results['full_n'+str(n)]=dict(status='BLOCKED',reason='profile exceeds900s bound',prediction=prediction)
                else:
                    limit=900 if prediction*1.1>480 else 480
                    write_json(OUT/('n'+str(n)+'_decision.json'),dict(prediction=prediction,margin=1.1,wall=limit,attempts=1,reason='first actual curved-contact mesh validation,not unchanged failed linear campaign'))
                    pending[pool.submit(run,'n'+str(n),nodes=n,wall=limit)]=('full',n)
            write_json(OUT/'completed.json',results)
if __name__=='__main__':main()
