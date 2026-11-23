"""One-step input knockout isnot q/v resetting or a grasp improvement."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);base=BASE/'results/b3_step_base1143';pause=BASE/'results/b3_pause_step1150'
    read=lambda p:list(csv.DictReader(p.open()));b=read(base/'finger0.csv');r=read(pause/'finger0.csv');bp={x['phase']:x for x in read(base/'step.phases.csv')};rp={x['phase']:x for x in read(pause/'step.phases.csv')}
    prefix={f:max(float(abs(np.fromstring(x[f],sep=' ')-np.fromstring(y[f],sep=' ')).max()) for x,y in zip(b,r) if float(x['time_s'])<.05-1e-12) for f in ('q_m','v_m_s','guide0_q_m','guide1_q_m')}
    free_errors={f:float(abs(np.fromstring(bp['build_end'][f],sep=' ')-np.fromstring(rp['build_end'][f],sep=' ')).max()) for f in ('guide_free_q','guide_free_v','free_free_q','free_free_v')}
    zero_errors={f:float(abs(np.fromstring(rp['accepted_end'][f],sep=' ')-np.fromstring(rp['build_end'][freef],sep=' ')).max()) for f,freef in [('guide_v','guide_free_v'),('free_v','free_free_v')]}
    changed=[float(x['time_s']) for x,y in zip(b,r) if abs(float(x['command_N'])-float(y['command_N']))>1e-12];lam=np.fromstring(rp['accepted_end']['lambda'],sep=' ')
    same_matrices={name:sha(base/name)==sha(pause/name) for name in ('step.A.csv','step.previous_K.csv','step.build_end.J.csv')}
    d=dict(status='PASS_ONE_STEP_PHASE_SEPARATION_ONLY' if max(prefix.values())==0 and max(free_errors.values())==0 and max(zero_errors.values())==0 and np.all(lam==0) and all(same_matrices.values()) and len(changed)==1 else 'FAIL_PHASE_SEPARATION',prior_prefix_errors=prefix,free_motion_errors=free_errors,paused_accepted_minus_free_velocity_errors=zero_errors,changed_command_times_s=changed,paused_lambda_Ns=lam.tolist(),matrix_hash_identity=same_matrices,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',holding='NOT RUN',conclusion='Same previous state,A,K,Jandfree prediction;ONE explicit input change removesconstraintimpulseandvelocitycorrection. Doesnot establish splittingasuniqueerrorcause or justify velocitypostprocessing.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [base/'finger0.csv',pause/'finger0.csv',base/'step.phases.csv',pause/'step.phases.csv',pause/'pause.csv',Path(__file__)]})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
