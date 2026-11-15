"""Actual public MBK/RHS/solution comparison at first resumed physical step."""
import numpy as np
from curve_checkpoint_common import CPROOT, OUT, chunk, merge_states, write_json
from trial_validation import read_states


def load(path):
    matrix = {}; rhs = {}; solution = {}
    with path.open() as f:
        size = int(next(f))
        for s in f:
            v = s.split()
            if v[0] == 'A':
                matrix[int(v[1]), int(v[2])] = float(v[3])
            elif v[0] == 'V':
                rhs[int(v[1])] = float(v[2]); solution[int(v[1])] = float(v[3])
            else:
                raise ValueError('unknown MBKS record')
    if len(rhs) != size:
        raise ValueError('incomplete MBKS diagnostic')
    return matrix, rhs, solution


def main():
    out = CPROOT / 'solver_probe_v4'; out.mkdir(exist_ok=False)
    source = OUT / 'grasp/n21'
    reference, _ = chunk(out / 'uninterrupted', source, 16000)
    first, _ = chunk(out / 'part1', source, 8000)
    second, _ = chunk(out / 'part2', source, 8000, input_checkpoint=first)
    a = load(reference.with_name(reference.name + '.MBKS'))
    b = load(second.with_name(second.name + '.MBKS'))
    errors = {}
    for label, u, v in zip(('matrix', 'rhs', 'solution'), a, b):
        keys = set(u) | set(v)
        errors[label] = max(abs(u.get(k, 0.) - v.get(k, 0.)) for k in keys)
    merge_states([out / 'part1', out / 'part2'], out / 'state.txt')
    u = read_states(out / 'uninterrupted/state.txt'); v = read_states(out / 'state.txt')
    if len(u) != len(v):
        raise ValueError('trajectory record count')
    state_errors = {k: float(np.max(np.abs(np.array([r[k] for r in u]) -
                                              np.array([r[k] for r in v]))))
                    for k in ('X', 'V', 'R')}
    write_json(out / 'summary.json', dict(
        status='EXPERIMENTAL', first_resumed_step=8001,
        public_linear_system_absolute_errors=errors, subsequent_state_errors=state_errors,
        scope='same frozen physical state/force/tangent; public actual assembled '
              'MBK/RHS/solution; not private engine-state edits or certified restart'))
    print(errors, state_errors)


if __name__ == '__main__':
    main()
