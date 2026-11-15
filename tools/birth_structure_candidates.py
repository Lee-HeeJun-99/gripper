"""Fresh actual SOFA verification of independent refined-FEM Pareto designs."""
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
import beam_multilayer as engine
from integrated_trial import Config
from birth_common import OUT,write_json
def main():
    engine.OUT=OUT;study=json.loads((OUT/'structure_refined/summary.json').read_text());plan={};cases={}
    for n in (21,41):plan['free_n'+str(n)]=Config(nodes=n,k=0,load=1e-6,duration=12.)
    for c in study['pareto']:
        for suffix,n,dt in [('base',21,.0005),('repeat',21,.0005),('halfdt',21,.00025),('mesh',41,.0005)]:
            name=f"candidate{c['number']}_{suffix}";plan[name]=Config(nodes=n,k=c['params']['k'],connectors=tuple(i*(n-1)//10 for i in c['connector_indices']),load=1e-6,duration=12.,dt=dt)
    write_json(OUT/'structure_candidate_plan.json',{k:vars(v) for k,v in plan.items()})
    with ThreadPoolExecutor(2)as pool:
        futures={pool.submit(engine.run,k,v):k for k,v in plan.items()}
        for future in as_completed(futures):
            name=futures[future]
            try:cases[name]=future.result()
            except Exception as e:cases[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'structure_candidate_runs.json',cases)
    decisions={}
    for c in study['pareto']:
        prefix=f"candidate{c['number']}_";r={s:cases[prefix+s] for s in ('base','repeat','halfdt','mesh')};checks={}
        if all(x.get('status')=='PASS' for x in r.values()) and all(cases['free_n'+str(n)].get('status')=='PASS' for n in (21,41)):
            for s,limit in [('repeat',1e-6),('halfdt',.001),('mesh',.01)]:
                for metric in ('tip_deflection_mm','max_interface_slip_mm'):checks[s+'_'+metric]=dict(relative_difference=abs(r['base'][metric]/r[s][metric]-1),limit=limit)
            ratio=cases['free_n21']['tip_deflection_mm']/r['base']['tip_deflection_mm'];status='PASS' if all(x['relative_difference']<x['limit'] for x in checks.values()) else 'FAIL'
        else:ratio=None;status='FAIL'
        decisions[str(c['number'])]=dict(status=status,scope='100mm structure ONLY, not grasp or calibrated material design',stiffness_ratio=ratio,checks=checks,trial_numbers=list(r),grasp_optimization='BLOCKED')
    write_json(OUT/'structure_candidate_decisions.json',decisions);print(decisions)
if __name__=='__main__':main()
