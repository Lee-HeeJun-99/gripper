"""Read-only matched actual object-row inventory; no causal/controller inference."""
import argparse, csv, json, re, time
from pathlib import Path
import numpy as np
from analyse import BASE, sha

def main():
    p=argparse.ArgumentParser(); p.add_argument('--tag',required=True); a=p.parse_args()
    out=BASE/'results'/a.tag; out.mkdir(exist_ok=False); start=time.monotonic(); results=[]
    for case in ('dispatch_finite_holding1586','yoke_hold_diagnostic1741'):
        src=BASE/'results'/case; rows=list(csv.DictReader((src/'object.csv').open()))
        t=np.array([float(r['time_s']) for r in rows]); v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows])
        dt=np.diff(np.r_[0,t]); index={x:i for i,x in enumerate(t)}
        impulse=np.zeros((len(t),3,6)); normal=np.zeros_like(impulse)
        for r in csv.DictReader((src/'response_rows.csv').open()):
            names=r['model0']+' '+r['model1']; m=re.search(r'/finger([012])/skinCollision/',names)
            if '/object/' not in names or not m: continue
            k=index[float(r['time_s'])]; j=int(m[1]); value=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
            impulse[k,j]+=value
            if (int(r['row_id'])-int(r['first_row']))%3==0: normal[k,j]+=value
        hold=(t>=1.6-1e-12)&(t<=2+1e-12); ids=np.flatnonzero(hold)
        peak=ids[np.linalg.norm(v[hold,:3],axis=1).argmax()]
        actual=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows])
        previous=np.vstack([np.zeros((1,6)),v[:-1]])
        expected=.1*(v[:,:3]-previous[:,:3]); expected[:,2]+=.981*dt
        bands=[]
        for lo,hi in ((1.2,1.4),(1.4,1.6),(1.6,1.8),(1.8,2.0)):
            mask=(t>lo)&(t<=hi+1e-12)
            bands.append(dict(interval_s=[lo,hi],mean_finger_force_N=(impulse[mask,:,:3]/dt[mask,None,None]).mean(0).tolist(),max_speed_mm_s=float(np.linalg.norm(v[mask,:3],axis=1).max()*1000)))
        results.append(dict(case=case,peak_time_s=float(t[peak]),peak_velocity_mm_s=(1000*v[peak,:3]).tolist(),peak_finger_force_N=(impulse[peak,:,:3]/dt[peak]).tolist(),hold_mean_finger_force_N=(impulse[hold,:,:3]/dt[hold,None,None]).mean(0).tolist(),hold_mean_normal_torque_Nm=(normal[hold,:,3:]/dt[hold,None,None]).mean(0).tolist(),maximum_object_momentum_residual_Ns=float(abs(expected-actual[:,:3]).max()),maximum_skin_partition_difference_Ns=float(abs(impulse.sum(1)-actual).max()),time_bands=bands,input_sha256={f:sha(src/f) for f in ('object.csv','response_rows.csv','scene.scn')}))
    d=dict(status='PASS_MATCHED_READ_ONLY_INVENTORY_ONLY',results=results,runtime_s=time.monotonic()-start,source_sha256=sha(Path(__file__)),scope='Actual stored response-row impulses, no contact-area inference. Different hardware/mass configurations prevent single-variable causal attribution. Normal torque is measured cached-row wrench, not proof of physically radial contact. No motor-port velocity available in these files; no feedback law justified by this inventory. No new Native run or grasp PASS.')
    (out/'summary.json').write_text(json.dumps(d,indent=2)); (out/'producer.py').write_bytes(Path(__file__).read_bytes()); print(json.dumps(d,indent=2))
if __name__=='__main__': main()
