"""Read-only Native discrete contact rows;NOT a continuous impact/event solver."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def rows(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);p.add_argument('--references',nargs='+',required=True);a=p.parse_args()
    if len(a.cases)!=len(a.references):raise ValueError('one uninstrumented reference per case required')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];details=[];files={}
    for case,ref in zip(a.cases,a.references):
        folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());dt=meta['dt_s']
        for alarm in ('1','5'):
            d=folder/alarm;states=[rows(d/f'guide{i}.csv') for i in (0,1)];response=[rows(d/f'response{i}.csv') for i in (0,1)]
            purity=0.
            for i in (0,1):
                original=rows(BASE/'results'/ref/alarm/f'guide{i}.csv')
                if len(original)!=len(states[i]):raise ValueError('incomplete trajectory')
                for x,y in zip(states[i],original):
                    for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):
                        purity=max(purity,float(np.max(abs(vec(x[key])-vec(y[key])))))
            detector=rows(d/'detector.csv');first=None;momentum=0.;row_sum=0.;pair_balance=0.;normal_norm=0.;coulomb_excess=0.
            for k,state in enumerate(states[0]):
                t=float(state['time_s']);active=[[r for r in rs if float(r['time_s'])==t] for rs in response]
                previous=[np.array(meta['initial_rigid_v'][i]) if k==0 else vec(states[i][k-1]['rigid_v']) for i in (0,1)]
                current=[vec(states[i][k]['rigid_v']) for i in (0,1)]
                for i in (0,1):
                    total=sum((vec(r['object_impulse_Ns_Nms']) for r in active[i]),np.zeros(6))
                    row_sum=max(row_sum,float(np.max(abs(total-vec(states[i][k]['object_impulse_Ns_Nms'])))))
                    # Public mass audit,translation block only;no invented rotational model.
                    mass=json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['mass_kg']
                    momentum=max(momentum,float(np.max(abs(mass*(current[i][:3]-previous[i][:3])-total[:3]))))
                for left,right in zip(active[0],active[1]):
                    if left['row_id']!=right['row_id']:raise ValueError('row identity mismatch')
                    lam=float(left['lambda_Ns']);imp=[vec(r['object_impulse_Ns_Nms']) for r in (left,right)]
                    pair_balance=max(pair_balance,float(np.max(abs(imp[0][:3]+imp[1][:3]))))
                    # This recovers ACTUALLY USED mapped J from nonzero J^T lambda.
                    # Zero rows cannot be divided:normal/velocity remain NULL.
                    J=[x/lam for x in imp] if lam!=0 else None
                    offset=int(left['row_id'])-int(left['first_row'])
                    if J is not None and offset==0:normal_norm=max(normal_norm,abs(np.linalg.norm(J[0][:3])-1))
                    pre=None if J is None else float(sum(j@v for j,v in zip(J,previous)))
                    post=None if J is None else float(sum(j@v for j,v in zip(J,current)))
                    details.append(dict(case=case,alarm_mm=int(alarm),time_s=t,step_start_s=t-dt,row_id=int(left['row_id']),row_role=('normal' if offset==0 else 'tangent'),lambda_Ns=lam,J0=None if J is None else J[0].tolist(),J1=None if J is None else J[1].tolist(),previous_velocity_on_used_row_m_s=pre,accepted_velocity_on_used_row_m_s=post,model0=left['model0'],model1=left['model1']))
                    if first is None and offset==0 and lam>0:first=dict(accepted_time_s=t,step_start_s=t-dt,normal_impulse_Ns=lam,previous_velocity_on_used_row_m_s=pre,accepted_velocity_on_used_row_m_s=post,normal_on_body0=J[0][:3].tolist())
                if active[0]:
                    l=np.array([float(r['lambda_Ns']) for r in active[0]])
                    if len(l)!=3:raise ValueError('expected one frictional contact block')
                    coulomb_excess=max(coulomb_excess,float(np.linalg.norm(l[1:])-.3*l[0]))
            totals=[sum((vec(s['object_impulse_Ns_Nms']) for s in data),np.zeros(6)).tolist() for data in states]
            records.append(dict(case=case,reference=ref,alarm_mm=int(alarm),dt_s=dt,strict_observer_state_max_error=purity,strict_state_gate=1e-12,observer_state_pass=purity<=1e-12,detector_first_accepted_time_s=None if not detector else float(detector[0]['accepted_time_s']),first_nonzero_normal_row=first,linear_momentum_residual_Ns=momentum,response_row_sum_residual_Ns_Nms=row_sum,equal_opposite_linear_impulse_residual_Ns=pair_balance,normal_unit_residual=normal_norm,coulomb_cone_excess_Ns=coulomb_excess,total_body_impulses_Ns_Nms=totals,minimum_gap_mm=next(r['minimum_gap_mm'] for r in meta['records'] if int(r['alarm_mm'])==int(alarm))))
        for f in folder.rglob('*'):
            if f.is_file():files[str(f.relative_to(BASE.parent))]=sha(f)
    result=dict(status='READ_ONLY_NATIVE_ENTRY_DIAGNOSTIC_NOT_TIME_OR_GRASP_PASS',scope='Native response provenance and impulse pullback;previous/current discrete velocities projected on the same USED Jacobian,NOT same-time pre/post continuous impact states. Normal unavailable for zero multiplier. No exact event-time claim. Metadata query purity tested against frozen uninstrumented trajectories.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),records=records,source_files=files)
    (out/'rows.json').write_text(json.dumps(details,indent=2));(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(records,indent=2))

if __name__=='__main__':main()
