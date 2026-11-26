"""Index completed actual AK product work and retarget unfinished tasks only.
This is result indexing, not a claim these tasks were registered before execution.
"""
import json,datetime,subprocess
from baseline_registry import ROOT,REPO,ref,dump
def main():
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text())
    ids={t['id'] for t in q['tasks']};now=datetime.datetime.now(datetime.timezone.utc).isoformat();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    for name,track,result,status,scope in [
        ('AJ_collet_actual_coverage','A','validation/transmission/AJ_collet_requirements1/summary.json','PASS','Actual necessary demand/coverage only; ahead-of-shaft clamp identified; capacity remains unqualified'),
        ('AK_integral_support_missing_foot','C','validation/transmission/AK_support1/summary.json','FAIL','Actual4.8126945mm2 missing foot support per sector, legacy aperture; original failure preserved'),
        ('AK_integral_support_corrected','C','validation/transmission/AK_support2/summary.json','PASS','235-part candidate finite one-piece support and full nominal foot contact only; no strength release')]:
        assert name not in ids,'Do not duplicate completed work';r=ROOT/result;assert r.is_file()
        task=dict(id=name,track=track,status=status,priority=1,result=result,scope=scope,last_run_utc=now,consecutive_runs=1,system_gate_contribution=4,registration_note='Post-execution result indexing; exact producer snapshots and immutable result references retained')
        q['tasks'].append(task);h['cycles'].append(dict(task=name,track=track,time_utc=now,status=status,evidence=ref(r),HEAD_at_result_indexing=head,execution='current interactive session; no external launch'))
    h['historical_starting_HEAD_field_note']='Existing starting_HEAD fields were sampled by completion recorder; interpret as HEAD at result indexing, not a verified job-start timestamp.'
    for t in q['tasks']:
        if t['status'] in ('READY','RUNNING'):
            t.update(target_candidate=c['definition'],target_revision=c['revision'],target_parts=c['parts'])
        if t['id']=='AI_whole_palm_support':t['criteria']='Current235-part AK actual whole-Palm mounting/contact geometry and real Root/drive load ports; equilibrium, energy,1% convergence. Preserve old cut-edge stress FAIL; do not transfer old clamp or AH mount results.'
        if t['id']=='fixture_preparation':t['selection_note']='AF preliminary input-supported fixture is NOT compatible with AK one-piece grounded support/front collet; actual reaction stand, calibrated sensor and guarded unpowered protocol required.'
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
if __name__=='__main__':main()
