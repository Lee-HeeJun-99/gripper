"""Two native surface meshes, isolated from SDF compliance/convergence claims."""
import json
import numpy as np
from beam_common import OUT,write_json,sha
from trial_validation import read_states
from closure_frame_evaluate import relative_angles
def main():
    target=OUT/'native_surface_comparison.json'
    if target.exists():raise FileExistsError(target)
    records={}
    for lat in (12,24):
        out=OUT/('native_physical'+str(lat));c=json.loads((out/'input/config.json').read_text());raw=read_states(out/'state.txt');X=np.array([s['X'] for s in raw]).reshape(-1,c['object_index']+1,7);t=np.array([s['time'] for s in raw]);o=c['object_index'];before=np.argmin(abs(t-6));hold=(t>=6-1e-8)&(t<14-1e-8);base=np.broadcast_to(X[before,o,3:],X[hold,o,3:].shape);balance=json.loads((out/'balance.json').read_text());result=json.loads((out/'result.json').read_text());records[str(lat)]=dict(displacement_mm=float(np.linalg.norm(X[hold,o,:3]-X[before,o,:3],axis=1).max()),rotation_increment_rad=float(relative_angles(base,X[hold,o,3:]).max()),balance=balance,object_checks=result['checks'],state_sha256=sha(out/'state.txt'))
    errors={k:abs(records['12'][k]/records['24'][k]-1) for k in ('displacement_mm','rotation_increment_rad')};checks=dict(mesh_diagnostic=all(x<.01 for x in errors.values()),physical_balance=all(r['balance']['status']=='PASS' for r in records.values()),object_subchecks=all(all(r['object_checks'].values()) for r in records.values()));write_json(target,dict(status='PASS' if all(checks.values()) else 'FAIL',records=records,relative_errors=errors,limit=.01,checks=checks,full_grasp_certified=False,scope='one sphere surface latitude12/24 diagnostic with new beam; fixed finger mesh/buffer/dt, NOT full spatial/dt/contact-law convergence'));print(checks,errors)
if __name__=='__main__':main()
