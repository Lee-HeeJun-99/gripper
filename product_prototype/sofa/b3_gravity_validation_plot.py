"""Static figures from actual accepted Native states;not concept geometry."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);fig,ax=plt.subplots(3,1,figsize=(9,10),layout='constrained');inputs=[]
    for case,label in [('b3_linear_gravity_coupon1162','Native field-Rayleigh'),('b3_linear_gravity_ode1166','Native ODE-Rayleigh')]:
        src=BASE/'results'/case;file=src/'states.csv';inputs.append(file);rows=list(csv.DictReader(file.open()));mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);ids=np.flatnonzero(local[:,0]==100);q=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);t=[float(r['time_s']) for r in rows];ax[0].plot(t,q[:,ids,2].mean(axis=1)*1000,label=label)
    ax[0].set(ylabel='Actual width-mean tip Z (mm)',title='Accepted Native linear coupon states; no Cable/contact/Guide')
    for case,label in [('b3_linear_gravity_assess1163','Field: physical-damping assumption FAIL'),('b3_linear_gravity_ode_assess1167','ODE: discrete identity ONLY')]:
        file=BASE/'results'/case/'trace.json';inputs.append(file);rows=json.loads(file.read_text());ax[1].semilogy([r['time_s'] for r in rows],[r['native_v_vs_discrete']['relative']*100 for r in rows],label=label)
    ax[1].axhline(.1,color='black',linestyle='--',label='0.1% gate');ax[1].set(ylabel='Velocity relative difference (%)',title='Unfloored comparison; NOT continuous-time convergence')
    file=BASE/'results/b3_linear_energy_contract1171/b3_linear_gravity_ode1166.json';inputs.append(file);rows=json.loads(file.read_text());t=[r['time_s'] for r in rows]
    for key,label in [('backward_Euler_numerical_loss_J','Reference BE numerical loss'),('reference_velocity_damping_work_J','Reference viscous work')]:ax[2].plot(t,[r[key]*1e9 for r in rows],label=label)
    ax[2].set(ylabel='Model-derived cumulative work (nJ)',title='Quadratic linear reference only; NOT measured heat or full Native energy')
    for panel in ax:panel.set_xlabel('Physical time (s)');panel.grid(alpha=.3);panel.legend(fontsize=8)
    fig.savefig(out/'actual_native_gravity_validation.png',dpi=150);fig.savefig(out/'actual_native_gravity_validation.svg');plt.close(fig);d=dict(status='ACTUAL_STATE_REFERENCE_FIGURES_ONLY',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in inputs});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
