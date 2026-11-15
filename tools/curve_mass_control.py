from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from curve_common import OUT,write_json
from curve_trial import run
def main():
    # Prior actual profiles bound the same topology/contact/layout;diagonal
    # entries change but total mass,per-mass inertia and sparsity stay fixed.
    for n,profile in((11,'profile_n11'),(21,'fixed_profile_n21')):
        r=json.loads((OUT/'grasp'/profile/'metrics.json').read_text())
        if r['status']!='EXPERIMENTAL'or r['process']['runtime_s']*4.5*1.1>480:raise RuntimeError('missing bounded topology profile')
    write_json(OUT/'mass_control_plan.json',dict(reason='falsify first-order uniform-nodal mass quadrature error;total mass and per-mass inertia unchanged,reference tributary weights derived not tuned',long_children=2,wall=480,memory=4294967296,default_layout='same10connectors/11guides'))
    records={};queued41=False
    with ThreadPoolExecutor(2)as pool:
        pending={pool.submit(run,'mass_n'+str(n),nodes=n,fixed_layout=True,tributary_mass=True):('full',n)for n in(11,21)}
        while pending:
            future=next(as_completed(pending));stage,n=pending.pop(future)
            try:r=future.result();records[stage+'_n'+str(n)]=dict(status=r['status'],process=r['process'])
            except Exception as e:r={};records[stage+'_n'+str(n)]=dict(status='FAIL',reason=repr(e))
            if not queued41:pending[pool.submit(run,'mass_profile_n41',nodes=41,profile=True,fixed_layout=True,tributary_mass=True)]=('profile',41);queued41=True
            elif stage=='profile'and r.get('status')=='EXPERIMENTAL':
                prediction=r['process']['runtime_s']*4.5
                if prediction*1.1>900:records['full_n41']=dict(status='BLOCKED',prediction=prediction)
                else:
                    wall=900 if prediction*1.1>480 else 480;write_json(OUT/'mass_n41_decision.json',dict(prediction=prediction,margin=1.1,wall=wall,attempts=1));pending[pool.submit(run,'mass_n41',nodes=41,fixed_layout=True,tributary_mass=True,wall=wall)]=('full',41)
            write_json(OUT/'mass_completed.json',records)
if __name__=='__main__':main()
