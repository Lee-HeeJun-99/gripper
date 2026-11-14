"""Optuna Pareto search, gated by actual SOFA validation. dt is never sampled."""
import argparse
import json
from pathlib import Path
import sys
import datetime
from run_trial import ROOT, run_trial, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials',type=int,default=24)
    parser.add_argument('--study',default='regrip_native_v1')
    parser.add_argument('--out',type=Path,default=ROOT/'results/optimization')
    args=parser.parse_args()
    session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    gate_path=ROOT/'results/physics_validation/gate.json'
    if not gate_path.exists():
        raise RuntimeError('physics gate is missing; run validate_physics.py first')
    gate=json.loads(gate_path.read_text())
    if not gate['passed']:
        raise RuntimeError('physics gate failed; optimization is prohibited')
    for path,digest in gate.get('source_sha256',{}).items():
        if sha(ROOT/path)!=digest:
            raise RuntimeError('source changed since validation: '+path)
    for key,path in [('plugin_sha256',ROOT/'build/plugin/bin/libSofaTangentialV110.so'),
                     ('diagnostics_sha256',ROOT/'build/diagnostics/libReGripDiagnostics.so')]:
        if gate[key]!=sha(path):
            raise RuntimeError('validation does not cover current binary: '+key)
    args.out.mkdir(parents=True,exist_ok=True)
    try:
        import optuna
    except ImportError:
        (args.out/'status.json').write_text(json.dumps(dict(status='blocked',reason='Optuna is not installed',
            trials_executed=0,best_parameters=None),indent=2))
        print('BLOCKED: Optuna is not installed. No optimization trials or optimum were produced.',file=sys.stderr)
        return 1
    # Existing compatible studies can resume; incompatible binary hashes get a separate study.
    study=optuna.create_study(study_name=args.study,storage='sqlite:///'+str((args.out/'study.sqlite3').resolve()),
            load_if_exists=True,directions=['maximize','minimize'],sampler=optuna.samplers.TPESampler(seed=11))
    identity=dict(plugin_sha256=gate['plugin_sha256'],diagnostics_sha256=gate['diagnostics_sha256'])
    old=study.user_attrs.get('validated_identity')
    if old is not None and old!=identity:
        raise RuntimeError('study belongs to different validated binaries; use a new study')
    study.set_user_attr('validated_identity',identity)
    study.set_user_attr('scope',gate['scope'])
    off=run_trial(args.out/f'off_run_{session}',k=0)
    if off['status']!='complete':
        raise RuntimeError('OFF reference has not reached equilibrium')
    off_tip,off_slip=off['tip_deflection_mm'],off['max_x_slip_mm']

    def objective(trial):
        k=trial.suggest_float('shear_stiffness',.01,100,log=True)
        count=trial.suggest_int('connector_count',1,10)
        # Rank 10 legal mesh locations to sample a count-constrained subset.
        ranks=[(trial.suggest_float(f'location_rank_{i}',0,1),i) for i in range(1,11)]
        connectors=sorted(i for _,i in sorted(ranks,reverse=True)[:count])
        trial.set_user_attr('connector_indices',connectors)
        trial.set_user_attr('positions_mm',[3*i for i in connectors])
        base=args.out/f'trial_{trial.number:05d}'
        results=[run_trial(base/'on',k=k,connectors=connectors),
                 run_trial(base/'on_dt_half',k=k,connectors=connectors,dt=.00025),
                 run_trial(base/'on_extended',k=k,connectors=connectors,duration=6)]
        if any(r['status']!='complete' for r in results):
            trial.set_user_attr('failure_reason','unstable or unconverged SOFA experiment')
            raise optuna.TrialPruned('invalid physics; no performance value assigned')
        tip=results[0]['tip_deflection_mm']
        if any(abs(r['tip_deflection_mm']/tip-1)>.001 for r in results[1:]):
            raise optuna.TrialPruned('dt or duration convergence failed')
        # Same mesh/material/load; setting k=0 removes all connector energy.
        # OFF configuration is therefore independent of selected connector subset.
        if tip<=0 or tip>off_tip*1.001:
            raise optuna.TrialPruned('invalid stiffness response')
        ratio=off_tip/tip
        slip=results[0]['max_x_slip_mm']/off_slip
        trial.set_user_attr('validation_passed',True)
        trial.set_user_attr('raw_metrics',str(base/'on/metrics.json'))
        return ratio,slip

    study.optimize(objective,n_trials=args.trials)
    candidates=[]
    for trial in study.best_trials:
        if not trial.user_attrs.get('validation_passed'):
            continue
        c=trial.user_attrs['connector_indices'];k=trial.params['shear_stiffness']
        directory=args.out/f'pareto_{trial.number:05d}_{session}'
        fine=run_trial(directory/'mesh_refine',k=k,n=21,connectors=[2*i for i in c])
        base=json.loads(Path(trial.user_attrs['raw_metrics']).read_text())
        mesh_ok=fine['status']=='complete' and abs(fine['tip_deflection_mm']/base['tip_deflection_mm']-1)<.01
        if mesh_ok:
            candidates.append(dict(trial=trial.number,k=k,connector_indices=c,positions_mm=[3*i for i in c],
                                   stiffness_ratio=trial.values[0],normalized_slip=trial.values[1],
                                   mesh_validated=True))
    (args.out/'pareto_candidates.json').write_text(json.dumps(candidates,indent=2))
    (args.out/'status.json').write_text(json.dumps(dict(status='complete',total_trials=len(study.trials),
           valid_pareto_count=len(candidates),scope=gate['scope'],global_optimum_claimed=False),indent=2))
    return 0


if __name__=='__main__':sys.exit(main())
