"""Actual Optuna campaign on the unchanged validated30mm model, NOT grasp."""
import json,os,subprocess,sys
from grasp_common import ROOT,OUT,write_json,sha,PYTHON

def main():
    import optuna
    out=OUT/'optuna_v2';out.mkdir(parents=True,exist_ok=False)
    storage='sqlite:///'+str(out/'mechanisms.sqlite3');study=optuna.create_study(study_name='failure_prune',storage=storage,sampler=optuna.samplers.RandomSampler(seed=11),pruner=optuna.pruners.ThresholdPruner(upper=0))
    def mechanism(trial):
        x=trial.suggest_float('x',0,1)
        if trial.number==1:raise RuntimeError('intentional smoke failure; no value')
        if trial.number==2:
            trial.report(x,0)
            assert trial.should_prune()
            raise optuna.TrialPruned('intentional pruning smoke')
        return x*x
    study.optimize(mechanism,n_trials=3,catch=(RuntimeError,));resumed=optuna.load_study(study_name='failure_prune',storage=storage)
    states=[t.state.name for t in resumed.trials];assert states==['COMPLETE','FAIL','PRUNED'] and resumed.trials[1].values is None
    def seed_samples():
        s=optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=11));return [s.ask().suggest_float('x',0,1) for _ in range(5)]
    assert seed_samples()==seed_samples()
    write_json(out/'mechanisms.json',dict(status='PASS',states=states,resume_count=len(resumed.trials),seed_reproducible=True,pruned_intermediate_value=resumed.trials[2].values,pruned_excluded_from_best=resumed.best_trial.number!=2,scope='API/failure injection only; Optuna stores last reported intermediate on PRUNED, never count it as a completed performance objective'))
    env=dict(os.environ,REGRIP_BUILD_ROOT=str(ROOT/'build/revalidation_20261114_final'),OPENBLAS_NUM_THREADS='1',PYTHONPATH=str(ROOT/'.python-deps/grasp')+':'+str(ROOT)+':'+str(ROOT/'tools'))
    records=[]
    for stage,count in [('smoke',3),('main',24)]:
        command=[PYTHON,'tools/optimize.py','--gate','results/revalidation_20261114T132734Z/physics_release/gate.json','--out',str(out/'actual'),'--study','validated_planar_20261115','--trials',str(count)]
        try:
            result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=900);code=result.returncode;log=result.stdout+result.stderr
        except subprocess.TimeoutExpired as exc:code=None;log=str(exc)
        (out/(stage+'.log')).write_text(log);records.append(dict(stage=stage,command=command,exit_code=code));write_json(out/'commands.json',records)
        if code!=0:raise RuntimeError(stage+' failed; inspect preserved log')
    actual=optuna.load_study(study_name='validated_planar_20261115',storage='sqlite:///'+str(out/'actual/study.sqlite3'))
    r=dict(status='PASS',optuna_version=optuna.__version__,total_trials=len(actual.trials),complete=sum(t.state.name=='COMPLETE' for t in actual.trials),pruned=sum(t.state.name=='PRUNED' for t in actual.trials),failed=sum(t.state.name=='FAIL' for t in actual.trials),pareto=[dict(number=t.number,values=t.values,params=t.params,attrs=t.user_attrs) for t in actual.best_trials],scope='unchanged validated30mm planar stiffness/slip only; grasp objectives BLOCKED',optimizer_sha256=sha(ROOT/'tools/optimize.py'))
    write_json(out/'summary.json',r);print(r)

if __name__=='__main__':main()
