"""Native contact impulse reconstructed before root/guide reaction accounting."""
import argparse,json
import numpy as np
from beam_common import OUT,write_json
from trial_validation import read_states
def main():
    p=argparse.ArgumentParser();p.add_argument('--lat',type=int,default=12);a=p.parse_args();out=OUT/('native_lat'+str(a.lat));target=out/'balance.json'
    if target.exists():raise FileExistsError(target)
    c=json.loads((out/'input/config.json').read_text());states={round(s['time'],7):s for s in read_states(out/'state.txt')};rows=[json.loads(s) for s in (out/'native.jsonl').read_text().splitlines()];n=c['nodes'];o=c['object_index'];totals=[];disp=[];angles=[];omega=[]
    for row in rows:
        if not 13.9-1e-8<=row['time']<14-1e-8:continue
        state=states[round(row['time'],7)];R=np.array(state['R']).reshape(-1,6)+np.array(row['generalized_impulse']).reshape(-1,6)/c['dt'];X=np.array(state['X']).reshape(-1,7);V=np.array(state['V']).reshape(-1,6);support=np.zeros_like(R);support[:o:n]=-R[:o:n]
        for i in range(o):
            if i%n: support[i,[1,3,5]]=-R[i,[1,3,5]]
        F=support[:,:3].sum(axis=0);M=(support[:,3:]+np.cross(X[:,:3]-X[o,:3],support[:,:3])).sum(axis=0);M[2]+=5e-6;totals.append(np.r_[F,M]);angles.append(2*np.arctan2(np.linalg.norm(X[o,3:6]),abs(X[o,6])));omega.append(np.max(abs(V[o,3:])))
    err=np.max(np.abs(np.array(totals)),axis=0);write_json(target,dict(status='PASS' if max(err[:3])/1e-6<1e-3 and max(err[3:])/5e-6<1e-3 else 'FAIL',global_force_relative=float(max(err[:3])/1e-6),global_moment_relative=float(max(err[3:])/5e-6),max_object_angle_rad=float(max(angles)),max_omega=float(max(omega)),scope='tail global root+planar-guide reactions after J-transpose impulse/dt; no SDF compliance or complete grasp equivalence'));print(target)
if __name__=='__main__':main()
