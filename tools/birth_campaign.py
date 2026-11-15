"""Finite remaining canonical-grid campaign; max4 physics children globally."""
import json,time
from concurrent.futures import ThreadPoolExecutor
from birth_common import ROOT,OUT,write_json
from birth_trial import run
def main():
    campaign=ROOT/'results/birth_20261115';queue=[('normal16',dict(samples=16,duration=18)),('normal32',dict(samples=32,duration=18)),('cell4',dict(cell_order=4,duration=18)),('repeat',dict(duration=24)),('n21',dict(nodes=21,duration=18)),('profile_n41',dict(nodes=41,profile=True)),('profile_dtquarter',dict(dt=.000125,profile=True)),('profile_h_eighth',dict(history=.00125,profile=True)),('journal_profile',dict(profile=True,journal=True))];active={};results={};start=time.monotonic();write_json(OUT/'remaining_plan.json',dict(queue=queue,max_global_children=4,launch_budget_s=2400,default_wall_s=480))
    with ThreadPoolExecutor(4)as pool:
        while queue or active:
            for future,name in list(active.items()):
                if not future.done():continue
                del active[future]
                try:r=future.result();results[name]=dict(status=r['status'],process=r['process'])
                except Exception as e:r={};results[name]=dict(status='FAIL',reason=repr(e))
                if r.get('status')=='EXPERIMENTAL' and name in ('profile_n41','profile_dtquarter','profile_h_eighth','journal_profile'):
                    target,params={'profile_n41':('n41',dict(nodes=41,duration=18)),'profile_dtquarter':('dt_quarter',dict(dt=.000125,duration=18)),'profile_h_eighth':('history_eighth',dict(history=.00125,duration=18)),'journal_profile':('journal_full',dict(duration=24,journal=True))}[name];prediction=r['process']['runtime_s']*params['duration']/4
                    if prediction>900:results[target]=dict(status='BLOCKED',reason='profile predicts more than bounded900s',prediction=prediction)
                    else:
                        limit=900 if prediction>480 else 480;params['wall']=limit;write_json(OUT/(target+'_execution_plan.json'),dict(profile=name,prediction=prediction,wall=limit,memory_bytes=4294967296,attempts=1,reason='new canonical-grid compiled model; prior scalar/AD and trajectory equivalence verified; no repeat of an unchanged failed binary'));queue.append((target,params))
                write_json(OUT/'remaining_results.json',results)
            own=set(active.values());external=0
            for p in campaign.rglob('process.json'):
                if p.parent.parent.name=='grasp' and p.parent.name not in own and not(p.parent/'metrics.json').exists():external+=1
            while queue and external+len(active)<4 and time.monotonic()-start<2400:
                name,params=queue.pop(0)
                if(OUT/'grasp'/name).exists():raise FileExistsError('refusing old campaign case '+name)
                active[pool.submit(run,name,**params)]=name
            if time.monotonic()-start>=2400 and queue:
                for name,_ in queue:results[name]=dict(status='NOT RUN',reason='bounded campaign launch budget');queue=[];write_json(OUT/'remaining_results.json',results)
            if queue or active:time.sleep(2)
    print({k:v['status'] for k,v in results.items()})
if __name__=='__main__':main()
