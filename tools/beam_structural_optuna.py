"""True Optuna on validated linear100mm structure ONLY; grasp stays gated."""
import json,hashlib
from beam_common import ROOT,OUT,BUILD,material,sha,write_json,PYTHON
from closure_validation_suite import logged
from models.conservative_beam.linear_reference import solve
def main():
    import optuna
    out=OUT/'structural_optuna';out.mkdir(exist_ok=False);build=BUILD/'test_beam_linear'
    compile_result=logged(['g++','-std=c++17','-O3','tests/test_beam_linear.cpp','-o',str(build)],out/'compile',120)
    if compile_result['exit_code']:raise RuntimeError('linear limit compile')
    unit=logged([str(build)],out/'unit',30)
    if unit['exit_code']:raise RuntimeError('linear limit not verified')
    m=material();base=dict(EA=m['EA'],GA=m['GAz'],EI=m['EIy']);off=solve(**base);checks={}
    for k in (0,100):
        reference=solve(k=k,connectors=list(range(1,11)),**base);actual=json.loads((OUT/f'multilayer/L2_k{k}/metrics.json').read_text());checks[str(k)]=dict(actual_status=actual['status'],relative_tip_difference=abs(reference['tip_deflection_mm']/actual['tip_deflection_mm']-1),reference=reference,actual_metrics_sha256=sha(OUT/f'multilayer/L2_k{k}/metrics.json'))
    write_json(out/'reference_gate.json',checks)
    if any(r['actual_status']!='PASS' or r['relative_tip_difference']>.005 for r in checks.values()):raise RuntimeError('independent FEM vs actual SOFA gate failed')
    identity=dict(model_sha256=sha(ROOT/'models/conservative_beam/linear_reference.py'),optimizer_sha256=sha(ROOT/'tools/beam_structural_optuna.py'),material=base,scope='100mm two-layer linear elastic coupling stiffness/slip ONLY; no object/contact/wire/vacuum or grasp objectives; dt not sampled',seed=2911)
    storage='sqlite:///'+str(out/'study.sqlite3');study=optuna.create_study(study_name='linear_structure100mm',storage=storage,directions=['maximize','minimize'],sampler=optuna.samplers.TPESampler(seed=2911));study.set_user_attr('identity',identity)
    def objective(t):
        k=t.suggest_float('k',.001,100,log=True);count=t.suggest_int('connector_count',1,10);ranks=[(t.suggest_float('location_'+str(i),0,1),i) for i in range(1,11)];ids=sorted(i for _,i in sorted(ranks,reverse=True)[:count]);signature=hashlib.sha256(json.dumps([k,ids]).encode()).hexdigest()
        if any(p.user_attrs.get('design_hash')==signature and p.state.name=='COMPLETE' for p in study.trials):raise optuna.TrialPruned('duplicate independent design')
        r=solve(k=k,connectors=ids,**base);t.set_user_attr('design_hash',signature);t.set_user_attr('connector_indices',ids);t.set_user_attr('origin','independent linear FEM');t.set_user_attr('residual',r['relative_residual']);write_json(out/f'trial_{t.number}.json',r);return off['tip_deflection_mm']/r['tip_deflection_mm'],r['max_slip_mm']
    study.optimize(objective,n_trials=3);study=optuna.load_study(study_name='linear_structure100mm',storage=storage,sampler=optuna.samplers.TPESampler(seed=2911))
    if study.user_attrs['identity']!=identity:raise RuntimeError('study source/model mismatch')
    while sum(t.state.name=='COMPLETE' for t in study.trials)<24 and len(study.trials)<36:study.optimize(objective,n_trials=1)
    r=dict(status='PASS' if sum(t.state.name=='COMPLETE' for t in study.trials)>=24 else 'FAIL',identity=identity,total=len(study.trials),complete=sum(t.state.name=='COMPLETE' for t in study.trials),pruned=sum(t.state.name=='PRUNED' for t in study.trials),failed=sum(t.state.name=='FAIL' for t in study.trials),resumed=True,pareto=[dict(number=t.number,values=t.values,params=t.params,connector_indices=t.user_attrs['connector_indices']) for t in study.best_trials],scope='independent static FEM Optuna; NOT100mm grasp optimization; selected candidates still require fresh SOFA validation');write_json(out/'summary.json',r);print(r)
if __name__=='__main__':main()
