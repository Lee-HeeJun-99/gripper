"""Explicit operator-authorized cycle59 recovery; never called by a Worker.

Prepare independent audits and an exact request, or save that sealed request
through the unchanged Supervisor. Never reset/stash/delete/exclude new files.
Original rejected request, logs, checkpoint and all physics failures preserved.
"""
import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path
from baseline_registry import REPO, ROOT, sha, ref, dump
from supervised_save import changed, untracked, save
from goal_manager_policy import engineering_record, outcome
from save_preflight import inspect, seal, verify

RT=ROOT/'runtime/goal_authorized_20261127_7'
OUT=ROOT/'validation/integrated/save59_operator_recovery2'
CP=RT/'checkpoint_before59.json'
REQUEST=RT/'save_request59_recovered.json'
SEAL=RT/'save_seal59_recovered.json'


def load(p): return json.loads(p.read_text())


def bounded(script, tag):
    command=['/home/ubuntu/miniconda3/envs/robot_ws/bin/python',str(ROOT/'scripts'/script),tag]
    env=dict(os.environ,PYTHONPATH='/tmp/regrip_stage1_ocp:/tmp/regrip_stage2_fem',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    log=OUT/(tag+'.log'); started=time.monotonic()
    def limits(): resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    with log.open('x') as output:
        child=subprocess.Popen(command,cwd=REPO,env=env,stdout=output,stderr=subprocess.STDOUT,
                               start_new_session=True,preexec_fn=limits)
        timeout=False
        try: code=child.wait(timeout=420)
        except subprocess.TimeoutExpired:
            timeout=True;os.killpg(child.pid,signal.SIGTERM)
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);child.wait()
            code=child.returncode
    summary=ROOT/'validation/integrated'/tag/'summary.json'
    result=dict(command=command,source=ref(ROOT/'scripts'/script),exit_code=code,
                elapsed_s=time.monotonic()-started,timeout=timeout,reaped=True,
                memory_limit_bytes=4*1024**3,timeout_s=420,log=ref(log),
                summary=ref(summary) if summary.exists() else None)
    dump(OUT/(tag+'_execution.json'),result)
    if timeout or code: raise ValueError('Independent recovery audit failed: '+tag)
    d=load(summary)
    checks=d.get('checks',{})
    assert all(checks.values()) and d.get('whole_system_release') is False
    return result


