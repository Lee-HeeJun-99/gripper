"""Fail-closed gate: never create a100mm objective or study from unqualified grasp."""
import json
from closure_common import ROOT,OUT,sha,write_json,provenance
def main():
    import optuna
    paths=dict(planar=ROOT/'results/grasp_20261115/optuna_v2/summary.json',contact=OUT/'gate.json',energy=OUT/'energy_audit.json',balance=OUT/'balance_audit.json',threefinger=OUT/'threefinger/gate.json')
    evidence={k:dict(path=str(p),sha256=sha(p),data=json.loads(p.read_text())) for k,p in paths.items() if p.exists()};reasons=[];integrity=[]
    from closure_frame_common import PLUGIN
    for name,t in evidence.get('threefinger',{}).get('data',{}).get('trials',{}).items():
        directory=OUT/'threefinger/trials'/name;path=directory/'metrics.json'
        if not path.is_file() or sha(path)!=t.get('metrics_sha256'):integrity.append(name+':metrics');continue
        r=json.loads(path.read_text());identity=r.get('identity',{})
        if identity.get('binary_sha256')!=sha(PLUGIN):integrity.append(name+':current binary')
        for source,digest in identity.get('source_sha256',{}).items():
            if not (ROOT/source).is_file() or sha(ROOT/source)!=digest:integrity.append(name+':source:'+source)
        for artifact,digest in r.get('artifacts',{}).items():
            if not (directory/artifact).is_file() or sha(directory/artifact)!=digest:integrity.append(name+':artifact:'+artifact)
    if integrity:reasons.append('source/binary/raw integrity mismatch')
    if evidence.get('contact',{}).get('data',{}).get('spatial_temporal_history_convergence')!='PASS':reasons.append('adaptive contact convergence failed or incomplete')
    if evidence.get('threefinger',{}).get('data',{}).get('same_condition_12_wrenches_with_recovery')!='PASS':reasons.append('threefinger same-condition12-wrench/recovery gate failed or incomplete')
    if evidence.get('threefinger',{}).get('data',{}).get('spatial_temporal_history_convergence')!='PASS':reasons.append('improved geometry spatial/time/history convergence failed or incomplete')
    if evidence.get('energy',{}).get('data',{}).get('global_energy_closure')!='PASS':reasons.append('actual Beam force has no demonstrated exact potential; global energy gate blocked')
    balances=evidence.get('balance',{}).get('data',{})
    if not balances or any(v.get('global_balance_status')!='PASS' for v in balances.values()):reasons.append('whole-system root/guide reaction wrench balance failed or incomplete')
    write_json(OUT/'optimization_guard.json',dict(status='BLOCKED' if reasons else 'EXPERIMENTAL',optuna_import='PASS',optuna_version=optuna.__version__,new_100mm_trials=0,new_study_created=False,objective_values=None,reasons=reasons,integrity_errors=integrity,evidence={k:{kk:vv for kk,vv in v.items() if kk!='data'} for k,v in evidence.items()},scope='old30mm Optuna is separate historical measured evidence; no100mm optimization while required physics gates fail',provenance=provenance()))
    print('100mm BLOCKED',reasons)
if __name__=='__main__':main()
