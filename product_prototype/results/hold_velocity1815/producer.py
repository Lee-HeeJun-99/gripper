"""Independent actual impulse-to-velocity budget over hold-to-peak intervals."""
import argparse,csv,json,re
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);results=[]
    for case in ('dispatch_finite_holding1586','yoke_hold_diagnostic1741'):
        src=BASE/'results'/case;rows=list(csv.DictReader((src/'object.csv').open()))
        t=np.array([float(r['time_s']) for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ')[:3] for r in rows]);dt=np.diff(np.r_[0,t]);idx={x:i for i,x in enumerate(t)}
        hold=np.flatnonzero((t>=1.6-1e-12)&(t<=2+1e-12));begin=int(hold[0]);peak=int(hold[np.linalg.norm(v[hold],axis=1).argmax()])
        groups={name:np.zeros((len(t),3)) for name in ['other']+[f'finger{j}_{kind}' for j in range(3) for kind in ('normal','tangent')]}
        for r in csv.DictReader((src/'response_rows.csv').open()):
            names=r['model0']+' '+r['model1']
            if '/object/' not in names:continue
            m=re.search(r'/finger([012])/skinCollision/',names);name='other'
            if m:name=f'finger{m[1]}_'+('normal' if (int(r['row_id'])-int(r['first_row']))%3==0 else 'tangent')
            groups[name][idx[float(r['time_s'])]]+=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]
        allimp=np.sum(list(groups.values()),axis=0)
        predicted=np.cumsum(allimp/.1+dt[:,None]*np.array([0,0,-9.81]),axis=0)
        residual=float(abs(predicted-v).max());assert residual<1e-10
        interval=slice(begin+1,peak+1);contributions={name:(values[interval].sum(0)/.1*1000).tolist() for name,values in groups.items()}
        contributions['gravity']=[0,0,float(-9.81*dt[interval].sum()*1000)]
        reconstructed=np.sum(list(contributions.values()),axis=0)
        delta=(v[peak]-v[begin])*1000;error=float(abs(reconstructed-delta).max());assert error<1e-7
        results.append(dict(case=case,begin_time_s=float(t[begin]),peak_time_s=float(t[peak]),begin_velocity_mm_s=(v[begin]*1000).tolist(),peak_velocity_mm_s=(v[peak]*1000).tolist(),actual_delta_velocity_mm_s=delta.tolist(),contact_and_gravity_delta_velocity_mm_s=contributions,full_trajectory_max_reconstruction_error_m_s=residual,interval_budget_error_mm_s=error,input_sha256={f:sha(src/f) for f in ('object.csv','response_rows.csv')}))
    d=dict(status='PASS_ACTUAL_IMPULSE_VELOCITY_BOOKKEEPING',results=results,source_sha256=sha(Path(__file__)),scope='No causal proof or alternative trajectory: actual impulses depend on actual state. Cannot remove guide contacts or change friction by subtracting impulses. No global energy, hardware or Native convergence PASS. All original data read-only.')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
