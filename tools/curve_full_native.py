"""Canonical >=21node qualification,after strict-FP path equivalence."""
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
from curve_common import ROOT,OUT,write_json
from curve_trial import run
from trial_validation import read_states
def main():
    profile=run('equivalence_profile',profile=True,fixed_layout=True,tributary_mass=True)
    old=[r for r in read_states(ROOT/'results/autonomous_20261116_curve_a01/grasp/mass_n11/state.txt')if r['time']<=4+1e-8];actual=read_states(OUT/'grasp/equivalence_profile/state.txt')
    errors={k:float(np.max(np.abs(np.array([r[k]for r in old])-np.array([r[k]for r in actual]))))for k in('X','V','R')}
    equivalent=profile['status']=='EXPERIMENTAL'and all(v<1e-12 for v in errors.values());write_json(OUT/'path_equivalence.json',dict(status='PASS'if equivalent else'FAIL',errors=errors,scope='same source,strict-FP native Beam+contact,actual4s mass-weighted trajectory;no cross-binary mesh pooling'))
    if not equivalent:return
    plan=[('n21',dict(nodes=21)),('n41',dict(nodes=41)),('history_fine',dict(nodes=21,history=.00125)),('halfdt',dict(nodes=21,dt=.00025)),('quarterdt',dict(nodes=21,dt=.000125)),('repeat24',dict(nodes=21,duration=24))];records={}
    write_json(OUT/'canonical_plan.json',dict(cases=plan,parallel=3,memory=4294967296,default_wall=480,exception_wall=900,reason='derived tributary mass removes first-order quadrature;11node remains underresolved,qualify21against41without weakening1percent;all comparisons use one runtime binary pair'))
    with ThreadPoolExecutor(3)as pool:
        pending={pool.submit(run,'profile_'+name,profile=True,fixed_layout=True,tributary_mass=True,**kw):('profile',name,kw)for name,kw in plan}
        while pending:
            future=next(as_completed(pending));stage,name,kw=pending.pop(future)
            try:r=future.result();records[stage+'_'+name]=dict(status=r['status'],process=r['process'])
            except Exception as e:r={};records[stage+'_'+name]=dict(status='FAIL',reason=repr(e))
            if stage=='profile'and r.get('status')=='EXPERIMENTAL':
                prediction=r['process']['runtime_s']*kw.get('duration',18)/4
                if prediction*1.1>900:records['full_'+name]=dict(status='BLOCKED',prediction=prediction,reason='profile plus margin exceeds900s')
                else:
                    wall=900 if prediction*1.1>480 else 480;write_json(OUT/(name+'_decision.json'),dict(prediction=prediction,wall=wall,margin=1.1,attempts=1));pending[pool.submit(run,name,fixed_layout=True,tributary_mass=True,wall=wall,**kw)]=('full',name,kw)
            write_json(OUT/'canonical_completed.json',records)
if __name__=='__main__':main()
