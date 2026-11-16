"""Fresh, bounded independent vector-reference tests; never a SOFA gate."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from closure_validation_suite import logged
from curve_common import ROOT, sha, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--only',choices=['return','field','snapshot','conditioning','certificate','normalized','frame','outward','pullback'])
    parser.add_argument('--outward-normalized',action='store_true')
    args = parser.parse_args()
    if args.outward_normalized and args.only!='normalized':raise ValueError('explicit normalized reference scope required')
    if not args.tag.replace('_', '').isalnum():
        raise ValueError('simple unique campaign tag required')
    out = ROOT / 'results' / ('vector_history_' + args.tag)
    out.mkdir(exist_ok=False)
    paths = [ROOT / 'models/yield_front_history/VectorReturn.h',
             ROOT / 'tests/test_vector_return.cpp', Path(__file__).resolve()]
    for optional in ['models/yield_front_history/VectorField.h',
                     'tests/test_vector_field.cpp',
                     'models/contact_energy/SlipBandReference.h',
                     'models/yield_front_history/ScalarField.h',
                     'models/yield_front_history/AdaptiveSnapshot.h',
                     'tests/test_vector_snapshot.cpp',
                     'tests/test_vector_conditioning.cpp']:
        p = ROOT / optional
        if p.exists():
            paths.append(p)
    for name in ('models/yield_front_history/ExactInterval.h','tests/test_vector_certificate.cpp','models/yield_front_history/NormalizedSnapshot.h','tests/test_vector_normalized.cpp'):
        p=ROOT/name
        if p.exists():paths.append(p)
    paths.append(ROOT / 'models/yield_front_history/PolynomialFronts.h')
    if (ROOT/'tests/test_vector_frame.cpp').exists():paths.append(ROOT/'tests/test_vector_frame.cpp')
    for name in ('models/yield_front_history/OutwardPolynomial.h','tests/test_vector_outward.cpp'):
        if (ROOT/name).exists():paths.append(ROOT/name)
    for name in ('models/yield_front_history/MaterialDerivative.h','tests/test_vector_pullback.cpp','models/conservative_beam/EnergyKernel.h','models/conservative_beam/AutoDiff.h','models/finite_rotation/Kernel.h'):
        if (ROOT/name).exists():paths.append(ROOT/name)
    before={str(p.relative_to(ROOT)): sha(p) for p in paths}
    write_json(out / 'identity.json', dict(
        commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        sources=before,
        scope='independent fixed-patch vector reference; not SOFA/grasp certification'))
    for p in paths:
        target = out / 'sources' / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    stages = {}
    for name in ([args.only]if args.only else['return', 'field', 'snapshot']):
        source = ROOT / ('tests/test_vector_' + name + '.cpp')
        if not source.exists():
            continue
        binary = out / (name + '.bin')
        stages[name + '_build'] = logged(['g++', '-std=c++17', '-O2', '-ffp-contract=off',
            '-Wall', '-Wextra', '-Wpedantic', '-Werror', source, '-o', binary], out / (name + '_build'), 120)
        if stages[name + '_build']['exit_code']:
            break
        if before!={str(p.relative_to(ROOT)):sha(p)for p in paths}:
            stages['source_drift']=dict(exit_code=1,reason='source changed during compile;binary not accepted')
            break
        stages[name] = logged([binary]+(['outward']if args.outward_normalized else[]), out / name, 180)
        stages[name]['binary_sha256'] = sha(binary)
        if stages[name]['exit_code']:
            break
    write_json(out / 'summary.json', dict(status='PASS' if stages and all(
        x['exit_code'] == 0 for x in stages.values()) else 'FAIL', stages=stages,
        sofa='NOT RUN', global_energy='BLOCKED'))
    print(json.dumps(dict(out=str(out), stages={k:v['exit_code'] for k,v in stages.items()})))


if __name__ == '__main__':
    main()
