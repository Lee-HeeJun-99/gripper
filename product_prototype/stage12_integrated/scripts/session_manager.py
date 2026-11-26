"""Opt-in bounded external CLI manager. Prepared, NOT installed or launched.

Never bypass approval/sandbox; no credentials inspected. Clean tracked tree
required; no reset/stash/checkout. User stop file + TERM/INT terminate own child.
Number of launches is a budget, not a guarantee of token/cost ceiling.
"""
import argparse,fcntl,json,os,signal,subprocess,time
from pathlib import Path
from baseline_registry import ROOT,REPO,sha,dump
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
def fingerprint():
    paths=[ROOT/'RELEASE_STATUS.json',ROOT/'INTEGRATED_TASKS.json',ROOT/'CURRENT_BASELINE.json']
    results={str(p.relative_to(REPO)):sha(p) for base in (ROOT/'validation',ROOT/'cad/exports',ROOT/'hardware_test/fixtures') for p in base.rglob('summary.json')}
    return dict(HEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),evidence={str(p.relative_to(REPO)):sha(p) for p in paths},actual_result_artifacts=results)
def has_progress(before,after):return before.get('actual_result_artifacts')!=after.get('actual_result_artifacts')
def command(prompt):return ['codex','exec','--sandbox','workspace-write','--json','-C',str(REPO),prompt]
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--max-runs',type=int,default=1);p.add_argument('--per-run-seconds',type=int,default=1800);p.add_argument('--tag',required=True);a=p.parse_args()
    if not 1<=a.max_runs<=10 or not 1<=a.per_run_seconds<=7200:p.error('Explicit bounds:1..10 runs,1..7200seconds each')
    prompt='Continue ReGrip Stage1/Stage2 integrated work. Read AGENTS.md, stage12_integrated/CHECKPOINT.md, actual Git and NEXT_TASK. Implement ONE bounded evidence-supported cycle, save results and local commit, then exit. No push, history rewrite, SDK change, purchase, hardware, credentials or Stage3. Never infer release from coupons. Respect stop file stage12_integrated/runtime/STOP and existing4GiB/420s child policy. No subagents. Preserve all historical files. If no safe task, document blockers and exit.'
    cmd=command(prompt)
    if not a.execute:print(json.dumps(dict(mode='DRY_RUN_NO_EXTERNAL_EXECUTION',command=cmd,max_runs=a.max_runs,seconds=a.per_run_seconds)));return
    runtime=ROOT/'runtime';runtime.mkdir(exist_ok=True);run=runtime/a.tag;run.mkdir(exist_ok=False)
    with (runtime/'manager.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if git('status','--porcelain','--untracked-files=no'):raise RuntimeError('Tracked worktree dirty; preserve it and stop, never clean automatically')
        if git('branch','--show-current')!='development/regrip-autonomous-research':raise RuntimeError('Wrong branch; never switch it automatically')
        halted=False;child=None
        def stop(sig,frame):
            nonlocal halted
            halted=True
            if child is not None and child.poll() is None:os.killpg(child.pid,signal.SIGTERM)
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        failures=0;log=[]
        for i in range(a.max_runs):
            if halted or (runtime/'STOP').exists():break
            before=fingerprint()
            # Always use a new bounded session, not --last in an unrelated repo.
            with (run/f'run{i}.jsonl').open('x') as output,(run/f'run{i}.stderr').open('x') as err:
                child=subprocess.Popen(cmd,cwd=REPO,stdout=output,stderr=err,start_new_session=True)
                deadline=time.monotonic()+a.per_run_seconds
                while child.poll() is None:
                    if halted or (runtime/'STOP').exists() or time.monotonic()>deadline:
                        os.killpg(child.pid,signal.SIGTERM)
                        try:child.wait(timeout=10)
                        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
                        halted=True;break
                    time.sleep(.5)
            after=fingerprint();progress=has_progress(before,after)
            if after['branch']!=before['branch'] or subprocess.run(['git','merge-base','--is-ancestor',before['HEAD'],after['HEAD']],cwd=REPO).returncode:
                halted=True # preserve unexpected state, never try to repair by reset
            dirty=bool(git('status','--porcelain','--untracked-files=no'))
            # No automatic cleanup of failed/uncommitted work.
            failures=failures+1 if child.returncode!=0 or not progress else 0
            log.append(dict(run=i,exit_code=child.returncode,before=before,after=after,progress=progress,dirty=dirty))
            dump(run/'summary.json',dict(runs=log,stopped=halted,automatic_cleanup=False))
            if dirty or failures>=2:break
            # Re-run actual gate, do not trust final message or stale status file.
            audit=subprocess.run(['python',str(ROOT/'scripts/integrated_release_gate.py'),'--tag',f'manager_{a.tag}_{i}'],cwd=REPO,stdout=subprocess.DEVNULL)
            if audit.returncode==0:break
        print(json.dumps(dict(runs=len(log),stopped=halted,logs=str(run))))
if __name__=='__main__':main()
