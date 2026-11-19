"""Independent algebra on measured initial native matrices,NOT accepted states."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.linalg import solve
from native_bending_coupon import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    source=BASE/'results/native_beam_reference_precision439/flat_straight0_observed'
    K=np.zeros((126,126))
    for row in csv.DictReader((source/'native.dforce.csv').open()):K[int(row['i']),int(row['j'])]=float(row['K'])
    F=np.zeros(126);F[-4]=-1e-6;u=np.zeros(126);u[12:]=solve(K[12:,12:],F[12:],assume_a='sym')
    residual=(K@u-F).reshape(-1,6);q=np.column_stack([np.linspace(0,.1,21),np.zeros(21),np.zeros(21)])
    reaction=residual[:2];total_F=F.reshape(-1,6).sum(axis=0)[:3]+reaction[:,:3].sum(axis=0)
    torque=np.cross(q,F.reshape(-1,6)[:,:3]).sum(axis=0)+F.reshape(-1,6)[:,3:].sum(axis=0)
    torque+=np.cross(q[:2],reaction[:,:3]).sum(axis=0)+reaction[:,3:].sum(axis=0)
    reference=1e-6*.095**3/(3*250e6*(.002*.0005**3/12));work=float(F@u);energy=float(.5*u@K@u)
    np.savez(out/'PRIVATE_LINEAR_REFERENCE_NOT_ACCEPTED_STATE.npz',K=K,u_linear_reference=u,F=F)
    identity=[]
    for case in ('flat_straight0','curved_straight0'):
        folder=BASE/'results/native_beam_reference_precision439'
        control=list(csv.DictReader((folder/(case+'_control')/'states.csv').open()))
        observed=list(csv.DictReader((folder/(case+'_observed')/'states.csv').open()))
        errors={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(control,observed)) for key in ('q','v')}
        identity.append(dict(case=case,control_outputs=len(control),observed_outputs=len(observed),errors=errors,
            same_times=[x['time_s'] for x in control]==[x['time_s'] for x in observed],scope='mapped centers q/v only;not post-step quaternion certification'))
    regression=[]
    for case in ('flat_straight1','flat_straight0','curved_straight0'):
        for filename in ('native.initial.csv','native.assembled.csv','native.dforce.csv'):
            older=BASE/'results/native_beam_reference432'/(case+'_observed')/filename
            newer=BASE/'results/native_beam_reference_precision439'/(case+'_observed')/filename
            regression.append(dict(case=case,file=filename,bytes_identical=sha(older)==sha(newer)))
    result=dict(scope='Independent INITIAL linearized native stiffness reference,NOT actual loaded SOFA or B3 certification',
        source_matrix_sha256=sha(source/'native.dforce.csv'),producer_sha256=sha(Path(__file__)),
        private_tip_m=float(-u[-4]),approximate_Euler_tip_m=reference,relative_reference_error=float(abs(-u[-4]-reference)/reference),
        free_force_residual_N=float(np.linalg.norm(residual[2:,:3])),free_torque_residual_Nm=float(np.linalg.norm(residual[2:,3:])),
        global_linear_balance_N=total_F.tolist(),global_angular_balance_Nm=torque.tolist(),
        linearized_energy_J=energy,linearized_half_external_work_J=.5*work,
        energy_identity_defect_J=energy-.5*work,actual_loaded_native_status='FAIL433/435;reference is NEVER installed into state',
        actual_observer_control_comparison=identity,
        precision_observer_regression=regression,
        excluded_trial434='Unused keyTimes/keyForces attributes:zero applied load;not loaded bending evidence;old bytes retained')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
