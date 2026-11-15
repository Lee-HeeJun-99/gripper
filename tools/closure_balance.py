"""Separate reconstructed free residual, root/guide reaction and global balance."""
import json
import numpy as np
from closure_common import OUT,sha,write_json
from trial_validation import read_states
def main():
    results={}
    for group,name in [('twofinger','wrenches_Fxplus'),('threefinger','wrenches_Tzplus')]:
        directory=OUT/('threefinger/trials' if group=='threefinger' else 'trials')/name;r=json.loads((directory/'metrics.json').read_text());c=r['config'];raw=read_states(directory/'state.txt');s=min(raw,key=lambda s:abs(s['time']-13.98));x=np.array(s['X']).reshape(-1,7);forces=np.array(s['R']).reshape(-1,6);n=c['nodes'];obj=c['object_index'];origin=x[obj,:3];support=np.zeros_like(forces)
        for i in range(obj):
            axes=range(6) if i%n==0 else (1,3,5)
            for a in axes:support[i,a]=-forces[i,a]
        def total(w):return np.r_[w[:,:3].sum(axis=0),(w[:,3:]+np.cross(x[:,:3]-origin,w[:,:3])).sum(axis=0)]
        external=np.zeros_like(forces);external[obj,c['axis']]=c['load'];internal=total(forces-external);reaction=total(support);balance=total(external+support);scale=abs(c['load'])/(c['object_radius'] if c['axis']>=3 else 1);normalized=np.r_[balance[:3]/scale,balance[3:]/(scale*c['object_radius'])]
        results[group]=dict(time=s['time'],external_wrench_about_object_com=total(external).tolist(),root_and_guide_reaction_wrench=reaction.tolist(),global_external_plus_reaction=balance.tolist(),internal_resultant_wrench=internal.tolist(),normalized_global_balance=normalized.tolist(),global_balance_status='PASS' if abs(normalized).max()<1e-3 else 'FAIL',metrics_sha256=sha(directory/'metrics.json'),scope='static R reconstructed by summing every local ForceField at recorded state; no mass/Rayleigh dynamic residual or actual linear-solver residual claimed; fixed DOFs and planar guide reactions separate from free residual')
    write_json(OUT/'balance_audit.json',results);print({k:v['global_balance_status'] for k,v in results.items()})
if __name__=='__main__':main()
