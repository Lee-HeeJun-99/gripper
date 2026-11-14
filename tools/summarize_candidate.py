"""Report the strongest tested sweep case, without calling it an optimum."""
import json
import argparse
from baseline_regression import ROOT
from pathlib import Path
from optimize import validate_gate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,default=ROOT/'results/physics_validation')
    parser.add_argument('--out',type=Path,default=ROOT/'reports/revalidated_sweep_candidate.json')
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('refusing existing candidate report')
    root=args.results
    validate_gate(root/'gate.json')
    free=json.loads((root/'free/metrics.json').read_text())
    candidates=[]
    for name in ('k001','k01','k1','k10','k100'):
        r=json.loads((root/name/'metrics.json').read_text())
        if r['status']=='complete':candidates.append((name,r))
    name,best=max(candidates,key=lambda item:item[1]['effective_stiffness'])
    n=best['config']['n'];indices=best['config']['connectors'] or list(range(1,n))
    output=dict(status='best_fixed_sweep_case_only',is_optuna_result=False,is_global_optimum=False,
                k=best['config']['k'],connector_count=len(indices),connector_indices=indices,
                positions_mm=[30*i/(n-1) for i in indices],dt_numerical_verification_only=best['config']['dt'],
                tip_deflection_mm=best['tip_deflection_mm'],max_x_slip_mm=best['max_x_slip_mm'],
                stiffness_ratio=best['effective_stiffness']/free['effective_stiffness'],
                slip_reduction_percent=100*(1-best['max_x_slip_mm']/free['max_x_slip_mm']),
                relative_equilibrium_residual=best['relative_residual'],
                source=str(root/name/'metrics.json'),
                limitation='Equivalent circular beam, small planar rotations; no pressure mapping')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
