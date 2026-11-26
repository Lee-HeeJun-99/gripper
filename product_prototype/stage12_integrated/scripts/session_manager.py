"""Opt-in bounded external CLI manager; live status never implies release.

Never bypass approval/sandbox; no credentials inspected. Clean tracked tree
required; no reset/stash/checkout. User stop file + TERM/INT terminate own child.
Number of launches is a budget, not a guarantee of token/cost ceiling.
"""
import argparse,fcntl,json,os,signal,subprocess,time,sys
from pathlib import Path
from baseline_registry import ROOT,REPO,sha,dump
from supervised_save import untracked,changed,save as supervised_save
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def fingerprint():
    paths=[ROOT/'RELEASE_STATUS.json',ROOT/'INTEGRATED_TASKS.json',ROOT/'CURRENT_BASELINE.json']
    results={str(p.relative_to(REPO)):sha(p) for base in (ROOT/'validation',ROOT/'cad/exports',ROOT/'hardware_test/fixtures') for p in base.rglob('summary.json')}
    return dict(HEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),evidence={str(p.relative_to(REPO)):sha(p) for p in paths},actual_result_artifacts=results)
def has_progress(before,after):return before.get('actual_result_artifacts')!=after.get('actual_result_artifacts')
def command(prompt):return ['codex','exec','--sandbox','workspace-write','--json','-C',str(REPO),prompt]
def active_tasks(queue):return [r['id'] for r in queue['tasks'] if r['status']=='RUNNING']
def signalled_child_stop(child):
    if child is None or child.poll() is not None:return
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:return
    try:child.wait(timeout=15)
    except subprocess.TimeoutExpired:
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        child.wait()
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--max-runs',type=int,default=1);p.add_argument('--per-run-seconds',type=int,default=1800);p.add_argument('--tag',required=True);a=p.parse_args()
    if not 1<=a.max_runs<=10 or not 1<=a.per_run_seconds<=7200:p.error('Explicit bounds:1..10 runs,1..7200seconds each')
    prompt='Continue ReGrip Stage1/Stage2 integrated research authorized by the user. Read AGENTS.md, product_prototype/stage12_integrated/CHECKPOINT.md, actual Git, queue and NEXT_TASK. Implement ONE bounded evidence-supported actual design/analysis cycle, run verification, preserve all failures, update queue/checkpoints, then submit the exact save manifest specified below and exit. DO NOT attempt git add/commit: child .git remains read-only. The separately authorized manager validates and performs only the explicit local save. Never bypass sandbox permissions. If READY is empty, inspect unmet release gates and independent mechanisms before declaring no safe work. Never create meaningless repeated experiments or count provenance/report-only artifacts as research progress. Goal SAME-REVISION STAGE1_STAGE2_INTEGRATED_DIGITAL_RELEASE_PASS. No push, history rewrite, deletion of old data, SDK change, tolerance relaxation, fake PASS, purchase, hardware, credentials, Stage3 or recursive/external manager launching. Do not modify session_manager.py, manager_controls.py, supervised_save.py, supervised_save_controls.py, commit_guard.py or criteria.json. Never infer system release from coupons or change old FAILs. Respect product_prototype/stage12_integrated/runtime/STOP and4GiB/420s analysis children. No subagents. Finish early enough to save a complete manifest; exit with no RUNNING tasks or live analysis children. The manager terminates the process group at its time budget. Preserve unrelated untracked files; never list them in the save manifest. Dependencies may be installed only within granted paths/permissions, with environments ignored by Git. If no safe task, document evidence-based blockers without inventing PASS.'
    cmd=command(prompt)
    if not a.execute:print(json.dumps(dict(mode='DRY_RUN_NO_EXTERNAL_EXECUTION',command=cmd,max_runs=a.max_runs,seconds=a.per_run_seconds)));return
    runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True)
    if Path(a.tag).name!=a.tag or a.tag in ('.','..'):p.error('Tag must be a single directory name')
    run=runtime/a.tag;run.mkdir(exist_ok=False)
    with (runtime/'manager.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        lock.seek(0);lock.truncate();lock.write(str(os.getpid())+'\n');lock.flush()
        if git('status','--porcelain','--untracked-files=no'):raise RuntimeError('Tracked worktree dirty; preserve it and stop, never clean automatically')
        if git('branch','--show-current')!='development/regrip-autonomous-research':raise RuntimeError('Wrong branch; never switch it automatically')
        halted=False;child=None;reason='RUN_BUDGET_EXHAUSTED';started=time.time()
        saver=ROOT/'scripts/supervised_save.py';guard=ROOT.parent/'stage2_load_transfer/scripts/commit_guard.py'
        metadata=dict(manager_PID=os.getpid(),tag=a.tag,max_runs=a.max_runs,per_run_seconds=a.per_run_seconds,maximum_child_seconds=a.max_runs*a.per_run_seconds,started_unix=started,manager_source_SHA256=sha(Path(__file__)),save_helper_SHA256=sha(saver),staged_guard_SHA256=sha(guard),automatic_cleanup=False)
        def status(state,**extra):dump(run/'status.json',dict(metadata,state=state,updated_unix=time.time(),**extra))
        status('STARTING')
        def stop(sig,frame):
            nonlocal halted
            halted=True
            if child is not None and child.poll() is None:
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        failures=0;log=[]
        for i in range(a.max_runs):
            if halted or (runtime/'STOP').exists():reason='USER_STOP';break
            if git('status','--porcelain','--untracked-files=no'):reason='DIRTY_TRACKED_WORKTREE';break
            if active_tasks(json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())):reason='RUNNING_TASK_RECORD_REQUIRES_PROCESS_AUDIT';break
            if sha(Path(__file__))!=metadata['manager_source_SHA256']:reason='MANAGER_SOURCE_CHANGED';break
            before=fingerprint()
            old_untracked=untracked(REPO)
            request_path=run/f'save_request{i}.json'
            save_prompt=f' Write {request_path.relative_to(REPO)} with JSON keys expected_HEAD="{before["HEAD"]}", message (one-line <=160 chars), files (ALL this-cycle modified/new nonignored files as {{"path":repository-relative path,"SHA256":actual digest}}), and results (one or more newly created research summary.json references drawn exactly from files). Only product_prototype/stage1_manufacturing, stage2_load_transfer, stage12_integrated and these4common reports may be saved: product_prototype/reports/CHECKPOINT.md, product_prototype/reports/AUTONOMOUS_RESUME.md, reports/INTEGRATED_CURRENT_STATUS.md, reports/INTEGRATED_NEXT_TASKS.md. Preserve existing CAD/BOM/results and use new tags. No deletion/symlink/raw CSV/>=50MB files. Do not list pre-existing untracked work. Record pending supervisor save honestly, never invent commit SHA. Every changed tracked file and every new nonignored file from this cycle must be listed. Use actual result references, not synthetic-only tests. Exit after the manifest is complete.'
            cmd=command(prompt+save_prompt)
            # Always use a new bounded session, not --last in an unrelated repo.
            with (run/f'run{i}.jsonl').open('x') as output,(run/f'run{i}.stderr').open('x') as err:
                child=subprocess.Popen(cmd,cwd=REPO,stdout=output,stderr=err,start_new_session=True)
                deadline=time.monotonic()+a.per_run_seconds
                status('RESEARCH_RUNNING',run=i,child_PID=child.pid,deadline_unix=time.time()+a.per_run_seconds,HEAD=before['HEAD'])
                while child.poll() is None:
                    if halted or (runtime/'STOP').exists() or time.monotonic()>deadline:
                        reason='USER_STOP' if halted or (runtime/'STOP').exists() else 'PER_RUN_TIME_LIMIT'
                        signalled_child_stop(child)
                        halted=True;break
                    time.sleep(.5)
            if not halted and child.returncode==0 and (changed(REPO) or untracked(REPO)-old_untracked):
                try:
                    if (runtime/'STOP').exists():raise RuntimeError('User STOP before save')
                    if active_tasks(json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())):raise RuntimeError('RUNNING task at save boundary')
                    if sha(saver)!=metadata['save_helper_SHA256']:raise RuntimeError('Save helper modified')
                    request=json.loads(request_path.read_text())
                    result=supervised_save(REPO,request,before['HEAD'],old_untracked,guard,metadata['staged_guard_SHA256'])
                    dump(run/f'save_result{i}.json',result)
                except Exception as error:
                    halted=True;reason='SUPERVISED_SAVE_REJECTED'
                    dump(run/f'save_error{i}.json',dict(status='FAIL',error=type(error).__name__+': '+str(error),automatic_cleanup=False))
            after=fingerprint();progress=has_progress(before,after)
            if after['branch']!=before['branch'] or subprocess.run(['git','merge-base','--is-ancestor',before['HEAD'],after['HEAD']],cwd=REPO).returncode:
                halted=True;reason='BRANCH_OR_HISTORY_CHANGED' # never reset
            dirty=bool(git('status','--porcelain','--untracked-files=no'))
            if active_tasks(json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())):halted=True;reason='RUNNING_TASK_RECORD_REQUIRES_PROCESS_AUDIT'
            # No automatic cleanup of failed/uncommitted work.
            failures=failures+1 if child.returncode!=0 or not progress else 0
            log.append(dict(run=i,exit_code=child.returncode,before=before,after=after,progress=progress,dirty=dirty))
            dump(run/'summary.json',dict(runs=log,stopped=halted,automatic_cleanup=False))
            status('BETWEEN_CYCLES',completed_runs=len(log),failures=failures,HEAD=after['HEAD'])
            if halted:break
            if dirty:reason='DIRTY_TRACKED_WORKTREE';break
            if failures>=2:reason='TWO_FAILURES_OR_NO_PROGRESS';break
            # Re-run actual gate, do not trust final message or stale status file.
            # Actual gate function, read-only; no supervisor-made tracked dirt.
            code="import sys,json;sys.path.insert(0,'product_prototype/stage12_integrated/scripts');from integrated_release_gate import audit;from baseline_registry import ROOT;print(json.dumps(audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))))"
            audit=subprocess.run([sys.executable,'-B','-c',code],cwd=REPO,capture_output=True,text=True,timeout=60)
            if audit.returncode:reason='RELEASE_AUDIT_EXECUTION_ERROR';break
            verdict=json.loads(audit.stdout);dump(run/f'release_audit{i}.json',verdict)
            if verdict['status']=='STAGE1_STAGE2_INTEGRATED_DIGITAL_RELEASE_PASS':reason='INTEGRATED_RELEASE_GATE_PASS';break
            if verdict['status']!='INTEGRATED_NOT_QUALIFIED':reason='RELEASE_AUDIT_EXECUTION_ERROR';break
        dump(run/'summary.json',dict(metadata,runs=log,stop_reason=reason,stopped=halted,finished_unix=time.time()))
        status('STOPPED',completed_runs=len(log),stop_reason=reason,HEAD=git('rev-parse','HEAD'))
        print(json.dumps(dict(runs=len(log),stopped=halted,stop_reason=reason,logs=str(run))))
if __name__=='__main__':main()
