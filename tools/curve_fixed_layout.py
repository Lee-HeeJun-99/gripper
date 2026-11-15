from concurrent.futures import ThreadPoolExecutor,as_completed
from curve_common import OUT,write_json
from curve_trial import run
def main():
    records={}
    with ThreadPoolExecutor(2)as pool:
        pending={pool.submit(run,'fixed_profile_n'+str(n),nodes=n,profile=True,fixed_layout=True):('profile',n)for n in(21,41)}
        while pending:
            future=next(as_completed(pending));stage,n=pending.pop(future);name=stage+'_n'+str(n)
            try:r=future.result();records[name]=dict(status=r['status'],process=r['process'])
            except Exception as e:r={};records[name]=dict(status='FAIL',reason=repr(e))
            if stage=='profile'and r.get('status')=='EXPERIMENTAL':
                prediction=r['process']['runtime_s']*4.5
                if prediction*1.1>900:records['full_n'+str(n)]=dict(status='BLOCKED',prediction=prediction,reason='profile cost exceeds bound')
                else:
                    wall=900 if prediction*1.1>480 else 480
                    write_json(OUT/('fixed_n'+str(n)+'_decision.json'),dict(prediction=prediction,wall=wall,attempts=1,physical_layout='same10connectors/11guides as n11;no point stiffness rescaling',reason='falsify physical-layout drift under mesh refinement'))
                    pending[pool.submit(run,'fixed_n'+str(n),nodes=n,fixed_layout=True,wall=wall)]=('full',n)
            write_json(OUT/'fixed_completed.json',records)
if __name__=='__main__':main()
