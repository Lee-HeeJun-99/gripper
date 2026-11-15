"""Matched actual trajectories: expose unexplained energy, never fit it away."""
import csv
import json
import numpy as np
from curve_common import OUT, sha, write_json


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    journal = OUT / 'transaction_journal_8s_v6'
    returns = OUT / 'return_journal_v4'
    target = OUT / 'matched_energy_decomposition_v4.json'
    if target.exists():
        raise ValueError('refuse overwritten energy evidence')
    for p in (journal, returns):
        s = json.loads((p / 'summary.json').read_text())
        if s['status'] != 'PASS' or any(s['instrumentation_state_difference'].values()):
            raise ValueError('exact trajectory equivalence required before matching diagnostics')
    a = rows(journal / 'energy.csv'); b = rows(returns / 'return.csv')
    posts = [r for r in a if r['stage'] == 'post_commit']
    initial = next(r for r in a if r['stage'] == 'begin')
    if len(posts) != len(b):
        raise ValueError('matched transaction count')
    plastic = np.cumsum([float(r['plastic']) for r in b])
    projection = np.cumsum([float(r['derived_endpoint_projection']) for r in b])
    detach = np.cumsum([float(r['detachment']) for r in b])
    layers = [rows(returns / ('layer' + str(i) + '.csv')) for i in range(3)]
    def stored(r):
        return sum(float(r[k]) for k in ('beam_U', 'layer_U', 'contact_U', 'K'))
    E0 = stored(initial); samples = []
    for j, layer in enumerate(zip(*layers)):
        step = 20 * (j + 1); r = posts[step-1]; q = b[step-1]
        if int(r['step']) != step or int(q['step']) != step or max(
                abs(float(x['time']) - float(r['time'])) for x in (*layer, q)) > 1e-10:
            raise ValueError('transaction times do not align')
        known_layer_loss = sum(float(x['dissipated']) for x in layer)
        energy_change = stored(r) - E0
        work = float(r['external_begin_force_work']) + float(r['actuator_begin_force_work'])
        damping = float(r['Rayleigh_mass_work']) + float(r['Rayleigh_stiffness_work'])
        velocity_projection = float(r['derived_velocity_projection_loss'])
        known_losses = damping + velocity_projection + plastic[step-1] + detach[step-1] + known_layer_loss
        raw = energy_change - work + known_losses
        beam_projection = float(r['derived_beam_quadratic_projection'])
        beam_remainder = float(r['beam_nonlinear_remainder'])
        layer_projection = float(r['layer_quadratic_projection'])
        normal_projection = float(r['normal_quadratic_projection'])
        layer_remainder = float(r['layer_nonlinear_or_return_remainder'])
        normal_remainder = float(r['normal_nonlinear_remainder'])
        euler_work=float(r['derived_actuator_Euler_work'])+float(r['derived_external_Euler_work'])
        remaining=raw+projection[step-1]+beam_projection+layer_projection+normal_projection
        samples.append(dict(time=float(r['time']), step=step, stored_change=energy_change,
                            external_and_actuator_work=work, rayleigh_work=damping,
                            velocity_projection=velocity_projection, contact_plastic=plastic[step-1],
                            contact_detachment=detach[step-1], layer_slider_loss=known_layer_loss,
                            tangent_endpoint_projection=projection[step-1],
                            derived_beam_quadratic_projection=beam_projection,
                            measured_beam_nonlinear_remainder=beam_remainder,
                            layer_quadratic_projection=layer_projection,
                            normal_quadratic_projection=normal_projection,
                            layer_nonlinear_or_return_remainder=layer_remainder,
                            normal_nonlinear_remainder=normal_remainder,
                            derived_active_Euler_work=euler_work,
                            begin_force_vs_Euler_active_work_difference=work-euler_work,
                            unexplained_without_tangent_projection=raw,
                            unexplained_with_tangent_projection=raw+projection[step-1],
                            unexplained_with_derived_beam_and_tangent_terms=raw+projection[step-1]+beam_projection,
                            unexplained_after_explicit_beam_remainder=raw+projection[step-1]+beam_projection-beam_remainder,
                            unexplained_after_derived_potential_terms=remaining-beam_remainder-layer_remainder-normal_remainder,
                            balance_with_derived_terms_and_Euler_active_work=remaining+work-euler_work,
                            balance_after_explicit_potential_remainders=remaining+work-euler_work-beam_remainder-layer_remainder-normal_remainder))
    write_json(target, dict(
        status='EXPERIMENTAL', global_energy='BLOCKED', actual_matched_steps=len(b),
        samples=samples, final=samples[-1],
        maximum_unexplained_without_tangent_projection=max(abs(r['unexplained_without_tangent_projection']) for r in samples),
        analysis_source_sha256=sha(__import__('pathlib').Path(__file__)),
        unknown_terms=['pressure parameter work not independently derived',
                       'material-to-global contact work and normal transport',
                       'non-Beam nonlinear stored-energy/linearized-Euler remainder'],
        excluded_storage=['RoutedCable virtual potential: actuator work is counted instead'],
        diagnostic_sources={str(p):sha(p) for p in (journal/'energy.csv', returns/'return.csv',
                            *(returns/('layer'+str(i)+'.csv') for i in range(3)))},
        scope='Two read-only actual SOFA journals have EXACT same X/V/R as the same '
              'uninterrupted baseline. Match their step20 boundaries. Unexplained '
              'residual is not numerical dissipation; neither variant certifies closure.'))
    print(samples[-1])


if __name__ == '__main__':
    main()
