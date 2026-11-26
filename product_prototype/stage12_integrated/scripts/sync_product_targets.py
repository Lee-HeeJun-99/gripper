"""Synchronize unfinished product tasks to actual latest candidate, not PASSs."""
import json
from baseline_registry import ROOT,ref,dump
def main():
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());tasks={t['id']:t for t in q['tasks']}
    for t in q['tasks']:
        if t['status'] in ('READY','RUNNING'):
            t['target_candidate']=c['definition'];t['target_revision']=c['revision'];t['target_parts']=c['parts']
    t=tasks['AI_whole_palm_support'];t['criteria']='Same current250-part RevAJ geometry, actual full-Palm mounting/load ports, static equilibrium and1% response convergence; local tab clamp-edge stress FAIL is not deleted or promoted'
    t['prerequisites']=['local_palm_tabs','idler_integral_M3_shoulder'];t['evidence']=ref(ROOT/'validation/convergence/AI_tab_convergence2/summary.json')
    tasks['alignment_alternative'].update(priority=8,selection_note='Fallback only if direct shared-pilot topology is rejected. Do not repeat disc-only Oldham kinematics; actual full rated interfaces/restoring reactions needed.')
    tasks['fixture_preparation']['selection_note']='AF stand was a different preliminary cartridge. Latest RevAJ bench mounting, input reaction, guards/sensor adapters and blank physical records still required.'
    name='AJ_idler_thread_and_load_proof'
    if name in tasks:raise ValueError('Duplicate new physical task')
    q['tasks'].append(dict(id=name,track='A',priority=1,status='READY',target_revision=c['revision'],target_parts=c['parts'],target_candidate=c['definition'],hypothesis='Actual larger neck and fillets need finite thread/core/preload/load proof, not a major-diameter nominal strength calculation',criteria='Actual minimum thread core, material evidence, bracket/washer/nut load path, mesh1% where needed, complete reaction/energy; no protected force assumption from catalog-only data',prerequisites=['idler_integral_M3_shoulder'],system_gate_contribution=4,cost='4GiB/420s per bounded child',fallback='standard_rated_shoulder_or_double_supported_idler',last_run_utc=None,consecutive_runs=0))
    dump(ROOT/'INTEGRATED_TASKS.json',q)
if __name__=='__main__':main()
