"""Fail-closed gate: never create a100mm objective or study from unqualified grasp."""
import json
from closure_common import ROOT,OUT,sha,write_json,provenance
def main():
    import optuna
    paths=dict(planar=ROOT/'results/grasp_20261115/optuna_v2/summary.json',contact=OUT/'gate.json',energy=OUT/'energy_audit.json',threefinger=OUT/'threefinger/gate.json')
    evidence={k:dict(path=str(p),sha256=sha(p),data=json.loads(p.read_text())) for k,p in paths.items() if p.exists()};reasons=[]
    if evidence.get('contact',{}).get('data',{}).get('spatial_temporal_history_convergence')!='PASS':reasons.append('adaptive contact convergence failed or incomplete')
    if evidence.get('threefinger',{}).get('data',{}).get('same_condition_12_wrenches_with_recovery')!='PASS':reasons.append('threefinger same-condition12-wrench/recovery gate failed or incomplete')
    if evidence.get('threefinger',{}).get('data',{}).get('spatial_temporal_history_convergence')!='PASS':reasons.append('improved geometry spatial/time/history convergence failed or incomplete')
    if evidence.get('energy',{}).get('data',{}).get('global_energy_closure')!='PASS':reasons.append('actual Beam force has no demonstrated exact potential; global energy gate blocked')
    write_json(OUT/'optimization_guard.json',dict(status='BLOCKED' if reasons else 'EXPERIMENTAL',optuna_import='PASS',optuna_version=optuna.__version__,new_100mm_trials=0,new_study_created=False,objective_values=None,reasons=reasons,evidence={k:{kk:vv for kk,vv in v.items() if kk!='data'} for k,v in evidence.items()},scope='old30mm Optuna is separate historical measured evidence; no100mm optimization while required physics gates fail',provenance=provenance()))
    print('100mm BLOCKED',reasons)
if __name__=='__main__':main()
