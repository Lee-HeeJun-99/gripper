"""Immutable cohort index; integrity is never physics certification."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from curve_common import ROOT,sha,write_json

COHORTS=['autonomous_20261116_curve_a01','autonomous_20261116_curve_native_a01',
         'autonomous_20261116_full_native_a01','autonomous_20261116_scalar_a01',
         'autonomous_20261116_checkpoint_a01',
         'autonomous_20261116_diagnostics_checks_a01','autonomous_20261116_diagnostics_checks_a02',
         'autonomous_20261116_diagnostics_checks_a03','autonomous_20261116_diagnostics_checks_a04',
         'autonomous_20261116_diagnostics_checks_a05']


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    p=argparse.ArgumentParser();p.add_argument('--version',default='v1');p.add_argument('--verify',action='store_true');p.add_argument('--include-compensation',action='store_true');p.add_argument('--include-continuation',action='store_true');args=p.parse_args()
    if not args.version.isalnum():raise ValueError('simple immutable version name required')
    manifest=ROOT/'reports'/('CURVED_RESEARCH_EVIDENCE_MANIFEST_'+args.version.upper()+'.json')
    if args.verify:
        d=json.loads(manifest.read_text());errors=[]
        for name,h in d['files'].items():
            q=ROOT/name
            if not q.is_file()or sha(q)!=h:errors.append(name)
        for name,h in d['committed_source_blobs'].items():
            if hashlib.sha256(git('show',d['source_checkpoint']+':'+name)).hexdigest()!=h:errors.append('git_blob:'+name)
        print(json.dumps(dict(status='FAIL'if errors else'PASS',checked_artifacts=len(d['files']),checked_source_blobs=len(d['committed_source_blobs']),errors=errors,scope='integrity only')))
        if errors:raise SystemExit(1)
        return
    if manifest.exists():raise ValueError('refuse overwritten evidence index')
    cohorts=list(COHORTS)
    if args.include_compensation:
        comp=ROOT/'results/autonomous_20261116_beam_compensation_a01'
        status=json.loads((comp/'refinement_status.json').read_text())
        if any('full_'+n not in status for n in('mesh41_half','history_fine_half','mesh11_half'))or not(comp/'energy_after_arithmetic_48000_v9/summary.json').exists():raise ValueError('cohort still active;do not hash writing files')
        cohorts.append(comp.name)
    if args.include_continuation:
        cohorts += ['autonomous_20261116_fixed_clock_a01', 'autonomous_20261116_event_clock_a01', 'autonomous_20261116_phase_grid_a01']
        cohorts += ['autonomous_20261116_diagnostics_checks_a0'+str(i) for i in (6,7,8,9)]
        phase=ROOT/'results/autonomous_20261116_phase_grid_a01'
        for case in ('slip_front/coarse24','slip_front/history24','energy_v15_coarse_4s','energy_v15_fine_4s','energy_v15_fine_8s','energy_v15_fine_24s','history1000nm_prefix82_v1','history1000nm_full24_v1','patch_refinement_v2/uniform_profile4','patch_refinement_v2/local625_profile4','patch_refinement_v2/local312_profile4','patch_refinement_v2/local625_prefix82','patch_refinement_v2/local312_prefix82','patch_refinement_v2/invariants'):
            if not(phase/case/'summary.json').is_file():raise ValueError('continuation still active '+case)
    for name in cohorts:
        if not(ROOT/'results'/name).is_dir():raise ValueError('missing evidence cohort '+name)
    dest=ROOT/'reports/curved_evidence'/args.version;dest.mkdir(parents=True,exist_ok=False)
    source_paths=git('ls-files','models/curved_contact','models/beam_translation_compensation','models/contact_energy','models/fixed_step_clock','models/event_step_clock','diagnostics/curved_contact','diagnostics/physics_checkpoint','diagnostics/contact_return_energy','diagnostics/transaction_energy','diagnostics/damping_matrix','diagnostics/slip_front','tools/curve_*.py','tests/test_curved*','tests/test_checkpoint_guards.py','tests/test_energy_source_scope.py','tests/test_return*','tests/test_pressure_return_energy.cpp','tests/test_beam_translation_compensation.cpp','tests/test_phase*','tests/test_local_history_guards.py','tests/test_slip_band.cpp','tests/test_contact_work*','tests/test_damping_inference.py','tests/test_event_clock.cpp','tests/test_fixed_clock.cpp','tests/test_contact_rayleigh.cpp').decode().splitlines()
    source_paths+=git('ls-files','models/patch_refined_contact','diagnostics/patch_refined_contact','diagnostics/patch_invariants','tests/test_patch_source_proof.py','tests/test_patch_log_guards.py').decode().splitlines()
    changed=git('diff','HEAD','--name-only','--',*source_paths).decode().splitlines()
    if changed:raise ValueError('commit source before sealing '+repr(changed))
    commit=git('rev-parse','HEAD').decode().strip()
    blobs={n:hashlib.sha256(git('show',commit+':'+n)).hexdigest()for n in source_paths}
    compact={};files=[]
    for name in cohorts:
        campaign=ROOT/'results'/name;files.extend(p for p in campaign.rglob('*')if p.is_file())
        decisions=list(campaign.glob('grasp/*/metrics.json'))+list(campaign.glob('*/metrics.json'))+list(campaign.glob('*/summary.json'))+list(campaign.glob('patch_refinement_v2/*/summary.json'))
        for path in decisions:
            r=json.loads(path.read_text());c=r.get('config',{})
            compact[str(path.relative_to(ROOT))]=dict(
                metrics={k:r.get(k)for k in('status','bounded_hold_pass','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','recovery_pass','friction_dissipation','process','checks','failure_reason')},
                config={k:c.get(k)for k in('nodes','history','dt','duration','profile_only','layout_policy','mass_quadrature','solver_template','integration_arithmetic')},
                declared_scope=r.get('scope'),physics_scope='actual individual scope ONLY;not12wrench/global energy/real material certificate;v1patch local profile PASSs are invalidated in PATCH_V1_INVALIDATION.json')
    write_json(dest/'actual_trials.json',compact)
    # Index actual selected executables/generated sources/manifests,not caches.
    for folder in(ROOT/'build').glob('autonomous_20261116*'):
        for path in folder.rglob('*'):
            if path.is_file()and(path.suffix in('.so','.inc')or path.name.endswith('manifest.json')or(path.suffix==''and path.name in('physics_checkpoint','transaction_journal','contact_return_journal','curved_api','curved_invariants','slip_front_probe','damping_matrix_probe','patch_api','patch_invariants'))):files.append(path)
    files.append(dest/'actual_trials.json')
    if args.include_continuation:files.extend(ROOT/'reports/curved_evidence'/n for n in('PATCH_V1_INVALIDATION.json','implementation_failures.json'))
    hashes={str(path.relative_to(ROOT)):sha(path)for path in sorted(set(files))}
    write_json(manifest,dict(schema=1,source_checkpoint=commit,branch=git('branch','--show-current').decode().strip(),cohorts=cohorts,files=hashes,committed_source_blobs=blobs,scope='Immutable raw/source/build integrity cohort;current working-tree evolution does not rewrite historical Git blobs;NO physics success inferred;future added files are outside this cohort',physics_status='FAIL/EXPERIMENTAL;see individual unchanged gates',raw_bytes=sum((ROOT/n).stat().st_size for n in hashes if n.startswith('results/'))))
    print('indexed',len(hashes),'artifacts and',len(blobs),'committed source blobs')


if __name__=='__main__':main()
