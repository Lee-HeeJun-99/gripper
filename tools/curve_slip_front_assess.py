"""Localize actual sampled return loss; never substitute samples for cycle integrals."""
import csv
import math
from collections import defaultdict
from curve_common import OUT, sha, write_json


def main():
    cases = {}
    for name in ('coarse24', 'history24'):
        path = OUT / 'slip_front' / name / 'points.csv'
        groups = defaultdict(list)
        with path.open() as stream:
            for raw in csv.DictReader(stream):
                row = {k: float(v) for k, v in raw.items()}
                if not all(math.isfinite(v) for v in row.values()):
                    raise ValueError('nonfinite actual point')
                if row['weighted_plastic'] < 0 or row['weight_mm'] <= 0:
                    raise ValueError('invalid return loss or material weight')
                if not math.isclose(row['weighted_plastic'], row['weight_mm'] * row['plastic_density'], rel_tol=1e-14, abs_tol=1e-40):
                    raise ValueError('inconsistent point integral')
                groups[row['time']].append(row)
        snapshots = []
        for time, rows in sorted(groups.items()):
            losses = sorted((r['weighted_plastic'] for r in rows), reverse=True)
            total = math.fsum(losses)
            cumulative = 0.0
            count95 = 0
            for loss in losses:
                if cumulative >= .95 * total:
                    break
                cumulative += loss
                count95 += 1
            positive = [r for r in rows if r['weighted_plastic'] > 0]
            snapshots.append(dict(time=time, active_points=len(rows), sliding_points=sum(r['sliding'] for r in rows), positive_loss_points=len(positive), points_for_95_percent=count95, participation_count=total**2 / math.fsum(x*x for x in losses) if total else 0, one_step_loss_Fmm=total, loss_sites=[dict(edge=int(r['edge']), material_mm=r['ideal_reference_mm'], weight_mm=r['weight_mm'], loss_Fmm=r['weighted_plastic']) for r in positive]))
        cases[name] = dict(source_sha256=sha(path), snapshots=snapshots)
    write_json(OUT / 'slip_front' / 'localization_v1.json', dict(status='PASS', scope='finite nonnegative actual read-only point diagnostics; NOT convergence approval. These are selected instantaneous increments, not complete cycle integrals.', cases=cases))
    for name, case in cases.items():
        print(name, [(r['time'], r['active_points'], r['positive_loss_points'], r['points_for_95_percent'], r['one_step_loss_Fmm']) for r in case['snapshots']])


if __name__ == '__main__':
    main()
