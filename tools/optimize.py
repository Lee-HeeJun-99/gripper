"""Optuna Pareto search, gated by actual SOFA validation. dt is never sampled."""
import argparse
import json
from pathlib import Path
import sys
import datetime
import math
import hashlib
from run_trial import ROOT, run_trial, sha
from verification_common import BUILD,assert_build_current
from trial_validation import verify_artifacts


def validate_gate(gate_path):
    assert_build_current()
    gate_path=Path(gate_path)
    gate=json.loads(gate_path.read_text())
    if gate.get('passed') is not True or len(gate.get('checks',{}))<45 or not all(gate['checks'].values()):
        raise RuntimeError('physics gate failed or incomplete')
    required={'tools/run_trial.py','tools/trial_validation.py','plugin/src/TangentialRigidForceField.cpp','tools/native_scene.py'}
    if not required.issubset(gate.get('source_sha256',{})):raise RuntimeError('gate lacks required source fingerprints')
    for path,digest in gate['source_sha256'].items():
        if sha(ROOT/path)!=digest:raise RuntimeError('source changed since validation: '+path)
    for key,path in [('plugin_sha256',BUILD/'plugin/bin/libSofaTangentialV110.so'),
                     ('diagnostics_sha256',BUILD/'diagnostics/libReGripDiagnostics.so')]:
        if gate[key]!=sha(path):raise RuntimeError('binary changed since validation: '+key)
    for name,digest in gate.get('run_metrics_sha256',{}).items():
        if sha(gate_path.parent/name/'metrics.json')!=digest:raise RuntimeError('changed metrics: '+name)
        verify_artifacts(gate_path.parent/name)
    return gate


def objective_values(off,on):
    if any(r.get('status')!='complete' or not r.get('equilibrium_validated') for r in (off,on)):
        raise ValueError('non-equilibrium results have no objective value')
    for key in ('load','n','length_mm','layer_thickness_mm','young_modulus','poisson_ratio','total_mass'):
        if off['config'][key]!=on['config'][key]:raise ValueError('OFF/ON physical conditions differ: '+key)
    tip=on['tip_deflection_mm'];reference=off['tip_deflection_mm']
    if not all(math.isfinite(v) for v in (tip,reference,on['max_x_slip_mm'],off['max_x_slip_mm'])) or reference<=0 or off['max_x_slip_mm']<=0:
        raise ValueError('nonfinite or invalid reference metrics')
    if tip<=0 or tip>reference*1.001 or on['max_x_slip_mm']<0:raise ValueError('invalid stiffness/slip response')
    return reference/tip,on['max_x_slip_mm']/off['max_x_slip_mm']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials',type=int,default=24)
    parser.add_argument('--study',default='regrip_native_v1')
    parser.add_argument('--out',type=Path,default=ROOT/'results/optimization')
    parser.add_argument('--gate',type=Path,default=ROOT/'results/physics_validation/gate.json')
    args=parser.parse_args()
    if args.trials<1:parser.error('--trials must be positive')
    session=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    gate_path=args.gate
    if not gate_path.exists():
        raise RuntimeError('physics gate is missing; run validate_physics.py first')
    gate=validate_gate(gate_path)
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
    identity=dict(plugin_sha256=gate['plugin_sha256'],diagnostics_sha256=gate['diagnostics_sha256'],
                  source_sha256=gate['source_sha256'],optimizer_sha256=sha(Path(__file__)))
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
        signature=hashlib.sha256(json.dumps([k,connectors]).encode()).hexdigest()
        if any(t.user_attrs.get('design_sha256')==signature and t.user_attrs.get('validation_passed') for t in study.trials):
            raise optuna.TrialPruned('duplicate physical design')
        trial.set_user_attr('design_sha256',signature)
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
        ratio,slip=objective_values(off,results[0])
        trial.set_user_attr('validation_passed',True)
        trial.set_user_attr('raw_metrics',str(base/'on/metrics.json'))
        trial.set_user_attr('metrics_sha256',sha(base/'on/metrics.json'))
        return ratio,slip

    study.optimize(objective,n_trials=args.trials)
    candidates=[]
    for trial in study.best_trials:
        if not trial.user_attrs.get('validation_passed'):
            continue
        c=trial.user_attrs['connector_indices'];k=trial.params['shear_stiffness']
        directory=args.out/f'pareto_{trial.number:05d}_{session}'
        fine=run_trial(directory/'mesh_refine',k=k,n=21,connectors=[2*i for i in c])
        repeat=run_trial(directory/'independent_repeat',k=k,connectors=c)
        metric_path=Path(trial.user_attrs['raw_metrics'])
        if sha(metric_path)!=trial.user_attrs['metrics_sha256']:raise RuntimeError('Pareto metrics changed')
        base=verify_artifacts(metric_path.parent)
        mesh_ok=(fine['status']=='complete' and repeat['status']=='complete'
                 and abs(fine['tip_deflection_mm']/base['tip_deflection_mm']-1)<.01
                 and abs(repeat['tip_deflection_mm']/base['tip_deflection_mm']-1)<1e-10)
        if mesh_ok:
            candidates.append(dict(trial=trial.number,k=k,connector_indices=c,positions_mm=[3*i for i in c],
                                   stiffness_ratio=trial.values[0],normalized_slip=trial.values[1],
                                   mesh_validated=True))
    (args.out/'pareto_candidates.json').write_text(json.dumps(candidates,indent=2))
    (args.out/'status.json').write_text(json.dumps(dict(status='complete',total_trials=len(study.trials),
           valid_pareto_count=len(candidates),scope=gate['scope'],global_optimum_claimed=False),indent=2))
    return 0


if __name__=='__main__':sys.exit(main())
