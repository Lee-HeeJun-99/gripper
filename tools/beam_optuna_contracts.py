"""Actual SQLite/failed/pruned/seed checks on the independent structural model."""
import sqlite3
from beam_common import OUT,write_json,material
from models.conservative_beam.linear_reference import solve
def main():
    import optuna
    out=OUT/'optuna_contracts';out.mkdir(exist_ok=False);m=material();base=dict(EA=m['EA'],GA=m['GAz'],EI=m['EIy']);free=solve(**base);samples=[]
    for name in ('a','b'):
        storage='sqlite:///'+str(out/(name+'.sqlite3'));s=optuna.create_study(study_name=name,storage=storage,directions=['maximize','minimize'],sampler=optuna.samplers.TPESampler(seed=2911));params=[]
        def objective(t):
            k=t.suggest_float('k',.001,100,log=True);params.append(k);r=solve(k=k,connectors=tuple(range(1,11)),**base);return free['tip_deflection_mm']/r['tip_deflection_mm'],r['max_slip_mm']
        s.optimize(objective,n_trials=3);samples.append(params);s=optuna.load_study(study_name=name,storage=storage)
        if name=='a':
            def fail(t):raise ValueError('intentional invalid physical trial')
            def prune(t):raise optuna.TrialPruned('intentional pre-evaluation gate')
            s.optimize(fail,n_trials=1,catch=(ValueError,));s.optimize(prune,n_trials=1);trials=s.trials
            with sqlite3.connect(out/(name+'.sqlite3')) as db:integrity=db.execute('pragma integrity_check').fetchone()[0]
            checks=dict(three_complete=sum(t.state.name=='COMPLETE' for t in trials)==3,failed_has_no_values=trials[3].state.name=='FAIL' and trials[3].values is None,pruned_has_no_values=trials[4].state.name=='PRUNED' and trials[4].values is None,resumed=len(trials)==5,sqlite_integrity=integrity=='ok',pareto=bool(s.best_trials))
    checks['seed_reproducible']=samples[0]==samples[1];write_json(out/'summary.json',dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,seed_samples=samples,scope='independent linear-FEM objectives; manual pre-evaluation TrialPruned, NOT an intermediate multiobjective pruning algorithm; restart and fresh seeded studies are different guarantees'));print(checks)
if __name__=='__main__':main()
