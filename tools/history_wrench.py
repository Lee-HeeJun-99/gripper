"""Geometric cone diagnostics from NORMAL samples, NOT dynamic certification."""
import csv,json
import numpy as np
from history_common import ROOT,OUT,write_json,sha
from closure_wrench import analyze
from trial_validation import read_states
def main():
    out=OUT/'wrench_geometry';out.mkdir(exist_ok=False);records={}
    for name in ('repeated','normal_q32'):
        path=OUT/'grasp'/name;c=json.loads((path/'config.json').read_text());state=min(read_states(path/'state.txt'),key=lambda x:abs(x['time']-13.98));center=np.array(state['X']).reshape(-1,7)[c['object_index'],:3]
        with (path/'contact.csv.patch.csv').open() as f:rows=[r for r in csv.DictReader(f) if abs(float(r['time'])-state['time'])<1e-7 and float(r['Fn'])>0]
        points=[[float(r[k])-center[j] for j,k in enumerate(('px','py','pz'))] for r in rows];normals=[[float(r[k]) for k in ('nx','ny','nz')] for r in rows];caps=[float(r['Fn']) for r in rows]
        result=analyze(points,normals,caps,c['mu'],c['object_radius']);control=analyze(points,normals,caps,0,c['object_radius'])
        records[name]=dict(geometry=result,mu_zero_control=control,time=state['time'],patch_sha256=sha(path/'contact.csv.patch.csv'),scope='normal quadrature point discretization and measured normal-force caps ONLY; not full tangent distribution nor12direction SOFA force/torque trial. Rank6 is not sufficient for force closure.')
    write_json(out/'metrics.json',dict(status='EXPERIMENTAL',records=records,full_grasp_certified=False));print({k:(v['geometry']['rank'],v['geometry']['cone_origin_strict_interior']) for k,v in records.items()})
if __name__=='__main__':main()
