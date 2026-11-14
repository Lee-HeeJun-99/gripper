"""Report the strongest tested sweep case, without calling it an optimum."""
import json
from baseline_regression import ROOT


def main():
    root=ROOT/'results/physics_validation'
    gate=json.loads((root/'gate.json').read_text())
    if not gate['passed']:raise RuntimeError('physics validation failed')
    free=json.loads((root/'free/metrics.json').read_text())
    candidates=[]
    for name in ('k001','k01','k1','k10','k100'):
        r=json.loads((root/name/'metrics.json').read_text())
        if r['status']=='complete':candidates.append(r)
    best=max(candidates,key=lambda r:r['effective_stiffness'])
    output=dict(status='best_fixed_sweep_case_only',is_optuna_result=False,is_global_optimum=False,
                k=best['config']['k'],connector_count=10,connector_indices=list(range(1,11)),
                positions_mm=list(range(3,31,3)),dt_numerical_verification_only=.0005,
                tip_deflection_mm=best['tip_deflection_mm'],max_x_slip_mm=best['max_x_slip_mm'],
                stiffness_ratio=best['effective_stiffness']/free['effective_stiffness'],
                slip_reduction_percent=100*(1-best['max_x_slip_mm']/free['max_x_slip_mm']),
                relative_equilibrium_residual=best['relative_residual'],
                source='results/physics_validation/k100/metrics.json',
                limitation='Equivalent circular beam, small planar rotations; no pressure mapping')
    (ROOT/'reports/best_tested_candidate.json').write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
