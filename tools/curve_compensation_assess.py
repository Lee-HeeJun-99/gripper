"""Separate all unchanged gates for the independent arithmetic version."""
import argparse
import json
import numpy as np
from curve_common import OUT,write_json
from curve_assess import layout_signature
from birth_assess import same_physics,observables
from history_assess import comparison
from trial_validation import read_states


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',default='v1');args=p.parse_args()
    target=OUT/('qualification_'+args.checkpoint+'.json')
    if target.exists():raise ValueError('refuse overwritten qualification checkpoint')
    records={}
    for file in(OUT/'grasp').glob('*/metrics.json'):
        r=json.loads(file.read_text())
        if not r['config']['profile_only']:records[file.parent.name]=r
    checks={}
    pairs=[('base','halfdt',.001),('halfdt','quarterdt',.001),('base','quarterdt',.001),
           ('mesh11_half','halfdt',.01),('halfdt','mesh41_half',.01),
           ('halfdt','history_fine_half',.01),('base','repeat24',1e-6)]
    for a,b,limit in pairs:
        name=a+'_'+b
        if a not in records or b not in records:checks[name]=dict(status='NOT RUN',reason='actual result not yet present');continue
        u,v=records[a],records[b];same_physics(u,v)
        for key in('structural_compensation','curved'):
            if u['identity'][key]!=v['identity'][key]:raise ValueError('compiled model identity differs '+key)
        if u['identity']['inherited']['inherited']['beam']['plugin_sha256']!=v['identity']['inherited']['inherited']['beam']['plugin_sha256']:raise ValueError('Beam binary differs')
        if layout_signature(a)!=layout_signature(b):raise ValueError('physical hardware changes with mesh')
        for k in('mass_quadrature','solver_template','integration_arithmetic'):
            if u['config'].get(k)!=v['config'].get(k):raise ValueError('experimental definition differs '+k)
        r=comparison(u,v,limit);r['motion_only_status']=r['status'];x,y=observables(OUT/'grasp'/a),observables(OUT/'grasp'/b)
        r['observables']={k:dict(absolute=abs(x[k]-y[k]),relative=abs(x[k]-y[k])/abs(y[k])if y[k]else(0 if x[k]==0 else None))for k in x}
        loss=r['observables']['friction_dissipation']['relative'];r['loss_status']='PASS'if loss is not None and loss<=limit else'FAIL'
        r['underlying_physical_pass']=bool(u.get('bounded_hold_pass')and v.get('bounded_hold_pass'))
        r['status']='PASS'if r['motion_only_status']=='PASS'and r['loss_status']=='PASS'and r['underlying_physical_pass']else'FAIL';checks[name]=r
    repetition={}
    if'base'in records and'repeat24'in records:
        a=read_states(OUT/'grasp/base/state.txt');b=[r for r in read_states(OUT/'grasp/repeat24/state.txt')if r['time']<=18+1e-8]
        if len(a)!=len(b):raise ValueError('repeat actual frame count')
        repetition={k:float(np.max(np.abs(np.array([r[k]for r in a])-np.array([r[k]for r in b]))))for k in('X','V','R')}
    write_json(target,dict(status='EXPERIMENTAL',checks=checks,raw_repeat_errors=repetition,recovery_24=records.get('repeat24',{}).get('recovery_pass'),grasp_optimization='BLOCKED',global_energy='BLOCKED',cases={n:{k:r.get(k)for k in('status','bounded_hold_pass','global_force_residual','global_moment_residual','process','failure_reason')}for n,r in records.items()},scope='old standard-EulerFAILs remain;half-dt is a candidate only after its own fine-reference and independent spatial/history/energy checks;coarse11not silently certified'))
    print({n:(r['status'],r.get('loss_status'),r.get('relative_difference'))for n,r in checks.items()})


if __name__=='__main__':main()
