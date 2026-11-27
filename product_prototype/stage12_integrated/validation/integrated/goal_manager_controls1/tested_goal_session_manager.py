"""Goal-driven operator manager: no total session/time completion limit.

Existing Supervisor validation/commit code is reused unchanged. Runtime logs
are ignored, old data never cleaned. Workers cannot modify this trusted code.
Account/service limits, STOP, integrity failures and real stagnation pause it.
"""
import fcntl,json,os,shutil,signal,subprocess,sys,time
from pathlib import Path
from baseline_registry import ROOT,REPO,sha,dump
from supervised_save import untracked,changed,validate,save
from goal_manager_policy import PASS,engineering_record,outcome,stream_health

BRANCH='development/regrip-autonomous-research'
TRUSTED=('session_manager.py','goal_session_manager.py','goal_manager_policy.py','supervised_save.py','baseline_registry.py','integrated_release_gate.py')
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def command(prompt):return ['codex','exec','--sandbox','workspace-write','--json','-C',str(REPO),prompt]
def audit():
    code="import sys,json;sys.path.insert(0,'product_prototype/stage12_integrated/scripts');from integrated_release_gate import audit;from baseline_registry import ROOT;print(json.dumps(audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))))"
    r=subprocess.run([sys.executable,'-B','-c',code],cwd=REPO,capture_output=True,text=True,timeout=60)
    if r.returncode:raise RuntimeError('Independent gate process failed')
    d=json.loads(r.stdout)
    if d.get('status') not in (PASS,'INTEGRATED_NOT_QUALIFIED'):raise ValueError('Unknown gate verdict')
    if d['status']==PASS and d.get('errors'):raise ValueError('Inconsistent gate PASS')
    return d
def account_check():
    # No credential files opened, no API-key fallback or paid-provider selection.
    if any(os.environ.get(k) for k in ('OPENAI_API_KEY','CODEX_API_KEY')):raise RuntimeError('PAID_API_ENV_REQUIRES_EXPLICIT_BUDGET')
    r=subprocess.run(['codex','login','status'],capture_output=True,text=True,timeout=30)
    if r.returncode or 'logged in using chatgpt' not in (r.stdout+r.stderr).lower():raise RuntimeError('Existing account auth unavailable; do not inspect credentials or switch billing')
def stop_group(child):
    # A completed leader may still have analysis descendants in its own group.
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:child.wait(timeout=5)
    except subprocess.TimeoutExpired:pass
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
def source_pins():
    paths=[ROOT/'scripts'/n for n in TRUSTED]
    paths += [ROOT.parent/'stage2_load_transfer/scripts/commit_guard.py',ROOT.parent/'stage2_load_transfer/scripts/stage2_release_gate.py',ROOT.parent/'stage2_load_transfer/models/analytical/criteria.json']
    return {str(p.relative_to(REPO)):sha(p) for p in paths}
def running():return [t['id'] for t in json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())['tasks'] if t['status']=='RUNNING']
def historical_usage(runtime,current):
    records=[]
    for p in sorted(runtime.glob('authorized_*/')):
        if p==current:continue
        status=p/'status.json';summary=p/'summary.json'
        s=json.loads(status.read_text()) if status.exists() else {}
        d=json.loads(summary.read_text()) if summary.exists() else {}
        records.append(dict(tag=p.name,completed_sessions=max(s.get('completed_runs',0),len(d.get('runs',[]))),manager_wall_seconds=(d['finished_unix']-d['started_unix'] if 'finished_unix' in d and 'started_unix' in d else None),child_seconds=None))
    return records