def prepare():
    OUT.mkdir(exist_ok=False)
    cp=load(CP); original=load(RT/'save_request59.json');ledger=load(RT/'ledger.json')
    pins=ledger['source_pins']; assert all(sha(REPO/p)==h for p,h in pins.items())
    assert not (ROOT/'runtime/STOP').exists()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==cp['HEAD']
    prior=ROOT/'validation/integrated/primary_cycle59_record'
    worker_old=load(prior/'start_untracked.json')
    misplaced=sorted(set(worker_old)-set(cp['preexisting_untracked']))
    expected=[str((prior/('prior_'+n)).relative_to(REPO)) for n in
              ['CHECKPOINT.md','CURRENT_CANDIDATE.json','NEXT_TASK.json','PRIMARY_PRODUCT.json']]
    assert misplaced==sorted(expected)
    copies=[]
    for name in misplaced:
        path=REPO/name; original_name='product_prototype/stage12_integrated/'+path.name[6:]
        raw=subprocess.check_output(['git','show',cp['HEAD']+':'+original_name],cwd=REPO)
        assert raw==path.read_bytes()
        copies.append(dict(file=ref(path),matches_HEAD_path=original_name))
    old_hashes={p:h for p,h in worker_old.items() if p in cp['preexisting_untracked']}
    assert len(old_hashes)==len(cp['preexisting_untracked'])
    assert all((REPO/p).is_file() and sha(REPO/p)==h for p,h in old_hashes.items())
    assert all(sha(REPO/r['path'])==r['SHA256'] for r in original['files'])
    dump(OUT/'original_rejection.json',load(RT/'save_error59.json'))
    dump(OUT/'original_ledger.json',ledger)
    dump(OUT/'original_status.json',load(RT/'status.json'))
    dump(OUT/'original_manifest.json',original)
    # Full canonical CAD/BOM identity, not only newly changed STEP files.
    candidate=load(ROOT/'cad/exports/primaryP1_captive59c/summary.json')
    assert len(candidate['part_references'])==77
    assert all(sha(REPO/r['path'])==r['SHA256'] for r in
               [*candidate['part_references'].values(),candidate['assembly'],candidate['BOM']])
    controls=subprocess.run([sys.executable,str(ROOT/'scripts/save_preflight_controls.py')],cwd=REPO,
                            capture_output=True,text=True,timeout=60,check=True)
    controls_doc=json.loads(controls.stdout);assert all(controls_doc['checks'].values())
    dump(OUT/'preflight_controls.json',controls_doc)
    runs=[]
    for script,tag in [('primary_screw_audit59.py','save59_recovery_screw2'),
                       ('primary_cage_audit59c.py','save59_recovery_cage2'),
                       ('primary_socket_audit59b.py','save59_recovery_socket2')]:
        runs.append(bounded(script,tag))
    actual=load(prior/'summary.json')
    assert actual['accepted_physical_product_equilibria']==0
    assert not actual['whole_system_release'] and len(actual['remaining_unqualified_system_gate_ids'])==22
    assert actual['protected_peak_N'] is None and actual['global_energy_closure'] is None
    # Verify every original result plus recorded execution, not just exit code.
    for r in original['results']:
        d=load(REPO/r['path']); assert sha(REPO/r['path'])==r['SHA256']
        assert not d.get('whole_system_release',False)
    for r in actual['executions']:
        d=load(REPO/r['path']);assert sha(REPO/r['path'])==r['SHA256']
        assert d['reaped'] and not d['timeout'] and not d['STOP']
        assert sha(REPO/d['log']['path'])==d['log']['SHA256']
    status=dict(status='OPERATOR_SAVE59_CONTENT_AND_LOCAL_PHYSICS_AUDITS_VERIFIED_NOT_RELEASE',
                original_manager_checkpoint=ref(CP),original_manifest=ref(RT/'save_request59.json'),
                cause='Worker took start_untracked after creating four prior-state copies; used later inventory instead of original manager checkpoint.',
                omitted_new_prior_copies=copies,original_manifest_files=289,original_new_and_modified_files=293,
                stale_original_manifest_hashes=[],additional_original_manifest_files=[],
                protected_sources_unchanged=True,actual_original_user_files_verified=len(old_hashes),
                canonical_candidate=ref(ROOT/'cad/exports/primaryP1_captive59c/summary.json'),
                actual_parts=77,independent_recovery_audits=runs,controls=ref(OUT/'preflight_controls.json'),
                original_26_executions_checked=True,physics_scope='Necessary conditional cut statics, screw torque/virtual work, finite cage/socket geometry only.',
                accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],
                remaining_unqualified_system_gate_count=22,protected_peak_N=None,global_energy_closure=None,
                hardware_status='NOT_MEASURED',whole_system_release=False,
                safeguard='Unchanged Supervisor exact set/hash/index/guard remains final authority; original failure evidence preserved.',
                recovery_environment_failure_preserved='save59_operator_recovery1/save59_recovery_cage1_execution.json: missing skfem import; restored original recorded OCP+FEM PYTHONPATH, no model or criterion change.',
                source=ref(Path(__file__)))
    dump(OUT/'summary.json',status)
    # Operator authored additions are reviewed explicitly, then exact coverage is
    # independently checked against the original manager snapshot by Supervisor.
    paths=sorted(changed(REPO)|(untracked(REPO)-set(cp['preexisting_untracked'])))
    req=dict(original)
    req['files']=[ref(REPO/p) for p in paths]
    req['message']='Recover cycle59 exact archival omissions through unchanged Supervisor; add tested original-checkpoint save preflight'
    req['results']=original['results']+[ref(OUT/'summary.json')]
    assert not set(paths)&set(pins)
    assert inspect(REPO,req,cp,pins)['status']=='SAVE_PREFLIGHT_PASS'
    assert not REQUEST.exists() and not SEAL.exists()
    dump(REQUEST,req);dump(SEAL,seal(REPO,REQUEST,CP,pins))
    print(json.dumps(dict(status='RECOVERY_READY_FOR_AUTHORIZED_SUPERVISOR',files=len(paths),request=str(REQUEST),seal=str(SEAL))))


def commit():
    ledger=load(RT/'ledger.json');cp=load(CP);pins=ledger['source_pins'];req=load(REQUEST)
    assert ledger['sessions_started']==60 and ledger['completed_cycles']==58
    assert not (RT/'save_result59.json').exists()
    assert not (ROOT/'runtime/STOP').exists()
    verify(REPO,REQUEST,CP,pins,load(SEAL))
    record=engineering_record(req,REPO)
    assert record['signature'] not in ledger['seen_engineering_signatures']
    guard=ROOT.parent/'stage2_load_transfer/scripts/commit_guard.py'
    result=save(REPO,req,cp['HEAD'],set(cp['preexisting_untracked']),guard,pins[str(guard.relative_to(REPO))])
    dump(RT/'save_result59.json',result)
    classification=outcome(0,False,dict(external_limit=False,CLI_failed=False),True,record,ledger['seen_engineering_signatures'])
    assert classification=='VERIFIED_ENGINEERING_CYCLE'
    dump(RT/'cycle59.json',dict(classification=classification,before_HEAD=cp['HEAD'],after_HEAD=result['after_HEAD'],
                              exit_code=0,timed_out=False,saved=True,engineering=record,operator_recovery=True,
                              original_rejection=ref(RT/'save_error59.json'),recovery_audit=ref(OUT/'summary.json')))
    ledger.update(completed_cycles=59,last_engineering=record,no_progress=0,last_HEAD=result['after_HEAD'],
                  last_state='PAUSED',last_reason='OPERATOR_RECOVERED_READY_TO_RESUME')
    ledger['seen_engineering_signatures'].append(record['signature'])
    ledger['operator_recovery59']=dict(before_HEAD=cp['HEAD'],after_HEAD=result['after_HEAD'],
                                     audit=ref(OUT/'summary.json'),no_session_or_time_reset=True)
    dump(RT/'ledger.json',ledger)
    print(json.dumps(dict(status='SUPERVISOR_RECOVERY_SAVED',HEAD=result['after_HEAD'],sessions_started=60,
                          completed_cycles=59,recorded_child_seconds=ledger['recorded_child_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--save',action='store_true')
    args=parser.parse_args();commit() if args.save else prepare()
