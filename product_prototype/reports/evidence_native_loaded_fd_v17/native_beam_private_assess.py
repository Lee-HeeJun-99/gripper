"""Partition measured PRIVATE native forces; no accepted-state/PASS synthesis."""
import argparse,csv,json,re
from pathlib import Path
import numpy as np
from native_bending_coupon import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases={};fd=[]
    for label,name in [('linear','native_beam_private_force442'),('second_order','native_beam_second_order444')]:
        folder=BASE/'results'/name;data=json.loads((folder/'summary.json').read_text());rows=data['records']
        if not all(r['status']=='PRIVATE_FORCE_QUERY_ONLY' and all(e==0 for e in r['actual_state_error'].values()) and r['actual_times_identical'] for r in rows):raise ValueError('Invalid private query or changed actual state')
        x=np.log([r['scale'] for r in rows]);cases[label]=dict(source_summary_sha256=sha(folder/'summary.json'),
            fitted_axial_amplitude_exponent=float(np.polyfit(x,np.log([r['free_axial_residual_N'] for r in rows]),1)[0]),
            fitted_transverse_amplitude_exponent=float(np.polyfit(x,np.log([r['free_transverse_residual_N'] for r in rows]),1)[0]),records=rows)
        for row in csv.DictReader((folder/'scale_1/native').open()):
            fd.append(dict(reference=label,epsilon=float(row['epsilon']),
                force_relative=float(row['force_error_N'])/float(row['force_derivative_norm_N']),
                torque_relative=float(row['torque_error_Nm'])/float(row['torque_derivative_norm_Nm'])))
    native=[]
    for name in ('native_rectangular_ls_zero443','native_rectangular_small_load445'):
        log=(BASE/'results'/name/'21/process/stdout.log').read_text()
        residual=[float(x) for x in re.findall(r'\* Residual norm = ([\deE.+-]+)',log)]
        native.append(dict(case=name,status='FAIL_PRESERVED',reported_residual_trace=residual,
            reported_min_residual=min(residual) if residual else None,precision='native printLog rounded;not full-precision force inventory',
            log_sha256=sha(BASE/'results'/name/'21/process/stdout.log')))
    result=dict(scope='PRIVATE native force/kinematics diagnostics;NOT equilibrium,trajectory,physical heat or B3 promotion',
        producer_sha256=sha(Path(__file__)),cases=cases,private_FD=fd,native_plans=native,
        second_order_axial_reduction_at_scale1=cases['linear']['records'][0]['free_axial_residual_N']/cases['second_order']['records'][0]['free_axial_residual_N'],
        gate='NO_LOADED_OR_GRASP_PASS;actual zero-load state identity only')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axis=plt.subplots(figsize=(7,4))
    for label,data in cases.items():
        rows=data['records'];axis.loglog([r['scale'] for r in rows],[r['free_axial_residual_N'] for r in rows],'o-',label=label+' axial native residual')
    rows=cases['second_order']['records'];axis.loglog([r['scale'] for r in rows],[r['coordinate_representation_force_error_N'] for r in rows],'s--',label='second-order coordinate representation error (not a bound)')
    axis.axhline(1e-12,color='k',linestyle=':',label='unchanged force gate')
    axis.set_xlabel('PRIVATE reference amplitude / load scale (NOT dt)');axis.set_ylabel('Force norm [N]')
    axis.set_title('Native force at PRIVATE reference;NOT actual loaded states');axis.legend(fontsize=7);fig.tight_layout();fig.savefig(out/'PRIVATE_reference_force_scaling.png',dpi=160);plt.close(fig)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(output=str(out),linear_exponents=[cases['linear']['fitted_axial_amplitude_exponent'],cases['linear']['fitted_transverse_amplitude_exponent']],second_order_reduction=result['second_order_axial_reduction_at_scale1'],native=[dict(case=r['case'],reported_min=r['reported_min_residual']) for r in native])))

if __name__=='__main__':main()
