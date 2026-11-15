"""One explicitly profiled wall-time exception, not a relaxed physical gate."""
import json
from curve_common import OUT, write_json
from curve_trial import run


def main():
    previous = json.loads((OUT / 'canonical_completed.json').read_text())
    p = previous['profile_quarterdt']
    if p['status'] != 'EXPERIMENTAL' or p['process']['exit_code']:
        raise ValueError('completed actual quarter-step profile required')
    prediction = p['process']['runtime_s'] * 18 / 4
    wall = 1320
    if prediction * 1.1 > wall:
        raise ValueError('profile no longer fits the one-off resource allowance')
    path = OUT / 'quarterdt_exception_decision.json'
    if path.exists():
        raise ValueError('refuse a second attempt or overwritten decision')
    write_json(path, dict(
        status='EXPERIMENTAL', attempts=1, wall_seconds=wall,
        prediction_seconds=prediction, prediction_margin=1.1,
        memory_bytes=4294967296, maximum_long_children=4,
        previous_decision=previous['full_quarterdt'],
        reason='Actual 4s profile predicts1164s; one1320s uninterrupted run replaces '
               'unqualified restart. Checkpoint v2/v3 force and tangent restore exactly '
               'but subsequent path fails equivalence. User resource policy permits '
               'finite profile-justified exceptions; physical dt/history/solver/gates unchanged.'))
    result = run('quarterdt_exception', nodes=21, dt=.000125, fixed_layout=True,
                 tributary_mass=True, wall=wall)
    write_json(OUT / 'quarterdt_exception_result.json', dict(
        status=result['status'], process=result['process'],
        local_hold=result.get('bounded_hold_pass'),
        scope='one uninterrupted18s actual SOFA run; assess time/loss convergence separately'))


if __name__ == '__main__':
    main()
