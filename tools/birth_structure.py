"""New mesh-qualified linear-structure study, strictly separate from grasp."""
import json,hashlib
from birth_common import ROOT,OUT,write_json,sha
from beam_common import identity,material
from models.structural_interface.refined import solve,qualified
def main():
    import optuna
    identity();out=OUT/'structure_refined';out.mkdir(exist_ok=False);m=material();source=ROOT/'models/structural_interface/refined.py'
    reference=solve(84.1732992010,list(range(1,11)),41,m)
    if abs(reference['max_slip_mm']/3.5526954413564075e-7-1)>1e-8:raise ValueError('preserved independent reference mismatch')
    contract=dict(model_sha256=sha(source),runner_sha256=sha(ROOT/'tools/birth_structure.py'),material=m,seed=2911,scope='independent static100mm two-layer structure; all-interface mesh-refined objective, NO grasp objectives; actual candidates not yet approved')
    storage='sqlite:///'+str(out/'study.sqlite3');sampler=optuna.samplers.TPESampler(seed=2911);study=optuna.create_study(study_name='birth_structure_full_interface_100mm',storage=storage,directions=['maximize','minimize'],sampler=sampler);study.set_user_attr('identity',contract)
    def objective(t):
        k=t.suggest_float('k',.001,100,log=True);count=t.suggest_int('count',1,10);ranks=[(t.suggest_float('location_'+str(i),0,1),i) for i in range(1,11)];ids=sorted(i for _,i in sorted(ranks,reverse=True)[:count]);signature=hashlib.sha256(json.dumps([k,ids]).encode()).hexdigest()
        if any(p.state.name=='COMPLETE' and p.user_attrs.get('design_hash')==signature for p in study.trials):raise optuna.TrialPruned('duplicate')
        t.set_user_attr('connector_indices',ids);t.set_user_attr('design_hash',signature)
        try:r,sequence,error=qualified(k,ids,m);off=solve(0,[],r['nodes'],m)
        except ValueError as e:raise optuna.TrialPruned(str(e))
        t.set_user_attr('mesh_nodes',r['nodes']);t.set_user_attr('mesh_error',error);write_json(out/f'trial_{t.number}.json',dict(result=r,sequence=sequence,off=off,config=dict(k=k,physical_connector_positions_mm=[10*i for i in ids])));return off['tip_deflection_mm']/r['tip_deflection_mm'],r['max_slip_mm']
    study.optimize(objective,n_trials=3);study=optuna.load_study(study_name=study.study_name,storage=storage,sampler=sampler)
    if study.user_attrs['identity']!=contract:raise ValueError('study mixed identity')
    while sum(t.state.name=='COMPLETE' for t in study.trials)<24 and len(study.trials)<40:study.optimize(objective,n_trials=1)
    r=dict(status='PASS' if sum(t.state.name=='COMPLETE' for t in study.trials)>=24 else 'FAIL',complete=sum(t.state.name=='COMPLETE' for t in study.trials),pruned=sum(t.state.name=='PRUNED' for t in study.trials),failed=sum(t.state.name=='FAIL' for t in study.trials),resumed_after3=True,identity=contract,pareto=[dict(number=t.number,values=t.values,params=t.params,connector_indices=t.user_attrs['connector_indices'],mesh_nodes=t.user_attrs['mesh_nodes']) for t in study.best_trials],actual_sofa_candidate_approved=False,grasp_optimization='BLOCKED');write_json(out/'summary.json',r);print(r)
if __name__=='__main__':main()