def run_goal(args):
    if not 1<=args.per_run_seconds<=7200:raise ValueError('Worker time limit1..7200seconds required')
    if Path(args.tag).name!=args.tag or args.tag in ('.','..'):raise ValueError('Unsafe tag')
    if not args.execute:
        print(json.dumps(dict(mode='DRY_RUN_GOAL_ONLY',total_session_limit=None,total_research_time_limit=None,per_worker_seconds=args.per_run_seconds,sandbox='workspace-write',automatic_paid_fallback=False)));return
    runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True);run=runtime/args.tag
    with (runtime/'manager.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        lock.seek(0);lock.truncate();lock.write(str(os.getpid())+'\n');lock.flush()
        if git('branch','--show-current')!=BRANCH:raise RuntimeError('Wrong branch')
        if git('status','--porcelain','--untracked-files=no') or git('diff','--cached','--name-only'):raise RuntimeError('Preserve dirty tracked/index state; operator repair required')
        if running():raise RuntimeError('Running task needs process/state audit')
        pins=source_pins();guard=ROOT.parent/'stage2_load_transfer/scripts/commit_guard.py'
        if args.resume:
            ledger=json.loads((run/'ledger.json').read_text())
            if ledger['source_pins']!=pins:raise RuntimeError('Resume source mismatch; operator revalidation required')
        else:
            run.mkdir(exist_ok=False)
            ledger=dict(mode='GOAL_BASED',source_pins=pins,started_unix=time.time(),sessions_started=0,completed_cycles=0,recovery_workers=0,recorded_child_seconds=0.,historical_usage=historical_usage(runtime,run),seen_engineering_signatures=[],no_progress=0,strategy_reviews=0,account_usage=[],last_engineering=None)
        stopped=False;child=None;reason='NOT_COMPLETED';started=time.monotonic()
        def write(state,**extra):
            ledger.update(last_state=state,last_reason=extra.get('reason'),last_HEAD=git('rev-parse','HEAD'))
            dump(run/'ledger.json',ledger)
            dump(run/'status.json',dict(state=state,mode='GOAL_BASED',manager_PID=os.getpid(),tag=args.tag,max_runs=None,per_run_seconds=args.per_run_seconds,sessions_started=ledger['sessions_started'],completed_cycles=ledger['completed_cycles'],recovery_workers=ledger['recovery_workers'],recorded_child_seconds=ledger['recorded_child_seconds'],historical_completed_sessions=sum(x['completed_sessions'] for x in ledger['historical_usage']),total_completed_cycles=sum(x['completed_sessions'] for x in ledger['historical_usage'])+ledger['completed_cycles'],source_pins=pins,HEAD=ledger['last_HEAD'],updated_unix=time.time(),**extra))
        def halt(sig,frame):
            nonlocal stopped
            stopped=True
            if child is not None:
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
        signal.signal(signal.SIGTERM,halt);signal.signal(signal.SIGINT,halt)
        def check():
            if stopped or (runtime/'STOP').exists():return 'USER_STOP'
            if source_pins()!=pins:return 'TRUSTED_SOURCE_CHANGED'
            if shutil.disk_usage(REPO).free<2_000_000_000:return 'EXTERNAL_RESOURCE_LIMIT'
            return None
        def launch(prompt,prefix,seconds,recovery=False):
            nonlocal child
            if not recovery:ledger['sessions_started']+=1
            else:ledger['recovery_workers']+=1
            wall=time.monotonic();timed=False;log=run/(prefix+'.jsonl');err=run/(prefix+'.stderr')
            with log.open('x') as output,err.open('x') as error:
                child=subprocess.Popen(command(prompt),cwd=REPO,stdout=output,stderr=error,start_new_session=True)
                write('RECOVERY_RUNNING' if recovery else 'RESEARCH_RUNNING',run=prefix,child_PID=child.pid,deadline_unix=time.time()+seconds)
                while child.poll() is None:
                    if stopped or (runtime/'STOP').exists():break
                    if time.monotonic()-wall>=seconds:timed=True;break
                    time.sleep(.25)
                stop_group(child)
            ledger['recorded_child_seconds']+=time.monotonic()-wall
            health=stream_health(log,err);ledger['account_usage'].extend(health['usage'])
            return child.returncode,timed,health
        write('STARTING')
        try:
            account_check()
            while True:
                problem=check()
                if problem:reason=problem;break
                if git('status','--porcelain','--untracked-files=no'):reason='DIRTY_TRACKED_WORKTREE';break
                if running():reason='RUNNING_TASK_REQUIRES_AUDIT';break
                gate=audit();i=ledger['sessions_started'];dump(run/f'release_before{i}.json',gate)
                if gate['status']==PASS:
                    # Independent repeat, same source pins and committed identity.
                    head=git('rev-parse','HEAD');final=audit();dump(run/'final_release_audit.json',final)
                    if final['status']!=PASS or head!=git('rev-parse','HEAD') or check():reason='FINAL_AUDIT_INCONSISTENT';break
                    reason='INTEGRATED_RELEASE_GATE_PASS';write('COMPLETE',reason=reason);return
                before=git('rev-parse','HEAD');old=untracked(REPO);request=run/f'save_request{i}.json'
                dump(run/f'checkpoint_before{i}.json',dict(HEAD=before,preexisting_untracked=sorted(old),unmet_gate_errors=gate.get('errors',[]),running_tasks=running(),current_candidate=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text()) if (ROOT/'CURRENT_CANDIDATE.json').exists() else None))
                strategy=(' Previous cycle lacked unique engineering progress. Change mechanism/independent product track, do not retag/rerun old output.' if ledger['no_progress'] else '')
                prompt=f'''Continue authorized GOAL-BASED ReGrip Stage1/Stage2 engineering. Read AGENTS.md, latest actual Git, stage12_integrated/CHECKPOINT.md, GOAL_ENGINEERING_BRIEF.md, queue/NEXT_TASK and current candidate. Establish ONE primary actual minimal Motor->Drum->Tendon->Finger->Root->Ground Stage2 product specimen separate from the failed AO assembly; preserve3-Finger/cartridge/jamming extension. Reuse proven models and source-backed standard parts. Implement real CAD/load path, verify actual assembly and physical loads, preserve all failures. Do not only diagnose known collisions or produce ideal coupons. Work in one coherent candidate and update unmet22system gates and concrete next task, not a one-pass task list. No Stage3 until actual integrated release. No push/history rewrite/deletion/SDK/criteria relaxation/fake PASS/purchase/hardware/credentials/paid-provider selection/subagents/recursive launches. Workspace sandbox and child Git read-only boundaries stay intact. Do NOT modify manager/security/save/guard/gate sources listed in runtime ledger source_pins. Existing physical criteria unchanged. Respect runtime/STOP and4GiB/420s analysis children. Finish by{max(1,args.per_run_seconds-300)}seconds to allow saving. Record actual changed CAD,execution results,solved/remaining gates,failures,next mechanism in checkpoint. Exit with no RUNNING tasks or owned children. DO NOT git add/commit; authorized Supervisor saves exact verified bytes.
Write {request.relative_to(REPO)} with JSON keys expected_HEAD="{before}", message(one line<=160chars), files(ALL this-cycle modified/new nonignored files as path repository-relative and SHA256 actual digest), results(one or more newly-created actual research summary.json references drawn exactly from files), engineering_progress(category DESIGN_CHANGE or ACTUAL_PRODUCT_VALIDATION or BLOCKER_EVIDENCE,task_id exact selected queue ID,mechanism,system_gate_ids,actual_change_files from files,candidate_reference path/SHA256 for actual product validation,next_task_id,strategy_change boolean). Actual new CAD solids required for DESIGN_CHANGE; actual numerical product results required for validation. No prose-only progress or repeated retagging. Existing Supervisor exact allowlist/hash/immutableCAD/result/old-untracked/50MB/raw checks apply unchanged. Preserve all original user files. Save only stage1_manufacturing,stage2_load_transfer,stage12_integrated and four existing allowed common reports. Never modify existing evidence; use unique tags. If all meaningful work is externally blocked, include a new result with review of A/B/C alternatives and blockers; do not invent work or PASS.{strategy}'''
                code,timed,health=launch(prompt,f'run{i}',args.per_run_seconds)
                if check():reason=check();break
                if health['external_limit']:reason='EXTERNAL_ACCOUNT_OR_SERVICE_LIMIT';break
                # A time-limited worker is not project completion. Recover only
                # its exact current state/manifest; never reset/stash or hide data.
                if timed:
                    recovery=f'''SAVE-ONLY RECOVERY after bounded ReGrip worker timeout. No new research/manager/security/Git writes. All old worker descendants were terminated. Read {run.relative_to(REPO)}/checkpoint_before{i}.json and current actual files/results. Preserve all data. Complete interrupted state classification and {request.relative_to(REPO)} with original expected_HEAD {before},exact original manifest/schema from run{i}.jsonl. Account for every modified/new nonignored file against original preexisting_untracked; no deletes. Reclassify RUNNING only from actual stopped process/results, never manufacture PASS. Finish and exit within300seconds. If recovery is impossible explain exact state; do not bypass Supervisor.'''
                    code,again,rhealth=launch(recovery,f'recovery{i}',min(300,args.per_run_seconds),True)
                    if check():reason=check();break
                    if rhealth['external_limit']:reason='EXTERNAL_ACCOUNT_OR_SERVICE_LIMIT';break
                    if again or code:reason='TIMEOUT_RECOVERY_PAUSED';break
                saved=False;record=None;delta=changed(REPO)|(untracked(REPO)-old)
                if delta:
                    if code:reason='WORKER_FAILURE_WITH_UNSAVED_STATE';break
                    try:
                        if check():raise RuntimeError(check())
                        if running():raise RuntimeError('RUNNING task at save boundary')
                        req=json.loads(request.read_text());validate(REPO,req,before,old)
                        if any(r['path'] in pins for r in req['files']):raise ValueError('Trusted operator source in worker save')
                        record=engineering_record(req,REPO)
                        result=save(REPO,req,before,old,guard,pins[str(guard.relative_to(REPO))]);dump(run/f'save_result{i}.json',result);saved=True
                    except Exception as error:
                        dump(run/f'save_error{i}.json',dict(status='FAIL',error=type(error).__name__+': '+str(error),automatic_cleanup=False));reason='SUPERVISED_SAVE_OR_PROGRESS_REJECTED';break
                after=git('rev-parse','HEAD')
                if git('branch','--show-current')!=BRANCH or subprocess.run(['git','merge-base','--is-ancestor',before,after],cwd=REPO).returncode:reason='BRANCH_OR_HISTORY_CHANGED';break
                classification=outcome(code,timed,health,saved,record,ledger['seen_engineering_signatures'])
                dump(run/f'cycle{i}.json',dict(classification=classification,before_HEAD=before,after_HEAD=after,exit_code=code,timed_out=timed,saved=saved,engineering=record))
                if saved:ledger['completed_cycles']+=1;ledger['last_engineering']=record
                if classification=='VERIFIED_ENGINEERING_CYCLE':
                    ledger['seen_engineering_signatures'].append(record['signature']);ledger['no_progress']=0
                else:ledger['no_progress']+=1
                if ledger['no_progress']==2:ledger['strategy_reviews']+=1
                if ledger['no_progress']>=4:reason='STAGNATION_AFTER_STRATEGY_REVIEW';break
                if git('status','--porcelain','--untracked-files=no'):reason='DIRTY_AFTER_CYCLE';break
                if code and not timed:reason='WORKER_EXECUTION_FAILURE';break
                write('BETWEEN_CYCLES',last_cycle=classification)
        except Exception as error:
            reason='EXECUTION_OR_AUDIT_FAILURE';dump(run/'exception.json',dict(type=type(error).__name__,error=str(error),automatic_cleanup=False))
        finally:
            if child is not None:stop_group(child)
            ledger['manager_elapsed_seconds']=ledger.get('manager_elapsed_seconds',0)+time.monotonic()-started
            dump(run/'resume.json',dict(HEAD=git('rev-parse','HEAD'),reason=reason,dirty_tracked=git('status','--porcelain','--untracked-files=no'),running_tasks=running(),command=f'python3 product_prototype/stage12_integrated/scripts/session_manager.py --execute --until-release --resume --tag {args.tag} --per-run-seconds {args.per_run_seconds}',note='Do not bypass dirty/state/source/STOP checks; operator repair/revalidation may be required'))
            if reason!='INTEGRATED_RELEASE_GATE_PASS':write('PAUSED',reason=reason)
            else:write('COMPLETE',reason=reason)
            dump(run/'summary.json',dict(status='COMPLETE' if reason=='INTEGRATED_RELEASE_GATE_PASS' else 'PAUSED',stop_reason=reason,ledger=ledger,automatic_cleanup=False))
        print(json.dumps(dict(state='PAUSED' if reason!='INTEGRATED_RELEASE_GATE_PASS' else 'COMPLETE',reason=reason,sessions_started=ledger['sessions_started'],runtime=str(run))))
