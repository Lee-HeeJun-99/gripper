"""Independent sphere normal reference on actual NEW-grid 13.99s states."""
import json
import numpy as np
import scipy
from curve_common import ROOT, OUT, sha, write_json
from curve_normal_reference import check
from trial_validation import read_states


def main():
    target = OUT / 'normal_reference_phase_v1.json'
    if target.exists():
        raise ValueError('immutable evidence already exists')
    results = {}
    for name in ('full_coarse', 'full_fine', 'full_coarse_n41', 'full_coarse_history1250nm'):
        path = OUT / name
        states = read_states(path / 'state.txt')
        state = min(states, key=lambda row: abs(row['time'] - 13.99))
        if abs(state['time'] - 13.99) > 1e-9:
            raise ValueError('actual matching normal-reference epoch missing')
        result = check(path)
        if abs(result['actual_time'] - state['time']) > 1e-9:
            raise ValueError('observer/reference time mismatch')
        result['raw_sha256'] = {filename: sha(path / filename) for filename in ('config.json', 'state.txt', 'contact.csv')}
        results[name] = result
    write_json(target, dict(status='PASS' if all(row['status']=='PASS' for row in results.values()) else 'FAIL', numpy=np.__version__, scipy=scipy.__version__, reference_source_sha256=sha(ROOT/'tools/curve_normal_reference.py'), runner_source_sha256=sha(ROOT/'tools/curve_phase_normal.py'), results=results, scope='independent normal integration at actual frozen geometry;NOT friction-history/dynamics certification'))
    print({name: row['relative_cpp_quadrature_error'] for name, row in results.items()})


if __name__ == '__main__':
    main()
