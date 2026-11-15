"""Actual new-beam contact patch: rank, cone and capped LP, not dynamic certification."""
import json,csv
import numpy as np
from beam_common import OUT,write_json,sha
from closure_wrench import analyze
from trial_validation import read_states
def main():
    target=OUT/'wrench.json'
    if target.exists():raise FileExistsError(target)
    out=OUT/'grasp/Tz_v2';m=json.loads((out/'metrics.json').read_text());c=m['config'];r=min(read_states(out/'state.txt'),key=lambda x:abs(x['time']-13.98));o=np.array(r['X']).reshape(-1,7)[c['object_index'],:3]
    with (out/'contact.csv.patch.csv').open() as f:rows=[x for x in csv.DictReader(f) if abs(float(x['time'])-r['time'])<1e-7]
    points=[[float(x[k])-o[j] for j,k in enumerate(('px','py','pz'))] for x in rows];normals=[[float(x[k]) for k in ('nx','ny','nz')] for x in rows];caps=[float(x['Fn']) for x in rows];v=analyze(points,normals,caps,c['mu'],c['object_radius']);v.update(origin='actual SOFA conservative-beam patch, static LP postprocessing only',metrics_sha256=sha(out/'metrics.json'),time=r['time'],full_grasp_certified=False);write_json(target,v);print(v['rank'],v['cone_origin_strict_interior'],{k:r['feasible'] for k,r in v['bounded_feasibility'].items()})
if __name__=='__main__':main()
