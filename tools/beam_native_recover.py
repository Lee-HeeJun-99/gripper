"""Read-only recovery of the NumPy-bool serialization failure; no rerun."""
import json
import numpy as np
from beam_common import OUT,write_json,sha
from trial_validation import read_states
def main():
    out=OUT/'native_lat12';target=out/'recovered_result.json'
    if target.exists():raise FileExistsError(target)
    c=json.loads((out/'input/config.json').read_text());raw=read_states(out/'state.txt');rows=[json.loads(s) for s in (out/'native.jsonl').read_text().splitlines()];F={round(s['time'],7):np.array(s['R']).reshape(-1,6) for s in raw};tail=[s for s in rows if 13.9-1e-8<=s['time']<14-1e-8];o=c['object_index'];res=[];active=[]
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    for s in tail:
        if s['generalized_impulse'] is None:raise ValueError('constraint dimension mismatch')
        res.append((F[round(s['time'],7)]+np.array(s['generalized_impulse']).reshape(-1,6)/c['dt'])[o]);active.append(int(sum(np.array(s['lambda_impulse'])[::3]>1e-16)))
    err=np.max(abs(np.array(res)),axis=0);checks=dict(force=bool(err[:3].max()/1e-6<1e-3),moment=bool(err[3:].max()/5e-6<1e-3),speed=bool(max(np.max(abs(np.array(s['V'])[o])) for s in tail)<1e-5),contact=min(active)>0,execution='36000 iterations done' in log and '[ERROR]' not in log)
    r=dict(status='EXPERIMENTAL' if all(checks.values()) else 'FAIL',checks=checks,force_relative=float(err[:3].max()/1e-6),moment_relative=float(err[3:].max()/5e-6),minimum_positive_normal_contacts=min(active),frames=len(rows),full_grasp_certified=False,scope='installed-engine native contact, not patched SDK; J-transpose impulse/dt; recovered from immutable output after serialization error',artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
    write_json(target,r);print(r['status'],checks)
if __name__=='__main__':main()
